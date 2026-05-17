"""
BELDA — Module 3, Script 1: Simple Derived Features
=====================================================
Features created:
    1. improvement_potential   — numeric label improvement gap
    2. label_gap_readable      — human-readable version of the same gap
    3. glazing_upgrade_flag    — binary flag for single-glazed properties

Reads  : epc_windows_mapped_clean.parquet  (24,932,060 rows x 30 cols)
Writes : epc_module3a.parquet              (24,931,931 rows x 33 cols)

Rows dropped:
    129 rows where improvement_potential < 0
    (potential rating recorded as worse than current — assessor error
     or SAP methodology artefact in community-heated / modern electric
     storage buildings. 0.0005% of dataset.)

Processing:
    Streams in batches of 500,000 rows to keep RAM usage low.

Usage
-----
    python module3_script1_simple_features.py
"""

import time
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

# ---------------------------------------------------------------
# CONFIG
# ---------------------------------------------------------------
INPUT      = "epc_windows_mapped_clean.parquet"
OUTPUT     = "epc_script1_4.parquet"
BATCH_SIZE = 500_000 

# ---------------------------------------------------------------
# ENCODING REFERENCE (from Module 2)
# Energy rating: 1=A++, 2=A+, 3=A, 4=B, 5=C, 6=D, 7=E, 8=F, 9=G
# Higher integer = worse label.
# improvement_potential = CURRENT - POTENTIAL
# Positive = building can improve. Zero = already at ceiling.
# ---------------------------------------------------------------
LABEL_MAP = {
    1: "A++",
    2: "A+",
    3: "A",
    4: "B",
    5: "C",
    6: "D",
    7: "E",
    8: "F",
    9: "G"
}

print("=" * 60)
print("  BELDA — Module 3 Script 1: Simple Derived Features")
print("=" * 60)
print(f"\n  Input  : {INPUT}")
print(f"  Output : {OUTPUT}")
print(f"  Batch  : {BATCH_SIZE:,} rows\n")
print("  Features to create:")
print("    1. improvement_potential  (CURRENT - POTENTIAL rating)")
print("    2. label_gap_readable     (e.g. D→B)")
print("    3. glazing_upgrade_flag   (1 if Single glazing, else 0)\n")
print("  Rows to drop:")
print("    - improvement_potential < 0 (potential worse than current)\n")

# ---------------------------------------------------------------
# COUNTERS
# ---------------------------------------------------------------
parquet_file        = pq.ParquetFile(INPUT)
writer              = None
total_in            = 0
dropped_negative    = 0
rows_written        = 0
glazing_flag_total  = 0
t0                  = time.time()

print("  Streaming batches...\n")

for i, batch in enumerate(parquet_file.iter_batches(batch_size=BATCH_SIZE)):
    df = batch.to_pandas()
    batch_in  = len(df)
    total_in += batch_in

    # ----------------------------------------------------------
    # Feature 1: improvement_potential
    # Physical meaning: number of label grades a building could
    # climb if all assessor-recommended improvements were applied.
    # ----------------------------------------------------------
    df["improvement_potential"] = (
        df["CURRENT_ENERGY_RATING"] - df["POTENTIAL_ENERGY_RATING"]
    )

    # ----------------------------------------------------------
    # Drop rows where potential is worse than current
    # These are physically implausible and represent either SAP
    # methodology artefacts (community heating, modern electric
    # storage) or assessor entry errors. 129 rows total (0.0005%).
    # ----------------------------------------------------------
    negative_mask    = df["improvement_potential"] < 0
    batch_dropped    = negative_mask.sum()
    dropped_negative += batch_dropped
    df = df[~negative_mask].reset_index(drop=True)

    # ----------------------------------------------------------
    # Feature 2: label_gap_readable
    # Physical meaning: same gap as a human-readable string for
    # visualisations and thesis figures. Format: "CURRENT→POTENTIAL"
    # ----------------------------------------------------------
    df["label_gap_readable"] = (
        df["CURRENT_ENERGY_RATING"].map(LABEL_MAP)
        + "→"
        + df["POTENTIAL_ENERGY_RATING"].map(LABEL_MAP)
    )

    # ----------------------------------------------------------
    # Feature 3: glazing_upgrade_flag
    # Physical meaning: binary flag marking properties that still
    # have single glazing (U-value ~5.8 W/m²K vs ~1.6 for double).
    # 1 = single glazing present (upgrade opportunity)
    # 0 = double, triple, or secondary glazing
    # ----------------------------------------------------------
    df["glazing_upgrade_flag"] = (
        df["WINDOWS_DESCRIPTION"] == "Single glazing"
    ).astype(int)

    glazing_flag_total += df["glazing_upgrade_flag"].sum()

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
          f"dropped: {batch_dropped:>4} | "
          f"written: {rows_written:>12,}")

if writer:
    writer.close()

total_time = time.time() - t0

# ---------------------------------------------------------------
# SUMMARY
# ---------------------------------------------------------------
print(f"\n{'=' * 60}")
print("  Script 1 Complete")
print(f"{'=' * 60}")
print(f"  Rows in                        : {total_in:>12,}")
print(f"  Dropped (negative potential)   : {dropped_negative:>12,}  "
      f"({dropped_negative/total_in*100:.4f}%)")
print(f"  Rows written                   : {rows_written:>12,}")
print(f"  Columns                        : 30 → 33")
print(f"\n  Feature verification:")
print(f"    glazing_upgrade_flag = 1     : {glazing_flag_total:>12,}  "
      f"({glazing_flag_total/rows_written*100:.2f}%)")
print(f"    (expected ~1,177,159 / 4.72%)")
print(f"\n  Total time                     : {total_time:.1f}s")
print(f"\n  -> Ready for Script 2: built_form_simplified\n")