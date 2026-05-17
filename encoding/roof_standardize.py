# -*- coding: utf-8 -*-
"""
BELDA - Energy Label Data Analyzer
Step: ROOF_DESCRIPTION Standardization

What this script does:
- Loads epc_walls_standardized.parquet
- Extracts ROOF_TYPE and ROOF_INSULATION from ROOF_DESCRIPTION
- Verifies the results
- Saves epc_roof_standardized.parquet with new columns added
  and ROOF_DESCRIPTION dropped

Output columns:
    ROOF_TYPE       — type of roof structure (6 categories)
    ROOF_INSULATION — insulation level (8 categories)
"""

import pandas as pd
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

# ============================================================
# 1. LOAD
# ============================================================
INPUT_FILE  = "epc_walls_standardized.parquet"
OUTPUT_FILE = "epc_roof_standardized.parquet"

print("Loading data...")
df = pd.read_parquet(INPUT_FILE)
print(f"Loaded {len(df):,} rows and {len(df.columns)} columns")


# ============================================================
# 2. HELPER: extract mm thickness from description string
# Handles formats like "100 mm", "100mm", "300+ mm", "300+mm"
# Returns the numeric value or None if not found
# ============================================================
def extract_mm(text):
    match = re.search(r'(\d+)\s*\+?\s*mm', text, re.IGNORECASE)
    if match:
        return int(match.group(1))
    return None


# ============================================================
# 3. CLASSIFY ROOF TYPE
# ============================================================
def classify_roof_type(desc):
    if pd.isna(desc):
        return "Unknown"

    d = str(desc).lower().strip()

    # No roof — another dwelling or premises above
    if any(phrase in d for phrase in [
        "another dwelling above",
        "other premises above",
        "other dwelling above",
        "annedd arall uwchben",   # Welsh: another dwelling above
        "eiddo arall uwchben",    # Welsh: other premises above
    ]):
        return "No Roof"

    # U-value / Welsh descriptions / corrupted → Unknown
    if "thermal transmittance" in d or "trawsyriannedd" in d:
        return "Unknown"

    # Thatched roof
    if "thatch" in d or "gwellt" in d:
        return "Thatched"

    # Roof room (converted loft / dormer)
    if "roof room" in d or "ystafell" in d and "to" in d:
        return "Roof Room"

    # Flat roof
    if d.startswith("flat") or "yn wastad" in d:
        return "Flat"

    # Pitched roof — most common, check after others
    if "pitched" in d or "ar oleddf" in d:
        return "Pitched"

    return "Unknown"


# ============================================================
# 4. CLASSIFY ROOF INSULATION
# ============================================================
def classify_roof_insulation(desc):
    if pd.isna(desc):
        return "Unknown"

    d = str(desc).lower().strip()

    # No roof above — insulation not applicable
    if any(phrase in d for phrase in [
        "another dwelling above",
        "other premises above",
        "other dwelling above",
        "annedd arall uwchben",
        "eiddo arall uwchben",
    ]):
        return "No Roof"

    # U-value / Welsh / corrupted → Unknown
    if "thermal transmittance" in d or "trawsyriannedd" in d:
        return "Unknown"

    # No insulation
    if "no insulation" in d or "dim inswleiddio" in d:
        return "None"

    # Limited insulation (vague — treat as Low)
    if "limited insulation" in d or "inswleiddio cyfyngedig" in d:
        return "Low"

    # Insulated at rafters — different method, own category
    if "insulated at rafters" in d or "wrth y trawstiau" in d or "wrth y trawstia" in d:
        return "At Rafters"

    # Ceiling insulated (roof rooms)
    if "ceiling insulated" in d or "nenfwd" in d:
        return "At Rafters"

    # Try to extract mm thickness and bucket it
    mm = extract_mm(str(desc))
    if mm is not None:
        if mm == 0:
            return "None"
        elif mm < 75:
            return "Low"          # 1–74mm
        elif mm < 200:
            return "Medium"       # 75–199mm
        elif mm < 300:
            return "High"         # 200–299mm
        else:
            return "Very High"    # 300mm+

    # Generic "insulated (assumed)" with no mm — treat as Medium
    if "insulated (assumed)" in d or "wedi" in d and "inswleiddio" in d:
        return "Medium"

    # Generic "insulated" with no further info
    if "insulated" in d:
        return "Medium"

    # Thatched with additional insulation
    if "additional insulation" in d or "inswleiddio ychwanegol" in d:
        return "Medium"

    # Plain thatched — natural insulation but no added layer
    if "thatch" in d or "gwellt" in d:
        return "Low"

    return "Unknown"


# ============================================================
# 5. APPLY CLASSIFICATION
# ============================================================
print("\nClassifying ROOF_TYPE...")
df["ROOF_TYPE"] = df["ROOF_DESCRIPTION"].apply(classify_roof_type)
print("✅ ROOF_TYPE done")

print("Classifying ROOF_INSULATION...")
df["ROOF_INSULATION"] = df["ROOF_DESCRIPTION"].apply(classify_roof_insulation)
print("✅ ROOF_INSULATION done")


# ============================================================
# 6. VERIFICATION
# ============================================================
print("\n--- ROOF_TYPE DISTRIBUTION ---")
rt = df["ROOF_TYPE"].value_counts()
rt_pct = (rt / len(df) * 100).round(2)
for cat, count in rt.items():
    print(f"  {cat:<30} {count:>10,}  ({rt_pct[cat]:.2f}%)")

print(f"\n  Total unique categories : {df['ROOF_TYPE'].nunique()}")
print(f"  Unclassified (Unknown)  : {(df['ROOF_TYPE'] == 'Unknown').sum():,}")

print("\n--- ROOF_INSULATION DISTRIBUTION ---")
ri = df["ROOF_INSULATION"].value_counts()
ri_pct = (ri / len(df) * 100).round(2)
for cat, count in ri.items():
    print(f"  {cat:<30} {count:>10,}  ({ri_pct[cat]:.2f}%)")

print(f"\n  Total unique categories : {df['ROOF_INSULATION'].nunique()}")
print(f"  Unclassified (Unknown)  : {(df['ROOF_INSULATION'] == 'Unknown').sum():,}")

# Cross-tab sanity check
print("\n--- CROSS CHECK: ROOF TYPE vs INSULATION ---")
cross = pd.crosstab(df["ROOF_TYPE"], df["ROOF_INSULATION"])
print(cross.to_string())

# Sample unclassified
print("\n--- SAMPLE OF UNCLASSIFIED ROOF_TYPE (Unknown) ---")
unk_sample = df[df["ROOF_TYPE"] == "Unknown"]["ROOF_DESCRIPTION"].value_counts().head(10)
if len(unk_sample) == 0:
    print("  None — all rows classified ✅")
else:
    for desc, count in unk_sample.items():
        print(f"  {count:>8,}  {desc}")

print("\n--- SAMPLE OF UNCLASSIFIED ROOF_INSULATION (Unknown) ---")
unk_sample2 = df[df["ROOF_INSULATION"] == "Unknown"]["ROOF_DESCRIPTION"].value_counts().head(10)
if len(unk_sample2) == 0:
    print("  None — all rows classified ✅")
else:
    for desc, count in unk_sample2.items():
        print(f"  {count:>8,}  {desc}")


# ============================================================
# 7. DROP ORIGINAL COLUMN
# ============================================================
print("\nDropping original ROOF_DESCRIPTION column...")
df = df.drop(columns=["ROOF_DESCRIPTION"])
print("✅ Dropped")


# ============================================================
# 8. SAVE
# ============================================================
print(f"\nSaving to {OUTPUT_FILE} ...")
df.to_parquet(OUTPUT_FILE, index=False)
print(f"✅ Saved. Final shape: {df.shape[0]:,} rows x {df.shape[1]} columns")
print(f"\nNew columns added : ROOF_TYPE, ROOF_INSULATION")
print(f"Column removed    : ROOF_DESCRIPTION")
print(f"\nNext step: run the same process for HOTWATER_DESCRIPTION")