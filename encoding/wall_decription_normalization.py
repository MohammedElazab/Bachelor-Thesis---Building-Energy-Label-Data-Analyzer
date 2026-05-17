# -*- coding: utf-8 -*-
"""
BELDA - Energy Label Data Analyzer
Step: WALLS_DESCRIPTION Standardization

What this script does:
- Loads the ORIGINAL parquet file
- Extracts WALL_TYPE and WALL_INSULATION from WALLS_DESCRIPTION
- Verifies the results
- Saves a new parquet with both new columns added
  and WALLS_DESCRIPTION dropped

Output columns:
    WALL_TYPE       — what the wall is made of (10 categories)
    WALL_INSULATION — insulation status (5 categories)
"""

import pandas as pd
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

# ============================================================
# 1. LOAD ONLY WHAT WE NEED
# ============================================================
INPUT_FILE  = "epc_script4_4.parquet"
OUTPUT_FILE = "epc_walls_standardized.parquet"

print("Loading data...")
df = pd.read_parquet(INPUT_FILE)
print(f"Loaded {len(df):,} rows and {len(df.columns)} columns")


# ============================================================
# 2. DEFINE CLASSIFICATION FUNCTIONS
# ============================================================

def classify_wall_type(desc):
    """
    Extracts the wall material type from the description string.
    Returns one of 10 standardized categories.
    """
    if pd.isna(desc):
        return "Unknown"

    d = str(desc).lower().strip()

    # U-value only entries — no wall type info available, treat as Unknown
    if "thermal transmittance" in d or "trawsyriannedd" in d:
        return "Unknown"

    # Cavity wall — check before "solid" to avoid false matches
    if "cavity" in d or "ceudod" in d:
        return "Cavity"

    # Solid brick (English and Welsh)
    if "solid brick" in d or "briciau solet" in d:
        return "Solid Brick"

    # Timber frame (English and Welsh)
    if "timber frame" in d or "ffr" in d and "m bren" in d:
        return "Timber Frame"

    # Sandstone or limestone (various spellings)
    if "sandstone" in d or "limestone" in d or "tywodfaen" in d:
        return "Sandstone / Limestone"

    # Granite or whinstone (English and Welsh)
    if "granite" in d or "whinstone" in d or "gwenithfaen" in d or "risgraig" in d:
        return "Granite / Whinstone"

    # System built (English and Welsh)
    if "system built" in d or "system" in d and "hadeiladu" in d:
        return "System Built"

    # Cob (traditional earth wall)
    if "cob" in d:
        return "Cob"

    # Park home wall
    if "park home" in d:
        return "Park Home"

    # Basement wall
    if "basement" in d:
        return "Basement"

    # Curtain wall
    if "curtain" in d:
        return "Curtain Wall"

    return "Other"


def classify_wall_insulation(desc):
    """
    Extracts the insulation status from the description string.
    Returns one of 5 standardized categories.
    """
    if pd.isna(desc):
        return "Unknown"

    d = str(desc).lower().strip()

    # U-value only — insulation status embedded in the number, not the text
    # Grouped into Unknown since we can't derive insulation type from a number alone
    if "thermal transmittance" in d or "trawsyriannedd" in d:
        return "Unknown"

    # Fully insulated — filled cavity, external, internal, additional insulation
    if any(phrase in d for phrase in [
        "filled cavity",
        "with external insulation",
        "with internal insulation",
        "with additional insulation",
        "insulated at rafters",
        "insulated (assumed)",
        ", insulated",
        "wedi",           # Welsh for "has been" — appears in insulated phrases
        "inswleiddio a",  # Welsh: "insulated with"
        "gydag inswleiddio",  # Welsh: "with insulation"
    ]):
        # Make sure "no insulation" and "partial" don't sneak in here
        if "no insulation" not in d and "partial" not in d and "dim inswleiddio" not in d:
            return "Insulated"

    # Partial insulation
    if "partial insulation" in d or "rhannol" in d or "limited" in d:
        return "Partial"

    # No insulation (English and Welsh)
    if "no insulation" in d or "dim inswleiddio" in d:
        return "Uninsulated"

    # As built with no explicit insulation mention — treat as uninsulated
    if "as built" in d and "insul" not in d:
        return "Uninsulated"

    return "Unknown"


# ============================================================
# 3. APPLY THE CLASSIFICATION
# ============================================================
print("\nClassifying WALL_TYPE...")
df["WALL_TYPE"] = df["WALLS_DESCRIPTION"].apply(classify_wall_type)
print("✅ WALL_TYPE done")

print("Classifying WALL_INSULATION...")
df["WALL_INSULATION"] = df["WALLS_DESCRIPTION"].apply(classify_wall_insulation)
print("✅ WALL_INSULATION done")


# ============================================================
# 4. VERIFICATION
# ============================================================
print("\n--- WALL_TYPE DISTRIBUTION ---")
wt = df["WALL_TYPE"].value_counts()
wt_pct = (wt / len(df) * 100).round(2)
for cat, count in wt.items():
    print(f"  {cat:<25} {count:>10,}  ({wt_pct[cat]:.2f}%)")

print(f"\n  Total unique categories: {df['WALL_TYPE'].nunique()}")
print(f"  Unclassified (Other/Unknown): {(df['WALL_TYPE'].isin(['Other', 'Unknown'])).sum():,}")
# Note: U-Value Only entries are merged into Unknown

print("\n--- WALL_INSULATION DISTRIBUTION ---")
wi = df["WALL_INSULATION"].value_counts()
wi_pct = (wi / len(df) * 100).round(2)
for cat, count in wi.items():
    print(f"  {cat:<25} {count:>10,}  ({wi_pct[cat]:.2f}%)")

print(f"\n  Total unique categories: {df['WALL_INSULATION'].nunique()}")
print(f"  Unclassified (Unknown): {(df['WALL_INSULATION'] == 'Unknown').sum():,}")

# Cross-tab: wall type vs insulation status — sanity check
print("\n--- CROSS CHECK: WALL TYPE vs INSULATION STATUS ---")
cross = pd.crosstab(df["WALL_TYPE"], df["WALL_INSULATION"])
print(cross.to_string())

# Check a sample of "Other" and "Unknown" to catch misclassifications
print("\n--- SAMPLE OF UNCLASSIFIED WALL_TYPE (Other) ---")
other_sample = df[df["WALL_TYPE"] == "Other"]["WALLS_DESCRIPTION"].value_counts().head(10)
for desc, count in other_sample.items():
    print(f"  {count:>8,}  {desc}")

print("\n--- SAMPLE OF UNCLASSIFIED WALL_INSULATION (Unknown) ---")
unk_sample = df[df["WALL_INSULATION"] == "Unknown"]["WALLS_DESCRIPTION"].value_counts().head(10)
for desc, count in unk_sample.items():
    print(f"  {count:>8,}  {desc}")


# ============================================================
# 5. DROP ORIGINAL WALLS_DESCRIPTION
# ============================================================
print("\nDropping original WALLS_DESCRIPTION column...")
df = df.drop(columns=["WALLS_DESCRIPTION"])
print("✅ Dropped")


# ============================================================
# 6. SAVE
# ============================================================
print(f"\nSaving to {OUTPUT_FILE} ...")
df.to_parquet(OUTPUT_FILE, index=False)
print(f"✅ Saved. Final shape: {df.shape[0]:,} rows x {df.shape[1]} columns")
print(f"\nNew columns added : WALL_TYPE, WALL_INSULATION")
print(f"Column removed    : WALLS_DESCRIPTION")
print(f"\nNext step: run the same process for ROOF_DESCRIPTION and HOTWATER_DESCRIPTION")