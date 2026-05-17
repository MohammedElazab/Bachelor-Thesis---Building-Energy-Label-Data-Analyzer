# -*- coding: utf-8 -*-
"""
BELDA - Energy Label Data Analyzer
Step: Final Encoding v3

What this script does:
- Loads epc_hotwater_standardized.parquet (39 columns)
- Applies ordinal encoding to ordered categories
- Applies one-hot encoding to unordered categories
- Drops label_gap_readable (replaced by improvement_potential)
- Saves final epc_encoded.parquet ready for model training

Changes from v2:
- Input is now epc_hotwater_standardized.parquet (not the original)
- Added encoding for 6 new columns:
    WALL_TYPE, WALL_INSULATION (from walls standardization)
    ROOF_TYPE, ROOF_INSULATION (from roof standardization)
    HOTWATER_SOURCE, HOTWATER_SOLAR (from hotwater standardization)
- WALLS_DESCRIPTION, ROOF_DESCRIPTION, HOTWATER_DESCRIPTION
  already dropped in previous steps
"""

import pandas as pd
import sys

sys.stdout.reconfigure(encoding='utf-8')

# ============================================================
# 1. LOAD
# ============================================================
INPUT_FILE  = "epc_hotwater_standardized.parquet"
OUTPUT_FILE = "epc_encoded.parquet"

print("Loading data...")
df = pd.read_parquet(INPUT_FILE)
print(f"Loaded {len(df):,} rows and {len(df.columns)} columns")
print(f"Columns: {list(df.columns)}")


# ============================================================
# 2. DROP COLUMNS WE DON'T NEED
# ============================================================
print("\n--- DROPPING UNNECESSARY COLUMNS ---")

cols_to_drop = [
    "label_gap_readable",  # text like "D→B" — use improvement_potential instead
]

cols_to_drop = [col for col in cols_to_drop if col in df.columns]
if cols_to_drop:
    df = df.drop(columns=cols_to_drop)
    print(f"Dropped: {cols_to_drop}")
else:
    print("Nothing to drop — already removed in previous steps")


# ============================================================
# 3. ORDINAL ENCODING
# Columns with a natural order — lower number = worse/older
# ============================================================
print("\n--- APPLYING ORDINAL ENCODING ---")

# --- Construction Age Band ---
age_band_order = {
    "Pre-1900"     : 1,
    "1900-1929"    : 2,
    "1930-1949"    : 3,
    "1950-1966"    : 4,
    "1967-1975"    : 5,
    "1976-1982"    : 6,
    "1983-1990"    : 7,
    "1991-1995"    : 8,
    "1996-2002"    : 9,
    "2003-2006"    : 10,
    "2007 onwards" : 11,
}

if "CONSTRUCTION_AGE_BAND" in df.columns:
    df["CONSTRUCTION_AGE_BAND"] = df["CONSTRUCTION_AGE_BAND"].map(age_band_order)
    df["CONSTRUCTION_AGE_BAND"] = df["CONSTRUCTION_AGE_BAND"].fillna(0).astype(int)
    print("✅ CONSTRUCTION_AGE_BAND encoded")


# --- CO2 Intensity Category ---
co2_order = {
    "Low"    : 1,
    "Medium" : 2,
    "High"   : 3,
}

if "co2_intensity_category" in df.columns:
    df["co2_intensity_category"] = df["co2_intensity_category"].map(co2_order)
    df["co2_intensity_category"] = df["co2_intensity_category"].fillna(0).astype(int)
    print("✅ co2_intensity_category encoded")


# --- Wall Insulation ---
# Ordered from worst to best insulation
wall_insulation_order = {
    "Unknown"    : 0,
    "Uninsulated": 1,
    "Partial"    : 2,
    "Insulated"  : 3,
}

if "WALL_INSULATION" in df.columns:
    df["WALL_INSULATION"] = df["WALL_INSULATION"].map(wall_insulation_order)
    df["WALL_INSULATION"] = df["WALL_INSULATION"].fillna(0).astype(int)
    print("✅ WALL_INSULATION encoded")


# --- Roof Insulation ---
# Ordered from no insulation to maximum insulation
roof_insulation_order = {
    "Unknown"   : 0,
    "No Roof"   : 0,  # not applicable — same as unknown for model purposes
    "None"      : 1,
    "Low"       : 2,
    "At Rafters": 3,  # different method but reasonable mid-level performance
    "Medium"    : 4,
    "High"      : 5,
    "Very High" : 6,
}

if "ROOF_INSULATION" in df.columns:
    df["ROOF_INSULATION"] = df["ROOF_INSULATION"].map(roof_insulation_order)
    df["ROOF_INSULATION"] = df["ROOF_INSULATION"].fillna(0).astype(int)
    print("✅ ROOF_INSULATION encoded")


# ============================================================
# 4. ONE-HOT ENCODING
# Columns with no natural order — each category gets its own 0/1 column
# ============================================================
print("\n--- APPLYING ONE-HOT ENCODING ---")

one_hot_cols = [
    # Original columns
    "PROPERTY_TYPE",
    "BUILT_FORM",
    "built_form_simplified",
    "MAIN_FUEL",
    "MAINHEAT_DESCRIPTION",
    "WINDOWS_DESCRIPTION",
    # New standardized columns
    "WALL_TYPE",
    "ROOF_TYPE",
    "HOTWATER_SOURCE",
]

# Only encode columns that actually exist
one_hot_cols = [col for col in one_hot_cols if col in df.columns]
print(f"One-hot encoding: {one_hot_cols}")

df = pd.get_dummies(
    df,
    columns=one_hot_cols,
    drop_first=True,
    dtype=int
)

print(f"✅ One-hot encoding done. Dataframe now has {len(df.columns)} columns")


# ============================================================
# 5. VERIFY HOTWATER_SOLAR IS ALREADY BINARY
# It was created as 0/1 so no encoding needed — just confirm
# ============================================================
if "HOTWATER_SOLAR" in df.columns:
    unique_vals = df["HOTWATER_SOLAR"].unique()
    if set(unique_vals).issubset({0, 1}):
        print("✅ HOTWATER_SOLAR already binary (0/1) — no encoding needed")
    else:
        print(f"⚠️  HOTWATER_SOLAR has unexpected values: {unique_vals}")


# ============================================================
# 6. FINAL VERIFICATION
# ============================================================
print("\n--- FINAL VERIFICATION ---")

remaining_text_cols = df.select_dtypes(include="object").columns.tolist()

if len(remaining_text_cols) == 0:
    print("✅ All columns are now numeric. Data is model-ready.")
else:
    print(f"⚠️  These columns are still text:")
    for col in remaining_text_cols:
        sample = df[col].dropna().unique()[:5]
        print(f"   {col}: {sample}")


# ============================================================
# 7. FINAL SUMMARY
# ============================================================
print("\n--- FINAL DATASET SUMMARY ---")
print(f"Total rows    : {len(df):,}")
print(f"Total columns : {len(df.columns)}")
print(f"\nAll columns and their types:")
for col in df.columns:
    print(f"  {col:50s} {str(df[col].dtype)}")


# ============================================================
# 8. SAVE
# ============================================================
print(f"\nSaving to {OUTPUT_FILE} ...")
df.to_parquet(OUTPUT_FILE, index=False)
print(f"✅ Done. File saved: {OUTPUT_FILE}")
print(f"\nYour fully encoded dataset is ready for model training.")
print(f"Next step: EDA and model training.")