"""
BELDA — Task 4 Cleanup: Drop 'Other' heating system rows
=========================================================
Drops the 559 rows where MAINHEAT_DESCRIPTION = 'Other'

Reads  : epc_mainheat_mapped.parquet
Writes : epc_mainheat_mapped_clean.parquet

Usage
-----
    python epc_mainhead_remove_others.py
"""

import time
import pyarrow as pa
import pyarrow.parquet as pq
import pandas as pd

INPUT      = "epc_mainheat_mapped.parquet"
OUTPUT     = "epc_mainheat_mapped_clean.parquet"
BATCH_SIZE = 500_000

print("=" * 60)
print("  BELDA - Task 4 Cleanup: Drop 'Other' rows")
print("=" * 60)

parquet_file = pq.ParquetFile(INPUT)
writer       = None
total_in     = 0
total_dropped= 0
rows_written = 0
t0           = time.time()

for i, batch in enumerate(parquet_file.iter_batches(batch_size=BATCH_SIZE)):
    df = batch.to_pandas()
    total_in += len(df)

    before = len(df)
    df = df[df["MAINHEAT_DESCRIPTION"] != "Other"].reset_index(drop=True)
    total_dropped += before - len(df)

    table = pa.Table.from_pandas(df, preserve_index=False)
    if writer is None:
        writer = pq.ParquetWriter(OUTPUT, table.schema, compression="snappy")
    writer.write_table(table)
    rows_written += len(df)

if writer:
    writer.close()

print(f"  Rows in      : {total_in:>12,}")
print(f"  Rows dropped : {total_dropped:>12,}")
print(f"  Rows written : {rows_written:>12,}")
print(f"  Time         : {time.time()-t0:.1f}s")
print(f"\n  -> Output: {OUTPUT}\n")