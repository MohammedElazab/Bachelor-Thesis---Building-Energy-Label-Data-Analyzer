"""
BELDA — Step 2a: Roof Null Cross-Analysis
==========================================
Investigates whether ROOF_ENERGY_EFF and ROOF_ENV_EFF nulls
are structurally caused by property type (flats/maisonettes)
or are random missing data (assessor didn't fill them in).

Produces:
  - step2a_roof_null_analysis.csv  : full breakdown table
  - Printed summary in terminal

Usage
-----
    python step2a_roof_null_analysis.py
"""

import time
import pyarrow.parquet as pq
import pandas as pd

INPUT      = "epc_missing_field_removed.parquet"
OUTPUT_CSV = "step2a_roof_null_analysis.csv"
BATCH_SIZE = 500_000

ROOF_FIELD = "ROOF_ENERGY_EFF"   # ROOF_ENV_EFF is identical so one check covers both

print("=" * 60)
print("  BELDA - Step 2a: Roof Null Cross-Analysis")
print("=" * 60)

# ── Accumulators ──────────────────────────────────────────────────────────────
# For each PROPERTY_TYPE we track:
#   - total rows
#   - rows where ROOF_ENERGY_EFF is null
#   - rows where ROOF_ENERGY_EFF is NOT null

from collections import defaultdict
total_by_type       = defaultdict(int)
null_by_type        = defaultdict(int)
not_null_by_type    = defaultdict(int)

# Also track: among houses (non-flats), how many have roof nulls?
# This is the key question — if houses also have nulls, it's random missingness

total_rows  = 0
t0 = time.time()

parquet_file = pq.ParquetFile(INPUT)

print("\n  Scanning batches...\n")
for i, batch in enumerate(parquet_file.iter_batches(
        batch_size=BATCH_SIZE,
        columns=["PROPERTY_TYPE", "BUILT_FORM", ROOF_FIELD])):

    df = batch.to_pandas()

    is_null = df[ROOF_FIELD].isna()

    for prop_type, group in df.groupby("PROPERTY_TYPE", dropna=False):
        key = str(prop_type) if pd.notna(prop_type) else "Unknown"
        mask_null     = group[ROOF_FIELD].isna()
        total_by_type[key]    += len(group)
        null_by_type[key]     += mask_null.sum()
        not_null_by_type[key] += (~mask_null).sum()

    total_rows += len(df)
    print(f"  Batch {i+1:>3} | {total_rows:>12,} rows | {time.time()-t0:.0f}s elapsed")

print(f"\n  Scan complete. {total_rows:,} total rows.\n")

# ── Build summary table ───────────────────────────────────────────────────────
rows = []
for prop_type in sorted(total_by_type.keys()):
    total   = total_by_type[prop_type]
    nulls   = null_by_type[prop_type]
    present = not_null_by_type[prop_type]
    null_pct    = round(nulls   / total * 100, 2) if total > 0 else 0
    present_pct = round(present / total * 100, 2) if total > 0 else 0
    rows.append({
        "property_type":       prop_type,
        "total_rows":          total,
        "roof_null_count":     nulls,
        "roof_null_pct":       null_pct,
        "roof_present_count":  present,
        "roof_present_pct":    present_pct,
    })

report = pd.DataFrame(rows).sort_values("roof_null_pct", ascending=False)

# ── Print report ──────────────────────────────────────────────────────────────
print("=" * 60)
print("  ROOF_ENERGY_EFF Nulls by Property Type")
print("  (ROOF_ENV_EFF is identical — same rows are null)")
print("=" * 60)
print(f"\n  {'Property Type':<20} {'Total Rows':>12} {'Roof Null':>10} {'Null %':>8} {'Has Roof':>10} {'Has %':>7}")
print(f"  {'-'*20} {'-'*12} {'-'*10} {'-'*8} {'-'*10} {'-'*7}")
for _, row in report.iterrows():
    print(f"  {row['property_type']:<20} "
          f"{row['total_rows']:>12,} "
          f"{row['roof_null_count']:>10,} "
          f"{row['roof_null_pct']:>7.2f}% "
          f"{row['roof_present_count']:>10,} "
          f"{row['roof_present_pct']:>6.2f}%")

# ── Interpretation helper ─────────────────────────────────────────────────────
print(f"\n{'=' * 60}")
print("  Interpretation Guide")
print(f"{'=' * 60}")
print("""
  Read the 'Null %' column per property type:

  - Flat / Maisonette near 100% null
    -> Structural missingness. Roof fields don't apply.
       These are NOT data quality issues.

  - House / Bungalow near 0% null
    -> Roof was assessed as expected.
       Any nulls here ARE genuine data quality issues.

  - House / Bungalow with significant null %
    -> Mixed: some structural, some random missingness.
       Needs further investigation.
""")

report.to_csv(OUTPUT_CSV, index=False)
print(f"  Full report saved to: {OUTPUT_CSV}")
print("=" * 60)