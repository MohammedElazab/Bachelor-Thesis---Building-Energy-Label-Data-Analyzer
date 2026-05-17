# -*- coding: utf-8 -*-
"""
BELDA - Energy Label Data Analyzer
Utility: Extract all unique HOTWATER_DESCRIPTION values
"""

import pandas as pd
import sys

sys.stdout.reconfigure(encoding='utf-8')

INPUT_FILE = "epc_roof_standardized.parquet"

print(f"Loading HOTWATER_DESCRIPTION from {INPUT_FILE} ...")
df = pd.read_parquet(INPUT_FILE, columns=["HOTWATER_DESCRIPTION"])
print(f"Loaded {len(df):,} rows")

print("Extracting unique values...")

value_counts = (
    df["HOTWATER_DESCRIPTION"]
    .value_counts(dropna=False)
    .reset_index()
)
value_counts.columns = ["HOTWATER_DESCRIPTION", "COUNT"]
value_counts["PERCENTAGE"] = (value_counts["COUNT"] / len(df) * 100).round(4)

print(f"Total unique values: {len(value_counts)}")

csv_path = "hotwater_description_unique.csv"
value_counts.to_csv(csv_path, index=False, encoding="utf-8")
print(f"Saved to: {csv_path}")

print(f"\n--- TOP 50 MOST COMMON VALUES ---")
print(f"{'Count':>12}  {'%':>7}  Description")
print("-" * 80)

for _, row in value_counts.head(50).iterrows():
    desc  = str(row["HOTWATER_DESCRIPTION"])
    count = int(row["COUNT"])
    pct   = float(row["PERCENTAGE"])
    print(f"{count:>12,}  {pct:>6.2f}%  {desc}")

print(f"\n--- BOTTOM 20 (RAREST VALUES) ---")
print(f"{'Count':>12}  {'%':>7}  Description")
print("-" * 80)

for _, row in value_counts.tail(20).iterrows():
    desc  = str(row["HOTWATER_DESCRIPTION"])
    count = int(row["COUNT"])
    pct   = float(row["PERCENTAGE"])
    print(f"{count:>12,}  {pct:>6.2f}%  {desc}")

print(f"\nDone. Open {csv_path} to see all {len(value_counts)} values.")