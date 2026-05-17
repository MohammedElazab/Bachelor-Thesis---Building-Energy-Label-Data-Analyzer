"""
BELDA — Module 2 (Part A): Encoding & Outlier Removal
=======================================================
Performs 4 cleaning tasks, all in place:

  1. Ordinal encode 10 efficiency rating columns in place
     (Very Poor=1, Poor=2, Average=3, Good=4, Very Good=5)
  2. Label encode CURRENT_ENERGY_RATING + POTENTIAL_ENERGY_RATING in place
     (A++=1, A+=2, A=3, B=4, C=5, D=6, E=7, F=8, G=9)
  6. Remove outliers from ENERGY_CONSUMPTION_CURRENT (< 10 or > 500 kWh/m2/yr)
  7. Remove outliers from TOTAL_FLOOR_AREA (< 10 or > 1000 m2)

Reads  : epc_missing_field_removed.parquet
Writes : epc_changing_letters_to_numbers.parquet

Usage
-----
    python changing_letters_to_numbers_3.py
"""

import time
import pyarrow as pa
import pyarrow.parquet as pq
import pandas as pd

INPUT      = "epc_missing_field_removed.parquet"
OUTPUT     = "epc_changing_letters_to_numbers.parquet"
BATCH_SIZE = 500_000

# ── Mappings ──────────────────────────────────────────────────────────────────

ORDINAL_MAP = {
    "Very Poor" : 1,
    "Poor"      : 2,
    "Average"   : 3,
    "Good"      : 4,
    "Very Good" : 5,
}

LABEL_MAP = {
    "A++" : 1,
    "A+"  : 2,
    "A"   : 3,
    "B"   : 4,
    "C"   : 5,
    "D"   : 6,
    "E"   : 7,
    "F"   : 8,
    "G"   : 9,
}

EFF_COLS = [
    "WALLS_ENERGY_EFF",
    "WALLS_ENV_EFF",
    "ROOF_ENERGY_EFF",      # NaN kept for flats
    "ROOF_ENV_EFF",         # NaN kept for flats
    "WINDOWS_ENERGY_EFF",
    "WINDOWS_ENV_EFF",
    "MAINHEAT_ENERGY_EFF",
    "MAINHEAT_ENV_EFF",
    "HOT_WATER_ENERGY_EFF",
    "HOT_WATER_ENV_EFF",
]

# Outlier thresholds
CONSUMPTION_MIN =   10   # kWh/m2/yr - below this is physically impossible
CONSUMPTION_MAX =  500   # kWh/m2/yr - above this is a data entry error
FLOOR_AREA_MIN  =   10   # m2        - smaller than a garden shed
FLOOR_AREA_MAX  = 1000   # m2        - larger than a small office block

# ── Processing ────────────────────────────────────────────────────────────────
print("=" * 60)
print("  BELDA - Module 2A: Encoding & Outlier Removal")
print("=" * 60)
print(f"\n  Input  : {INPUT}")
print(f"  Output : {OUTPUT}\n")

parquet_file = pq.ParquetFile(INPUT)
writer       = None
total_in     = 0
dropped_consumption = 0
dropped_floor_area  = 0
rows_written = 0

# Track any unexpected values not in our maps
unknown_labels  = set()
unknown_ordinal = {col: set() for col in EFF_COLS}

t0 = time.time()
print("  Streaming batches...\n")

for i, batch in enumerate(parquet_file.iter_batches(batch_size=BATCH_SIZE)):
    df = batch.to_pandas()
    batch_in = len(df)
    total_in += batch_in

    # ── Task 1: Ordinal encode efficiency columns in place ─────────────────
    for col in EFF_COLS:
        # Track any values not in our map before mapping
        unknown = set(df[col].dropna().unique()) - set(ORDINAL_MAP.keys())
        unknown_ordinal[col].update(unknown)
        df[col] = df[col].map(ORDINAL_MAP).astype("Int64")  # Int64 = nullable int

    # ── Task 2: Label encode energy ratings in place ───────────────────────
    for col in ["CURRENT_ENERGY_RATING", "POTENTIAL_ENERGY_RATING"]:
        unknown = set(df[col].dropna().unique()) - set(LABEL_MAP.keys())
        unknown_labels.update(unknown)
        df[col] = df[col].map(LABEL_MAP).astype("Int64")  # Int64 = nullable int

    # ── Task 6: Drop consumption outliers ──────────────────────────────────
    before = len(df)
    df = df[
        (df["ENERGY_CONSUMPTION_CURRENT"] >= CONSUMPTION_MIN) &
        (df["ENERGY_CONSUMPTION_CURRENT"] <= CONSUMPTION_MAX)
    ].reset_index(drop=True)
    n_dropped_consumption  = before - len(df)
    dropped_consumption   += n_dropped_consumption

    # ── Task 7: Drop floor area outliers ───────────────────────────────────
    before = len(df)
    df = df[
        (df["TOTAL_FLOOR_AREA"] >= FLOOR_AREA_MIN) &
        (df["TOTAL_FLOOR_AREA"] <= FLOOR_AREA_MAX)
    ].reset_index(drop=True)
    n_dropped_floor     = before - len(df)
    dropped_floor_area += n_dropped_floor

    # ── Write batch ────────────────────────────────────────────────────────
    table = pa.Table.from_pandas(df, preserve_index=False)
    if writer is None:
        writer = pq.ParquetWriter(OUTPUT, table.schema, compression="snappy")
    writer.write_table(table)
    rows_written += len(df)

    print(f"  Batch {i+1:>3} | in: {batch_in:>8,} | "
          f"dropped cons: {n_dropped_consumption:>5,} | "
          f"dropped area: {n_dropped_floor:>5,} | "
          f"written: {rows_written:>12,}")

if writer:
    writer.close()

total_time    = time.time() - t0
total_dropped = dropped_consumption + dropped_floor_area

# ── Summary ───────────────────────────────────────────────────────────────────
print(f"\n{'=' * 60}")
print("  Module 2A Complete")
print(f"{'=' * 60}")
print(f"  Rows in                          : {total_in:>12,}")
print(f"  Dropped (consumption outliers)   : {dropped_consumption:>12,}  "
      f"({dropped_consumption/total_in*100:.3f}%)")
print(f"  Dropped (floor area outliers)    : {dropped_floor_area:>12,}  "
      f"({dropped_floor_area/total_in*100:.3f}%)")
print(f"  Total rows dropped               : {total_dropped:>12,}  "
      f"({total_dropped/total_in*100:.3f}%)")
print(f"  Rows written                     : {rows_written:>12,}")
print(f"  Total columns                    : 30 (unchanged)")
print(f"  Total time                       : {total_time:.1f}s")

# Report any unexpected values encountered
print(f"\n  Unknown label values (mapped to NaN): "
      f"{unknown_labels if unknown_labels else 'None'}")
any_unknown_ordinal = {k: v for k, v in unknown_ordinal.items() if v}
if any_unknown_ordinal:
    print(f"  Unknown ordinal values (mapped to NaN):")
    for col, vals in any_unknown_ordinal.items():
        print(f"    {col}: {vals}")
else:
    print(f"  Unknown ordinal values             : None")

print(f"\n  -> Ready for Module 2B: Text Standardisation\n")