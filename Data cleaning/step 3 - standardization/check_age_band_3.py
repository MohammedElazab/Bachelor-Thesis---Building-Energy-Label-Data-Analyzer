"""
BELDA — Task 3 Prep: Unique CONSTRUCTION_AGE_BAND values
=========================================================
Scans the full dataset and prints every unique value in
CONSTRUCTION_AGE_BAND so we can define era groupings.

Usage
-----
    python check_age_band_3.py
"""

import pyarrow.parquet as pq
import pandas as pd

INPUT = "epc_changing_letters_to_numbers_clean.parquet"

parquet_file = pq.ParquetFile(INPUT)
unique_vals  = set() 

for batch in parquet_file.iter_batches(
        batch_size=500_000,
        columns=["CONSTRUCTION_AGE_BAND"]):
    df = batch.to_pandas()
    unique_vals.update(df["CONSTRUCTION_AGE_BAND"].dropna().unique().tolist())

print(f"Total unique values: {len(unique_vals)}\n")
for v in sorted(unique_vals):
    print(f"  '{v}'")