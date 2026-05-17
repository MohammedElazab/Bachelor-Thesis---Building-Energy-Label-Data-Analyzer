# -*- coding: utf-8 -*-
"""
BELDA - Energy Label Data Analyzer
Step 5: Model Training

Trains a LightGBM classifier on the full 24.5M row encoded dataset.
LightGBM is used instead of XGBoost because it uses a leaf-wise growth
strategy with a more memory-efficient histogram implementation that does
not require a single contiguous memory allocation — making it suitable
for large datasets on consumer hardware.

Uses a 99/1 train/test split — at this scale 1% gives 245,000 test
rows which is more than enough for statistically valid evaluation.

Output files:
    belda_model.pkl          — trained LightGBM model
    epc_test.parquet         — test set (for SHAP analysis in Step 6)
    feature_importance.csv   — ranked feature importances
    confusion_matrix.png     — visual confusion matrix
    feature_importance.png   — visual feature importance chart
    training_report.txt      — full classification report
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
import pickle
import time
import sys
import os
from datetime import datetime

from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
)
import lightgbm as lgb

sys.stdout.reconfigure(encoding='utf-8')

os.makedirs("charts", exist_ok=True)

# ============================================================
# 1. LOAD DATA
# ============================================================
print("=" * 60)
print("BELDA — Model Training")
print("Algorithm: LightGBM Classifier")
print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 60)

print("\nLoading epc_encoded.parquet ...")
df = pd.read_parquet("epc_encoded.parquet")
print(f"Loaded {len(df):,} rows × {len(df.columns)} columns")


# ============================================================
# 2. DEFINE FEATURES AND TARGET
# ============================================================
print("\nDefining features and target...")

# Target variable
TARGET = "CURRENT_ENERGY_RATING"

# Columns to EXCLUDE from features:
# These are either derived from the target, or represent
# information you wouldn't have before an EPC assessment.
# Using them would give artificially high accuracy (data leakage).
EXCLUDE = [
    # Target itself
    "CURRENT_ENERGY_RATING",

    # Directly derived from target
    "CURRENT_ENERGY_EFFICIENCY",    # IS the numeric rating
    "POTENTIAL_ENERGY_RATING",      # derived from current rating
    "POTENTIAL_ENERGY_EFFICIENCY",  # derived from current rating
    "improvement_potential",        # current vs potential rating
    "co2_intensity_category",       # derived from CO2 emissions

    # Post-assessment outputs (not available before EPC)
    "ENERGY_CONSUMPTION_CURRENT",
    "ENERGY_CONSUMPTION_POTENTIAL",
    "ENVIRONMENT_IMPACT_CURRENT",
    "CO2_EMISSIONS_CURRENT",
    "CO2_EMISS_CURR_PER_FLOOR_AREA",

    # Any label columns if they exist
    "RATING_LABEL",
    "POT_LABEL",
]

# Keep only columns that exist in the dataframe
EXCLUDE = [col for col in EXCLUDE if col in df.columns]

# Feature columns = everything not excluded
FEATURE_COLS = [col for col in df.columns if col not in EXCLUDE]

print(f"Target        : {TARGET}")
print(f"Features used : {len(FEATURE_COLS)} columns")
print(f"Excluded      : {len(EXCLUDE)} columns")
print(f"\nFeature columns:")
for col in FEATURE_COLS:
    print(f"  {col}")


# ============================================================
# 3. PREPARE X AND y
# ============================================================
print("\nPreparing X and y...")

X = df[FEATURE_COLS].copy()
y = df[TARGET].copy()

# XGBoost requires class labels starting from 0
# Your ratings are 3–9 (A=3, B=4, C=5, D=6, E=7, F=8, G=9)
# Remap: subtract 3 so they become 0–6
y_model = y - 3

# Label mapping for reporting
LABEL_MAP  = {0:"A", 1:"B", 2:"C", 3:"D", 4:"E", 5:"F", 6:"G"}
LABELS_STR = [LABEL_MAP[i] for i in sorted(LABEL_MAP.keys())]

# Handle nullable Int64 columns — convert to float for XGBoost
for col in X.select_dtypes(include="Int64").columns:
    X[col] = X[col].astype("float32")

for col in X.select_dtypes(include=["int64", "int32", "int8"]).columns:
    X[col] = X[col].astype("float32")

for col in X.select_dtypes(include="float64").columns:
    X[col] = X[col].astype("float32")

print(f"X shape: {X.shape}")
print(f"y distribution (original labels):")
for rating, count in y.value_counts().sort_index().items():
    label = LABEL_MAP.get(int(rating) - 3, "?")
    pct   = count / len(y) * 100
    print(f"  {rating} ({label}): {count:>10,}  ({pct:.1f}%)")


# ============================================================
# 4. TRAIN / TEST SPLIT — 99% train, 1% test
# ============================================================
print("\nSplitting data 99% train / 1% test...")

X_train, X_test, y_train, y_test = train_test_split(
    X, y_model,
    test_size=0.01,
    random_state=42,
    stratify=y_model,   # ensures same label distribution in both sets
)

print(f"Training set  : {len(X_train):,} rows")
print(f"Test set      : {len(X_test):,} rows")

# Save test set for SHAP analysis in Step 6
print("\nSaving test set for SHAP analysis...")
test_df = X_test.copy()
test_df["CURRENT_ENERGY_RATING"] = y_test + 3  # restore original labels
test_df.to_parquet("epc_test.parquet", index=False)
print("✅ Saved: epc_test.parquet")


# ============================================================
# 5. DEFINE AND TRAIN THE MODEL
# ============================================================
print("\n" + "=" * 60)
print("Training XGBoost model on full training set...")
print("This may take 10–60 minutes depending on your hardware.")
print("=" * 60)

model = lgb.LGBMClassifier(
    n_estimators      = 300,        # number of trees
    max_depth         = 8,          # max depth per tree
    learning_rate     = 0.1,        # step size
    num_leaves        = 127,        # max leaves per tree (2^max_depth - 1)
    subsample         = 0.8,        # % of rows used per tree
    subsample_freq    = 1,          # subsample every iteration
    colsample_bytree  = 0.8,        # % of features per tree
    min_child_samples = 50,         # minimum rows in a leaf
    reg_alpha         = 0.1,        # L1 regularisation
    reg_lambda        = 0.1,        # L2 regularisation
    max_bin           = 255,        # histogram bins
    objective         = "multiclass",
    num_class         = 7,          # A B C D E F G
    metric            = "multi_logloss",
    n_jobs            = -1,         # use all CPU cores
    random_state      = 42,
    verbose           = -1,         # suppress LightGBM internal logs
)

start_time = time.time()

# LightGBM handles pandas DataFrames natively and efficiently
# No need to convert to numpy — it manages its own memory internally
print("Starting training...")

callbacks = [lgb.log_evaluation(period=50)]  # print every 50 trees

model.fit(
    X_train, y_train,
    eval_set=[(X_test, y_test)],
    callbacks=callbacks,
)

elapsed = time.time() - start_time
print(f"\n✅ Training complete in {elapsed/60:.1f} minutes")


# ============================================================
# 6. EVALUATE ON TEST SET
# ============================================================
print("\n" + "=" * 60)
print("Evaluating on test set...")
print("=" * 60)

y_pred      = model.predict(X_test)
accuracy    = accuracy_score(y_test, y_pred)
conf_matrix = confusion_matrix(y_test, y_pred)
class_report = classification_report(
    y_test, y_pred,
    target_names=LABELS_STR,
    zero_division=0
)

# Map predictions back to original labels for display
actual_labels    = [LABEL_MAP[int(v)] for v in y_test]
predicted_labels = [LABEL_MAP[int(v)] for v in y_pred]

print(f"\nAccuracy: {accuracy:.4f} ({accuracy*100:.2f}%)")
print(f"\nClassification Report:")
print(class_report)


# ============================================================
# 7. CONFUSION MATRIX CHART
# ============================================================
print("Generating confusion matrix chart...")

# Normalise by row so each cell shows % of actual label
conf_norm = conf_matrix.astype("float") / conf_matrix.sum(axis=1, keepdims=True)

fig, ax = plt.subplots(figsize=(10, 8))
sns.heatmap(
    conf_norm,
    annot=True,
    fmt=".2f",
    cmap="Blues",
    xticklabels=LABELS_STR,
    yticklabels=LABELS_STR,
    linewidths=0.5,
    linecolor="white",
    ax=ax,
    vmin=0, vmax=1,
    annot_kws={"size": 11},
)
ax.set_title("Confusion Matrix — Normalised by Actual Label\n(diagonal = correctly classified)", pad=15)
ax.set_xlabel("Predicted Label", fontsize=12)
ax.set_ylabel("Actual Label", fontsize=12)
fig.tight_layout()
fig.savefig("charts/confusion_matrix.png", dpi=150, bbox_inches="tight")
plt.close(fig)
print("✅ Saved: charts/confusion_matrix.png")


# ============================================================
# 8. FEATURE IMPORTANCE
# ============================================================
print("Extracting feature importance...")

importance_df = pd.DataFrame({
    "feature"   : FEATURE_COLS,
    "importance": model.feature_importances_,
}).sort_values("importance", ascending=False)

importance_df.to_csv("feature_importance.csv", index=False, encoding="utf-8")
print("✅ Saved: feature_importance.csv")

print("\nTop 20 most important features:")
print(f"{'Rank':<6} {'Feature':<45} {'Importance':>10}")
print("-" * 63)
for i, (_, row) in enumerate(importance_df.head(20).iterrows(), 1):
    print(f"{i:<6} {row['feature']:<45} {row['importance']:>10.4f}")

# Feature importance chart — top 20
fig, ax = plt.subplots(figsize=(11, 8))
top20 = importance_df.head(20)
ax.barh(
    top20["feature"][::-1],
    top20["importance"][::-1],
    color="#2C5F8A", edgecolor="white", linewidth=0.8, height=0.7
)
ax.set_title("Top 20 Feature Importances\n(XGBoost — gain-based)", pad=15)
ax.set_xlabel("Feature Importance Score")
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.spines["left"].set_visible(False)
fig.tight_layout()
fig.savefig("charts/feature_importance.png", dpi=150, bbox_inches="tight")
plt.close(fig)
print("✅ Saved: charts/feature_importance.png")


# ============================================================
# 9. SAVE MODEL
# ============================================================
print("\nSaving trained model...")
with open("belda_model.pkl", "wb") as f:
    pickle.dump(model, f)
print("✅ Saved: belda_model.pkl")


# ============================================================
# 10. SAVE FULL TRAINING REPORT
# ============================================================
report_lines = [
    "BELDA — Model Training Report",
    "=" * 60,
    f"Generated    : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
    f"Training rows: {len(X_train):,}",
    f"Test rows    : {len(X_test):,}",
    f"Features used: {len(FEATURE_COLS)}",
    f"Training time: {elapsed/60:.1f} minutes",
    "",
    f"ACCURACY: {accuracy:.4f} ({accuracy*100:.2f}%)",
    "",
    "CLASSIFICATION REPORT:",
    class_report,
    "",
    "TOP 20 FEATURE IMPORTANCES:",
    f"{'Rank':<6} {'Feature':<45} {'Importance':>10}",
    "-" * 63,
]
for i, (_, row) in enumerate(importance_df.head(20).iterrows(), 1):
    report_lines.append(f"{i:<6} {row['feature']:<45} {row['importance']:>10.4f}")

report_lines += [
    "",
    "EXCLUDED COLUMNS (data leakage prevention):",
]
for col in EXCLUDE:
    report_lines.append(f"  - {col}")

with open("training_report.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(report_lines))
print("✅ Saved: training_report.txt")


# ============================================================
# 11. FINAL SUMMARY
# ============================================================
print("\n" + "=" * 60)
print("TRAINING COMPLETE")
print("=" * 60)
print(f"  Accuracy          : {accuracy*100:.2f}%")
print(f"  Training rows     : {len(X_train):,}")
print(f"  Test rows         : {len(X_test):,}")
print(f"  Features used     : {len(FEATURE_COLS)}")
print(f"  Training time     : {elapsed/60:.1f} minutes")
print(f"  Top feature       : {importance_df.iloc[0]['feature']}")
print(f"\n  Output files:")
print(f"    belda_model.pkl")
print(f"    epc_test.parquet")
print(f"    feature_importance.csv")
print(f"    charts/confusion_matrix.png")
print(f"    charts/feature_importance.png")
print(f"    training_report.txt")
print("=" * 60)