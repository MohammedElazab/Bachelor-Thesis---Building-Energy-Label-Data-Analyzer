"""
BELDA — Module 3, Script 4: co2_intensity_category
===================================================
Creates a categorical band for CO2_EMISS_CURR_PER_FLOOR_AREA
based on percentile breakpoints from the data distribution.

Bands:
    Net Zero  : <= 0       Biomass/renewable community — SAP negative
                           emission factors reflecting net carbon benefit
    Low       : 1  – 33   Below p25 — better than average UK stock
    Medium    : 34 – 54   p25–p75 — typical UK stock
    High      : 55 – 74   p75–p95 — above average carbon intensity
    Very High : >= 75     Top 5% — poor performing, high carbon intensity

Negative values (3,157 rows, 0.013%) are physically valid — biomass
and renewable community heating systems are assigned zero or negative
CO2 factors in SAP methodology. These are NOT errors and are NOT
dropped. They are captured in the Net Zero band.

Extreme values (>200, 10 rows) are physically plausible edge cases
and fall naturally into the Very High band.

No rows are dropped in this script.

Reads  : epc_script3_4.parquet   (24,498,358 rows x 35 cols)
Writes : epc_script4_4.parquet   (24,498,358 rows x 36 cols)

Usage
-----
    python module3_script4_co2_category.py
"""

import time
import pyarrow as pa
import pyarrow.parquet as pq
import pandas as pd

# ---------------------------------------------------------------
# CONFIG
# ---------------------------------------------------------------
INPUT      = "epc_script3_4.parquet"
OUTPUT     = "epc_script4_4.parquet"
BATCH_SIZE = 500_000

# ---------------------------------------------------------------
# BAND THRESHOLDS
# Based on distribution analysis of CO2_EMISS_CURR_PER_FLOOR_AREA:
#   p25 = 33, p50 = 42, p75 = 54, p95 = 74
# ---------------------------------------------------------------
def assign_co2_category(value):
    if value <= 0:
        return "Net Zero"
    elif value <= 33:
        return "Low"
    elif value <= 54:
        return "Medium"
    elif value <= 74:
        return "High"
    else:
        return "Very High"

# Vectorised version using pd.cut for batch processing
BINS   = [float("-inf"), 0, 33, 54, 74, float("inf")]
LABELS = ["Net Zero", "Low", "Medium", "High", "Very High"]

print("=" * 60)
print("  BELDA — Module 3 Script 4: co2_intensity_category")
print("=" * 60)
print(f"\n  Input  : {INPUT}")
print(f"  Output : {OUTPUT}")
print(f"  Batch  : {BATCH_SIZE:,} rows\n")
print("  Bands:")
print("    Net Zero  : <= 0       (biomass/renewable — SAP negative factors)")
print("    Low       : 1  – 33   (below p25 — better than average UK stock)")
print("    Medium    : 34 – 54   (p25–p75 — typical UK stock)")
print("    High      : 55 – 74   (p75–p95 — above average carbon intensity)")
print("    Very High : >= 75     (top 5% — high carbon intensity)\n")
print("  No rows dropped in this script.\n")

# ---------------------------------------------------------------
# COUNTERS
# ---------------------------------------------------------------
parquet_file    = pq.ParquetFile(INPUT)
writer          = None
total_in        = 0
rows_written    = 0
category_counts = {}
null_count      = 0
t0              = time.time()

print("  Streaming batches...\n")

for i, batch in enumerate(parquet_file.iter_batches(batch_size=BATCH_SIZE)):
    df = batch.to_pandas()
    batch_in   = len(df)
    total_in  += batch_in

    # ----------------------------------------------------------
    # Feature: co2_intensity_category
    # Physical meaning: bands CO2 intensity per floor area into
    # five human-readable categories for grouped analysis and
    # cross-tabulation against heating system, fuel type, and
    # construction era.
    # ----------------------------------------------------------
    df["co2_intensity_category"] = pd.cut(
        df["CO2_EMISS_CURR_PER_FLOOR_AREA"],
        bins=BINS,
        labels=LABELS,
        right=True
    ).astype(str)

    # ----------------------------------------------------------
    # Sanity checks
    # ----------------------------------------------------------
    batch_nulls = df["co2_intensity_category"].isnull().sum()
    null_count += batch_nulls
    if batch_nulls > 0:
        print(f"  WARNING: Batch {i+1} — {batch_nulls} null categories. "
              f"Check CO2_EMISS_CURR_PER_FLOOR_AREA for unexpected nulls.")

    unexpected = df[~df["co2_intensity_category"].isin(LABELS + ["nan"])]
    if len(unexpected) > 0:
        print(f"  WARNING: Batch {i+1} — {len(unexpected)} unexpected "
              f"category values.")

    # Accumulate category counts
    counts = df["co2_intensity_category"].value_counts()
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
          f"written: {rows_written:>12,}")

if writer:
    writer.close()

total_time = time.time() - t0

# ---------------------------------------------------------------
# SUMMARY
# ---------------------------------------------------------------
print(f"\n{'=' * 60}")
print("  Script 4 Complete")
print(f"{'=' * 60}")
print(f"  Rows in                        : {total_in:>12,}")
print(f"  Rows dropped                   : {'0':>12}  (none — no rows dropped)")
print(f"  Rows written                   : {rows_written:>12,}")
print(f"  Columns                        : 35 → 36")
print(f"  Null categories                : {null_count:>12,}")

print(f"\n  co2_intensity_category distribution:")
print(f"  {'Category':<12} {'Count':>10} {'%':>7}")
print(f"  {'-'*12} {'-'*10} {'-'*7}")

category_order = ["Net Zero", "Low", "Medium", "High", "Very High"]
for cat in category_order:
    count = category_counts.get(cat, 0)
    print(f"  {cat:<12} {count:>10,} {count/rows_written*100:>6.3f}%")

print(f"\n  Total time                     : {total_time:.1f}s")
print(f"\n  -> Ready for Script 5: efficiency_ratio\n")