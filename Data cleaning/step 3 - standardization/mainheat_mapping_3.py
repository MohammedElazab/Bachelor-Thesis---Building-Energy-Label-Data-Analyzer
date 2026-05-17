"""
BELDA — Module 2, Task 4: Heating System Standardisation
=========================================================
Maps MAINHEAT_DESCRIPTION (1,249 unique values) to 8 clean
categories in place using keyword matching.

Includes Welsh language keywords and additional variants.

Reads  : epc_era_grouped.parquet
Writes : epc_mainheat_mapped.parquet

Usage
-----
    python mainheat_mapping_3.py
"""

import time
import re
import pyarrow as pa
import pyarrow.parquet as pq
import pandas as pd

INPUT      = "epc_era_grouped.parquet"
OUTPUT     = "epc_mainheat_mapped.parquet"
BATCH_SIZE = 500_000

# ── Keyword rules — order matters, first match wins ───────────────────────────
# (category, substring_keywords, whole_word_keywords)
# whole_word_keywords: matched as whole words only (won't match inside 'boiler')

RULES = [
    ("Heat pump",        ["heat pump",
                          "pwmp gwres"],                    []),

    ("Community",        ["community",
                          "cynllun cymunedol"],             []),

    ("LPG",              ["lpg", "bottled gas",
                          "bulk lpg"],                      []),

    ("Biomass",          ["wood", "pellet", "chip",
                          "biomass", "anthracite",
                          "smokeless", "dual fuel",
                          "b30k", "bioethanol",
                          "solid fuel", "solid-fuel",
                          "biofuel", "biogas",
                          "coed", "pelenni",              # Welsh: wood, pellets
                          "glo carreg"],                   # Welsh: anthracite
                         ["log", "coal", "glo"]),          # whole word: coal/Welsh coal

    ("Oil boiler",       ["olew"],                          # Welsh: oil
                         ["oil"]),                          # whole word only

    ("Electric storage", ["storage heater", "electricaire",
                          "electric ceiling",
                          "electric underfloor",
                          "underfloor heating, electric",
                          "underfloor, electric",
                          "room heater",
                          "no system present",
                          "portable electric",
                          "warm air, electric",
                          "warm air, electricaire",
                          "ceiling heating",
                          "electric boiler",
                          "boiler and radiators, electric",
                          "boiler, electric",
                          "radiator heating, electric",
                          "radiator heating, electricity",
                          "electricity",
                          "stor wresogyddion",            # Welsh: storage heaters
                          "gwresogi dan y llawr trydan",  # Welsh: electric underfloor
                          "gwresogyddion trydan",         # Welsh: electric heaters
                          "gwresogyddion ystafell, trydan", # Welsh: room heaters electric
                          "dim system ar gael",           # Welsh: no system present
                          "trydan"],                      # Welsh: electric (catch-all)
                         []),

    ("Gas boiler",       ["mains gas", "natural gas",
                          "warm air, mains gas",
                          "warm air, gas",
                          "boilers - gas",
                          "nwy prif gyflenwad",           # Welsh: mains gas
                          "awyr gynnes, nwy"],            # Welsh: warm air gas
                         []),
]

def classify(description):
    if pd.isna(description):
        return "Other"
    text = str(description).lower().strip()
    for category, substr_kws, word_kws in RULES:
        if any(kw in text for kw in substr_kws):
            return category
        if any(re.search(r'\b' + re.escape(kw) + r'\b', text) for kw in word_kws):
            return category
    return "Other"

# ── Quick local test before running ──────────────────────────────────────────
tests = [
    ("Boiler and radiators, mains gas",                "Gas boiler"),
    ("Boiler and radiators, oil",                      "Oil boiler"),
    ("Electric storage heaters",                       "Electric storage"),
    ("Air source heat pump, radiators, electric",      "Heat pump"),
    ("Community scheme",                               "Community"),
    ("Boiler and radiators, LPG",                      "LPG"),
    ("Boiler and radiators, wood pellets",             "Biomass"),
    ("Boiler and radiators, electric",                 "Electric storage"),
    ("Bwyler a rheiddiaduron, nwy prif gyflenwad",     "Gas boiler"),
    ("Pwmp gwres syGÇÖn tarddu yn yr awyr, trydan",    "Heat pump"),
    ("St+r wresogyddion trydan",                       "Electric storage"),
    ("Cynllun cymunedol",                              "Community"),
    ("Bwyler a rheiddiaduron, olew",                   "Oil boiler"),
    ("Solid-fuel boiler, solid fuel",                  "Biomass"),
    ("Boiler and radiators, liquid biofuel",           "Biomass"),
    ("Radiator heating, heat from boilers - gas",      "Gas boiler"),
]

print("=" * 60)
print("  Pre-run classification test")
print("=" * 60)
all_pass = True
for desc, expected in tests:
    result = classify(desc)
    status = "PASS" if result == expected else "FAIL"
    if status == "FAIL":
        all_pass = False
    print(f"  {status} | expected: {expected:<20} got: {result:<20} | {desc[:50]}")

if not all_pass:
    print("\n  Some tests failed — fix rules before running on full dataset.")
    exit(1)
else:
    print("\n  All tests passed. Starting full dataset processing...\n")

# ── Processing ────────────────────────────────────────────────────────────────
print("=" * 60)
print("  BELDA - Task 4: Heating System Standardisation")
print("=" * 60)
print(f"\n  Input  : {INPUT}")
print(f"  Output : {OUTPUT}\n")

parquet_file    = pq.ParquetFile(INPUT)
writer          = None
total_in        = 0
rows_written    = 0
category_counts = {}
t0              = time.time()

print("  Streaming batches...\n")

for i, batch in enumerate(parquet_file.iter_batches(batch_size=BATCH_SIZE)):
    df = batch.to_pandas()
    total_in += len(df)

    df["MAINHEAT_DESCRIPTION"] = df["MAINHEAT_DESCRIPTION"].apply(classify)

    counts = df["MAINHEAT_DESCRIPTION"].value_counts()
    for cat, n in counts.items():
        category_counts[cat] = category_counts.get(cat, 0) + n

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
print("  Task 4 Complete — Category Distribution")
print(f"{'=' * 60}")
print(f"\n  {'Category':<20} {'Count':>10} {'%':>8}")
print(f"  {'-'*20} {'-'*10} {'-'*8}")
for cat in ["Gas boiler", "Oil boiler", "Electric storage",
            "Heat pump", "Community", "LPG", "Biomass", "Other"]:
    n = category_counts.get(cat, 0)
    print(f"  {cat:<20} {n:>10,} {n/total_in*100:>7.2f}%")

other_n = category_counts.get("Other", 0)
if other_n > 0:
    print(f"\n  WARNING: {other_n:,} rows mapped to 'Other' — review if significant")
else:
    print(f"\n  No unmatched values — all rows cleanly categorised")

print(f"\n  Rows in        : {total_in:>12,}")
print(f"  Rows written   : {rows_written:>12,}")
print(f"  Columns        : 30 (unchanged)")
print(f"  Total time     : {total_time:.1f}s")
print(f"\n  -> Ready for Task 5: MAIN_FUEL Standardisation\n")