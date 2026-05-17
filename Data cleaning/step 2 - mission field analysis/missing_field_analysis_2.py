"""
BELDA — Step 2: Missing Value Analysis
=======================================
Scans epc_core.parquet and reports:
  1. Missing count + percentage per column
  2. Total rows containing at least one null (and percentage)

Streams in batches to avoid RAM issues.

Usage
-----
    python step2_missing_analysis.py
"""

import time
import pyarrow.parquet as pq
import pandas as pd
import numpy as np

INPUT      = "epc_missing_field_removed.parquet"
OUTPUT_CSV = "step2_missing_report.csv"
BATCH_SIZE = 500_000

print("=" * 60)
print("  BELDA - Step 2: Missing Value Analysis")
print("=" * 60)

parquet_file = pq.ParquetFile(INPUT)

# Read schema to get column names
columns = pq.read_schema(INPUT).names
print(f"\n  Columns to analyse : {len(columns)}")
print(f"  Batch size         : {BATCH_SIZE:,}\n")

# Accumulators
missing_counts = {col: 0 for col in columns}
rows_with_any_null = 0
total_rows = 0
t0 = time.time()

print("  Scanning batches...\n")

for i, batch in enumerate(parquet_file.iter_batches(batch_size=BATCH_SIZE)):
    df = batch.to_pandas()

    # Per-column null counts
    for col in columns:
        missing_counts[col] += df[col].isna().sum()

    # Rows with at least one null
    rows_with_any_null += df.isna().any(axis=1).sum()
    total_rows += len(df)

    print(f"  Batch {i+1:>3} | {total_rows:>12,} rows scanned | "
          f"{time.time()-t0:.0f}s elapsed")

print(f"\n  Scan complete. {total_rows:,} total rows.\n")

# ── Build report ──────────────────────────────────────────────────────────────
report = pd.DataFrame({
    "column":        list(missing_counts.keys()),
    "missing_count": list(missing_counts.values()),
})
report["missing_pct"] = (report["missing_count"] / total_rows * 100).round(2)
report = report.sort_values("missing_pct", ascending=False).reset_index(drop=True)

# ── Print report ──────────────────────────────────────────────────────────────
print("=" * 60)
print("  Missing Values per Column")
print("=" * 60)
print(f"\n  {'Column':<35} {'Missing':>10} {'%':>8}")
print(f"  {'-'*35} {'-'*10} {'-'*8}")
for _, row in report.iterrows():
    flag = " <-- ALL MISSING" if row['missing_pct'] == 100 else ""
    print(f"  {row['column']:<35} {int(row['missing_count']):>10,} "
          f"{row['missing_pct']:>7.2f}%{flag}")

# ── Rows with any null ────────────────────────────────────────────────────────
any_null_pct = round(rows_with_any_null / total_rows * 100, 2)
clean_rows   = total_rows - rows_with_any_null
clean_pct    = round(clean_rows / total_rows * 100, 2)

print(f"\n{'=' * 60}")
print(f"  Row-Level Summary")
print(f"{'=' * 60}")
print(f"  Total rows                  : {total_rows:>12,}")
print(f"  Rows with at least one null : {rows_with_any_null:>12,}  ({any_null_pct}%)")
print(f"  Fully complete rows         : {clean_rows:>12,}  ({clean_pct}%)")
print(f"\n  -> If {any_null_pct}% is acceptable to drop, no imputation needed.")
print(f"     If not, check which columns drive most of the nulls above.\n")

# ── Save CSV ──────────────────────────────────────────────────────────────────
report.to_csv(OUTPUT_CSV, index=False)
print(f"  Report saved to: {OUTPUT_CSV}")
print("=" * 60)