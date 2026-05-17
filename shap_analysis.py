# -*- coding: utf-8 -*-
"""
BELDA - Energy Label Data Analyzer
Step 6: SHAP Explanations

What this script does:
- Loads the trained LightGBM model and test set
- Calculates SHAP values for 5,000 sampled test houses
- Generates 4 thesis-ready charts:
    01_shap_summary.png       — feature impact across all houses
    02_shap_bar.png           — mean absolute SHAP per feature
    03_shap_dependence.png    — how wall insulation affects predictions
    04_shap_waterfall.png     — why one specific house got its label
- Saves SHAP values to shap_values.csv

Why 5,000 houses:
    SHAP is computationally expensive. 5,000 houses gives statistically
    representative results and takes minutes instead of hours.
    This is standard practice in applied ML research.
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pickle
import shap
import sys
import os

sys.stdout.reconfigure(encoding='utf-8')
os.makedirs("charts", exist_ok=True)

# Colour palette — consistent with EDA charts
LABEL_MAP    = {0:"A", 1:"B", 2:"C", 3:"D", 4:"E", 5:"F", 6:"G"}
LABEL_COLOURS = {
    0: "#1a9641",  # A
    1: "#a6d96a",  # B
    2: "#ffffbf",  # C
    3: "#fdae61",  # D
    4: "#f46d43",  # E
    5: "#d73027",  # F
    6: "#a50026",  # G
}
BG_COLOUR = "#F7F9FC"

plt.rcParams.update({
    "figure.facecolor" : BG_COLOUR,
    "axes.facecolor"   : BG_COLOUR,
    "font.family"      : "DejaVu Sans",
    "axes.titlesize"   : 13,
    "axes.titleweight" : "bold",
    "axes.labelsize"   : 11,
})

# ============================================================
# 1. LOAD MODEL AND TEST SET
# ============================================================
print("Loading model...")
with open("belda_model.pkl", "rb") as f:
    model = pickle.load(f)
print("✅ Model loaded")

print("Loading test set...")
test_df = pd.read_parquet("epc_test.parquet")
print(f"✅ Test set loaded: {len(test_df):,} rows")

# Separate features from target
TARGET     = "CURRENT_ENERGY_RATING"
FEATURE_COLS = [col for col in test_df.columns if col != TARGET]

X_test = test_df[FEATURE_COLS].copy()
y_test = test_df[TARGET].copy()

# Convert Int64 to float32 for SHAP compatibility
for col in X_test.select_dtypes(include="Int64").columns:
    X_test[col] = X_test[col].astype("float32")
for col in X_test.select_dtypes(include=["int64","int32","int8"]).columns:
    X_test[col] = X_test[col].astype("float32")
for col in X_test.select_dtypes(include="float64").columns:
    X_test[col] = X_test[col].astype("float32")


# ============================================================
# 2. USE FULL TEST SET FOR SHAP
# ============================================================
print("\nUsing full test set for SHAP analysis...")

X_shap = X_test.reset_index(drop=True)
y_shap = y_test.reset_index(drop=True)

# Remap to 0-based for display
y_shap_mapped = y_shap - 3

print(f"✅ Using all {len(X_shap):,} test houses")
print(f"Label distribution:")
for label, count in y_shap.value_counts().sort_index().items():
    print(f"  {label} ({LABEL_MAP[int(label)-3]}): {count:,}")


# ============================================================
# 3. CALCULATE SHAP VALUES
# ============================================================
print(f"\nCalculating SHAP values for all {len(X_shap):,} test houses...")
print("This will take longer than the sample version — expect 20–60 minutes.")

explainer   = shap.TreeExplainer(model)
shap_values = explainer.shap_values(X_shap)

# shap_values shape: (n_classes, n_samples, n_features) for LightGBM
# We focus on the dominant class D (index 3) for single-class plots
# and use all classes for the summary plot

print("✅ SHAP values calculated")
print(f"SHAP values shape: {np.array(shap_values).shape}")


# ============================================================
# 4. SAVE SHAP VALUES TO CSV
# ============================================================
print("\nSaving SHAP values to CSV...")

# LightGBM returns shap_values shape: (n_samples, n_features, n_classes)
# Rearrange to (n_classes, n_samples, n_features) for consistency
shap_array = np.array(shap_values)  # shape: (n_samples, n_features, n_classes)

# Mean absolute SHAP across all classes — overall feature importance
# Average over samples (axis=0) and classes (axis=2)
mean_abs_shap = np.mean(np.abs(shap_array), axis=(0, 2))  # shape: (n_features,)

shap_importance = pd.DataFrame({
    "feature"        : FEATURE_COLS,
    "mean_abs_shap"  : mean_abs_shap,
}).sort_values("mean_abs_shap", ascending=False).reset_index(drop=True)

shap_importance.to_csv("shap_importance.csv", index=False, encoding="utf-8")
print("✅ Saved: shap_importance.csv")

# Helper: extract shap values for a specific class
# shap_array shape: (n_samples, n_features, n_classes)
def get_class_shap(cls_idx):
    return shap_array[:, :, cls_idx]  # shape: (n_samples, n_features)

# Class D = index 3 (rating 6, remapped to 3)
shap_class    = 3
shap_for_D    = get_class_shap(shap_class)  # (n_samples, n_features)


# ============================================================
# 5. CHART 1 — SHAP SUMMARY PLOT
# Shows how each feature affects predictions across all houses.
# Each dot is one house. Red = high feature value, Blue = low.
# Position on x-axis = how much it pushed the prediction.
# ============================================================
print("\nGenerating Chart 1: SHAP Summary Plot...")

# Use class D (index 3) — most common label, most representative
shap_class = 3  # D

fig, ax = plt.subplots(figsize=(12, 9))
shap.summary_plot(
    shap_for_D,
    X_shap,
    feature_names=FEATURE_COLS,
    plot_type="dot",
    max_display=20,
    show=False,
    color_bar=True,
    alpha=0.6,
)
plt.title(
    "SHAP Summary Plot — Feature Impact on Energy Label D Prediction\n"
    "(Each dot = one house. Red = high feature value, Blue = low. "
    "Position = impact on prediction.)",
    pad=12, fontsize=12, fontweight="bold"
)
plt.tight_layout()
plt.savefig("charts/01_shap_summary.png", dpi=150,
            bbox_inches="tight", facecolor=BG_COLOUR)
plt.close()
print("✅ Saved: charts/01_shap_summary.png")


# ============================================================
# 6. CHART 2 — SHAP BAR PLOT (mean absolute SHAP)
# Clean horizontal bar chart showing overall feature importance
# based on SHAP — more reliable than model's built-in importance.
# ============================================================
print("Generating Chart 2: SHAP Bar Plot...")

top20 = shap_importance.head(20)

fig, ax = plt.subplots(figsize=(11, 8))
bars = ax.barh(
    top20["feature"][::-1],
    top20["mean_abs_shap"][::-1],
    color="#2C5F8A", edgecolor="white", linewidth=0.8, height=0.7
)

for bar, val in zip(bars, top20["mean_abs_shap"][::-1]):
    ax.text(val + 0.0005, bar.get_y() + bar.get_height()/2,
            f"{val:.4f}", va="center", fontsize=8.5, color="#444")

ax.set_title(
    "Top 20 Features by Mean Absolute SHAP Value\n"
    "(Higher = stronger influence on energy label prediction)",
    pad=12
)
ax.set_xlabel("Mean |SHAP Value| across all classes")
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.spines["left"].set_visible(False)
fig.tight_layout()
fig.savefig("charts/02_shap_bar.png", dpi=150,
            bbox_inches="tight", facecolor=BG_COLOUR)
plt.close()
print("✅ Saved: charts/02_shap_bar.png")


# ============================================================
# 7. CHART 3 — SHAP DEPENDENCE PLOT
# Shows how WALL_INSULATION values (0=Unknown, 1=Uninsulated,
# 2=Partial, 3=Insulated) affect predictions for label D.
# Each dot is one house, coloured by envelope_composite_score.
# ============================================================
print("Generating Chart 3: SHAP Dependence Plot...")

# Find column index for WALL_INSULATION and envelope_composite_score
wi_idx  = FEATURE_COLS.index("WALL_INSULATION")
env_idx = FEATURE_COLS.index("envelope_composite_score") \
          if "envelope_composite_score" in FEATURE_COLS else None

fig, ax = plt.subplots(figsize=(11, 7))

wi_values   = X_shap["WALL_INSULATION"].values
shap_wi     = shap_for_D[:, wi_idx]

if env_idx is not None:
    env_values = X_shap["envelope_composite_score"].values
    sc = ax.scatter(
        wi_values, shap_wi,
        c=env_values, cmap="RdYlGn",
        alpha=0.4, s=15, edgecolors="none"
    )
    cbar = plt.colorbar(sc, ax=ax)
    cbar.set_label("Envelope Composite Score", fontsize=10)
else:
    ax.scatter(wi_values, shap_wi, alpha=0.4, s=15,
               color="#2C5F8A", edgecolors="none")

# Add x-axis labels
ax.set_xticks([0, 1, 2, 3])
ax.set_xticklabels(["Unknown", "Uninsulated", "Partial", "Insulated"],
                   fontsize=10)

ax.axhline(0, color="#999", linewidth=1, linestyle="--")
ax.set_title(
    "SHAP Dependence Plot — Wall Insulation vs Label D Prediction\n"
    "(Above zero = pushes toward D label. "
    "Colour = Envelope Composite Score.)",
    pad=12
)
ax.set_xlabel("Wall Insulation Status")
ax.set_ylabel("SHAP Value for Label D")
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
fig.tight_layout()
fig.savefig("charts/03_shap_dependence.png", dpi=150,
            bbox_inches="tight", facecolor=BG_COLOUR)
plt.close()
print("✅ Saved: charts/03_shap_dependence.png")


# ============================================================
# 8. CHART 4 — SHAP WATERFALL PLOT
# Shows why one specific house got its predicted label.
# We pick the house closest to the median prediction — the
# most "typical" house in the sample.
# ============================================================
print("Generating Chart 4: SHAP Waterfall Plot...")

# Find the most "average" house — closest to median SHAP sum
shap_sums  = np.sum(np.abs(shap_for_D), axis=1)
median_sum = np.median(shap_sums)
house_idx  = int(np.argmin(np.abs(shap_sums - median_sum)))

house_actual    = LABEL_MAP[int(y_shap_mapped.iloc[house_idx])]
house_predicted = LABEL_MAP[int(model.predict(
    X_shap.iloc[[house_idx]]
)[0])]

# Get top 12 features by absolute SHAP for this house
house_shap  = shap_for_D[house_idx]
top_idx     = np.argsort(np.abs(house_shap))[::-1][:12]
top_features = [FEATURE_COLS[i] for i in top_idx]
top_shap     = [house_shap[i] for i in top_idx]
top_values   = [X_shap.iloc[house_idx][FEATURE_COLS[i]] for i in top_idx]

# Shorten feature names for display
short_names = {
    "TOTAL_FLOOR_AREA"             : "Floor Area",
    "CONSTRUCTION_AGE_BAND"        : "Construction Era",
    "envelope_composite_score"     : "Envelope Score",
    "MAINHEAT_ENERGY_EFF"          : "Heating Efficiency",
    "HOT_WATER_ENERGY_EFF"         : "Hot Water Efficiency",
    "HOT_WATER_ENV_EFF"            : "Hot Water Env. Efficiency",
    "ROOF_ENERGY_EFF"              : "Roof Efficiency",
    "MAINHEAT_ENV_EFF"             : "Heating Env. Efficiency",
    "WALLS_ENERGY_EFF"             : "Walls Efficiency",
    "ROOF_INSULATION"              : "Roof Insulation",
    "WINDOWS_ENERGY_EFF"           : "Windows Efficiency",
    "WALL_INSULATION"              : "Wall Insulation",
    "PROPERTY_TYPE_Flat"           : "Is Flat",
    "PROPERTY_TYPE_House"          : "Is House",
    "MAIN_FUEL_Mains gas"          : "Mains Gas",
    "MAINHEAT_DESCRIPTION_Gas boiler": "Gas Boiler",
}

display_names = [
    f"{short_names.get(f, f)} = {v:.1f}"
    for f, v in zip(top_features, top_values)
]

colours = ["#d73027" if v > 0 else "#1a9641" for v in top_shap]

fig, ax = plt.subplots(figsize=(11, 8))
y_pos = range(len(top_features))

bars = ax.barh(
    list(y_pos),
    top_shap[::-1] if False else top_shap,
    color=colours,
    edgecolor="white", linewidth=0.8, height=0.65
)

ax.set_yticks(list(y_pos))
ax.set_yticklabels(display_names, fontsize=9)
ax.axvline(0, color="#555", linewidth=1.2)
ax.set_title(
    f"SHAP Waterfall — Why This House Was Predicted as Label {house_predicted}\n"
    f"(Actual label: {house_actual} | "
    f"Red = pushes toward D, Green = pushes away from D)",
    pad=12
)
ax.set_xlabel("SHAP Value (impact on Label D prediction)")
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.spines["left"].set_visible(False)

# Legend
from matplotlib.patches import Patch
legend_elements = [
    Patch(facecolor="#d73027", label="Pushes toward D (worse)"),
    Patch(facecolor="#1a9641", label="Pushes away from D (better)"),
]
ax.legend(handles=legend_elements, loc="lower right", fontsize=9)

fig.tight_layout()
fig.savefig("charts/04_shap_waterfall.png", dpi=150,
            bbox_inches="tight", facecolor=BG_COLOUR)
plt.close()
print("✅ Saved: charts/04_shap_waterfall.png")


# ============================================================
# 9. FINAL SUMMARY
# ============================================================
print("\n" + "=" * 60)
print("SHAP ANALYSIS COMPLETE")
print("=" * 60)
print(f"\nTop 10 most influential features (SHAP-based):")
print(f"{'Rank':<6} {'Feature':<40} {'Mean |SHAP|':>12}")
print("-" * 60)
for i, row in shap_importance.head(10).iterrows():
    print(f"{i+1:<6} {row['feature']:<40} {row['mean_abs_shap']:>12.4f}")

print(f"\nWaterfall house:")
print(f"  Actual label    : {house_actual}")
print(f"  Predicted label : {house_predicted}")
print(f"  Top driver      : {short_names.get(top_features[0], top_features[0])}")

print(f"\nOutput files:")
print(f"  charts/01_shap_summary.png")
print(f"  charts/02_shap_bar.png")
print(f"  charts/03_shap_dependence.png")
print(f"  charts/04_shap_waterfall.png")
print(f"  shap_importance.csv")
print("=" * 60)
print("\nNext step: Step 7 — Streamlit app")