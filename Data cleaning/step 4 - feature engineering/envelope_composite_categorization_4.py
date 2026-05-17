"""
BELDA — Module 3, Script 3: envelope_composite_score
=====================================================
Creates a single numeric score (1.0–5.0) representing the overall
thermal quality of a building's envelope by averaging the assessor
efficiency ratings for walls, roof, and windows.

Null handling:
    ROOF_ENERGY_EFF is null for flats and maisonettes with no exposed
    roof (16.726% of rows — structural missingness retained from
    Module 2). For these properties the score is averaged over walls
    and windows only. HAS_OWN_ROOF is used to identify which rows
    have a valid roof rating.

    WALLS_ENERGY_EFF and WINDOWS_ENERGY_EFF are fully complete (0 nulls).

Score interpretation:
    1.0 — Very Poor envelope across all components
    2.0 — Poor
    3.0 — Average (typical UK stock)
    4.0 — Good
    5.0 — Very Good envelope across all components
    Values between integers reflect mixed component ratings.

No rows are dropped in this script.

Reads  : epc_script2_4.parquet   (24,498,358 rows x 34 cols)
Writes : epc_script3_4.parquet   (24,498,358 rows x 35 cols)

Usage
-----
    python module3_script3_envelope_score.py
"""

import time
import pyarrow as pa
import pyarrow.parquet as pq
import pandas as pd
import numpy as np

# ---------------------------------------------------------------
# CONFIG
# ---------------------------------------------------------------
INPUT      = "epc_script2_4.parquet"
OUTPUT     = "epc_script3_4.parquet"
BATCH_SIZE = 500_000

print("=" * 60)
print("  BELDA — Module 3 Script 3: envelope_composite_score")
print("=" * 60)
print(f"\n  Input  : {INPUT}")
print(f"  Output : {OUTPUT}")
print(f"  Batch  : {BATCH_SIZE:,} rows\n")
print("  Null handling:")
print("    HAS_OWN_ROOF = 1 → average of walls + roof + windows")
print("    HAS_OWN_ROOF = 0 → average of walls + windows only\n")
print("  No rows dropped in this script.\n")

# ---------------------------------------------------------------
# COUNTERS
# ---------------------------------------------------------------
parquet_file      = pq.ParquetFile(INPUT)
writer            = None
total_in          = 0
rows_written      = 0
with_roof_count   = 0
without_roof_count= 0
score_sum         = 0.0
score_min         = float("inf")
score_max         = float("-inf")
t0                = time.time()

print("  Streaming batches...\n")

for i, batch in enumerate(parquet_file.iter_batches(batch_size=BATCH_SIZE)):
    df = batch.to_pandas()
    batch_in   = len(df)
    total_in  += batch_in

    # ----------------------------------------------------------
    # Feature: envelope_composite_score
    # ----------------------------------------------------------
    # Split into two groups based on HAS_OWN_ROOF flag.
    # For properties with a roof: average all three components.
    # For properties without a roof (flats/maisonettes): average
    # walls and windows only — roof null is structural, not missing.
    # ----------------------------------------------------------

    has_roof     = df["HAS_OWN_ROOF"] == 1
    no_roof      = df["HAS_OWN_ROOF"] == 0

    with_roof_count    += has_roof.sum()
    without_roof_count += no_roof.sum()

    df["envelope_composite_score"] = np.nan

    # Buildings with roof — 3-component average
    df.loc[has_roof, "envelope_composite_score"] = (
        df.loc[has_roof, "WALLS_ENERGY_EFF"].astype(float)
        + df.loc[has_roof, "ROOF_ENERGY_EFF"].astype(float)
        + df.loc[has_roof, "WINDOWS_ENERGY_EFF"].astype(float)
    ) / 3.0

    # Buildings without roof — 2-component average
    df.loc[no_roof, "envelope_composite_score"] = (
        df.loc[no_roof, "WALLS_ENERGY_EFF"].astype(float)
        + df.loc[no_roof, "WINDOWS_ENERGY_EFF"].astype(float)
    ) / 2.0

    # Round to 2 decimal places for readability
    df["envelope_composite_score"] = df["envelope_composite_score"].round(2)

    # ----------------------------------------------------------
    # Sanity checks
    # ----------------------------------------------------------
    null_check = df["envelope_composite_score"].isnull().sum()
    if null_check > 0:
        print(f"  WARNING: Batch {i+1} — {null_check} null scores. "
              f"Check HAS_OWN_ROOF values.")

    out_of_range = ((df["envelope_composite_score"] < 1.0) |
                    (df["envelope_composite_score"] > 5.0)).sum()
    if out_of_range > 0:
        print(f"  WARNING: Batch {i+1} — {out_of_range} scores outside "
              f"1.0–5.0 range. Investigate.")

    # Accumulate stats
    score_sum += df["envelope_composite_score"].sum()
    batch_min  = df["envelope_composite_score"].min()
    batch_max  = df["envelope_composite_score"].max()
    if batch_min < score_min:
        score_min = batch_min
    if batch_max > score_max:
        score_max = batch_max

    # ----------------------------------------------------------
    # Write batch
    # ----------------------------------------------------------
    table = pa.Table.from_pandas(df, preserve_index=False)
    if writer is None:
        writer = pq.ParquetWriter(OUTPUT, table.schema,
                                  compression="snappy")
    writer.write_table(table)
    rows_written += len(df)

    print(f"  Batch {i+1:>3} | in: {batch_in:>8,} | "
          f"written: {rows_written:>12,}")

if writer:
    writer.close()

total_time  = time.time() - t0
score_mean  = score_sum / rows_written

# ---------------------------------------------------------------
# SUMMARY
# ---------------------------------------------------------------
print(f"\n{'=' * 60}")
print("  Script 3 Complete")
print(f"{'=' * 60}")
print(f"  Rows in                        : {total_in:>12,}")
print(f"  Rows dropped                   : {'0':>12}  (none — no rows dropped)")
print(f"  Rows written                   : {rows_written:>12,}")
print(f"  Columns                        : 34 → 35")
print(f"\n  Null handling breakdown:")
print(f"    With roof (3-component avg)  : {with_roof_count:>12,}  "
      f"({with_roof_count/rows_written*100:.3f}%)")
print(f"    Without roof (2-component)   : {without_roof_count:>12,}  "
      f"({without_roof_count/rows_written*100:.3f}%)")
print(f"\n  envelope_composite_score stats:")
print(f"    Min                          : {score_min:>12.2f}  (expected ≥ 1.0)")
print(f"    Max                          : {score_max:>12.2f}  (expected ≤ 5.0)")
print(f"    Mean                         : {score_mean:>12.2f}  "
      f"(expected ~2.5–3.5 for UK stock)")
print(f"\n  Total time                     : {total_time:.1f}s")
print(f"\n  -> Ready for Script 4: co2_intensity_category\n")