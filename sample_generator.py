"""
BELDA — Step 1 Verification
============================
Samples 20 rows from epc_core.parquet and saves them as a CSV
to confirm the column filtering was applied correctly.

Usage
-----
    python verify_step1.py
"""

import pyarrow.parquet as pq

INPUT      = "epc_script4_4.parquet"
OUTPUT_CSV = "epc_script4_4_sample20.csv"
 
print("=" * 60)
print("  BELDA - Step 4 Verification")
print("=" * 60)

# Read only the first 20 rows - no memory concern
parquet_file = pq.ParquetFile(INPUT)
batch = next(parquet_file.iter_batches(batch_size=20))
df = batch.to_pandas()

print(f"\n  Rows sampled : {len(df)}")
print(f"  Columns      : {len(df.columns)}")
print(f"\n  Column names:")
for i, col in enumerate(df.columns, 1):
    print(f"    {i:>2}. {col}")

df.to_csv(OUTPUT_CSV, index=False)
print(f"\n  Sample saved to: {OUTPUT_CSV}")
print("\n" + "=" * 60)
print("  If the CSV has 30 columns, Step 4 was successful.")
print("=" * 60)