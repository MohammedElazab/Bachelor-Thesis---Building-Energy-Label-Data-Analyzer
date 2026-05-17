"""
BELDA — Module 3, Script 2: built_form_simplified
==================================================
Creates the built_form_simplified feature by mapping the raw
BUILT_FORM column to 4 clean analytical categories.

Mapping:
    Detached              → Detached
    Semi-Detached         → Semi-detached
    End-Terrace           → End-Terrace
    Enclosed End-Terrace  → End-Terrace
    Mid-Terrace           → Mid-Terrace
    Enclosed Mid-Terrace  → Mid-Terrace
    NO DATA!              → DROP
    Not Recorded          → DROP

Physical rationale:
    Detached    — all four walls, roof, and floor fully exposed.
                  Largest envelope area relative to floor area.
    Semi-detached — one shared party wall; one side wall exposed.
                  Intermediate envelope exposure.
    End-Terrace — one shared party wall plus the Enclosed End-Terrace
                  variant (additional enclosure on one side). Front,
                  back, one side wall, roof and floor exposed.
    Mid-Terrace — two shared party walls plus the Enclosed Mid-Terrace
                  variant. Only front, back, roof and floor exposed.
                  Smallest envelope area of the terrace variants.
    Enclosed variants collapsed into their nearest equivalent because
    the enclosure is a minor structural detail (garage, passageway)
    that does not change the fundamental thermal category.

Rows dropped:
    BUILT_FORM == 'NO DATA!' or 'Not Recorded'
    ~433,573 rows (1.74%) — no usable built form information.

Reads  : epc_script1_4.parquet   (24,931,931 rows x 33 cols)
Writes : epc_script2_4.parquet   (~24,498,358 rows x 34 cols)

Usage
-----
    python module3_script2_built_form.py
"""

import time
import pyarrow as pa
import pyarrow.parquet as pq
import pandas as pd

# ---------------------------------------------------------------
# CONFIG
# ---------------------------------------------------------------
INPUT      = "epc_script1_4.parquet"
OUTPUT     = "epc_script2_4.parquet"
BATCH_SIZE = 500_000

# ---------------------------------------------------------------
# MAPPING
# ---------------------------------------------------------------
BUILT_FORM_MAP = {
    "Detached"             : "Detached",
    "Semi-Detached"        : "Semi-detached",
    "End-Terrace"          : "End-Terrace",
    "Enclosed End-Terrace" : "End-Terrace",
    "Mid-Terrace"          : "Mid-Terrace",
    "Enclosed Mid-Terrace" : "Mid-Terrace",
}

DROP_VALUES = {"NO DATA!", "Not Recorded"}

print("=" * 60)
print("  BELDA — Module 3 Script 2: built_form_simplified")
print("=" * 60)
print(f"\n  Input  : {INPUT}")
print(f"  Output : {OUTPUT}")
print(f"  Batch  : {BATCH_SIZE:,} rows\n")
print("  Mapping:")
for raw, simplified in BUILT_FORM_MAP.items():
    print(f"    {raw:<25} → {simplified}")
print(f"    {'NO DATA!':<25} → DROP")
print(f"    {'Not Recorded':<25} → DROP\n")

# ---------------------------------------------------------------
# COUNTERS
# ---------------------------------------------------------------
parquet_file      = pq.ParquetFile(INPUT)
writer            = None
total_in          = 0
dropped_nodata    = 0
dropped_notrecord = 0
rows_written      = 0
category_counts   = {}
unknown_values    = {}
t0                = time.time()

print("  Streaming batches...\n")

for i, batch in enumerate(parquet_file.iter_batches(batch_size=BATCH_SIZE)):
    df = batch.to_pandas()
    batch_in   = len(df)
    total_in  += batch_in

    # ----------------------------------------------------------
    # Drop NO DATA! and Not Recorded rows
    # ----------------------------------------------------------
    mask_nodata    = df["BUILT_FORM"] == "NO DATA!"
    mask_notrecord = df["BUILT_FORM"] == "Not Recorded"
    batch_nodata   = mask_nodata.sum()
    batch_notrecord= mask_notrecord.sum()

    dropped_nodata    += batch_nodata
    dropped_notrecord += batch_notrecord

    drop_mask = mask_nodata | mask_notrecord
    df = df[~drop_mask].reset_index(drop=True)

    # ----------------------------------------------------------
    # Apply mapping
    # ----------------------------------------------------------
    df["built_form_simplified"] = df["BUILT_FORM"].map(BUILT_FORM_MAP)

    # ----------------------------------------------------------
    # Check for any unmapped values (should be zero)
    # ----------------------------------------------------------
    unmapped = df[df["built_form_simplified"].isnull()]
    if len(unmapped) > 0:
        for val in unmapped["BUILT_FORM"].unique():
            unknown_values[val] = unknown_values.get(val, 0) + \
                (unmapped["BUILT_FORM"] == val).sum()

    # ----------------------------------------------------------
    # Accumulate category counts
    # ----------------------------------------------------------
    counts = df["built_form_simplified"].value_counts()
    for cat, count in counts.items():
        category_counts[cat] = category_counts.get(cat, 0) + count

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
          f"dropped: {batch_nodata + batch_notrecord:>6,} | "
          f"written: {rows_written:>12,}")

if writer:
    writer.close()

total_dropped = dropped_nodata + dropped_notrecord
total_time    = time.time() - t0

# ---------------------------------------------------------------
# SUMMARY
# ---------------------------------------------------------------
print(f"\n{'=' * 60}")
print("  Script 2 Complete")
print(f"{'=' * 60}")
print(f"  Rows in                        : {total_in:>12,}")
print(f"  Dropped (NO DATA!)             : {dropped_nodata:>12,}  "
      f"({dropped_nodata/total_in*100:.3f}%)")
print(f"  Dropped (Not Recorded)         : {dropped_notrecord:>12,}  "
      f"({dropped_notrecord/total_in*100:.3f}%)")
print(f"  Total dropped                  : {total_dropped:>12,}  "
      f"({total_dropped/total_in*100:.3f}%)")
print(f"  Rows written                   : {rows_written:>12,}")
print(f"  Columns                        : 33 → 34")

print(f"\n  built_form_simplified distribution:")
print(f"  {'Category':<20} {'Count':>10} {'%':>7}")
print(f"  {'-'*20} {'-'*10} {'-'*7}")
for cat, count in sorted(category_counts.items(),
                          key=lambda x: x[1], reverse=True):
    print(f"  {cat:<20} {count:>10,} {count/rows_written*100:>6.3f}%")

if unknown_values:
    print(f"\n  WARNING: {sum(unknown_values.values())} unmapped values found:")
    for val, count in unknown_values.items():
        print(f"    '{val}': {count:,}")
else:
    print(f"\n  Unmapped values: none ✓")

print(f"\n  Total time                     : {total_time:.1f}s")
print(f"\n  -> Ready for Script 3: envelope_composite_score\n")