# -*- coding: utf-8 -*-
"""
BELDA - Energy Label Data Analyzer
Step 4: Exploratory Data Analysis (EDA)

Generates 16 publication-ready charts for the thesis.
All charts saved as high-resolution PNG files in ./charts/

Charts:
  Group 1 — Data Overview
    01_energy_label_distribution.png
    02_improvement_potential_distribution.png
    03_property_type_distribution.png

  Group 2 — What Drives the Energy Label
    04_label_by_construction_era.png
    05_label_by_wall_type.png
    06_label_by_wall_insulation.png
    07_label_by_heating_system.png
    08_label_by_main_fuel.png
    09_label_by_glazing_type.png
    10_label_by_roof_insulation.png

  Group 3 — Where Is Improvement Potential
    11_improvement_by_wall_type.png
    12_improvement_by_construction_era.png
    13_improvement_by_heating_system.png
    14_co2_by_property_type.png

  Group 4 — Correlations
    15_correlation_heatmap.png
    16_envelope_score_vs_rating.png
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

# ============================================================
# 0. SETUP
# ============================================================
INPUT_FILE = "epc_encoded.parquet"
CHARTS_DIR = "charts"
os.makedirs(CHARTS_DIR, exist_ok=True)

# ── Colour palette ──────────────────────────────────────────
# Energy label colours (A=dark green → G=dark red)
LABEL_COLOURS = {
    3: "#1a9641",  # A — dark green
    4: "#a6d96a",  # B — light green
    5: "#ffffbf",  # C — yellow
    6: "#fdae61",  # D — orange
    7: "#f46d43",  # E — red-orange
    8: "#d73027",  # F — red
    9: "#a50026",  # G — dark red
}
LABEL_NAMES = {3: "A", 4: "B", 5: "C", 6: "D", 7: "E", 8: "F", 9: "G"}

# General palette for other charts
PALETTE    = "#2C5F8A"   # main blue
PALETTE2   = "#E8A838"   # accent amber
BG_COLOUR  = "#F7F9FC"
GRID_COLOUR= "#E0E6ED"

# ── Matplotlib global style ──────────────────────────────────
plt.rcParams.update({
    "figure.facecolor"   : BG_COLOUR,
    "axes.facecolor"     : BG_COLOUR,
    "axes.grid"          : True,
    "grid.color"         : GRID_COLOUR,
    "grid.linewidth"     : 0.8,
    "axes.spines.top"    : False,
    "axes.spines.right"  : False,
    "axes.spines.left"   : False,
    "axes.spines.bottom" : True,
    "font.family"        : "DejaVu Sans",
    "axes.titlesize"     : 14,
    "axes.titleweight"   : "bold",
    "axes.labelsize"     : 11,
    "xtick.labelsize"    : 10,
    "ytick.labelsize"    : 10,
})

def save(fig, filename):
    path = os.path.join(CHARTS_DIR, filename)
    fig.savefig(path, dpi=150, bbox_inches="tight", facecolor=BG_COLOUR)
    plt.close(fig)
    print(f"  ✅ Saved: {filename}")

def fmt_millions(x, _):
    return f"{x/1e6:.1f}M"

def fmt_thousands(x, _):
    return f"{x/1e3:.0f}K" if x >= 1000 else f"{int(x)}"


# ============================================================
# 1. LOAD DATA
# ============================================================
print("Loading data...")
df = pd.read_parquet(INPUT_FILE)
print(f"Loaded {len(df):,} rows × {len(df.columns)} columns")

# Map numeric rating to letter labels for display
df["RATING_LABEL"] = df["CURRENT_ENERGY_RATING"].map(LABEL_NAMES)
df["POT_LABEL"]    = df["POTENTIAL_ENERGY_RATING"].map(LABEL_NAMES)

# Rebuild readable categorical columns from one-hot for charts
# Property type
prop_map = {
    "PROPERTY_TYPE_House"      : "House",
    "PROPERTY_TYPE_Flat"       : "Flat",
    "PROPERTY_TYPE_Maisonette" : "Maisonette",
    "PROPERTY_TYPE_Park home"  : "Park Home",
}
df["PROP_TYPE"] = "Bungalow"
for col, label in prop_map.items():
    if col in df.columns:
        df.loc[df[col] == 1, "PROP_TYPE"] = label

# Heating system
heat_map = {
    "MAINHEAT_DESCRIPTION_Gas boiler"      : "Gas Boiler",
    "MAINHEAT_DESCRIPTION_Electric storage": "Electric Storage",
    "MAINHEAT_DESCRIPTION_Oil boiler"      : "Oil Boiler",
    "MAINHEAT_DESCRIPTION_Heat pump"       : "Heat Pump",
    "MAINHEAT_DESCRIPTION_Community"       : "Community",
    "MAINHEAT_DESCRIPTION_LPG"             : "LPG",
}
df["HEAT_TYPE"] = "Biomass"
for col, label in heat_map.items():
    if col in df.columns:
        df.loc[df[col] == 1, "HEAT_TYPE"] = label

# Main fuel
fuel_map = {
    "MAIN_FUEL_Mains gas"  : "Mains Gas",
    "MAIN_FUEL_Electricity": "Electricity",
    "MAIN_FUEL_Oil"        : "Oil",
    "MAIN_FUEL_LPG"        : "LPG",
}
df["FUEL_TYPE"] = "Biomass"
for col, label in fuel_map.items():
    if col in df.columns:
        df.loc[df[col] == 1, "FUEL_TYPE"] = label

# Glazing
glaz_map = {
    "WINDOWS_DESCRIPTION_Single glazing"    : "Single",
    "WINDOWS_DESCRIPTION_Secondary glazing" : "Secondary",
    "WINDOWS_DESCRIPTION_Triple glazing"    : "Triple",
}
df["GLAZ_TYPE"] = "Double"
for col, label in glaz_map.items():
    if col in df.columns:
        df.loc[df[col] == 1, "GLAZ_TYPE"] = label

# Wall type (from one-hot)
wall_type_cols = {
    "WALL_TYPE_Cavity"             : "Cavity",
    "WALL_TYPE_Solid Brick"        : "Solid Brick",
    "WALL_TYPE_System Built"       : "System Built",
    "WALL_TYPE_Sandstone / Limestone": "Sandstone/Limestone",
    "WALL_TYPE_Timber Frame"       : "Timber Frame",
    "WALL_TYPE_Granite / Whinstone": "Granite/Whinstone",
    "WALL_TYPE_Cob"                : "Cob",
    "WALL_TYPE_Park Home"          : "Park Home",
}
df["WALL_TYPE_LABEL"] = "Other/Unknown"
for col, label in wall_type_cols.items():
    if col in df.columns:
        df.loc[df[col] == 1, "WALL_TYPE_LABEL"] = label

# Wall insulation label
insul_map = {0: "Unknown", 1: "Uninsulated", 2: "Partial", 3: "Insulated"}
df["WALL_INSUL_LABEL"] = df["WALL_INSULATION"].map(insul_map)

# Roof insulation label
roof_insul_map = {
    0: "Unknown/No Roof", 1: "None", 2: "Low",
    3: "At Rafters", 4: "Medium", 5: "High", 6: "Very High"
}
df["ROOF_INSUL_LABEL"] = df["ROOF_INSULATION"].map(roof_insul_map)

# Construction era label
era_map = {
    1: "Pre-1900", 2: "1900-29", 3: "1930-49", 4: "1950-66",
    5: "1967-75",  6: "1976-82", 7: "1983-90", 8: "1991-95",
    9: "1996-02",  10: "2003-06", 11: "2007+"
}
df["ERA_LABEL"] = df["CONSTRUCTION_AGE_BAND"].map(era_map)

print("Column reconstruction done. Generating charts...\n")


# ============================================================
# CHART 01 — Energy Label Distribution
# ============================================================
print("Chart 01: Energy label distribution")

counts = df["CURRENT_ENERGY_RATING"].value_counts().sort_index()
labels = [LABEL_NAMES[k] for k in counts.index]
colors = [LABEL_COLOURS[k] for k in counts.index]

fig, ax = plt.subplots(figsize=(10, 6))
bars = ax.bar(labels, counts.values, color=colors, edgecolor="white", linewidth=0.8, width=0.65)

for bar, val in zip(bars, counts.values):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 50000,
            f"{val/1e6:.2f}M", ha="center", va="bottom", fontsize=9, color="#444")

ax.set_title("Distribution of Current Energy Labels\nUK Residential Properties (n=24.5M)", pad=15)
ax.set_xlabel("Energy Label")
ax.set_ylabel("Number of Properties")
ax.yaxis.set_major_formatter(mticker.FuncFormatter(fmt_millions))
ax.set_facecolor(BG_COLOUR)
fig.tight_layout()
save(fig, "01_energy_label_distribution.png")


# ============================================================
# CHART 02 — Improvement Potential Distribution
# ============================================================
print("Chart 02: Improvement potential distribution")

imp_counts = df["improvement_potential"].value_counts().sort_index()

fig, ax = plt.subplots(figsize=(10, 6))
bars = ax.bar(imp_counts.index.astype(str), imp_counts.values,
              color=PALETTE, edgecolor="white", linewidth=0.8, width=0.6)

for bar, val in zip(bars, imp_counts.values):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 30000,
            f"{val/1e6:.2f}M", ha="center", va="bottom", fontsize=9, color="#444")

ax.set_title("Distribution of Improvement Potential\n(Number of Label Grades a Property Could Improve)", pad=15)
ax.set_xlabel("Improvement Potential (Label Grades)")
ax.set_ylabel("Number of Properties")
ax.yaxis.set_major_formatter(mticker.FuncFormatter(fmt_millions))
save(fig, "02_improvement_potential_distribution.png")


# ============================================================
# CHART 03 — Property Type Distribution
# ============================================================
print("Chart 03: Property type distribution")

pt_counts = df["PROP_TYPE"].value_counts()

fig, ax = plt.subplots(figsize=(9, 6))
bars = ax.barh(pt_counts.index, pt_counts.values,
               color=PALETTE, edgecolor="white", linewidth=0.8, height=0.6)

for bar, val in zip(bars, pt_counts.values):
    ax.text(val + 50000, bar.get_y() + bar.get_height()/2,
            f"{val/1e6:.2f}M", va="center", fontsize=9, color="#444")

ax.set_title("Property Type Distribution", pad=15)
ax.set_xlabel("Number of Properties")
ax.xaxis.set_major_formatter(mticker.FuncFormatter(fmt_millions))
ax.invert_yaxis()
save(fig, "03_property_type_distribution.png")


# ============================================================
# CHART 04 — Energy Label by Construction Era
# ============================================================
print("Chart 04: Label by construction era")

era_order  = [era_map[i] for i in range(1, 12)]
era_rating = (df.groupby("ERA_LABEL")["CURRENT_ENERGY_RATING"]
                .mean()
                .reindex(era_order))

fig, ax = plt.subplots(figsize=(12, 6))
bars = ax.bar(era_rating.index, era_rating.values,
              color=PALETTE, edgecolor="white", linewidth=0.8, width=0.7)

for bar, val in zip(bars, era_rating.values):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02,
            f"{val:.2f}", ha="center", va="bottom", fontsize=8.5, color="#444")

ax.set_title("Average Energy Rating by Construction Era\n(Lower number = better label)", pad=15)
ax.set_xlabel("Construction Era")
ax.set_ylabel("Mean Current Energy Rating (3=A → 9=G)")
ax.set_xticks(range(len(era_rating)))
ax.set_xticklabels(era_rating.index, rotation=35, ha="right")

# Add reference lines for label boundaries
for val, name in [(3.5,"A/B"), (4.5,"B/C"), (5.5,"C/D"), (6.5,"D/E"), (7.5,"E/F")]:
    ax.axhline(val, color=GRID_COLOUR, linewidth=1.2, linestyle="--", zorder=0)

save(fig, "04_label_by_construction_era.png")


# ============================================================
# CHART 05 — Energy Label by Wall Type
# ============================================================
print("Chart 05: Label by wall type")

wall_order = (df.groupby("WALL_TYPE_LABEL")["CURRENT_ENERGY_RATING"]
                .mean()
                .sort_values()
                .index.tolist())

wall_rating = (df.groupby("WALL_TYPE_LABEL")["CURRENT_ENERGY_RATING"]
                 .mean()
                 .reindex(wall_order))

fig, ax = plt.subplots(figsize=(11, 6))
bars = ax.barh(wall_rating.index, wall_rating.values,
               color=PALETTE, edgecolor="white", linewidth=0.8, height=0.65)

for bar, val in zip(bars, wall_rating.values):
    ax.text(val + 0.01, bar.get_y() + bar.get_height()/2,
            f"{val:.2f}", va="center", fontsize=9, color="#444")

ax.set_title("Average Energy Rating by Wall Type\n(Lower = better label)", pad=15)
ax.set_xlabel("Mean Current Energy Rating (3=A → 9=G)")
save(fig, "05_label_by_wall_type.png")


# ============================================================
# CHART 06 — Energy Label by Wall Insulation
# ============================================================
print("Chart 06: Label by wall insulation")

insul_order  = ["Uninsulated", "Partial", "Insulated", "Unknown"]
insul_rating = (df.groupby("WALL_INSUL_LABEL")["CURRENT_ENERGY_RATING"]
                  .mean()
                  .reindex(insul_order)
                  .dropna())

colours_insul = [LABEL_COLOURS[8], LABEL_COLOURS[6], LABEL_COLOURS[4], "#999999"]
colours_insul = colours_insul[:len(insul_rating)]

fig, ax = plt.subplots(figsize=(9, 6))
bars = ax.bar(insul_rating.index, insul_rating.values,
              color=colours_insul, edgecolor="white", linewidth=0.8, width=0.55)

for bar, val in zip(bars, insul_rating.values):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02,
            f"{val:.2f}", ha="center", va="bottom", fontsize=10, color="#444")

ax.set_title("Average Energy Rating by Wall Insulation Status\n(Lower = better label)", pad=15)
ax.set_xlabel("Wall Insulation Status")
ax.set_ylabel("Mean Current Energy Rating (3=A → 9=G)")
save(fig, "06_label_by_wall_insulation.png")


# ============================================================
# CHART 07 — Energy Label by Heating System
# ============================================================
print("Chart 07: Label by heating system")

heat_order = (df.groupby("HEAT_TYPE")["CURRENT_ENERGY_RATING"]
                .mean()
                .sort_values()
                .index.tolist())

heat_rating = (df.groupby("HEAT_TYPE")["CURRENT_ENERGY_RATING"]
                 .mean()
                 .reindex(heat_order))

fig, ax = plt.subplots(figsize=(11, 6))
bars = ax.barh(heat_rating.index, heat_rating.values,
               color=PALETTE, edgecolor="white", linewidth=0.8, height=0.6)

for bar, val in zip(bars, heat_rating.values):
    ax.text(val + 0.01, bar.get_y() + bar.get_height()/2,
            f"{val:.2f}", va="center", fontsize=9, color="#444")

ax.set_title("Average Energy Rating by Heating System\n(Lower = better label)", pad=15)
ax.set_xlabel("Mean Current Energy Rating (3=A → 9=G)")
save(fig, "07_label_by_heating_system.png")


# ============================================================
# CHART 08 — Energy Label by Main Fuel
# ============================================================
print("Chart 08: Label by main fuel")

fuel_order = (df.groupby("FUEL_TYPE")["CURRENT_ENERGY_RATING"]
                .mean()
                .sort_values()
                .index.tolist())

fuel_rating = (df.groupby("FUEL_TYPE")["CURRENT_ENERGY_RATING"]
                 .mean()
                 .reindex(fuel_order))

fig, ax = plt.subplots(figsize=(10, 6))
bars = ax.barh(fuel_rating.index, fuel_rating.values,
               color=PALETTE2, edgecolor="white", linewidth=0.8, height=0.55)

for bar, val in zip(bars, fuel_rating.values):
    ax.text(val + 0.01, bar.get_y() + bar.get_height()/2,
            f"{val:.2f}", va="center", fontsize=9, color="#444")

ax.set_title("Average Energy Rating by Main Fuel Type\n(Lower = better label)", pad=15)
ax.set_xlabel("Mean Current Energy Rating (3=A → 9=G)")
save(fig, "08_label_by_main_fuel.png")


# ============================================================
# CHART 09 — Energy Label by Glazing Type
# ============================================================
print("Chart 09: Label by glazing type")

glaz_order  = ["Single", "Secondary", "Double", "Triple"]
glaz_rating = (df.groupby("GLAZ_TYPE")["CURRENT_ENERGY_RATING"]
                 .mean()
                 .reindex(glaz_order)
                 .dropna())

glaz_colours = [LABEL_COLOURS[8], LABEL_COLOURS[7],
                LABEL_COLOURS[5], LABEL_COLOURS[3]]
glaz_colours = glaz_colours[:len(glaz_rating)]

fig, ax = plt.subplots(figsize=(9, 6))
bars = ax.bar(glaz_rating.index, glaz_rating.values,
              color=glaz_colours, edgecolor="white", linewidth=0.8, width=0.55)

for bar, val in zip(bars, glaz_rating.values):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02,
            f"{val:.2f}", ha="center", va="bottom", fontsize=10, color="#444")

ax.set_title("Average Energy Rating by Glazing Type\n(Lower = better label)", pad=15)
ax.set_xlabel("Glazing Type")
ax.set_ylabel("Mean Current Energy Rating (3=A → 9=G)")
save(fig, "09_label_by_glazing_type.png")


# ============================================================
# CHART 10 — Energy Label by Roof Insulation
# ============================================================
print("Chart 10: Label by roof insulation")

roof_order  = ["None", "Low", "At Rafters", "Medium", "High", "Very High", "Unknown/No Roof"]
roof_rating = (df.groupby("ROOF_INSUL_LABEL")["CURRENT_ENERGY_RATING"]
                 .mean()
                 .reindex(roof_order)
                 .dropna())

fig, ax = plt.subplots(figsize=(11, 6))
bars = ax.bar(roof_rating.index, roof_rating.values,
              color=PALETTE, edgecolor="white", linewidth=0.8, width=0.65)

for bar, val in zip(bars, roof_rating.values):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02,
            f"{val:.2f}", ha="center", va="bottom", fontsize=9, color="#444")

ax.set_title("Average Energy Rating by Roof Insulation Level\n(Lower = better label)", pad=15)
ax.set_xlabel("Roof Insulation Level")
ax.set_ylabel("Mean Current Energy Rating (3=A → 9=G)")
ax.set_xticks(range(len(roof_rating)))
ax.set_xticklabels(roof_rating.index, rotation=20, ha="right")
save(fig, "10_label_by_roof_insulation.png")


# ============================================================
# CHART 11 — Improvement Potential by Wall Type
# ============================================================
print("Chart 11: Improvement potential by wall type")

wall_imp = (df.groupby("WALL_TYPE_LABEL")["improvement_potential"]
              .mean()
              .sort_values(ascending=False))

fig, ax = plt.subplots(figsize=(11, 6))
bars = ax.barh(wall_imp.index[::-1], wall_imp.values[::-1],
               color=PALETTE2, edgecolor="white", linewidth=0.8, height=0.65)

for bar, val in zip(bars, wall_imp.values[::-1]):
    ax.text(val + 0.005, bar.get_y() + bar.get_height()/2,
            f"{val:.2f}", va="center", fontsize=9, color="#444")

ax.set_title("Average Improvement Potential by Wall Type\n(Higher = more room to improve)", pad=15)
ax.set_xlabel("Mean Improvement Potential (Label Grades)")
save(fig, "11_improvement_by_wall_type.png")


# ============================================================
# CHART 12 — Improvement Potential by Construction Era
# ============================================================
print("Chart 12: Improvement potential by construction era")

era_imp = (df.groupby("ERA_LABEL")["improvement_potential"]
             .mean()
             .reindex(era_order))

fig, ax = plt.subplots(figsize=(12, 6))
bars = ax.bar(era_imp.index, era_imp.values,
              color=PALETTE2, edgecolor="white", linewidth=0.8, width=0.7)

for bar, val in zip(bars, era_imp.values):
    if not np.isnan(val):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.005,
                f"{val:.2f}", ha="center", va="bottom", fontsize=8.5, color="#444")

ax.set_title("Average Improvement Potential by Construction Era\n(Higher = more room to improve)", pad=15)
ax.set_xlabel("Construction Era")
ax.set_ylabel("Mean Improvement Potential (Label Grades)")
ax.set_xticks(range(len(era_imp)))
ax.set_xticklabels(era_imp.index, rotation=35, ha="right")
save(fig, "12_improvement_by_construction_era.png")


# ============================================================
# CHART 13 — Improvement Potential by Heating System
# ============================================================
print("Chart 13: Improvement potential by heating system")

heat_imp = (df.groupby("HEAT_TYPE")["improvement_potential"]
              .mean()
              .sort_values(ascending=False))

fig, ax = plt.subplots(figsize=(11, 6))
bars = ax.barh(heat_imp.index[::-1], heat_imp.values[::-1],
               color=PALETTE, edgecolor="white", linewidth=0.8, height=0.6)

for bar, val in zip(bars, heat_imp.values[::-1]):
    ax.text(val + 0.005, bar.get_y() + bar.get_height()/2,
            f"{val:.2f}", va="center", fontsize=9, color="#444")

ax.set_title("Average Improvement Potential by Heating System\n(Higher = more room to improve)", pad=15)
ax.set_xlabel("Mean Improvement Potential (Label Grades)")
save(fig, "13_improvement_by_heating_system.png")


# ============================================================
# CHART 14 — CO2 Intensity by Property Type
# ============================================================
print("Chart 14: CO2 intensity by property type")

co2_by_type = (df.groupby("PROP_TYPE")["CO2_EMISS_CURR_PER_FLOOR_AREA"]
                 .mean()
                 .sort_values(ascending=False))

fig, ax = plt.subplots(figsize=(10, 6))
bars = ax.bar(co2_by_type.index, co2_by_type.values,
              color=PALETTE, edgecolor="white", linewidth=0.8, width=0.6)

for bar, val in zip(bars, co2_by_type.values):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.3,
            f"{val:.1f}", ha="center", va="bottom", fontsize=9, color="#444")

ax.set_title("Average CO₂ Emissions per Floor Area by Property Type", pad=15)
ax.set_xlabel("Property Type")
ax.set_ylabel("Mean CO₂ Emissions (kg/m²/year)")
save(fig, "14_co2_by_property_type.png")


# ============================================================
# CHART 15 — Correlation Heatmap
# ============================================================
print("Chart 15: Correlation heatmap")

corr_cols = [
    "CURRENT_ENERGY_RATING",
    "CONSTRUCTION_AGE_BAND",
    "WALL_INSULATION",
    "ROOF_INSULATION",
    "WALLS_ENERGY_EFF",
    "ROOF_ENERGY_EFF",
    "WINDOWS_ENERGY_EFF",
    "MAINHEAT_ENERGY_EFF",
    "HOT_WATER_ENERGY_EFF",
    "envelope_composite_score",
    "TOTAL_FLOOR_AREA",
    "CO2_EMISS_CURR_PER_FLOOR_AREA",
    "improvement_potential",
    "HOTWATER_SOLAR",
]

corr_cols   = [c for c in corr_cols if c in df.columns]
corr_matrix = df[corr_cols].corr()

# Shorter display names
short_names = {
    "CURRENT_ENERGY_RATING"       : "Energy Rating",
    "CONSTRUCTION_AGE_BAND"       : "Construction Era",
    "WALL_INSULATION"             : "Wall Insulation",
    "ROOF_INSULATION"             : "Roof Insulation",
    "WALLS_ENERGY_EFF"            : "Walls Efficiency",
    "ROOF_ENERGY_EFF"             : "Roof Efficiency",
    "WINDOWS_ENERGY_EFF"          : "Windows Efficiency",
    "MAINHEAT_ENERGY_EFF"         : "Heating Efficiency",
    "HOT_WATER_ENERGY_EFF"        : "Hot Water Efficiency",
    "envelope_composite_score"    : "Envelope Score",
    "TOTAL_FLOOR_AREA"            : "Floor Area",
    "CO2_EMISS_CURR_PER_FLOOR_AREA": "CO₂ per m²",
    "improvement_potential"       : "Improvement Potential",
    "HOTWATER_SOLAR"              : "Solar Hot Water",
}

corr_matrix.index   = [short_names.get(c, c) for c in corr_matrix.index]
corr_matrix.columns = [short_names.get(c, c) for c in corr_matrix.columns]

fig, ax = plt.subplots(figsize=(13, 10))
mask = np.triu(np.ones_like(corr_matrix, dtype=bool), k=1)

sns.heatmap(
    corr_matrix,
    mask=mask,
    annot=True,
    fmt=".2f",
    cmap="RdBu_r",
    center=0,
    vmin=-1, vmax=1,
    linewidths=0.5,
    linecolor="white",
    annot_kws={"size": 8},
    ax=ax,
    cbar_kws={"shrink": 0.8}
)

ax.set_title("Feature Correlation Matrix\n(Pearson correlation coefficients)", pad=15)
ax.tick_params(axis="x", rotation=45)
ax.tick_params(axis="y", rotation=0)
fig.tight_layout()
save(fig, "15_correlation_heatmap.png")


# ============================================================
# CHART 16 — Envelope Score vs Energy Rating
# Uses aggregated statistics instead of raw data to avoid
# memory issues with 24.5M rows
# ============================================================
print("Chart 16: Envelope score vs energy rating")

rating_labels = sorted(df["CURRENT_ENERGY_RATING"].unique())

# Compute percentiles per label using groupby — no sampling needed
stats = (df.groupby("CURRENT_ENERGY_RATING")["envelope_composite_score"]
           .describe(percentiles=[0.25, 0.5, 0.75])
           .reindex(rating_labels))

fig, ax = plt.subplots(figsize=(11, 6))

for i, r in enumerate(rating_labels):
    row    = stats.loc[r]
    q1     = row["25%"]
    median = row["50%"]
    q3     = row["75%"]
    lo     = max(row["min"], q1 - 1.5 * (q3 - q1))
    hi     = min(row["max"], q3 + 1.5 * (q3 - q1))
    colour = LABEL_COLOURS[r]
    label  = LABEL_NAMES[r]

    # Box
    ax.broken_barh([(i - 0.25, 0.5)], (q1, q3 - q1),
                   facecolors=colour, edgecolors="white",
                   linewidth=1.2, alpha=0.85)

    # Median line
    ax.plot([i - 0.25, i + 0.25], [median, median],
            color="white", linewidth=2.5, zorder=5)

    # Whiskers
    ax.plot([i, i], [lo, q1], color="#888", linewidth=1.2)
    ax.plot([i, i], [q3, hi], color="#888", linewidth=1.2)
    ax.plot([i - 0.15, i + 0.15], [lo, lo], color="#888", linewidth=1.2)
    ax.plot([i - 0.15, i + 0.15], [hi, hi], color="#888", linewidth=1.2)

    # Median value label
    ax.text(i, median + 0.04, f"{median:.2f}",
            ha="center", va="bottom", fontsize=9, color="#333", zorder=6)

ax.set_xticks(range(len(rating_labels)))
ax.set_xticklabels([LABEL_NAMES[r] for r in rating_labels])
ax.set_title("Envelope Composite Score by Energy Label\n(Higher score = better walls + roof + windows)", pad=15)
ax.set_xlabel("Energy Label")
ax.set_ylabel("Envelope Composite Score (1=Poor → 5=Excellent)")
ax.set_ylim(0.8, 5.4)
save(fig, "16_envelope_score_vs_rating.png")


# ============================================================
# SUMMARY REPORT
# ============================================================
print("\n" + "="*60)
print("EDA COMPLETE — Summary of key findings")
print("="*60)

most_common_label = LABEL_NAMES[df["CURRENT_ENERGY_RATING"].mode()[0]]
pct_d_or_worse    = (df["CURRENT_ENERGY_RATING"] >= 6).mean() * 100
pct_improvable    = (df["improvement_potential"] > 0).mean() * 100
avg_improvement   = df["improvement_potential"].mean()
worst_wall_type   = df.groupby("WALL_TYPE_LABEL")["CURRENT_ENERGY_RATING"].mean().idxmax()
best_heat_system  = df.groupby("HEAT_TYPE")["CURRENT_ENERGY_RATING"].mean().idxmin()
worst_era         = df.groupby("ERA_LABEL")["CURRENT_ENERGY_RATING"].mean().idxmax()
best_era          = df.groupby("ERA_LABEL")["CURRENT_ENERGY_RATING"].mean().idxmin()

print(f"  Most common energy label     : {most_common_label}")
print(f"  % rated D or worse           : {pct_d_or_worse:.1f}%")
print(f"  % with improvement potential : {pct_improvable:.1f}%")
print(f"  Average improvement potential: {avg_improvement:.2f} grades")
print(f"  Worst performing wall type   : {worst_wall_type}")
print(f"  Best performing heating      : {best_heat_system}")
print(f"  Worst construction era       : {worst_era}")
print(f"  Best construction era        : {best_era}")
print(f"\n  All 16 charts saved to: ./{CHARTS_DIR}/")
print("="*60)