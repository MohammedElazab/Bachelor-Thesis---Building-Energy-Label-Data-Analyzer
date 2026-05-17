# -*- coding: utf-8 -*-
"""
BELDA - Energy Label Data Analyzer
Step: Encoding Verification v2

What this script does:
- Loads epc_encoded.parquet (77 columns)
- Verifies every column for correct values, types, and ranges
- Generates encoding_verification_report_v2.md
"""

import pandas as pd
import sys
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8')

# ============================================================
# 1. LOAD
# ============================================================
INPUT_FILE  = "epc_encoded.parquet"
OUTPUT_FILE = "encoding_verification_report_v2.md"

print(f"Loading {INPUT_FILE} ...")
df = pd.read_parquet(INPUT_FILE)
print(f"Loaded {len(df):,} rows and {len(df.columns)} columns")
print("Running verification checks...")


# ============================================================
# 2. EXPECTED DEFINITIONS
# ============================================================

# Ordinal columns and their allowed values
ORDINAL_EXPECTED = {
    "CONSTRUCTION_AGE_BAND" : list(range(0, 12)),       # 0–11
    "co2_intensity_category": [0, 1, 2, 3],             # 0=unknown, 1–3
    "WALL_INSULATION"       : [0, 1, 2, 3],             # 0=unknown, 1=uninsulated, 2=partial, 3=insulated
    "ROOF_INSULATION"       : list(range(0, 7)),         # 0–6
}

# Efficiency score columns — expected range 1–5
EFFICIENCY_COLS = [
    "WALLS_ENERGY_EFF", "WALLS_ENV_EFF",
    "ROOF_ENERGY_EFF",  "ROOF_ENV_EFF",
    "WINDOWS_ENERGY_EFF", "WINDOWS_ENV_EFF",
    "MAINHEAT_ENERGY_EFF", "MAINHEAT_ENV_EFF",
    "HOT_WATER_ENERGY_EFF", "HOT_WATER_ENV_EFF",
]

# All binary columns — must only contain 0 and 1
BINARY_COLS = [
    "HAS_OWN_ROOF",
    "glazing_upgrade_flag",
    "HOTWATER_SOLAR",
] + [col for col in df.columns if col.startswith((
    "PROPERTY_TYPE_",
    "BUILT_FORM_",
    "built_form_simplified_",
    "MAIN_FUEL_",
    "MAINHEAT_DESCRIPTION_",
    "WINDOWS_DESCRIPTION_",
    "WALL_TYPE_",
    "ROOF_TYPE_",
    "HOTWATER_SOURCE_",
))]

# Target columns and their expected range
TARGET_COLS = {
    "CURRENT_ENERGY_RATING"  : (1, 10),   # 3–9 in practice
    "POTENTIAL_ENERGY_RATING": (1, 10),
    "improvement_potential"  : (0, 10),
}

# Continuous columns — check not all null, show stats
CONTINUOUS_COLS = [
    "TOTAL_FLOOR_AREA",
    "CURRENT_ENERGY_EFFICIENCY",
    "POTENTIAL_ENERGY_EFFICIENCY",
    "ENERGY_CONSUMPTION_CURRENT",
    "ENERGY_CONSUMPTION_POTENTIAL",
    "ENVIRONMENT_IMPACT_CURRENT",
    "CO2_EMISSIONS_CURRENT",
    "CO2_EMISS_CURR_PER_FLOOR_AREA",
    "envelope_composite_score",
]

# Columns that must NOT exist in the encoded file
DROPPED_COLS = [
    "WALLS_DESCRIPTION",
    "ROOF_DESCRIPTION",
    "HOTWATER_DESCRIPTION",
    "label_gap_readable",
]


# ============================================================
# 3. HELPERS
# ============================================================
def null_stats(series):
    n_null = series.isna().sum()
    pct    = (n_null / len(series)) * 100
    return n_null, pct

def status(passed):
    return "✅ PASS" if passed else "❌ FAIL"


# ============================================================
# 4. BUILD REPORT
# ============================================================
lines = []

lines.append("# BELDA — Encoding Verification Report v2")
lines.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
lines.append(f"**Source file:** `{INPUT_FILE}`")
lines.append(f"**Total rows:** {len(df):,}")
lines.append(f"**Total columns:** {len(df.columns)}")
lines.append("")


# ── SECTION 1: Shape ─────────────────────────────────────
lines.append("---")
lines.append("## 1. Overall Shape Check")
lines.append("")

expected_rows = 24_498_358
expected_cols = 77

lines.append("| Check | Expected | Actual | Status |")
lines.append("|---|---|---|---|")
lines.append(f"| Row count    | {expected_rows:,} | {len(df):,} | {status(len(df) == expected_rows)} |")
lines.append(f"| Column count | {expected_cols} | {len(df.columns)} | {status(len(df.columns) == expected_cols)} |")
lines.append("")


# ── SECTION 2: Dropped columns ────────────────────────────
lines.append("---")
lines.append("## 2. Dropped Columns Verification")
lines.append("These columns must NOT exist in the encoded file.")
lines.append("")
lines.append("| Column | Present | Status |")
lines.append("|---|---|---|")

for col in DROPPED_COLS:
    present = col in df.columns
    lines.append(f"| `{col}` | {'YES ⚠️' if present else 'No'} | {status(not present)} |")
lines.append("")


# ── SECTION 3: No text columns ────────────────────────────
lines.append("---")
lines.append("## 3. Text Column Check")
lines.append("")

text_cols = df.select_dtypes(include="object").columns.tolist()
lines.append("| Check | Result | Status |")
lines.append("|---|---|---|")
lines.append(f"| Text columns remaining | {len(text_cols)} | {status(len(text_cols) == 0)} |")

if text_cols:
    lines.append("")
    lines.append("**Remaining text columns:**")
    for col in text_cols:
        lines.append(f"- `{col}`: {df[col].unique()[:5].tolist()}")
lines.append("")


# ── SECTION 4: Ordinal columns ────────────────────────────
lines.append("---")
lines.append("## 4. Ordinal Encoded Columns")
lines.append("")

ordinal_labels = {
    "CONSTRUCTION_AGE_BAND": {
        0: "Unknown", 1: "Pre-1900", 2: "1900-1929", 3: "1930-1949",
        4: "1950-1966", 5: "1967-1975", 6: "1976-1982", 7: "1983-1990",
        8: "1991-1995", 9: "1996-2002", 10: "2003-2006", 11: "2007 onwards"
    },
    "co2_intensity_category": {
        0: "Unknown", 1: "Low", 2: "Medium", 3: "High"
    },
    "WALL_INSULATION": {
        0: "Unknown", 1: "Uninsulated", 2: "Partial", 3: "Insulated"
    },
    "ROOF_INSULATION": {
        0: "Unknown / No Roof", 1: "None", 2: "Low",
        3: "At Rafters", 4: "Medium", 5: "High", 6: "Very High"
    },
}

for col, allowed in ORDINAL_EXPECTED.items():
    lines.append(f"### `{col}`")

    if col not in df.columns:
        lines.append("❌ FAIL — Column not found.")
        lines.append("")
        continue

    actual_vals = sorted(df[col].dropna().unique().tolist())
    unexpected  = [v for v in actual_vals if v not in allowed]
    n_null, pct = null_stats(df[col])
    ok          = len(unexpected) == 0

    lines.append(f"| Item | Detail |")
    lines.append(f"|---|---|")
    lines.append(f"| Status | {status(ok)} |")
    lines.append(f"| Data type | `{df[col].dtype}` |")
    lines.append(f"| Allowed values | {allowed} |")
    lines.append(f"| Actual unique values | {actual_vals} |")
    lines.append(f"| Unexpected values | {unexpected if unexpected else 'None'} |")
    lines.append(f"| Null count | {n_null:,} ({pct:.2f}%) |")
    lines.append("")
    lines.append("**Value distribution:**")
    lines.append("")
    lines.append("| Value | Label | Count | % of Total |")
    lines.append("|---|---|---|---|")

    val_counts = df[col].value_counts().sort_index()
    labels     = ordinal_labels.get(col, {})
    for val, count in val_counts.items():
        pct_val   = (count / len(df)) * 100
        label_str = labels.get(int(val), "—")
        lines.append(f"| {val} | {label_str} | {count:,} | {pct_val:.1f}% |")
    lines.append("")


# ── SECTION 5: Efficiency columns ────────────────────────
lines.append("---")
lines.append("## 5. Efficiency Score Columns (Expected Range: 1–5)")
lines.append("")
lines.append("| Column | Dtype | Min | Max | Nulls | Unexpected Values | Status |")
lines.append("|---|---|---|---|---|---|---|")

for col in EFFICIENCY_COLS:
    if col not in df.columns:
        lines.append(f"| `{col}` | — | — | — | — | — | ❌ MISSING |")
        continue
    col_min     = df[col].min()
    col_max     = df[col].max()
    n_null, pct = null_stats(df[col])
    unexpected  = df[col].dropna()
    n_unexp     = len(unexpected[(unexpected < 1) | (unexpected > 5)])
    ok          = (col_min >= 1) and (col_max <= 5) and (n_unexp == 0)
    lines.append(
        f"| `{col}` | `{df[col].dtype}` | {col_min} | {col_max} | "
        f"{n_null:,} ({pct:.1f}%) | {n_unexp:,} | {status(ok)} |"
    )
lines.append("")


# ── SECTION 6: Binary columns ─────────────────────────────
lines.append("---")
lines.append("## 6. Binary Columns (Expected Values: 0 and 1 only)")
lines.append("")
lines.append("| Column | Dtype | Unique Values | Count of 1s | Count of 0s | Nulls | Status |")
lines.append("|---|---|---|---|---|---|---|")

for col in BINARY_COLS:
    if col not in df.columns:
        lines.append(f"| `{col}` | — | — | — | — | — | ❌ MISSING |")
        continue
    unique_vals = sorted(df[col].dropna().unique().tolist())
    n_ones      = (df[col] == 1).sum()
    n_zeros     = (df[col] == 0).sum()
    n_null, pct = null_stats(df[col])
    ok          = set(unique_vals).issubset({0, 1})
    lines.append(
        f"| `{col}` | `{df[col].dtype}` | {unique_vals} | "
        f"{n_ones:,} | {n_zeros:,} | {n_null:,} ({pct:.1f}%) | {status(ok)} |"
    )
lines.append("")


# ── SECTION 7: Target columns ─────────────────────────────
lines.append("---")
lines.append("## 7. Target Variable Columns")
lines.append("")
lines.append("| Column | Dtype | Min | Max | Unique Values | Nulls | Status |")
lines.append("|---|---|---|---|---|---|---|")

for col, (exp_min, exp_max) in TARGET_COLS.items():
    if col not in df.columns:
        lines.append(f"| `{col}` | — | — | — | — | — | ❌ MISSING |")
        continue
    col_min     = df[col].min()
    col_max     = df[col].max()
    unique_vals = sorted(df[col].dropna().unique().tolist())
    n_null, pct = null_stats(df[col])
    ok          = (col_min >= exp_min) and (col_max <= exp_max)
    lines.append(
        f"| `{col}` | `{df[col].dtype}` | {col_min} | {col_max} | "
        f"{unique_vals} | {n_null:,} ({pct:.1f}%) | {status(ok)} |"
    )
lines.append("")


# ── SECTION 8: Continuous columns ────────────────────────
lines.append("---")
lines.append("## 8. Continuous / Numeric Columns")
lines.append("")
lines.append("| Column | Dtype | Min | Max | Mean | Nulls | Status |")
lines.append("|---|---|---|---|---|---|---|")

for col in CONTINUOUS_COLS:
    if col not in df.columns:
        lines.append(f"| `{col}` | — | — | — | — | — | ❌ MISSING |")
        continue
    col_min     = round(float(df[col].min()), 2)
    col_max     = round(float(df[col].max()), 2)
    col_mean    = round(float(df[col].mean()), 2)
    n_null, pct = null_stats(df[col])
    ok          = n_null < len(df)
    lines.append(
        f"| `{col}` | `{df[col].dtype}` | {col_min} | {col_max} | "
        f"{col_mean} | {n_null:,} ({pct:.1f}%) | {status(ok)} |"
    )
lines.append("")


# ── SECTION 9: New standardized columns summary ──────────
lines.append("---")
lines.append("## 9. New Standardized Columns Summary")
lines.append("Verification of the 6 columns created during description standardization.")
lines.append("")

new_cols_info = {
    "WALL_INSULATION"         : "Ordinal 0–3 (0=Unknown, 1=Uninsulated, 2=Partial, 3=Insulated)",
    "ROOF_INSULATION"         : "Ordinal 0–6 (0=Unknown/No Roof → 6=Very High)",
    "HOTWATER_SOLAR"          : "Binary 0/1 (0=No solar, 1=Has solar)",
    "WALL_TYPE_Cavity"        : "One-hot — baseline is Basement",
    "ROOF_TYPE_Pitched"       : "One-hot — baseline is Flat",
    "HOTWATER_SOURCE_Main System": "One-hot — baseline is Community",
}

lines.append("| Column | Type | Present | Nulls | Status |")
lines.append("|---|---|---|---|---|")

for col, description in new_cols_info.items():
    present     = col in df.columns
    n_null, pct = null_stats(df[col]) if present else (0, 0)
    ok          = present and n_null == 0
    lines.append(
        f"| `{col}` | {description} | {'Yes' if present else 'No'} | "
        f"{n_null:,} ({pct:.1f}%) | {status(ok)} |"
    )
lines.append("")


# ── SECTION 10: Full column inventory ────────────────────
lines.append("---")
lines.append("## 10. Full Column Inventory")
lines.append("")
lines.append("| # | Column | Dtype | Null Count | Null % |")
lines.append("|---|---|---|---|---|")

for i, col in enumerate(df.columns, 1):
    n_null, pct = null_stats(df[col])
    lines.append(f"| {i} | `{col}` | `{df[col].dtype}` | {n_null:,} | {pct:.2f}% |")
lines.append("")


# ── SECTION 11: Scorecard ─────────────────────────────────
lines.append("---")
lines.append("## 11. Summary Scorecard")
lines.append("")

checks = {
    "Correct row count"                   : len(df) == expected_rows,
    "Correct column count"                : len(df.columns) == expected_cols,
    "No text columns remaining"           : len(df.select_dtypes(include="object").columns) == 0,
    "Dropped columns removed"             : all(c not in df.columns for c in DROPPED_COLS),
    "CONSTRUCTION_AGE_BAND in range"      : df["CONSTRUCTION_AGE_BAND"].max() <= 11,
    "co2_intensity_category in range"     : df["co2_intensity_category"].max() <= 3,
    "WALL_INSULATION in range"            : df["WALL_INSULATION"].max() <= 3,
    "ROOF_INSULATION in range"            : df["ROOF_INSULATION"].max() <= 6,
    "HOTWATER_SOLAR is binary"            : set(df["HOTWATER_SOLAR"].unique()).issubset({0, 1}),
    "CURRENT_ENERGY_RATING present"       : "CURRENT_ENERGY_RATING" in df.columns,
    "All efficiency cols present"         : all(c in df.columns for c in EFFICIENCY_COLS),
    "All binary cols are 0/1"             : all(
                                                set(df[c].dropna().unique()).issubset({0, 1})
                                                for c in BINARY_COLS if c in df.columns
                                            ),
    "New wall cols present"               : all(c in df.columns for c in ["WALL_INSULATION", "WALL_TYPE_Cavity"]),
    "New roof cols present"               : all(c in df.columns for c in ["ROOF_INSULATION", "ROOF_TYPE_Pitched"]),
    "New hotwater cols present"           : all(c in df.columns for c in ["HOTWATER_SOURCE_Main System", "HOTWATER_SOLAR"]),
}

lines.append("| Check | Result |")
lines.append("|---|---|")

passed = 0
for check_name, result in checks.items():
    if result:
        passed += 1
    lines.append(f"| {check_name} | {status(result)} |")

lines.append("")
lines.append(f"**{passed}/{len(checks)} checks passed.**")

if passed == len(checks):
    lines.append("")
    lines.append("> ✅ All checks passed. The encoded dataset is fully verified and ready for EDA and model training.")
else:
    lines.append("")
    lines.append("> ⚠️ Some checks failed. Review the sections above for details.")

lines.append("")
lines.append("---")
lines.append("*BELDA Encoding Verification v2 — auto-generated by verification_script_v2.py*")


# ============================================================
# 5. WRITE REPORT
# ============================================================
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.write("\n".join(lines))

print(f"\n✅ Verification complete.")
print(f"Report saved to: {OUTPUT_FILE}")
print(f"{passed}/{len(checks)} checks passed.")