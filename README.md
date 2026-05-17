# BELDA — Building Energy Label Data Analyzer

Bachelor thesis project that analyzes the UK Energy Performance Certificate (EPC) register (~24.5 million residential properties in England & Wales), trains a LightGBM classifier to predict energy labels (A–G), and presents the results in an interactive Streamlit dashboard.

## Features

The web app (`app.py`) has three pages:

| Page | Description |
|------|-------------|
| **Data Explorer** | Browse EDA and model charts, dataset overview stats, and aggregate SHAP feature importance |
| **Label Predictor** | Enter building characteristics and get a predicted energy label with live SHAP explanations |
| **Improvement Advisor** | Ranked upgrade recommendations based on model feature impact |

## Model

- **Algorithm:** LightGBM multiclass classifier
- **Target:** `CURRENT_ENERGY_RATING` (A–G)
- **Features:** 66 (leakage-prone columns excluded)
- **Test accuracy:** 71.93% on 244,984 held-out properties (99/1 train/test split)

See `training_report.txt` for the full classification report and top feature importances.

## Quick start

### Prerequisites

- Python 3.10+
- The runtime artifacts listed below (included in a full local clone, or regenerated from the pipeline)

### Install dependencies

```bash
pip install streamlit pandas numpy scikit-learn lightgbm shap plotly pillow matplotlib seaborn pyarrow
```

### Run the app

From the repository root:

```bash
streamlit run app.py
```

### Files required to run the app

| File / folder | Purpose |
|---------------|---------|
| `belda_model.pkl` | Trained LightGBM model |
| `shap_importance.csv` | SHAP feature rankings (Data Explorer) |
| `feature_importance.csv` | Model feature importances (Data Explorer) |
| `charts/` | EDA, SHAP, and model visualization PNGs |

Large datasets (`.parquet`, pipeline CSVs) are listed in `.gitignore` and are **not** needed to run the dashboard.

## Project structure

```
├── app.py                 # Streamlit web application (Step 7)
├── model_training.py      # LightGBM training (Step 5)
├── shap_analysis.py       # SHAP explanations (Step 6)
├── eda.py                 # Exploratory data analysis charts (Step 4)
├── belda_model.pkl        # Saved model
├── feature_importance.csv
├── shap_importance.csv
├── training_report.txt
├── charts/                # Generated PNG charts
├── encoding/              # Wall, roof, hot-water standardization + final encoding
└── Data cleaning/         # EPC cleaning pipeline (steps 0–4)
    ├── step 0 - raw data/
    ├── step 1 - removing extra columns/
    ├── step 2 - mission field analysis/
    ├── step 3 - standardization/
    └── step 4 - feature engineering/
```

## Pipeline overview

Scripts are meant to be run in order. Each step reads Parquet produced by the previous one (paths are relative to the script’s working directory unless noted).

| Step | Location | What it does |
|------|----------|--------------|
| 0 | `Data cleaning/step 0 - raw data/` | Ingest raw EPC data → `epc_raw.parquet` |
| 1 | `Data cleaning/step 1 - removing extra columns/` | Keep 29 core fields → `epc_core.parquet` |
| 2 | `Data cleaning/step 2 - mission field analysis/` | Missing-field analysis, drop empty rows |
| 3 | `Data cleaning/step 3 - standardization/` | Map ratings, age bands, heating, fuel, windows |
| 4 | `Data cleaning/step 4 - feature engineering/` | Built form, envelope score, CO₂ categories → `epc_script4_4.parquet` |
| — | `encoding/` | Normalize wall/roof/hot-water text fields |
| — | `encoding/encoding.py` | Ordinal + one-hot encoding → `epc_encoded.parquet` (repo root) |
| 4 | `eda.py` | 16 EDA charts → `charts/` |
| 5 | `model_training.py` | Train LightGBM → `belda_model.pkl`, `feature_importance.csv`, etc. |
| 6 | `shap_analysis.py` | SHAP plots + `shap_importance.csv` |
| 7 | `app.py` | Streamlit dashboard |

Re-running the full pipeline requires the UK EPC source data and sufficient disk/RAM; intermediate Parquet files are multi‑GB.

## Regenerating artifacts

If you have `epc_encoded.parquet` at the repo root:

```bash
python eda.py
python model_training.py
python shap_analysis.py
streamlit run app.py
```

`shap_analysis.py` expects `epc_test.parquet` and `belda_model.pkl` from `model_training.py`.

## Data source

Properties are drawn from the **England & Wales domestic EPC register** (Open Data). The cleaned dataset contains approximately **24,498,358** certificate records after pipeline filtering.

## License

Academic / thesis use. Check UK government open-data terms for the underlying EPC dataset if you redistribute processed data.
