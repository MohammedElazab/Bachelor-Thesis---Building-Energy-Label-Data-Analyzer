"""
BELDA — Task 3 Prep: Count bad CONSTRUCTION_AGE_BAND values
=============================================================
Counts how many rows contain:
  - Future years (> 2026)
  - 'INVALID!' entries
  - 'NO DATA!' entries
  - Valid single years (1600-2026)
  - Standard England and Wales bands

Usage
-----
    python check_age_band_bad_values_3.py
"""

import pyarrow.parquet as pq
import pandas as pd

INPUT      = "epc_changing_letters_to_numbers_clean.parquet"
BATCH_SIZE = 500_000

# Anything above this year is a data entry error
MAX_VALID_YEAR = 2026

count_future  = 0
count_invalid = 0
count_nodata  = 0
count_valid_year   = 0
count_standard_band = 0
count_total   = 0

future_values = {}   # track which future years appear and how often

parquet_file = pq.ParquetFile(INPUT)

for batch in parquet_file.iter_batches(
        batch_size=BATCH_SIZE,
        columns=["CONSTRUCTION_AGE_BAND"]):
    df = batch.to_pandas()
    count_total += len(df)

    for val in df["CONSTRUCTION_AGE_BAND"]:
        if pd.isna(val):
            continue
        val = str(val).strip()

        if val == "INVALID!":
            count_invalid += 1
        elif val == "NO DATA!":
            count_nodata += 1
        elif val.startswith("England and Wales"):
            count_standard_band += 1
        elif val.isdigit():
            year = int(val)
            if year > MAX_VALID_YEAR:
                count_future += 1
                future_values[val] = future_values.get(val, 0) + 1
            else:
                count_valid_year += 1

print("=" * 60)
print("  BELDA - Task 3: CONSTRUCTION_AGE_BAND Bad Value Count")
print("=" * 60)
print(f"\n  Total rows scanned       : {count_total:>12,}")
print(f"\n  Standard bands           : {count_standard_band:>12,}  "
      f"({count_standard_band/count_total*100:.3f}%)")
print(f"  Valid single years       : {count_valid_year:>12,}  "
      f"({count_valid_year/count_total*100:.3f}%)")
print(f"\n  --- Bad values ---")
print(f"  Future years (> {MAX_VALID_YEAR})    : {count_future:>12,}  "
      f"({count_future/count_total*100:.3f}%)")
print(f"  INVALID!                 : {count_invalid:>12,}  "
      f"({count_invalid/count_total*100:.3f}%)")
print(f"  NO DATA!                 : {count_nodata:>12,}  "
      f"({count_nodata/count_total*100:.3f}%)")

total_bad = count_future + count_invalid + count_nodata
print(f"\n  Total bad rows           : {total_bad:>12,}  "
      f"({total_bad/count_total*100:.3f}%)")

print(f"\n  Future year breakdown:")
for yr in sorted(future_values.keys()):
    print(f"    {yr} : {future_values[yr]:,} rows")