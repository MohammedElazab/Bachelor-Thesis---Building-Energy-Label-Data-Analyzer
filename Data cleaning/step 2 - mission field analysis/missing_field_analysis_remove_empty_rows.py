"""
BELDA — Step 3: Row Cleaning & Feature Engineering
====================================================
Performs three operations in order:

  1. Drop rows where ROOF_ENERGY_EFF is null AND property type
     is House, Bungalow, or Park home (genuine data quality issue)

  2. Drop rows where ANY non-roof column is null
     (small, genuine data quality issues — ~1% of rows)

  3. Create HAS_OWN_ROOF binary flag
     1 = property has an assessed roof
     0 = structural null (Flat / Maisonette with no exposed roof)

Reads  : epc_core.parquet
Writes : epc_clean.parquet

Usage
-----
    python step3_clean_rows.py
"""

import time
import pyarrow as pa
import pyarrow.parquet as pq
import pandas as pd

INPUT      = "epc_core.parquet"
OUTPUT     = "epc_clean.parquet"
BATCH_SIZE = 500_000

# Property types where a null roof IS a data quality issue (not structural)
ROOF_REQUIRED_TYPES = {"House", "Bungalow", "Park home"}

# All columns except the two roof rating fields
# Nulls in these columns = genuine missing data → drop the row
ROOF_COLS = {"ROOF_ENERGY_EFF", "ROOF_ENV_EFF"}
ALL_COLS  = pq.read_schema(INPUT).names
NON_ROOF_COLS = [c for c in ALL_COLS if c not in ROOF_COLS]

print("=" * 60)
print("  BELDA - Step 3: Row Cleaning & Feature Engineering")
print("=" * 60)
print(f"\n  Input  : {INPUT}")
print(f"  Output : {OUTPUT}\n")
print("  Operations:")
print("  [1] Drop House/Bungalow/Park home rows with null ROOF_ENERGY_EFF")
print("  [2] Drop rows with any null in non-roof columns")
print("  [3] Create HAS_OWN_ROOF flag (1 = has roof, 0 = structural null)\n")

# ── Counters ──────────────────────────────────────────────────────────────────
total_rows_in        = 0
dropped_roof         = 0
dropped_other_nulls  = 0
rows_written         = 0
writer               = None
t0                   = time.time()

parquet_file = pq.ParquetFile(INPUT)

print("  Streaming batches...\n")

for i, batch in enumerate(parquet_file.iter_batches(batch_size=BATCH_SIZE)):
    df = batch.to_pandas()
    batch_size_in = len(df)
    total_rows_in += batch_size_in

    # ── Operation 1: Drop House/Bungalow/Park home with null roof ─────────────
    mask_roof_required = df["PROPERTY_TYPE"].isin(ROOF_REQUIRED_TYPES)
    mask_roof_null     = df["ROOF_ENERGY_EFF"].isna()
    drop_roof_mask     = mask_roof_required & mask_roof_null

    n_dropped_roof = drop_roof_mask.sum()
    dropped_roof  += n_dropped_roof
    df = df[~drop_roof_mask].reset_index(drop=True)

    # ── Operation 2: Drop rows with any null in non-roof columns ──────────────
    drop_other_mask    = df[NON_ROOF_COLS].isna().any(axis=1)
    n_dropped_other    = drop_other_mask.sum()
    dropped_other_nulls += n_dropped_other
    df = df[~drop_other_mask].reset_index(drop=True)

    # ── Operation 3: Create HAS_OWN_ROOF flag ─────────────────────────────────
    df["HAS_OWN_ROOF"] = df["ROOF_ENERGY_EFF"].notna().astype("int8")

    # ── Write batch ───────────────────────────────────────────────────────────
    table = pa.Table.from_pandas(df, preserve_index=False)
    if writer is None:
        writer = pq.ParquetWriter(OUTPUT, table.schema, compression="snappy")
    writer.write_table(table)
    rows_written += len(df)

    print(f"  Batch {i+1:>3} | in: {batch_size_in:>8,} | "
          f"dropped roof: {n_dropped_roof:>6,} | "
          f"dropped other: {n_dropped_other:>6,} | "
          f"written: {rows_written:>12,}")

if writer:
    writer.close()

total_time   = time.time() - t0
total_dropped = dropped_roof + dropped_other_nulls

# ── Summary ───────────────────────────────────────────────────────────────────
print(f"\n{'=' * 60}")
print("  Step 3 Complete")
print(f"{'=' * 60}")
print(f"  Rows read                        : {total_rows_in:>12,}")
print(f"  Dropped (roof / House/Bungalow)  : {dropped_roof:>12,}  "
      f"({dropped_roof/total_rows_in*100:.2f}%)")
print(f"  Dropped (other null fields)      : {dropped_other_nulls:>12,}  "
      f"({dropped_other_nulls/total_rows_in*100:.2f}%)")
print(f"  Total rows dropped               : {total_dropped:>12,}  "
      f"({total_dropped/total_rows_in*100:.2f}%)")
print(f"  Rows written to {OUTPUT:<20}: {rows_written:>12,}  "
      f"({rows_written/total_rows_in*100:.2f}%)")
print(f"  HAS_OWN_ROOF flag added          : YES (1=has roof, 0=no roof)")
print(f"  Total columns in output          : {len(ALL_COLS) + 1} (29 core + HAS_OWN_ROOF)")
print(f"  Total time                       : {total_time:.1f}s")
print(f"\n  -> Ready for Step 4: Data Type Standardisation\n")