"""
BELDA — Task 3 Step 1: Drop bad CONSTRUCTION_AGE_BAND values
=============================================================
Drops rows where CONSTRUCTION_AGE_BAND is:
  - 'INVALID!'
  - 'NO DATA!'
  - A future year (> 2026)

Reads  : epc_module2a.parquet
Writes : epc_module2b.parquet

Usage
-----
    python module2b_drop_bad_age_bands.py
"""

import time
import pyarrow as pa
import pyarrow.parquet as pq
import pandas as pd

INPUT      = "epc_changing_letters_to_numbers_clean.parquet"
OUTPUT     = "epc_changing_no_bad_age_bands.parquet"
BATCH_SIZE = 500_000
MAX_VALID_YEAR = 2026

print("=" * 60)
print("  BELDA - Task 3 Step 1: Drop bad CONSTRUCTION_AGE_BAND rows")
print("=" * 60)
print(f"\n  Input  : {INPUT}")
print(f"  Output : {OUTPUT}\n")
print("  Dropping:")
print("  - 'INVALID!'")
print("  - 'NO DATA!'")
print(f"  - Future years (> {MAX_VALID_YEAR})\n")

parquet_file        = pq.ParquetFile(INPUT)
writer              = None
total_in            = 0
dropped_invalid     = 0
dropped_nodata      = 0
dropped_future      = 0
rows_written        = 0
t0                  = time.time()

print("  Streaming batches...\n")

for i, batch in enumerate(parquet_file.iter_batches(batch_size=BATCH_SIZE)):
    df = batch.to_pandas()
    batch_in  = len(df)
    total_in += batch_in

    cab = df["CONSTRUCTION_AGE_BAND"].astype(str).str.strip()

    # Count each type before dropping
    mask_invalid = cab == "INVALID!"
    mask_nodata  = cab == "NO DATA!"
    mask_future  = cab.apply(
        lambda v: v.isdigit() and int(v) > MAX_VALID_YEAR
    )

    dropped_invalid += mask_invalid.sum()
    dropped_nodata  += mask_nodata.sum()
    dropped_future  += mask_future.sum()

    # Drop all bad rows in one go
    bad_mask = mask_invalid | mask_nodata | mask_future
    df = df[~bad_mask].reset_index(drop=True)

    table = pa.Table.from_pandas(df, preserve_index=False)
    if writer is None:
        writer = pq.ParquetWriter(OUTPUT, table.schema, compression="snappy")
    writer.write_table(table)
    rows_written += len(df)

    print(f"  Batch {i+1:>3} | in: {batch_in:>8,} | "
          f"dropped: {mask_invalid.sum() + mask_nodata.sum() + mask_future.sum():>7,} | "
          f"written: {rows_written:>12,}")

if writer:
    writer.close()

total_dropped = dropped_invalid + dropped_nodata + dropped_future
total_time    = time.time() - t0

print(f"\n{'=' * 60}")
print("  Task 3 Step 1 Complete")
print(f"{'=' * 60}")
print(f"  Rows in                  : {total_in:>12,}")
print(f"  Dropped (INVALID!)       : {dropped_invalid:>12,}  "
      f"({dropped_invalid/total_in*100:.3f}%)")
print(f"  Dropped (NO DATA!)       : {dropped_nodata:>12,}  "
      f"({dropped_nodata/total_in*100:.3f}%)")
print(f"  Dropped (future years)   : {dropped_future:>12,}  "
      f"({dropped_future/total_in*100:.3f}%)")
print(f"  Total dropped            : {total_dropped:>12,}  "
      f"({total_dropped/total_in*100:.3f}%)")
print(f"  Rows written             : {rows_written:>12,}")
print(f"  Total time               : {total_time:.1f}s")
print(f"\n  -> Ready for Task 3 Step 2: Era Grouping\n")