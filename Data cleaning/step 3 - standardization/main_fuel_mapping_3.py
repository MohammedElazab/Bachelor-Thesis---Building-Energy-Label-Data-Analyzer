"""
BELDA — Module 2, Task 5: MAIN_FUEL Standardisation
=====================================================
1. Drops rows where MAIN_FUEL is INVALID!, NO DATA!, or
   "no heating system" variants
2. Maps all remaining values to 5 clean categories in place:
   Mains gas, Electricity, Oil, LPG, Biomass

Community variants are merged into their fuel type category
since MAINHEAT_DESCRIPTION already captures the community
distinction.

Reads  : epc_mainheat_mapped_clean.parquet
Writes : epc_module2e.parquet

Usage
-----
    python module2e_main_fuel.py
"""

import time
import re
import pyarrow as pa
import pyarrow.parquet as pq
import pandas as pd

INPUT      = "epc_mainheat_mapped_clean.parquet"
OUTPUT     = "epc_mainfuel_mapped.parquet"
BATCH_SIZE = 500_000 

# ── Rows to drop ──────────────────────────────────────────────────────────────
DROP_VALUES = {
    "INVALID!",
    "NO DATA!",
    "To be used only when there is no heating/hot-water system",
    "To be used only when there is no heating/hot-water system or data is from a community network",
}

# ── Keyword rules — order matters, first match wins ───────────────────────────
RULES = [
    ("Biomass",      ["wood", "pellet", "chip", "log",
                      "biomass", "coal", "anthracite",
                      "smokeless", "dual fuel", "b30k", "b30d",
                      "biogas", "bioethanol", "biodiesel",
                      "waste combustion", "solid fuel",
                      "heat from boilers using",
                      "heat from boilers that"]),
    ("Mains gas",    ["mains gas", "gas: mains gas",
                      "backwards compatibility"]),
    ("LPG",          ["lpg", "bottled lpg", "bulk lpg",
                      "gas: bulk lpg", "gas: bottled lpg",
                      "lng", "special condition"]),
    ("Oil",          ["oil", "rapeseed",
                      "appliances able to use mineral"]),
    ("Electricity",  ["electric", "heat pump",
                      "from heat network",
                      "heat from electric"]),
]

def classify(value):
    if pd.isna(value):
        return None
    text = str(value).lower().strip()
    for category, keywords in RULES:
        if any(kw in text for kw in keywords):
            return category
    return "Other"

# ── Pre-run tests ─────────────────────────────────────────────────────────────
tests = [
    ("mains gas (not community)",                           "Mains gas"),
    ("mains gas (community)",                               "Mains gas"),
    ("mains gas - this is for backwards compatibility only and should not be used", "Mains gas"),
    ("Gas: mains gas",                                      "Mains gas"),
    ("electricity (not community)",                         "Electricity"),
    ("electricity (community)",                             "Electricity"),
    ("Electricity: electricity, unspecified tariff",        "Electricity"),
    ("oil (not community)",                                 "Oil"),
    ("oil (community)",                                     "Oil"),
    ("Oil: heating oil",                                    "Oil"),
    ("LPG (not community)",                                 "LPG"),
    ("bottled LPG",                                         "LPG"),
    ("Gas: bulk LPG",                                       "LPG"),
    ("house coal (not community)",                          "Biomass"),
    ("wood logs",                                           "Biomass"),
    ("bulk wood pellets",                                   "Biomass"),
    ("anthracite",                                          "Biomass"),
    ("dual fuel - mineral + wood",                          "Biomass"),
    ("waste combustion (community)",                        "Biomass"),
    ("biomass (community)",                                 "Biomass"),
    ("biogas - landfill - this is for backwards compatibility only and should not be used", "Biomass"),
    ("Community heating schemes: heat from electric heat pump", "Electricity"),
    ("Community heating schemes: heat from mains gas",      "Mains gas"),
    ("from heat network data (community)",                  "Electricity"),
]

print("=" * 60)
print("  Pre-run classification tests")
print("=" * 60)
all_pass = True
for val, expected in tests:
    result = classify(val)
    status = "PASS" if result == expected else "FAIL"
    if status == "FAIL":
        all_pass = False
    print(f"  {status} | expected: {expected:<15} got: {str(result):<15} | {val[:55]}")

if not all_pass:
    print("\n  Some tests failed — fix rules before running.")
    exit(1)
else:
    print("\n  All tests passed. Starting full dataset processing...\n")

# ── Processing ────────────────────────────────────────────────────────────────
print("=" * 60)
print("  BELDA - Task 5: MAIN_FUEL Standardisation")
print("=" * 60)
print(f"\n  Input  : {INPUT}")
print(f"  Output : {OUTPUT}\n")

parquet_file    = pq.ParquetFile(INPUT)
writer          = None
total_in        = 0
rows_written    = 0
dropped_bad     = 0
category_counts = {}
t0              = time.time()

print("  Streaming batches...\n")

for i, batch in enumerate(parquet_file.iter_batches(batch_size=BATCH_SIZE)):
    df = batch.to_pandas()
    total_in += len(df)

    # Drop bad rows
    before = len(df)
    df = df[~df["MAIN_FUEL"].isin(DROP_VALUES)].reset_index(drop=True)
    dropped_bad += before - len(df)

    # Map in place
    df["MAIN_FUEL"] = df["MAIN_FUEL"].apply(classify)

    # Track distribution
    counts = df["MAIN_FUEL"].value_counts()
    for cat, n in counts.items():
        category_counts[cat] = category_counts.get(cat, 0) + n

    table = pa.Table.from_pandas(df, preserve_index=False)
    if writer is None:
        writer = pq.ParquetWriter(OUTPUT, table.schema, compression="snappy")
    writer.write_table(table)
    rows_written += len(df)

    print(f"  Batch {i+1:>3} | in: {len(df):>8,} | "
          f"dropped: {before - len(df):>5,} | "
          f"written: {rows_written:>12,}")

if writer:
    writer.close()

total_time = time.time() - t0

print(f"\n{'=' * 60}")
print("  Task 5 Complete — Category Distribution")
print(f"{'=' * 60}")
print(f"\n  {'Category':<15} {'Count':>10} {'%':>8}")
print(f"  {'-'*15} {'-'*10} {'-'*8}")
for cat in ["Mains gas", "Electricity", "Oil", "LPG", "Biomass", "Other"]:
    n = category_counts.get(cat, 0)
    print(f"  {cat:<15} {n:>10,} {n/total_in*100:>7.2f}%")

other_n = category_counts.get("Other", 0)
if other_n > 0:
    print(f"\n  WARNING: {other_n:,} rows mapped to 'Other' — review if significant")
else:
    print(f"\n  No unmatched values — all rows cleanly categorised")

print(f"\n  Rows in        : {total_in:>12,}")
print(f"  Dropped (bad)  : {dropped_bad:>12,}")
print(f"  Rows written   : {rows_written:>12,}")
print(f"  Columns        : 30 (unchanged)")
print(f"  Total time     : {total_time:.1f}s")
print(f"\n  -> Module 2 Complete!\n")