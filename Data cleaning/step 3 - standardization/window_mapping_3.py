"""
BELDA — Module 2, Task 6: WINDOWS_DESCRIPTION Standardisation
==============================================================
Maps WINDOWS_DESCRIPTION (69 unique values) to 4 clean
categories in place based on glazing technology:

  Single glazing    : all single glazed variants
  Secondary glazing : all secondary glazing variants
  Double glazing    : all double/multiple glazing variants
  Triple glazing    : all triple/high performance variants

Coverage variants (fully/mostly/partial/some) are collapsed
into the dominant glazing technology category. Garbage entries
mapped to Other and dropped after.

Welsh language entries mapped using Welsh keywords.

Reads  : epc_module2e.parquet
Writes : epc_module2f.parquet

Usage
-----
    python module2f_windows.py
"""

import time
import pyarrow as pa
import pyarrow.parquet as pq
import pandas as pd

INPUT      = "epc_mainfuel_mapped.parquet" 
OUTPUT     = "epc_windows_mapped.parquet"
BATCH_SIZE = 500_000

# ── Keyword rules — order matters, first match wins ───────────────────────────
RULES = [
    ("Triple glazing",    ["triple", "high performance",
                           "ffenestri perfformiad uchel",  # Welsh: high performance
                           "gwydrau triphlyg"]),            # Welsh: triple glazed
    ("Secondary glazing", ["secondary",
                           "gwydrau eilaidd"]),             # Welsh: secondary glazed
    ("Single glazing",    ["single glazed", "single glazing",
                           "gwydrau sengl",                 # Welsh: single glazed
                           "rhai gwydrau"]),                # Welsh: some glazing
    ("Double glazing",    ["double", "multiple glazing",
                           "gwydrau dwbl",                  # Welsh: double glazed
                           "gwydrau lluosog"]),             # Welsh: multiple glazing
]

def classify(value):
    if pd.isna(value):
        return "Other"
    text = str(value).lower().strip()
    for category, keywords in RULES:
        if any(kw in text for kw in keywords):
            return category
    return "Other"

# ── Pre-run tests ─────────────────────────────────────────────────────────────
tests = [
    ("Fully double glazed",                "Double glazing"),
    ("Partial double glazing",             "Double glazing"),
    ("Mostly double glazing",              "Double glazing"),
    ("Some double glazing",                "Double glazing"),
    ("double glazing",                     "Double glazing"),
    ("Multiple glazing throughout",        "Double glazing"),
    ("Single glazed",                      "Single glazing"),
    ("Single glazeddouble glazing",        "Single glazing"),
    ("Single glazedSingle glazing",        "Single glazing"),
    ("High performance glazing",           "Triple glazing"),
    ("Fully triple glazed",                "Triple glazing"),
    ("Mostly triple glazing",              "Triple glazing"),
    ("Partial triple glazing",             "Triple glazing"),
    ("Full secondary glazing",             "Secondary glazing"),
    ("Partial secondary glazing",          "Secondary glazing"),
    ("Some secondary glazing",             "Secondary glazing"),
    ("Mostly secondary glazing",           "Secondary glazing"),
    ("Ffenestri perfformiad uchel",        "Triple glazing"),
    ("Gwydrau dwbl llawn",                 "Double glazing"),
    ("Gwydrau sengl",                      "Single glazing"),
    ("Gwydrau eilaidd llawn",              "Secondary glazing"),
    ("Gwydrau triphlyg llawn",             "Triple glazing"),
    ("Fully",                              "Other"),
    ("Mostly",                             "Other"),
    ("(other premises below)",             "Other"),
    ("Suspended, no insulation (assumed)", "Other"),
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
    print(f"  {status} | expected: {expected:<22} got: {result:<22} | {val[:40]}")

if not all_pass:
    print("\n  Some tests failed — fix rules before running.")
    exit(1)
else:
    print("\n  All tests passed. Starting full dataset processing...\n")

# ── Processing ────────────────────────────────────────────────────────────────
print("=" * 60)
print("  BELDA - Task 6: WINDOWS_DESCRIPTION Standardisation")
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

    df["WINDOWS_DESCRIPTION"] = df["WINDOWS_DESCRIPTION"].apply(classify)

    counts = df["WINDOWS_DESCRIPTION"].value_counts()
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
print("  Task 6 Complete — Category Distribution")
print(f"{'=' * 60}")
print(f"\n  {'Category':<22} {'Count':>10} {'%':>8}")
print(f"  {'-'*22} {'-'*10} {'-'*8}")
for cat in ["Double glazing", "Single glazing", "Triple glazing",
            "Secondary glazing", "Other"]:
    n = category_counts.get(cat, 0)
    print(f"  {cat:<22} {n:>10,} {n/total_in*100:>7.2f}%")

other_n = category_counts.get("Other", 0)
if other_n > 0:
    print(f"\n  WARNING: {other_n:,} rows mapped to 'Other' — will be dropped next")
else:
    print(f"\n  No unmatched values")

print(f"\n  Rows in        : {total_in:>12,}")
print(f"  Rows written   : {rows_written:>12,}")
print(f"  Columns        : 30 (unchanged)")
print(f"  Total time     : {total_time:.1f}s")
print(f"\n  -> Next: Drop Other rows\n")