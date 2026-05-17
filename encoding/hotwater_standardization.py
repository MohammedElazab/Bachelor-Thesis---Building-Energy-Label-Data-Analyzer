# -*- coding: utf-8 -*-
"""
BELDA - Energy Label Data Analyzer
Step: HOTWATER_DESCRIPTION Standardization

What this script does:
- Loads epc_roof_standardized.parquet
- Extracts HOTWATER_SOURCE and HOTWATER_SOLAR from HOTWATER_DESCRIPTION
- Verifies the results
- Saves epc_hotwater_standardized.parquet with new columns added
  and HOTWATER_DESCRIPTION dropped

Output columns:
    HOTWATER_SOURCE — where the hot water comes from (8 categories)
    HOTWATER_SOLAR  — whether solar panels supplement hot water (0/1 flag)
"""

import pandas as pd
import sys

sys.stdout.reconfigure(encoding='utf-8')

# ============================================================
# 1. LOAD
# ============================================================
INPUT_FILE  = "epc_roof_standardized.parquet"
OUTPUT_FILE = "epc_hotwater_standardized.parquet"

print("Loading data...")
df = pd.read_parquet(INPUT_FILE)
print(f"Loaded {len(df):,} rows and {len(df.columns)} columns")


# ============================================================
# 2. CLASSIFY HOTWATER SOURCE
# ============================================================
def classify_hotwater_source(desc):
    """
    Extracts the primary hot water source from the description.
    Returns one of 8 standardized categories.
    """
    if pd.isna(desc):
        return "Unknown"

    d = str(desc).lower().strip()

    # Blank or whitespace only
    if d == "" or d == "description":
        return "Unknown"

    # Welsh / corrupted
    if any(w in d for w in [
        "twymwr", "tanddwr", "brif system", "o'r brif",
        "cynllun cymunedol", "trochi trydan", "trydan ar unwaith",
        "bwyler", "popty", "dim system", "o gynllun",
    ]):
        return "Unknown"

    # Heat pump — check before electric to avoid overlap
    if any(phrase in d for phrase in [
        "heat pump",
        "community heat pump",
    ]):
        return "Heat Pump"

    # Community scheme
    if "community" in d or "community scheme" in d:
        return "Community"

    # Electric immersion / instantaneous / no system (defaults to immersion)
    if any(phrase in d for phrase in [
        "electric immersion",
        "electric instantaneous",
        "instantaneous at point of use",
        "no system present",
        "no hot water system",
        "electric multipoint",
        "electric heat pump for water",  # water-only heat pump
    ]):
        return "Electric Immersion"

    # Dedicated gas system (not the main boiler)
    if any(phrase in d for phrase in [
        "gas multipoint",
        "gas instantaneous",
        "gas boiler/circulator",
        "gas range cooker",
        "single-point gas",
        "point gas water heater",
        "back boiler",
    ]):
        return "Dedicated Gas"

    # Dedicated oil system
    if any(phrase in d for phrase in [
        "oil range cooker",
        "oil boiler/circulator",
    ]):
        return "Dedicated Oil"

    # Solid fuel
    if any(phrase in d for phrase in [
        "solid fuel",
        "room heaters",
    ]):
        return "Dedicated Solid Fuel"

    # From main system — most common, check after all specific ones
    if any(phrase in d for phrase in [
        "from main system",
        "from main heating system",
        "from second main heating system",
        "from secondary system",
        "from secondary heater",
        "from community scheme",
        "from hot-water only community",
    ]):
        return "Main System"

    return "Unknown"


# ============================================================
# 3. CLASSIFY SOLAR FLAG
# ============================================================
def classify_hotwater_solar(desc):
    """
    Returns 1 if solar panels supplement the hot water system, 0 otherwise.
    """
    if pd.isna(desc):
        return 0

    d = str(desc).lower().strip()

    if "plus solar" in d or "solar" in d:
        return 1

    return 0


# ============================================================
# 4. APPLY CLASSIFICATION
# ============================================================
print("\nClassifying HOTWATER_SOURCE...")
df["HOTWATER_SOURCE"] = df["HOTWATER_DESCRIPTION"].apply(classify_hotwater_source)
print("✅ HOTWATER_SOURCE done")

print("Classifying HOTWATER_SOLAR...")
df["HOTWATER_SOLAR"] = df["HOTWATER_DESCRIPTION"].apply(classify_hotwater_solar)
print("✅ HOTWATER_SOLAR done")


# ============================================================
# 5. VERIFICATION
# ============================================================
print("\n--- HOTWATER_SOURCE DISTRIBUTION ---")
hs = df["HOTWATER_SOURCE"].value_counts()
hs_pct = (hs / len(df) * 100).round(2)
for cat, count in hs.items():
    print(f"  {cat:<25} {count:>10,}  ({hs_pct[cat]:.2f}%)")

print(f"\n  Total unique categories : {df['HOTWATER_SOURCE'].nunique()}")
print(f"  Unclassified (Unknown)  : {(df['HOTWATER_SOURCE'] == 'Unknown').sum():,}")

print("\n--- HOTWATER_SOLAR DISTRIBUTION ---")
solar = df["HOTWATER_SOLAR"].value_counts()
for val, count in solar.items():
    pct = count / len(df) * 100
    label = "Has solar" if val == 1 else "No solar"
    print(f"  {label:<25} {count:>10,}  ({pct:.2f}%)")

# Cross-tab sanity check
print("\n--- CROSS CHECK: HOTWATER SOURCE vs SOLAR ---")
cross = pd.crosstab(df["HOTWATER_SOURCE"], df["HOTWATER_SOLAR"])
cross.columns = ["No Solar", "Has Solar"]
print(cross.to_string())

# Sample unclassified
print("\n--- SAMPLE OF UNCLASSIFIED HOTWATER_SOURCE (Unknown) ---")
unk_sample = df[df["HOTWATER_SOURCE"] == "Unknown"]["HOTWATER_DESCRIPTION"].value_counts().head(15)
if len(unk_sample) == 0:
    print("  None — all rows classified ✅")
else:
    for desc, count in unk_sample.items():
        print(f"  {count:>8,}  {desc}")


# ============================================================
# 6. DROP ORIGINAL COLUMN
# ============================================================
print("\nDropping original HOTWATER_DESCRIPTION column...")
df = df.drop(columns=["HOTWATER_DESCRIPTION"])
print("✅ Dropped")


# ============================================================
# 7. SAVE
# ============================================================
print(f"\nSaving to {OUTPUT_FILE} ...")
df.to_parquet(OUTPUT_FILE, index=False)
print(f"✅ Saved. Final shape: {df.shape[0]:,} rows x {df.shape[1]} columns")
print(f"\nNew columns added : HOTWATER_SOURCE, HOTWATER_SOLAR")
print(f"Column removed    : HOTWATER_DESCRIPTION")
print(f"\nNext step: re-run the encoding script on epc_hotwater_standardized.parquet")