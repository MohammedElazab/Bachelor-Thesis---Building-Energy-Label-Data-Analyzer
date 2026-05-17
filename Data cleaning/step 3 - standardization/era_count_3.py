"""
BELDA — Task 3 Verification: Era Distribution
==============================================
Counts rows per era group to confirm the mapping
looks physically sensible.

Usage
-----
    python verify_era_distribution.py
"""

import pyarrow.parquet as pq
import pandas as pd
from collections import Counter

INPUT      = "epc_era_grouped.parquet"
BATCH_SIZE = 500_000

era_counts = Counter()
total_rows = 0

parquet_file = pq.ParquetFile(INPUT)
for batch in parquet_file.iter_batches(
        batch_size=BATCH_SIZE,
        columns=["CONSTRUCTION_AGE_BAND"]):
    df = batch.to_pandas()
    era_counts.update(df["CONSTRUCTION_AGE_BAND"].tolist())
    total_rows += len(df)

# Define display order
ERA_ORDER = [
    "Pre-1900", "1900-1929", "1930-1949", "1950-1966",
    "1967-1975", "1976-1982", "1983-1990", "1991-1995",
    "1996-2002", "2003-2006", "2007 onwards"
]

print("=" * 60)
print("  BELDA - Task 3 Verification: Era Distribution")
print("=" * 60)
print(f"\n  Total rows : {total_rows:,}\n")
print(f"  {'Era':<20} {'Count':>10} {'%':>8}")
print(f"  {'-'*20} {'-'*10} {'-'*8}")
for era in ERA_ORDER:
    count = era_counts.get(era, 0)
    print(f"  {era:<20} {count:>10,} {count/total_rows*100:>7.2f}%")

# Flag anything unexpected
known = set(ERA_ORDER)
unexpected = {k: v for k, v in era_counts.items() if k not in known}
if unexpected:
    print(f"\n  Unexpected values found:")
    for k, v in unexpected.items():
        print(f"    '{k}' : {v:,} rows")
else:
    print(f"\n  No unexpected values found ✓")