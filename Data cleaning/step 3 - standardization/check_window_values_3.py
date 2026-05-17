"""
BELDA — Task 6 Prep: Unique WINDOWS_DESCRIPTION values
=======================================================
Scans the full dataset and saves every unique value in
WINDOWS_DESCRIPTION with its row count to an MD file.

Usage
-----
    python check_window_values_3.py
"""

import pyarrow.parquet as pq
import pandas as pd
from collections import Counter 

INPUT      = "epc_mainfuel_mapped.parquet"
BATCH_SIZE = 500_000
OUT_MD     = "windows_unique_values.md"

counts     = Counter()
total_rows = 0
 
parquet_file = pq.ParquetFile(INPUT)
print("Scanning batches...")
for i, batch in enumerate(parquet_file.iter_batches(
        batch_size=BATCH_SIZE,
        columns=["WINDOWS_DESCRIPTION"])):
    df = batch.to_pandas()
    counts.update(df["WINDOWS_DESCRIPTION"].dropna().tolist())
    total_rows += len(df)
    print(f"  Batch {i+1:>3} | {total_rows:>12,} rows scanned", end="\r")

print(f"\n\nTotal rows scanned  : {total_rows:,}")
print(f"Unique values found : {len(counts):,}")

with open(OUT_MD, "w", encoding="utf-8") as f:
    f.write("# WINDOWS_DESCRIPTION — Unique Values\n\n")
    f.write(f"**Total rows scanned:** {total_rows:,}  \n")
    f.write(f"**Unique values:** {len(counts):,}\n\n")
    f.write("| Rank | Count | % | Description |\n")
    f.write("|---|---|---|---|\n")
    for i, (val, count) in enumerate(counts.most_common(), 1):
        f.write(f"| {i} | {count:,} | {count/total_rows*100:.3f}% | {val} |\n")

print(f"MD saved : {OUT_MD}")