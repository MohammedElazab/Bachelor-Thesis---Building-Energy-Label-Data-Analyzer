# -*- coding: utf-8 -*-
"""
BELDA - Energy Label Data Analyzer
Utility: Extract all unique WALLS_DESCRIPTION values

What this script does:
- Loads the ORIGINAL parquet file (before encoding)
- Extracts every unique value in WALLS_DESCRIPTION
- Saves them to a text file and a csv file so we can
  examine them and decide how to standardize
"""

import pandas as pd
import sys

sys.stdout.reconfigure(encoding='utf-8')

# ============================================================
# LOAD ONLY THE WALLS_DESCRIPTION COLUMN
# No need to load all 51 columns — saves memory and time
# ============================================================
INPUT_FILE = "epc_script4_4.parquet"

print(f"Loading WALLS_DESCRIPTION from {INPUT_FILE} ...")
df = pd.read_parquet(INPUT_FILE, columns=["WALLS_DESCRIPTION"])
print(f"Loaded {len(df):,} rows")

# ============================================================
# GET UNIQUE VALUES WITH THEIR COUNTS
# Sorted by frequency so we see the most common ones first
# ============================================================
print("Extracting unique values...")

value_counts = (
    df["WALLS_DESCRIPTION"]
    .value_counts(dropna=False)
    .reset_index()
)
value_counts.columns = ["WALLS_DESCRIPTION", "COUNT"]
value_counts["PERCENTAGE"] = (value_counts["COUNT"] / len(df) * 100).round(4)

print(f"Total unique values: {len(value_counts)}")

# ============================================================
# SAVE TO CSV — easy to inspect in Excel
# ============================================================
csv_path = "walls_description_unique.csv"
value_counts.to_csv(csv_path, index=False, encoding="utf-8")
print(f"Saved to: {csv_path}")

# ============================================================
# ALSO PRINT TOP 50 TO TERMINAL so you can see immediately
# ============================================================
print(f"\n--- TOP 50 MOST COMMON VALUES ---")
print(f"{'Count':>12}  {'%':>7}  Description")
print("-" * 80)

for _, row in value_counts.head(50).iterrows():
    desc  = str(row["WALLS_DESCRIPTION"])
    count = int(row["COUNT"])
    pct   = float(row["PERCENTAGE"])
    print(f"{count:>12,}  {pct:>6.2f}%  {desc}")

print(f"\n--- BOTTOM 20 (RAREST VALUES) ---")
print(f"{'Count':>12}  {'%':>7}  Description")
print("-" * 80)

for _, row in value_counts.tail(20).iterrows():
    desc  = str(row["WALLS_DESCRIPTION"])
    count = int(row["COUNT"])
    pct   = float(row["PERCENTAGE"])
    print(f"{count:>12,}  {pct:>6.2f}%  {desc}")

print(f"\nDone. Open walls_description_unique.csv to see all {len(value_counts)} values.")