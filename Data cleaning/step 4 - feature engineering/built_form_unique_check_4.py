"""
BELDA — Module 3, Script 2 Pre-check: BUILT_FORM Analysis
==========================================================
Streams through epc_module3a.parquet and produces a full
distribution analysis of the BUILT_FORM column before
the simplification mapping is written.

Usage
-----
    python module3_script2_precheck_built_form.py
"""

import time
import pyarrow.parquet as pq
import pandas as pd

INPUT      = "epc_script1_4.parquet"
BATCH_SIZE = 500_000

print("=" * 60)
print("  BELDA — Module 3 Script 2 Pre-check: BUILT_FORM")
print("=" * 60)
print(f"\n  Input  : {INPUT}")
print(f"  Batch  : {BATCH_SIZE:,} rows\n")

# ---------------------------------------------------------------
# Stream and collect value counts
# ---------------------------------------------------------------
parquet_file = pq.ParquetFile(INPUT)
value_counts = {}
total_rows   = 0
null_count   = 0
t0           = time.time()

print("  Streaming batches...\n")

for i, batch in enumerate(parquet_file.iter_batches(
        batch_size=BATCH_SIZE, columns=["BUILT_FORM"])):

    df = batch.to_pandas()
    total_rows += len(df)
    null_count += df["BUILT_FORM"].isnull().sum()

    counts = df["BUILT_FORM"].value_counts()
    for val, count in counts.items():
        value_counts[val] = value_counts.get(val, 0) + count

    print(f"  Batch {i+1:>3} | rows processed: {total_rows:>12,}")

total_time = time.time() - t0

# ---------------------------------------------------------------
# Build summary DataFrame
# ---------------------------------------------------------------
summary = pd.DataFrame({
    "value":  list(value_counts.keys()),
    "count":  list(value_counts.values())
})
summary["pct"]         = (summary["count"] / total_rows * 100).round(3)
summary["cumulative"]  = summary["count"].cumsum()
summary["cum_pct"]     = (summary["cumulative"] / total_rows * 100).round(2)
summary = summary.sort_values("count", ascending=False).reset_index(drop=True)
summary["rank"]        = summary.index + 1

# ---------------------------------------------------------------
# Print results
# ---------------------------------------------------------------
print(f"\n{'=' * 60}")
print("  BUILT_FORM Distribution")
print(f"{'=' * 60}")
print(f"  Total rows          : {total_rows:>12,}")
print(f"  Null values         : {null_count:>12,}  "
      f"({null_count/total_rows*100:.4f}%)")
print(f"  Unique values       : {len(value_counts):>12,}")
print(f"  Time                : {total_time:.1f}s")

print(f"\n  {'Rank':<5} {'Value':<35} {'Count':>10} {'%':>7} {'Cum%':>7}")
print(f"  {'-'*5} {'-'*35} {'-'*10} {'-'*7} {'-'*7}")

for _, row in summary.iterrows():
    print(f"  {int(row['rank']):<5} {str(row['value']):<35} "
          f"{int(row['count']):>10,} "
          f"{row['pct']:>6.3f}% "
          f"{row['cum_pct']:>6.2f}%")

print(f"\n{'=' * 60}")
print("  Use this output to define the built_form_simplified mapping")
print("  in Script 2 before running the full transformation.")
print(f"{'=' * 60}\n")