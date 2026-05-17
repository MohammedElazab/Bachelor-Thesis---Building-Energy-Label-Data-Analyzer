import sys
sys.stdout.reconfigure(encoding="utf-8")

"""
BELDA - Module 4: Group Analysis
=================================
Produces six grouped summary tables from the cleaned, feature-engineered
EPC dataset. All operations are descriptive aggregations only - no modelling,
no imputation, no transformation. The dataset is assumed to be fully clean
and feature-engineered (output of Module 3).

Input:  epc_script4_4.parquet
Output: Six printed tables + epc_module4_results.xlsx (one sheet per table)
"""

import pandas as pd
import numpy as np

# ── Configuration ─────────────────────────────────────────────────────────────

INPUT_FILE = "epc_script4_4.parquet"
OUTPUT_FILE = "epc_module4_results.xlsx"

# Ordered label sequence for sorting (encoded as integers 1–9 in the dataset)
LABEL_ORDER = [1, 2, 3, 4, 5, 6, 7, 8, 9]
LABEL_NAMES = {1: "A++", 2: "A+", 3: "A", 4: "B", 5: "C", 6: "D", 7: "E", 8: "F", 9: "G"}

# Construction era order (chronological)
ERA_ORDER = [
    "Pre-1900", "1900-1929", "1930-1949", "1950-1966",
    "1967-1975", "1976-1982", "1983-1990", "1991-1995",
    "1996-2002", "2003-2006", "2007 onwards"
]

# ── Load Data ─────────────────────────────────────────────────────────────────

print("Loading dataset...")
df = pd.read_parquet(INPUT_FILE)
print(f"  Rows loaded: {len(df):,}")
print(f"  Columns:     {df.shape[1]}\n")

# ── Table 1: Mean Consumption by Energy Label ─────────────────────────────────
# Groups all buildings by their current energy label and computes mean, median,
# and standard deviation of energy consumption. Establishes the numeric profile
# of what each label grade means in terms of kWh/m²/year.

print("=" * 60)
print("TABLE 1 — Mean consumption by energy label")
print("=" * 60)

table1 = (
    df.groupby("CURRENT_ENERGY_RATING")["ENERGY_CONSUMPTION_CURRENT"]
    .agg(mean="mean", median="median", std="std", count="count")
    .loc[lambda x: x.index.isin(LABEL_ORDER)]
    .sort_index()
    .rename(index=LABEL_NAMES)
    .round(1)
)

print(table1.to_string())
print()

# ── Table 2: Label Distribution by Construction Era ───────────────────────────
# Cross-tabulates construction era against energy label. Each row is normalised
# to 100% so the label composition of each era can be compared regardless of
# how many buildings exist in each era. Shows how UK building regulations across
# decades translated into real energy performance outcomes.

print("=" * 60)
print("TABLE 2 — Label distribution by construction era (%)")
print("=" * 60)

table2_raw = pd.crosstab(
    df["CONSTRUCTION_AGE_BAND"],
    df["CURRENT_ENERGY_RATING"],
    normalize="index"
) * 100

# Reorder rows chronologically and rename columns to letter grades
table2 = (
    table2_raw
    .reindex([e for e in ERA_ORDER if e in table2_raw.index])
    .rename(columns=LABEL_NAMES)
    .round(1)
)

print(table2.to_string())
print()

# ── Table 3: EUI by Heating System ───────────────────────────────────────────
# Groups buildings by their primary heating system and computes mean, median,
# and count of energy consumption. Isolates the effect of heating system type
# on energy use intensity, independent of building age or envelope quality.

print("=" * 60)
print("TABLE 3 — Energy consumption by heating system")
print("=" * 60)

table3 = (
    df.groupby("MAINHEAT_DESCRIPTION")["ENERGY_CONSUMPTION_CURRENT"]
    .agg(mean="mean", median="median", std="std", count="count")
    .sort_values("mean")
    .round(1)
)

print(table3.to_string())
print()

# ── Table 4: CO₂ Intensity by Energy Label and Heating System ─────────────────
# 2D cross-table with energy labels as rows and heating systems as columns.
# Each cell shows mean CO₂ emissions per m². Separates carbon intensity from
# energy consumption to expose the fuel effect: two buildings at the same label
# grade can have very different carbon footprints depending on energy carrier.

print("=" * 60)
print("TABLE 4 — CO₂ intensity by energy label × heating system (mean kg/m²/yr)")
print("=" * 60)

table4 = (
    df.groupby(["CURRENT_ENERGY_RATING", "MAINHEAT_DESCRIPTION"])["CO2_EMISS_CURR_PER_FLOOR_AREA"]
    .mean()
    .unstack(level="MAINHEAT_DESCRIPTION")
    .loc[lambda x: x.index.isin(LABEL_ORDER)]
    .sort_index()
    .rename(index=LABEL_NAMES)
    .round(1)
)

print(table4.to_string())
print()

# ── Table 5: CO₂ Intensity by Construction Era ────────────────────────────────
# Groups buildings by construction era and computes mean and median CO₂
# intensity. Shows whether older buildings carry a compounded carbon penalty
# beyond just poor efficiency — reflecting both inefficient envelopes and
# reliance on higher-carbon fuels like oil and LPG.

print("=" * 60)
print("TABLE 5 — CO₂ intensity by construction era")
print("=" * 60)

table5 = (
    df.groupby("CONSTRUCTION_AGE_BAND")["CO2_EMISS_CURR_PER_FLOOR_AREA"]
    .agg(mean="mean", median="median", std="std", count="count")
    .reindex([e for e in ERA_ORDER if e in df["CONSTRUCTION_AGE_BAND"].unique()])
    .round(1)
)

print(table5.to_string())
print()

# ── Table 6: Correlation Matrix ───────────────────────────────────────────────
# Pearson correlation coefficients between four continuous variables:
# energy consumption, CO₂ intensity, envelope composite score, and floor area.
# Identifies which physical building characteristics are most strongly associated
# with energy outcomes. Used descriptively only — no causal claims are made.

print("=" * 60)
print("TABLE 6 — Correlation matrix")
print("=" * 60)

corr_cols = [
    "ENERGY_CONSUMPTION_CURRENT",
    "CO2_EMISS_CURR_PER_FLOOR_AREA",
    "envelope_composite_score",
    "TOTAL_FLOOR_AREA"
]

table6 = df[corr_cols].corr().round(3)

print(table6.to_string())
print()

# ── Export to Excel ───────────────────────────────────────────────────────────

print("Exporting all tables to", OUTPUT_FILE)

with pd.ExcelWriter(OUTPUT_FILE, engine="openpyxl") as writer:
    table1.to_excel(writer, sheet_name="T1_Consumption_by_Label")
    table2.to_excel(writer, sheet_name="T2_Label_by_Era")
    table3.to_excel(writer, sheet_name="T3_Consumption_by_Heating")
    table4.to_excel(writer, sheet_name="T4_CO2_Label_x_Heating")
    table5.to_excel(writer, sheet_name="T5_CO2_by_Era")
    table6.to_excel(writer, sheet_name="T6_Correlation_Matrix")

print("Done.")