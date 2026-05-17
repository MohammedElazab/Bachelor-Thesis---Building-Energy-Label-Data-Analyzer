"""
BELDA — Task 4: Investigate 'Other' heating system rows
========================================================
Finds all MAINHEAT_DESCRIPTION values that mapped to 'Other'
and saves them to an MD file for review.

Usage
-----
    python check_other_heating_3.py
"""

import re
import pyarrow.parquet as pq
import pandas as pd
from collections import Counter

INPUT      = "epc_era_grouped.parquet"
OUT_MD     = "mainheat_other_values.md"
BATCH_SIZE = 500_000

# Same rules as module2d
RULES = [
    ("Heat pump",        ["heat pump"],          []),
    ("Community",        ["community"],          []),
    ("LPG",              ["lpg", "bottled gas", "bulk lpg"], []),
    ("Biomass",          ["wood", "pellet", "chip", "biomass",
                          "anthracite", "smokeless", "dual fuel",
                          "b30k", "bioethanol"], ["log", "coal"]),
    ("Oil boiler",       [],                     ["oil"]),
    ("Electric storage", ["storage heater", "electricaire",
                          "electric ceiling", "electric underfloor",
                          "underfloor heating, electric",
                          "underfloor, electric", "room heater",
                          "no system present", "portable electric",
                          "warm air, electric", "warm air, electricaire",
                          "ceiling heating"], []),
    ("Gas boiler",       ["mains gas", "natural gas",
                          "warm air, mains gas", "warm air, gas"], []),
]

def classify(description):
    if pd.isna(description): return "Other"
    text = str(description).lower().strip()
    for category, substr_kws, word_kws in RULES:
        if any(kw in text for kw in substr_kws): return category
        if any(re.search(r'\b' + kw + r'\b', text) for kw in word_kws): return category
    return "Other"

other_counts = Counter()
total_rows   = 0

parquet_file = pq.ParquetFile(INPUT)
print("Scanning for Other values...")
for i, batch in enumerate(parquet_file.iter_batches(
        batch_size=BATCH_SIZE,
        columns=["MAINHEAT_DESCRIPTION"])):
    df = batch.to_pandas()
    total_rows += len(df)
    mask = df["MAINHEAT_DESCRIPTION"].apply(classify) == "Other"
    other_counts.update(df.loc[mask, "MAINHEAT_DESCRIPTION"].tolist())
    print(f"  Batch {i+1:>3} | {total_rows:>12,} rows scanned", end="\r")

print(f"\n\nTotal Other values : {sum(other_counts.values()):,}")
print(f"Unique descriptions: {len(other_counts):,}")

with open(OUT_MD, "w", encoding="utf-8") as f:
    f.write("# MAINHEAT_DESCRIPTION — Unmatched 'Other' Values\n\n")
    f.write(f"**Total Other rows:** {sum(other_counts.values()):,}  \n")
    f.write(f"**Unique descriptions:** {len(other_counts):,}\n\n")
    f.write("| Rank | Count | % of total | Description |\n")
    f.write("|---|---|---|---|\n")
    for i, (val, count) in enumerate(other_counts.most_common(), 1):
        f.write(f"| {i} | {count:,} | {count/total_rows*100:.3f}% | {val} |\n")

print(f"Saved to: {OUT_MD}")