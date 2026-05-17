"""
BELDA — Task 3 Step 2: Construction Era Grouping
=================================================
Maps all CONSTRUCTION_AGE_BAND values to 11 standardised
era groups in place. Handles both:
  - Standard bands: 'England and Wales: 1996-2002' -> '1996-2002'
  - Single years  : '1965' -> '1950-1966'

Era groups:
  Pre-1900      : before 1900
  1900-1929     : 1900-1929
  1930-1949     : 1930-1949
  1950-1966     : 1950-1966
  1967-1975     : 1967-1975
  1976-1982     : 1976-1982
  1983-1990     : 1983-1990
  1991-1995     : 1991-1995
  1996-2002     : 1996-2002
  2003-2006     : 2003-2006
  2007 onwards  : 2007 and later

Reads  : epc_changing_no_bad_age_bands.parquet
Writes : epc_era_grouped.parquet

Usage
-----
    python age_band_categorization_3.py
"""

import time
import pyarrow as pa
import pyarrow.parquet as pq
import pandas as pd

INPUT      = "epc_changing_no_bad_age_bands.parquet"
OUTPUT     = "epc_era_grouped.parquet"
BATCH_SIZE = 500_000

# ── Standard band -> era mapping ──────────────────────────────────────────────
BAND_TO_ERA = {
    "England and Wales: before 1900" : "Pre-1900",
    "England and Wales: 1900-1929"   : "1900-1929",
    "England and Wales: 1930-1949"   : "1930-1949",
    "England and Wales: 1950-1966"   : "1950-1966",
    "England and Wales: 1967-1975"   : "1967-1975",
    "England and Wales: 1976-1982"   : "1976-1982",
    "England and Wales: 1983-1990"   : "1983-1990",
    "England and Wales: 1991-1995"   : "1991-1995",
    "England and Wales: 1996-2002"   : "1996-2002",
    "England and Wales: 2003-2006"   : "2003-2006",
    "England and Wales: 2007 onwards": "2007 onwards",
    "England and Wales: 2007-2011"   : "2007 onwards",
    "England and Wales: 2012 onwards": "2007 onwards",
    "England and Wales: 2012-2021"   : "2007 onwards",
    "England and Wales: 2022 onwards": "2007 onwards",
}

def year_to_era(year: int) -> str:
    """Map a single construction year to its era group."""
    if year < 1900: return "Pre-1900"
    elif year <= 1929: return "1900-1929"
    elif year <= 1949: return "1930-1949"
    elif year <= 1966: return "1950-1966"
    elif year <= 1975: return "1967-1975"
    elif year <= 1982: return "1976-1982"
    elif year <= 1990: return "1983-1990"
    elif year <= 1995: return "1991-1995"
    elif year <= 2002: return "1996-2002"
    elif year <= 2006: return "2003-2006"
    else:              return "2007 onwards"

def map_era(val: str) -> str:
    """Map any CONSTRUCTION_AGE_BAND value to an era group."""
    val = str(val).strip()
    # Standard band
    if val in BAND_TO_ERA:
        return BAND_TO_ERA[val]
    # Single year
    if val.isdigit():
        return year_to_era(int(val))
    # Anything else — should not exist after Step 1 but flag it
    return "Unknown"

# ── Processing ────────────────────────────────────────────────────────────────
print("=" * 60)
print("  BELDA - Task 3 Step 2: Era Grouping")
print("=" * 60)
print(f"\n  Input  : {INPUT}")
print(f"  Output : {OUTPUT}\n")

parquet_file  = pq.ParquetFile(INPUT)
writer        = None
total_in      = 0
rows_written  = 0
unknown_count = 0
t0            = time.time()

print("  Streaming batches...\n")

for i, batch in enumerate(parquet_file.iter_batches(batch_size=BATCH_SIZE)):
    df = batch.to_pandas()
    total_in += len(df)

    # Map in place
    df["CONSTRUCTION_AGE_BAND"] = df["CONSTRUCTION_AGE_BAND"].apply(map_era)

    # Track any unexpected values that slipped through
    unknown_count += (df["CONSTRUCTION_AGE_BAND"] == "Unknown").sum()

    table = pa.Table.from_pandas(df, preserve_index=False)
    if writer is None:
        writer = pq.ParquetWriter(OUTPUT, table.schema, compression="snappy")
    writer.write_table(table)
    rows_written += len(df)

    print(f"  Batch {i+1:>3} | in: {len(df):>8,} | written: {rows_written:>12,}")

if writer:
    writer.close()

total_time = time.time() - t0

print(f"\n{'=' * 60}")
print("  Task 3 Step 2 Complete")
print(f"{'=' * 60}")
print(f"  Rows in          : {total_in:>12,}")
print(f"  Rows written     : {rows_written:>12,}")
print(f"  Unknown values   : {unknown_count:>12,}  "
      f"({'none — clean' if unknown_count == 0 else 'REVIEW NEEDED'})")
print(f"  Total time       : {total_time:.1f}s")
print(f"\n  Era distribution will be verified in next step.")
print(f"  -> Ready for Task 3 Verification\n")