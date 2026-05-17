# -*- coding: utf-8 -*-
"""
BELDA - Energy Label Data Analyzer
Step 7: Streamlit Web Application

Run with:
    streamlit run app.py

Pages:
    1. Data Explorer    — interactive EDA charts
    2. Label Predictor  — predict energy label with live SHAP
    3. Improvement Advisor — ranked upgrade recommendations
"""

import streamlit as st
import pandas as pd
import numpy as np
import pickle
import shap
import plotly.graph_objects as go
import plotly.express as px
from PIL import Image
import os
import warnings
warnings.filterwarnings("ignore")

# ============================================================
# PAGE CONFIG
# ============================================================
st.set_page_config(
    page_title="BELDA — Energy Label Data Analyzer",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================
# STYLING
# ============================================================
st.markdown("""
<style>
    /* Dark canvas so theme / widget text (often light) stays readable */
    header[data-testid="stHeader"] {
        background-color: #0f172a !important;
        border-bottom: 1px solid rgba(148, 163, 184, 0.12);
    }
    div[data-testid="stDecoration"] {
        background-image: none;
        background-color: #0f172a;
    }
    .stApp {
        background: linear-gradient(165deg, #0b1220 0%, #0f172a 40%, #111827 100%);
        color: #e2e8f0;
    }
    .main {
        background-color: transparent;
        color: #e2e8f0;
    }
    section.main .block-container {
        color: #cbd5e1;
    }
    .main .block-container p,
    .main .block-container li {
        color: #cbd5e1;
    }
    .main .block-container h1,
    .main .block-container h2,
    .main .block-container h3 {
        color: #f8fafc !important;
    }
    /* Widget captions / labels */
    .main [data-testid="stWidgetLabel"] p,
    .main [data-testid="stWidgetLabel"] span {
        color: #e2e8f0 !important;
    }

    .metric-card {
        background: #1e293b;
        border: 1px solid rgba(148, 163, 184, 0.15);
        border-radius: 12px;
        padding: 20px 24px;
        box-shadow: 0 4px 16px rgba(0,0,0,0.25);
        text-align: center;
        margin-bottom: 16px;
    }
    .metric-card .value {
        font-size: 2.2rem;
        font-weight: 700;
        color: #7dd3fc;
        margin: 0;
    }
    .metric-card .label {
        font-size: 0.85rem;
        color: #94a3b8;
        margin-top: 4px;
    }

    .label-badge {
        display: inline-block;
        width: 80px;
        height: 80px;
        line-height: 80px;
        border-radius: 50%;
        font-size: 2.5rem;
        font-weight: 900;
        text-align: center;
        color: white;
        margin: 8px auto;
    }

    .section-header {
        font-size: 1.3rem;
        font-weight: 700;
        color: #f8fafc;
        border-left: 4px solid #38bdf8;
        padding-left: 12px;
        margin: 24px 0 16px 0;
    }

    .upgrade-card {
        background: #1e293b;
        border-radius: 10px;
        padding: 16px 20px;
        margin-bottom: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.2);
        border: 1px solid rgba(148, 163, 184, 0.12);
        border-left: 5px solid #38bdf8;
        color: #e2e8f0;
    }

    .shap-positive { color: #fca5a5; font-weight: 600; }
    .shap-negative { color: #86efac; font-weight: 600; }

    /* —— Sidebar (matches main app shell) —— */
    [data-testid="stSidebar"] {
        background: linear-gradient(185deg, #0b1220 0%, #0f172a 45%, #111827 100%) !important;
        border-right: 1px solid rgba(148, 163, 184, 0.12);
        box-shadow: 4px 0 24px rgba(0, 0, 0, 0.15);
    }
    [data-testid="stSidebar"] > div:first-child {
        padding-top: 0.5rem;
    }
    .sidebar-brand {
        padding: 1rem 1rem 1.05rem;
        margin: 0 0 0.5rem 0;
        background: linear-gradient(135deg, rgba(30, 58, 95, 0.5) 0%, rgba(15, 23, 42, 0.92) 100%);
        border: 1px solid rgba(56, 189, 248, 0.14);
        border-radius: 16px;
        box-shadow: 0 6px 24px rgba(0, 0, 0, 0.28);
    }
    .sidebar-brand-tag {
        font-size: 0.62rem;
        font-weight: 700;
        letter-spacing: 0.16em;
        text-transform: uppercase;
        color: #7dd3fc !important;
        margin: 0 0 0.55rem 0;
    }
    .sidebar-brand-row {
        display: flex;
        align-items: center;
        gap: 0.75rem;
    }
    .sidebar-brand-icon {
        width: 42px;
        height: 42px;
        border-radius: 12px;
        background: linear-gradient(145deg, #2C5F8A, #1e4a6e);
        display: flex;
        align-items: center;
        justify-content: center;
        flex-shrink: 0;
        box-shadow: 0 4px 12px rgba(44, 95, 138, 0.35);
    }
    .sidebar-brand-icon svg {
        width: 24px;
        height: 24px;
        color: #fff;
    }
    .sidebar-brand-title {
        font-size: 1.28rem;
        font-weight: 800;
        letter-spacing: -0.03em;
        color: #f8fafc !important;
        margin: 0;
        line-height: 1.1;
    }
    .sidebar-brand-sub {
        font-size: 0.78rem;
        font-weight: 600;
        color: #94a3b8 !important;
        margin: 0.2rem 0 0 0;
        line-height: 1.3;
    }
    .sidebar-brand-foot {
        font-size: 0.72rem;
        color: #64748b !important;
        margin: 0.65rem 0 0 0;
        line-height: 1.4;
    }
    .sidebar-section-kicker {
        font-size: 0.62rem;
        font-weight: 700;
        letter-spacing: 0.14em;
        text-transform: uppercase;
        color: #7dd3fc !important;
        margin: 0.75rem 0 0.45rem 0.1rem;
    }
    .sidebar-divider {
        height: 1px;
        margin: 1rem 0;
        background: linear-gradient(90deg, transparent, rgba(148, 163, 184, 0.22), transparent);
        border: none;
    }
    .sidebar-stat-card {
        background: rgba(30, 41, 59, 0.55);
        border: 1px solid rgba(148, 163, 184, 0.12);
        border-radius: 12px;
        padding: 0.75rem 0.85rem;
        margin-bottom: 0.55rem;
    }
    .sidebar-stat-card h4 {
        font-size: 0.65rem;
        font-weight: 700;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        color: #94a3b8 !important;
        margin: 0 0 0.5rem 0;
    }
    .sidebar-stat-row {
        font-size: 0.8rem;
        color: #e2e8f0 !important;
        line-height: 1.45;
        margin: 0;
    }
    .sidebar-stat-row + .sidebar-stat-row {
        margin-top: 0.35rem;
    }
    .sidebar-stat-muted {
        font-size: 0.74rem !important;
        color: #94a3b8 !important;
    }
    .sidebar-stat-accent {
        color: #7dd3fc !important;
        font-weight: 700;
    }
    /* Navigation radio — pill list */
    [data-testid="stSidebar"] .stRadio > div {
        gap: 0.4rem !important;
    }
    [data-testid="stSidebar"] .stRadio label,
    [data-testid="stSidebar"] .stRadio label p,
    [data-testid="stSidebar"] .stRadio label span {
        color: #e2e8f0 !important;
    }
    [data-testid="stSidebar"] .stRadio label {
        border-radius: 10px !important;
        padding: 0.5rem 0.55rem !important;
        background: rgba(15, 23, 42, 0.55) !important;
        border: 1px solid rgba(148, 163, 184, 0.12) !important;
        transition: border-color 0.15s ease, background 0.15s ease !important;
    }
    [data-testid="stSidebar"] .stRadio label:hover {
        border-color: rgba(56, 189, 248, 0.35) !important;
        background: rgba(30, 58, 95, 0.35) !important;
    }
    [data-testid="stSidebar"] .stRadio [data-checked="true"],
    [data-testid="stSidebar"] .stRadio label:has(input:checked) {
        border-color: rgba(56, 189, 248, 0.55) !important;
        background: linear-gradient(90deg, rgba(30, 58, 95, 0.65), rgba(49, 46, 129, 0.35)) !important;
        box-shadow: 0 0 0 1px rgba(56, 189, 248, 0.12);
    }

    /* —— Label Predictor (modern shell) —— */
    .predictor-hero {
        background: linear-gradient(135deg, #1e293b 0%, #1e3a5f 45%, #312e81 100%);
        border: 1px solid rgba(148, 163, 184, 0.2);
        border-radius: 20px;
        padding: 1.5rem 1.75rem 1.35rem;
        margin-bottom: 1.25rem;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.35);
    }
    .predictor-hero-inner {
        display: flex;
        align-items: flex-start;
        gap: 1rem;
        flex-wrap: wrap;
    }
    .predictor-hero-icon {
        flex-shrink: 0;
        width: 48px;
        height: 48px;
        border-radius: 14px;
        background: linear-gradient(145deg, #2C5F8A, #1e4a6e);
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 4px 14px rgba(44, 95, 138, 0.35);
    }
    .predictor-hero-icon svg { width: 28px; height: 28px; color: #fff; }
    .predictor-hero h1 {
        font-size: 1.65rem !important;
        font-weight: 800 !important;
        letter-spacing: -0.02em;
        margin: 0 0 0.35rem 0 !important;
        color: #f8fafc !important;
        line-height: 1.2 !important;
    }
    .predictor-hero p.lead {
        margin: 0;
        font-size: 0.98rem;
        color: #cbd5e1;
        max-width: 52rem;
        line-height: 1.55;
    }
    .predictor-section-label {
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 0.14em;
        text-transform: uppercase;
        color: #7dd3fc;
        margin-bottom: 0.35rem;
    }
    .predictor-section-title {
        font-size: 1.2rem;
        font-weight: 700;
        color: #f8fafc;
        border-left: 4px solid #38bdf8;
        padding-left: 12px;
        margin: 0.5rem 0 1rem 0;
    }
    .predictor-col-head {
        display: flex;
        align-items: center;
        gap: 0.65rem;
        margin-bottom: 0.85rem;
        padding: 0.65rem 0.75rem;
        background: linear-gradient(180deg, #1e293b 0%, #0f172a 100%);
        border: 1px solid rgba(148, 163, 184, 0.18);
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
    }
    .predictor-col-head svg {
        flex-shrink: 0;
        width: 28px;
        height: 28px;
    }
    .predictor-col-head .stack { line-height: 1.25; }
    .predictor-col-kicker {
        font-size: 0.65rem;
        font-weight: 700;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        color: #94a3b8;
    }
    .predictor-col-head strong {
        font-size: 1rem;
        color: #f1f5f9;
        font-weight: 700;
    }
    .predict-loading-strip {
        display: flex;
        align-items: center;
        gap: 0.65rem;
        padding: 0.65rem 1rem;
        margin: 0.5rem 0 0.75rem 0;
        background: linear-gradient(90deg, #1e3a5f 0%, #1e293b 50%, #312e81 100%);
        border: 1px solid rgba(56, 189, 248, 0.25);
        border-radius: 12px;
        font-size: 0.9rem;
        font-weight: 600;
        color: #e0f2fe;
    }
    .predict-loading-strip .spin {
        width: 20px;
        height: 20px;
        border: 2.5px solid rgba(56, 189, 248, 0.25);
        border-top-color: #38bdf8;
        border-radius: 50%;
        animation: predictor-spin 0.7s linear infinite;
    }
    @keyframes predictor-spin {
        to { transform: rotate(360deg); }
    }
    /* Primary button polish on wide layout */
    .stButton > button[kind="primary"] {
        border-radius: 12px !important;
        font-weight: 700 !important;
        padding: 0.65rem 1.25rem !important;
        background: linear-gradient(180deg, #e85d4c 0%, #d44536 100%) !important;
        border: none !important;
        box-shadow: 0 4px 14px rgba(212, 69, 54, 0.35) !important;
        transition: transform 0.15s ease, box-shadow 0.15s ease !important;
    }
    .stButton > button[kind="primary"]:hover {
        box-shadow: 0 6px 20px rgba(212, 69, 54, 0.45) !important;
    }

    /* Inputs: slightly lifted surfaces on dark bg */
    .main .stSelectbox [data-baseweb="select"] > div,
    .main div[data-baseweb="select"] > div {
        background-color: #1e293b !important;
        border-color: rgba(148, 163, 184, 0.25) !important;
        color: #f8fafc !important;
    }
    .main .stSlider [data-baseweb="slider"] {
        background-color: transparent;
    }

    /* Data Explorer — frame dataframe / tables on dark canvas */
    .main [data-testid="stDataFrame"] {
        border: 1px solid rgba(148, 163, 184, 0.2);
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
    }
</style>
""", unsafe_allow_html=True)

# ============================================================
# CONSTANTS
# ============================================================
LABEL_NAMES   = {3:"A", 4:"B", 5:"C", 6:"D", 7:"E", 8:"F", 9:"G"}
LABEL_COLOURS = {
    "A": "#1a9641", "B": "#a6d96a", "C": "#d9ef8b",
    "D": "#fdae61", "E": "#f46d43", "F": "#d73027", "G": "#a50026",
}
LABEL_BG = {
    "A": "#e8f5e9", "B": "#f1f8e9", "C": "#fffde7",
    "D": "#fff3e0", "E": "#fbe9e7", "F": "#fce4ec", "G": "#f3e5f5",
}

CHARTS_DIR = "charts"


# ============================================================
# LOAD MODEL — cached so it only loads once
# ============================================================
@st.cache_resource
def load_model():
    with open("belda_model.pkl", "rb") as f:
        return pickle.load(f)

@st.cache_data
def load_shap_importance():
    return pd.read_csv("shap_importance.csv")

@st.cache_data
def load_feature_importance():
    return pd.read_csv("feature_importance.csv")

model           = load_model()
shap_importance = load_shap_importance()
feat_importance = load_feature_importance()


# ============================================================
# FEATURE COLUMNS — must match training exactly
# ============================================================
FEATURE_COLS = [
    "CONSTRUCTION_AGE_BAND", "TOTAL_FLOOR_AREA",
    "WALLS_ENERGY_EFF", "WALLS_ENV_EFF",
    "ROOF_ENERGY_EFF", "ROOF_ENV_EFF",
    "WINDOWS_ENERGY_EFF", "WINDOWS_ENV_EFF",
    "MAINHEAT_ENERGY_EFF", "MAINHEAT_ENV_EFF",
    "HOT_WATER_ENERGY_EFF", "HOT_WATER_ENV_EFF",
    "HAS_OWN_ROOF", "glazing_upgrade_flag",
    "envelope_composite_score",
    "WALL_INSULATION", "ROOF_INSULATION", "HOTWATER_SOLAR",
    "PROPERTY_TYPE_Flat", "PROPERTY_TYPE_House",
    "PROPERTY_TYPE_Maisonette", "PROPERTY_TYPE_Park home",
    "BUILT_FORM_Enclosed End-Terrace", "BUILT_FORM_Enclosed Mid-Terrace",
    "BUILT_FORM_End-Terrace", "BUILT_FORM_Mid-Terrace",
    "BUILT_FORM_Semi-Detached",
    "built_form_simplified_End-Terrace",
    "built_form_simplified_Mid-Terrace",
    "built_form_simplified_Semi-detached",
    "MAIN_FUEL_Electricity", "MAIN_FUEL_LPG",
    "MAIN_FUEL_Mains gas", "MAIN_FUEL_Oil",
    "MAINHEAT_DESCRIPTION_Community",
    "MAINHEAT_DESCRIPTION_Electric storage",
    "MAINHEAT_DESCRIPTION_Gas boiler",
    "MAINHEAT_DESCRIPTION_Heat pump",
    "MAINHEAT_DESCRIPTION_LPG",
    "MAINHEAT_DESCRIPTION_Oil boiler",
    "WINDOWS_DESCRIPTION_Secondary glazing",
    "WINDOWS_DESCRIPTION_Single glazing",
    "WINDOWS_DESCRIPTION_Triple glazing",
    "WALL_TYPE_Cavity", "WALL_TYPE_Cob", "WALL_TYPE_Curtain Wall",
    "WALL_TYPE_Granite / Whinstone", "WALL_TYPE_Other",
    "WALL_TYPE_Park Home", "WALL_TYPE_Sandstone / Limestone",
    "WALL_TYPE_Solid Brick", "WALL_TYPE_System Built",
    "WALL_TYPE_Timber Frame", "WALL_TYPE_Unknown",
    "ROOF_TYPE_No Roof", "ROOF_TYPE_Pitched",
    "ROOF_TYPE_Roof Room", "ROOF_TYPE_Thatched", "ROOF_TYPE_Unknown",
    "HOTWATER_SOURCE_Dedicated Gas", "HOTWATER_SOURCE_Dedicated Oil",
    "HOTWATER_SOURCE_Dedicated Solid Fuel",
    "HOTWATER_SOURCE_Electric Immersion",
    "HOTWATER_SOURCE_Heat Pump", "HOTWATER_SOURCE_Main System",
    "HOTWATER_SOURCE_Unknown",
]

# Efficiency lookup tables
WALL_TYPE_EFF = {
    "Cavity"             : (4, 4),
    "Solid Brick"        : (2, 2),
    "Timber Frame"       : (3, 3),
    "Sandstone/Limestone": (2, 2),
    "Granite/Whinstone"  : (2, 2),
    "System Built"       : (3, 3),
    "Cob"                : (2, 2),
    "Park Home"          : (2, 2),
    "Other/Unknown"      : (3, 3),
}
INSUL_EFF_BOOST = {"Uninsulated": 0, "Partial": 1, "Insulated": 2}

ROOF_EFF_MAP = {
    "None": 1, "Low": 2, "At Rafters": 3,
    "Medium": 4, "High": 5, "Very High": 5,
    "Unknown/No Roof": 3,
}
GLAZ_EFF_MAP = {
    "Single": 1, "Secondary": 2, "Double": 3, "Triple": 5,
}
HEAT_EFF_MAP = {
    "Gas Boiler": (3, 3), "Oil Boiler": (2, 2),
    "Electric Storage": (3, 2), "Heat Pump": (5, 5),
    "Community": (4, 4), "LPG": (2, 2), "Biomass": (4, 5),
}
HW_EFF_MAP = {
    "Main System": (3, 3), "Electric Immersion": (3, 2),
    "Community": (4, 4), "Dedicated Gas": (3, 3),
    "Dedicated Oil": (2, 2), "Heat Pump": (5, 5),
    "Dedicated Solid Fuel": (2, 3), "Unknown": (3, 3),
}


# ============================================================
# HELPER: build feature vector from user inputs
# ============================================================
def build_feature_vector(inputs):
    """Convert user inputs dict into a model-ready dataframe row."""
    row = {col: 0.0 for col in FEATURE_COLS}

    # Ordinal features
    row["CONSTRUCTION_AGE_BAND"] = inputs["age_band"]
    row["TOTAL_FLOOR_AREA"]      = inputs["floor_area"]
    row["HAS_OWN_ROOF"]          = inputs["has_own_roof"]
    row["HOTWATER_SOLAR"]        = inputs["solar"]
    row["WALL_INSULATION"]       = inputs["wall_insulation"]
    row["ROOF_INSULATION"]       = inputs["roof_insulation"]

    # Wall efficiency
    base_eff = WALL_TYPE_EFF.get(inputs["wall_type"], (3, 3))
    boost    = INSUL_EFF_BOOST.get(inputs["wall_insulation_label"], 0)
    row["WALLS_ENERGY_EFF"] = min(5, base_eff[0] + boost)
    row["WALLS_ENV_EFF"]    = min(5, base_eff[1] + boost)

    # Roof efficiency
    roof_eff = ROOF_EFF_MAP.get(inputs["roof_insulation_label"], 3)
    row["ROOF_ENERGY_EFF"] = roof_eff if inputs["has_own_roof"] else 3
    row["ROOF_ENV_EFF"]    = roof_eff if inputs["has_own_roof"] else 3

    # Glazing efficiency
    glaz_eff = GLAZ_EFF_MAP.get(inputs["glazing"], 3)
    row["WINDOWS_ENERGY_EFF"] = glaz_eff
    row["WINDOWS_ENV_EFF"]    = glaz_eff
    row["glazing_upgrade_flag"] = 1 if glaz_eff < 3 else 0

    # Heating efficiency
    heat_eff = HEAT_EFF_MAP.get(inputs["heating"], (3, 3))
    row["MAINHEAT_ENERGY_EFF"] = heat_eff[0]
    row["MAINHEAT_ENV_EFF"]    = heat_eff[1]

    # Hot water efficiency
    hw_eff = HW_EFF_MAP.get(inputs["hotwater"], (3, 3))
    row["HOT_WATER_ENERGY_EFF"] = hw_eff[0]
    row["HOT_WATER_ENV_EFF"]    = hw_eff[1]

    # Envelope composite score
    row["envelope_composite_score"] = round(
        (row["WALLS_ENERGY_EFF"] + row["ROOF_ENERGY_EFF"] +
         row["WINDOWS_ENERGY_EFF"]) / 3, 2
    )

    # Property type one-hot
    pt = inputs["property_type"]
    if pt != "Bungalow":
        col = f"PROPERTY_TYPE_{pt}"
        if col in row:
            row[col] = 1.0

    # Built form one-hot
    bf = inputs["built_form"]
    if bf != "Detached":
        col = f"BUILT_FORM_{bf}"
        if col in row:
            row[col] = 1.0
        # simplified
        simp = bf.replace("Enclosed ", "")
        simp_col = f"built_form_simplified_{simp}"
        if simp_col in row:
            row[simp_col] = 1.0

    # Main fuel one-hot
    fuel = inputs["fuel"]
    if fuel != "Biomass":
        col = f"MAIN_FUEL_{fuel}"
        if col in row:
            row[col] = 1.0

    # Heating description one-hot
    heat_desc_map = {
        "Gas Boiler": "Gas boiler", "Oil Boiler": "Oil boiler",
        "Electric Storage": "Electric storage", "Heat Pump": "Heat pump",
        "Community": "Community", "LPG": "LPG",
    }
    heat_desc = heat_desc_map.get(inputs["heating"])
    if heat_desc:
        col = f"MAINHEAT_DESCRIPTION_{heat_desc}"
        if col in row:
            row[col] = 1.0

    # Glazing description one-hot
    glaz_desc_map = {
        "Single": "Single glazing",
        "Secondary": "Secondary glazing",
        "Triple": "Triple glazing",
    }
    glaz_desc = glaz_desc_map.get(inputs["glazing"])
    if glaz_desc:
        col = f"WINDOWS_DESCRIPTION_{glaz_desc}"
        if col in row:
            row[col] = 1.0

    # Wall type one-hot
    wall_col_map = {
        "Cavity": "Cavity", "Solid Brick": "Solid Brick",
        "Timber Frame": "Timber Frame",
        "Sandstone/Limestone": "Sandstone / Limestone",
        "Granite/Whinstone": "Granite / Whinstone",
        "System Built": "System Built", "Cob": "Cob",
        "Park Home": "Park Home", "Other/Unknown": "Unknown",
    }
    wall_col = wall_col_map.get(inputs["wall_type"])
    if wall_col:
        col = f"WALL_TYPE_{wall_col}"
        if col in row:
            row[col] = 1.0

    # Roof type one-hot
    roof_type_map = {
        "Pitched": "Pitched", "Flat": "Flat",
        "Roof Room": "Roof Room", "Thatched": "Thatched",
    }
    if inputs["has_own_roof"]:
        roof_col = f"ROOF_TYPE_{roof_type_map.get(inputs['roof_type'], 'Pitched')}"
        if roof_col in row:
            row[roof_col] = 1.0
    else:
        row["ROOF_TYPE_No Roof"] = 1.0

    # Hot water source one-hot
    hw_col_map = {
        "Main System": "Main System",
        "Electric Immersion": "Electric Immersion",
        "Community": "Community",
        "Dedicated Gas": "Dedicated Gas",
        "Dedicated Oil": "Dedicated Oil",
        "Heat Pump": "Heat Pump",
        "Dedicated Solid Fuel": "Dedicated Solid Fuel",
    }
    hw_col = hw_col_map.get(inputs["hotwater"])
    if hw_col and hw_col != "Community":
        col = f"HOTWATER_SOURCE_{hw_col}"
        if col in row:
            row[col] = 1.0

    return pd.DataFrame([row])[FEATURE_COLS].astype("float32")


# ============================================================
# HELPER: run prediction + SHAP
# ============================================================
def predict_with_shap(feature_df):
    """Returns predicted label, raw prediction array, and SHAP values."""
    pred_class  = int(model.predict(feature_df)[0])
    pred_label  = LABEL_NAMES.get(pred_class + 3, "?")

    explainer   = shap.TreeExplainer(model)
    shap_vals   = explainer.shap_values(feature_df)
    # Shape: (1, n_features, n_classes) — get class D (index 3)
    shap_for_D  = np.array(shap_vals)[0, :, pred_class]

    return pred_label, pred_class, shap_for_D


def label_colour(label):
    return LABEL_COLOURS.get(label, "#999")


def render_label_badge(label, size=80):
    colour = label_colour(label)
    return f"""
    <div style="text-align:center;">
        <div style="
            display:inline-block;
            width:{size}px; height:{size}px;
            line-height:{size}px;
            border-radius:50%;
            background:{colour};
            font-size:{int(size*0.4)}px;
            font-weight:900;
            color:white;
            text-align:center;
        ">{label}</div>
    </div>"""


# ============================================================
# SIDEBAR NAVIGATION
# ============================================================
with st.sidebar:
    st.markdown("""
    <div class="sidebar-brand">
      <p class="sidebar-brand-tag">Thesis dashboard</p>
      <div class="sidebar-brand-row">
        <div class="sidebar-brand-icon" aria-hidden="true">
          <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M4 10.5L12 4l8 6.5V20a1 1 0 01-1 1h-5v-6H10v6H5a1 1 0 01-1-1v-9.5z"
                  stroke="currentColor" stroke-width="1.65" stroke-linejoin="round"/>
          </svg>
        </div>
        <div>
          <p class="sidebar-brand-title">BELDA</p>
          <p class="sidebar-brand-sub">Energy Label Data Analyzer</p>
        </div>
      </div>
      <p class="sidebar-brand-foot">Bachelor thesis · UK EPC dataset</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<p class="sidebar-section-kicker">Navigate</p>', unsafe_allow_html=True)
    page = st.radio(
        "Navigate",
        ["📊 Data Explorer", "🔮 Label Predictor", "🔧 Improvement Advisor"],
        label_visibility="collapsed",
    )

    st.markdown('<div class="sidebar-divider"></div>', unsafe_allow_html=True)
    st.markdown('<p class="sidebar-section-kicker">Context</p>', unsafe_allow_html=True)

    st.markdown("""
    <div class="sidebar-stat-card">
      <h4>Dataset</h4>
      <p class="sidebar-stat-row"><span class="sidebar-stat-accent">24,498,358</span> properties</p>
      <p class="sidebar-stat-row sidebar-stat-muted">England &amp; Wales EPC Register</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="sidebar-stat-card">
      <h4>Model</h4>
      <p class="sidebar-stat-row"><span class="sidebar-stat-accent">LightGBM</span> classifier</p>
      <p class="sidebar-stat-row">Accuracy <span class="sidebar-stat-accent">71.93%</span></p>
      <p class="sidebar-stat-row"><span class="sidebar-stat-accent">66</span> features</p>
    </div>
    """, unsafe_allow_html=True)


# ============================================================
# PAGE 1 — DATA EXPLORER
# ============================================================
if page == "📊 Data Explorer":

    st.markdown("""
    <div class="predictor-hero">
      <div class="predictor-hero-inner">
        <div class="predictor-hero-icon" aria-hidden="true">
          <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M4 20h16M4 20V5" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/>
            <rect x="6" y="12" width="3.5" height="6" rx="0.6" fill="currentColor" opacity="0.92"/>
            <rect x="11" y="8" width="3.5" height="10" rx="0.6" fill="currentColor" opacity="0.72"/>
            <rect x="16" y="14" width="3.5" height="4" rx="0.6" fill="currentColor" opacity="0.52"/>
          </svg>
        </div>
        <div>
          <div class="predictor-section-label">Exploratory analysis</div>
          <h1>Data Explorer</h1>
          <p class="lead">Explore energy performance patterns across 24.5 million UK residential properties,
          browse EDA and model charts from the thesis pipeline, and inspect aggregate SHAP importance.</p>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Key stats banner ──────────────────────────────────────
    st.markdown('<p class="predictor-section-label">At a glance</p>'
                '<div class="predictor-section-title">Dataset Overview</div>',
                unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown("""<div class="metric-card">
            <p class="value">24.5M</p>
            <p class="label">Total Properties</p>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown("""<div class="metric-card">
            <p class="value">58.7%</p>
            <p class="label">Rated D or Worse</p>
        </div>""", unsafe_allow_html=True)
    with c3:
        st.markdown("""<div class="metric-card">
            <p class="value">73.6%</p>
            <p class="label">Have Improvement Potential</p>
        </div>""", unsafe_allow_html=True)
    with c4:
        st.markdown("""<div class="metric-card">
            <p class="value">1.13</p>
            <p class="label">Avg. Improvable Grades</p>
        </div>""", unsafe_allow_html=True)

    # ── Chart viewer ─────────────────────────────────────────
    st.markdown('<p class="predictor-section-label">Charts</p>'
                '<div class="predictor-section-title">EDA and model visuals</div>',
                unsafe_allow_html=True)

    chart_options = {
        "01 — Energy Label Distribution"           : "01_energy_label_distribution.png",
        "02 — Improvement Potential Distribution"  : "02_improvement_potential_distribution.png",
        "03 — Property Type Distribution"          : "03_property_type_distribution.png",
        "04 — Label by Construction Era"           : "04_label_by_construction_era.png",
        "05 — Label by Wall Type"                  : "05_label_by_wall_type.png",
        "06 — Label by Wall Insulation"            : "06_label_by_wall_insulation.png",
        "07 — Label by Heating System"             : "07_label_by_heating_system.png",
        "08 — Label by Main Fuel"                  : "08_label_by_main_fuel.png",
        "09 — Label by Glazing Type"               : "09_label_by_glazing_type.png",
        "10 — Label by Roof Insulation"            : "10_label_by_roof_insulation.png",
        "11 — Improvement by Wall Type"            : "11_improvement_by_wall_type.png",
        "12 — Improvement by Construction Era"     : "12_improvement_by_construction_era.png",
        "13 — Improvement by Heating System"       : "13_improvement_by_heating_system.png",
        "14 — CO₂ by Property Type"               : "14_co2_by_property_type.png",
        "15 — Feature Correlation Heatmap"         : "15_correlation_heatmap.png",
        "16 — Envelope Score vs Energy Label"      : "16_envelope_score_vs_rating.png",
        "SHAP — Summary Plot"                      : "01_shap_summary.png",
        "SHAP — Feature Importance (Bar)"          : "02_shap_bar.png",
        "SHAP — Wall Insulation Dependence"        : "03_shap_dependence.png",
        "SHAP — Waterfall (Typical House)"         : "04_shap_waterfall.png",
        "Model — Confusion Matrix"                 : "confusion_matrix.png",
        "Model — Feature Importance"               : "feature_importance.png",
    }

    selected = st.selectbox("Select a chart to view:", list(chart_options.keys()))
    filename = chart_options[selected]

    # Try EDA charts folder first, then charts folder
    paths = [
        os.path.join(CHARTS_DIR, filename),
        filename,
    ]
    img_path = next((p for p in paths if os.path.exists(p)), None)

    if img_path:
        img = Image.open(img_path)
        st.image(img, use_container_width=True)
    else:
        st.warning(f"Chart not found: {filename}")

    # ── SHAP importance table ─────────────────────────────────
    st.markdown('<p class="predictor-section-label">Model interpretability</p>'
                '<div class="predictor-section-title">Top 20 Features by SHAP Importance</div>',
                unsafe_allow_html=True)

    top20 = shap_importance.head(20).copy()
    top20.index = range(1, 21)
    top20.columns = ["Feature", "Mean |SHAP Value|"]
    top20["Mean |SHAP Value|"] = top20["Mean |SHAP Value|"].round(4)
    st.dataframe(top20, use_container_width=True)


# ============================================================
# PAGE 2 — LABEL PREDICTOR
# ============================================================
elif page == "🔮 Label Predictor":

    st.markdown("""
    <div class="predictor-hero">
      <div class="predictor-hero-inner">
        <div class="predictor-hero-icon" aria-hidden="true">
          <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M12 2L3 7v10l9 5 9-5V7l-9-5z" stroke="currentColor" stroke-width="1.6"
                  stroke-linejoin="round"/>
            <path d="M12 22V12M12 12L3 7M12 12l9-5" stroke="currentColor" stroke-width="1.6"
                  stroke-linecap="round"/>
            <circle cx="12" cy="8" r="2" fill="currentColor" opacity="0.9"/>
          </svg>
        </div>
        <div>
          <div class="predictor-section-label">Interactive model</div>
          <h1>Energy Label Predictor</h1>
          <p class="lead">Enter your property details to predict its current energy label and see SHAP-driven
          explanations of what drives the rating.</p>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Input form ────────────────────────────────────────────
    st.markdown('<p class="predictor-section-label">Inputs</p>'
                '<div class="predictor-section-title">Property Details</div>',
                unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        <div class="predictor-col-head">
          <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
            <path d="M4 21h16M6 21V10l6-6 6 6v11" stroke="#2C5F8A" stroke-width="1.7"
                  stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M9 21v-6h6v6" stroke="#2C5F8A" stroke-width="1.7"
                  stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M10 10h4" stroke="#94a3b8" stroke-width="1.4" stroke-linecap="round"/>
          </svg>
          <div class="stack">
            <span class="predictor-col-kicker">Building</span><br/>
            <strong>Structure</strong>
          </div>
        </div>
        """, unsafe_allow_html=True)
        property_type = st.selectbox(
            "Property Type",
            ["House", "Flat", "Bungalow", "Maisonette", "Park home"]
        )
        built_form = st.selectbox(
            "Built Form",
            ["Detached", "Semi-Detached", "End-Terrace",
             "Mid-Terrace", "Enclosed End-Terrace", "Enclosed Mid-Terrace"]
        )
        age_band = st.selectbox(
            "Construction Era",
            ["Pre-1900", "1900-1929", "1930-1949", "1950-1966",
             "1967-1975", "1976-1982", "1983-1990", "1991-1995",
             "1996-2002", "2003-2006", "2007 onwards"],
            index=3
        )
        floor_area = st.slider("Floor Area (m²)", 10, 500, 88)
        has_own_roof = st.radio(
            "Has Own Roof?",
            ["Yes", "No"],
            horizontal=True
        )

    with col2:
        st.markdown("""
        <div class="predictor-col-head">
          <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
            <rect x="3" y="9" width="18" height="12" rx="1.5" stroke="#2C5F8A" stroke-width="1.6"/>
            <path d="M3 13h18M7 9V6l5-3 5 3v3" stroke="#2C5F8A" stroke-width="1.6"
                  stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M7 16h3v5H7zM14 16h3v5h-3z" fill="#cbd5e1" stroke="#2C5F8A" stroke-width="1"/>
          </svg>
          <div class="stack">
            <span class="predictor-col-kicker">Envelope</span><br/>
            <strong>Fabric</strong>
          </div>
        </div>
        """, unsafe_allow_html=True)
        wall_type = st.selectbox(
            "Wall Type",
            ["Cavity", "Solid Brick", "Timber Frame",
             "Sandstone/Limestone", "Granite/Whinstone",
             "System Built", "Cob", "Park Home", "Other/Unknown"]
        )
        wall_insulation_label = st.selectbox(
            "Wall Insulation",
            ["Insulated", "Partial", "Uninsulated"]
        )
        if has_own_roof == "Yes":
            roof_type = st.selectbox(
                "Roof Type",
                ["Pitched", "Flat", "Roof Room", "Thatched"]
            )
            roof_insulation_label = st.selectbox(
                "Roof Insulation",
                ["Very High", "High", "Medium", "At Rafters",
                 "Low", "None"]
            )
        else:
            roof_type = "Pitched"
            roof_insulation_label = "Unknown/No Roof"
            st.info("No roof data needed — another dwelling is above.")

        glazing = st.selectbox(
            "Glazing Type",
            ["Double", "Triple", "Single", "Secondary"]
        )

    with col3:
        st.markdown("""
        <div class="predictor-col-head">
          <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
            <path d="M12 3c-2 3.5-5 5.2-5 8.8a5 5 0 1010 0c0-3.6-3-5.3-5-8.8z"
                  stroke="#2C5F8A" stroke-width="1.6" stroke-linejoin="round"/>
            <path d="M12 14v7M9 21h6" stroke="#2C5F8A" stroke-width="1.6" stroke-linecap="round"/>
            <path d="M12 10l1.2 1.6a2 2 0 01-2.4 0L12 10z" fill="#e85d4c" opacity="0.85"/>
          </svg>
          <div class="stack">
            <span class="predictor-col-kicker">Services</span><br/>
            <strong>Systems</strong>
          </div>
        </div>
        """, unsafe_allow_html=True)
        heating = st.selectbox(
            "Heating System",
            ["Gas Boiler", "Heat Pump", "Electric Storage",
             "Oil Boiler", "Community", "LPG", "Biomass"]
        )
        fuel = st.selectbox(
            "Main Fuel",
            ["Mains gas", "Electricity", "Oil", "LPG", "Biomass"]
        )
        hotwater = st.selectbox(
            "Hot Water Source",
            ["Main System", "Electric Immersion", "Community",
             "Dedicated Gas", "Dedicated Oil", "Heat Pump",
             "Dedicated Solid Fuel"]
        )
        solar = st.radio(
            "Solar Hot Water?",
            ["No", "Yes"],
            horizontal=True
        )

    # ── Predict button ────────────────────────────────────────
    st.markdown("---")
    predict_btn = st.button("Predict Energy Label", type="primary",
                            use_container_width=True)
    loading_strip = st.empty()

    if predict_btn:
        # Map inputs to numeric values
        age_map = {
            "Pre-1900":1, "1900-1929":2, "1930-1949":3, "1950-1966":4,
            "1967-1975":5, "1976-1982":6, "1983-1990":7, "1991-1995":8,
            "1996-2002":9, "2003-2006":10, "2007 onwards":11
        }
        wall_insul_map = {"Uninsulated":1, "Partial":2, "Insulated":3}
        roof_insul_map = {
            "None":1, "Low":2, "At Rafters":3,
            "Medium":4, "High":5, "Very High":6, "Unknown/No Roof":0
        }

        inputs = {
            "property_type"       : property_type,
            "built_form"          : built_form,
            "age_band"            : age_map[age_band],
            "floor_area"          : float(floor_area),
            "has_own_roof"        : 1 if has_own_roof == "Yes" else 0,
            "wall_type"           : wall_type,
            "wall_insulation"     : wall_insul_map[wall_insulation_label],
            "wall_insulation_label": wall_insulation_label,
            "roof_type"           : roof_type,
            "roof_insulation"     : roof_insul_map[roof_insulation_label],
            "roof_insulation_label": roof_insulation_label,
            "glazing"             : glazing,
            "heating"             : heating,
            "fuel"                : fuel,
            "hotwater"            : hotwater,
            "solar"               : 1 if solar == "Yes" else 0,
        }

        loading_strip.markdown("""
        <div class="predict-loading-strip" role="status" aria-live="polite">
          <div class="spin" aria-hidden="true"></div>
          <span>Running prediction and SHAP analysis…</span>
        </div>
        """, unsafe_allow_html=True)

        with st.status("Prediction in progress…", expanded=True) as status:
            status.write("Building the feature vector from your inputs.")
            feature_df = build_feature_vector(inputs)
            status.write("Running the classifier and computing SHAP explanations (may take a few seconds).")
            pred_label, pred_class, shap_for_pred = predict_with_shap(feature_df)
            status.update(label="Prediction complete", state="complete")

        loading_strip.empty()

        # ── Results ───────────────────────────────────────────
        st.markdown('<div class="section-header">Prediction Results</div>',
                    unsafe_allow_html=True)

        rc1, rc2, rc3 = st.columns([1, 1, 2])

        with rc1:
            st.markdown("**Predicted Energy Label**")
            st.markdown(render_label_badge(pred_label, 100),
                        unsafe_allow_html=True)
            st.markdown(f"<p style='text-align:center; color:{label_colour(pred_label)}; "
                        f"font-weight:700; font-size:1.1rem;'>Label {pred_label}</p>",
                        unsafe_allow_html=True)

        with rc2:
            st.markdown("**What This Means**")
            descriptions = {
                "A": "Excellent — very low energy costs and emissions.",
                "B": "Very Good — well above average efficiency.",
                "C": "Good — above average, typical of newer homes.",
                "D": "Average — the most common UK label. Room to improve.",
                "E": "Below average — higher than necessary energy bills.",
                "F": "Poor — significantly inefficient. Upgrade recommended.",
                "G": "Very Poor — major inefficiencies. Urgent upgrades needed.",
            }
            st.info(descriptions.get(pred_label, ""))

        with rc3:
            # SHAP explanation bar chart
            st.markdown("**What's Driving This Label**")
            top_idx     = np.argsort(np.abs(shap_for_pred))[::-1][:10]
            top_features = [FEATURE_COLS[i] for i in top_idx]
            top_shap     = [float(shap_for_pred[i]) for i in top_idx]

            short_names = {
                "TOTAL_FLOOR_AREA"              : "Floor Area",
                "CONSTRUCTION_AGE_BAND"         : "Construction Era",
                "envelope_composite_score"      : "Envelope Score",
                "MAINHEAT_ENERGY_EFF"           : "Heating Efficiency",
                "HOT_WATER_ENERGY_EFF"          : "Hot Water Efficiency",
                "HOT_WATER_ENV_EFF"             : "HW Environmental Eff.",
                "ROOF_ENERGY_EFF"               : "Roof Efficiency",
                "MAINHEAT_ENV_EFF"              : "Heating Env. Eff.",
                "WALLS_ENERGY_EFF"              : "Walls Efficiency",
                "ROOF_INSULATION"               : "Roof Insulation",
                "WINDOWS_ENERGY_EFF"            : "Windows Efficiency",
                "WALL_INSULATION"               : "Wall Insulation",
                "PROPERTY_TYPE_Flat"            : "Is Flat",
                "PROPERTY_TYPE_House"           : "Is House",
                "HAS_OWN_ROOF"                  : "Has Own Roof",
                "MAIN_FUEL_Mains gas"           : "Mains Gas",
                "MAINHEAT_DESCRIPTION_Gas boiler": "Gas Boiler",
                "HOTWATER_SOURCE_Main System"   : "HW from Main System",
                "HOTWATER_SOURCE_Electric Immersion": "Electric Immersion HW",
            }

            display_names = [short_names.get(f, f) for f in top_features]
            colours = ["#d73027" if v > 0 else "#1a9641" for v in top_shap]

            fig = go.Figure(go.Bar(
                x=top_shap[::-1],
                y=display_names[::-1],
                orientation="h",
                marker_color=colours[::-1],
                text=[f"{v:+.3f}" for v in top_shap[::-1]],
                textposition="outside",
            ))
            fig.update_layout(
                title=dict(
                    text="Feature Impact (Red = pushes toward this label)",
                    font=dict(color="#f8fafc", size=15),
                ),
                height=380,
                margin=dict(l=0, r=60, t=40, b=0),
                plot_bgcolor="#1e293b",
                paper_bgcolor="#0f172a",
                font=dict(color="#cbd5e1"),
                xaxis=dict(
                    title=dict(text="SHAP Value", font=dict(color="#94a3b8")),
                    gridcolor="rgba(148,163,184,0.25)",
                    zerolinecolor="#64748b",
                ),
                yaxis=dict(
                    gridcolor="rgba(148,163,184,0.15)",
                ),
                showlegend=False,
            )
            fig.add_vline(x=0, line_width=1, line_color="#94a3b8")
            st.plotly_chart(fig, use_container_width=True)

        # ── Top 3 issues ──────────────────────────────────────
        st.markdown('<div class="section-header">Top 3 Factors Limiting This Label</div>',
                    unsafe_allow_html=True)

        positive_shap = [(FEATURE_COLS[i], float(shap_for_pred[i]))
                         for i in np.argsort(shap_for_pred)[::-1]
                         if shap_for_pred[i] > 0][:3]

        advice_map = {
            "CONSTRUCTION_AGE_BAND" : "Older construction era — harder to improve but insulation upgrades help significantly.",
            "WALL_INSULATION"       : "Wall insulation status — consider cavity fill or solid wall insulation.",
            "WALLS_ENERGY_EFF"      : "Wall thermal performance — upgrading insulation is the highest-impact improvement.",
            "ROOF_INSULATION"       : "Roof insulation level — increasing loft insulation to 300mm+ is cost-effective.",
            "MAINHEAT_ENERGY_EFF"   : "Heating system efficiency — consider upgrading to a heat pump.",
            "HOT_WATER_ENERGY_EFF"  : "Hot water system — consider upgrading to a more efficient system.",
            "WINDOWS_ENERGY_EFF"    : "Glazing performance — upgrading to double or triple glazing would help.",
            "TOTAL_FLOOR_AREA"      : "Floor area — larger homes use more energy. Better insulation reduces this impact.",
            "PROPERTY_TYPE_Flat"    : "Property type affects shared heat loss assumptions in the EPC methodology.",
            "HAS_OWN_ROOF"          : "Having your own roof increases heat loss potential — ensure it is well insulated.",
        }

        for i, (feat, val) in enumerate(positive_shap, 1):
            advice = advice_map.get(feat, f"Feature {short_names.get(feat, feat)} is contributing to this label.")
            st.markdown(f"""
            <div class="upgrade-card">
                <strong>#{i} — {short_names.get(feat, feat)}</strong>
                <span class="shap-positive"> (+{val:.3f} SHAP)</span><br>
                <span style="color:#94a3b8; font-size:0.9rem;">{advice}</span>
            </div>""", unsafe_allow_html=True)


# ============================================================
# PAGE 3 — IMPROVEMENT ADVISOR
# ============================================================
elif page == "🔧 Improvement Advisor":

    st.markdown("""
    <div class="predictor-hero">
      <div class="predictor-hero-inner">
        <div class="predictor-hero-icon" aria-hidden="true">
          <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M14.7 6.3a1 1 0 000 1.4l1.6 1.6a1 1 0 001.4 0l3.77-3.77a6 6 0 01-7.94 7.94l-6.91 6.91a2.12 2.12 0 01-3-3l6.91-6.91a6 6 0 017.94-7.94l-3.76 3.76z"
                  stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M5 19l2-2M9 15l1-1" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
          </svg>
        </div>
        <div>
          <div class="predictor-section-label">Upgrade planning</div>
          <h1>Improvement Advisor</h1>
          <p class="lead">See what upgrades would improve your energy label and in what order, using the
          same feature pipeline and model as the label predictor.</p>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<p class="predictor-section-label">Starting point</p>'
                '<div class="predictor-section-title">Current Property Details</div>',
                unsafe_allow_html=True)

    ia1, ia2, ia3 = st.columns(3)

    with ia1:
        st.markdown("""
        <div class="predictor-col-head">
          <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
            <path d="M4 21h16M6 21V10l6-6 6 6v11" stroke="#2C5F8A" stroke-width="1.7"
                  stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M9 21v-6h6v6" stroke="#2C5F8A" stroke-width="1.7"
                  stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M10 10h4" stroke="#94a3b8" stroke-width="1.4" stroke-linecap="round"/>
          </svg>
          <div class="stack">
            <span class="predictor-col-kicker">Building</span><br/>
            <strong>Structure</strong>
          </div>
        </div>
        """, unsafe_allow_html=True)
        ia_property_type = st.selectbox("Property Type",
            ["House", "Flat", "Bungalow", "Maisonette", "Park home"],
            key="ia_pt")
        ia_built_form = st.selectbox("Built Form",
            ["Detached", "Semi-Detached", "End-Terrace", "Mid-Terrace",
             "Enclosed End-Terrace", "Enclosed Mid-Terrace"], key="ia_bf")
        ia_age = st.selectbox("Construction Era",
            ["Pre-1900", "1900-1929", "1930-1949", "1950-1966",
             "1967-1975", "1976-1982", "1983-1990", "1991-1995",
             "1996-2002", "2003-2006", "2007 onwards"],
            index=3, key="ia_age")
        ia_floor = st.slider("Floor Area (m²)", 10, 500, 88, key="ia_floor")
        ia_roof = st.radio("Has Own Roof?", ["Yes","No"],
                           horizontal=True, key="ia_roof")

    with ia2:
        st.markdown("""
        <div class="predictor-col-head">
          <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
            <rect x="3" y="9" width="18" height="12" rx="1.5" stroke="#2C5F8A" stroke-width="1.6"/>
            <path d="M3 13h18M7 9V6l5-3 5 3v3" stroke="#2C5F8A" stroke-width="1.6"
                  stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M7 16h3v5H7zM14 16h3v5h-3z" fill="#cbd5e1" stroke="#2C5F8A" stroke-width="1"/>
          </svg>
          <div class="stack">
            <span class="predictor-col-kicker">Envelope</span><br/>
            <strong>Current Fabric</strong>
          </div>
        </div>
        """, unsafe_allow_html=True)
        ia_wall_type = st.selectbox("Wall Type",
            ["Cavity", "Solid Brick", "Timber Frame",
             "Sandstone/Limestone", "Granite/Whinstone",
             "System Built", "Cob", "Park Home", "Other/Unknown"],
            key="ia_wt")
        ia_wall_insul = st.selectbox("Current Wall Insulation",
            ["Uninsulated", "Partial", "Insulated"], key="ia_wi")
        ia_roof_type = st.selectbox("Roof Type",
            ["Pitched", "Flat", "Roof Room", "Thatched"], key="ia_rt")
        ia_roof_insul = st.selectbox("Current Roof Insulation",
            ["None", "Low", "At Rafters", "Medium", "High", "Very High"],
            key="ia_ri")
        ia_glazing = st.selectbox("Current Glazing",
            ["Single", "Double", "Secondary", "Triple"], key="ia_gl")

    with ia3:
        st.markdown("""
        <div class="predictor-col-head">
          <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
            <path d="M12 3c-2 3.5-5 5.2-5 8.8a5 5 0 1010 0c0-3.6-3-5.3-5-8.8z"
                  stroke="#2C5F8A" stroke-width="1.6" stroke-linejoin="round"/>
            <path d="M12 14v7M9 21h6" stroke="#2C5F8A" stroke-width="1.6" stroke-linecap="round"/>
            <path d="M12 10l1.2 1.6a2 2 0 01-2.4 0L12 10z" fill="#e85d4c" opacity="0.85"/>
          </svg>
          <div class="stack">
            <span class="predictor-col-kicker">Services</span><br/>
            <strong>Current Systems</strong>
          </div>
        </div>
        """, unsafe_allow_html=True)
        ia_heating = st.selectbox("Heating System",
            ["Gas Boiler", "Heat Pump", "Electric Storage",
             "Oil Boiler", "Community", "LPG", "Biomass"], key="ia_heat")
        ia_fuel = st.selectbox("Main Fuel",
            ["Mains gas", "Electricity", "Oil", "LPG", "Biomass"],
            key="ia_fuel")
        ia_hotwater = st.selectbox("Hot Water Source",
            ["Main System", "Electric Immersion", "Community",
             "Dedicated Gas", "Dedicated Oil", "Heat Pump",
             "Dedicated Solid Fuel"], key="ia_hw")
        ia_solar = st.radio("Solar Hot Water?", ["No","Yes"],
                            horizontal=True, key="ia_sol")

    st.markdown("---")
    advise_btn = st.button("Generate Improvement Plan",
                           type="primary", use_container_width=True)
    ia_loading_strip = st.empty()

    if advise_btn:
        age_map = {
            "Pre-1900":1, "1900-1929":2, "1930-1949":3, "1950-1966":4,
            "1967-1975":5, "1976-1982":6, "1983-1990":7, "1991-1995":8,
            "1996-2002":9, "2003-2006":10, "2007 onwards":11
        }
        wall_insul_map = {"Uninsulated":1, "Partial":2, "Insulated":3}
        roof_insul_num = {
            "None":1, "Low":2, "At Rafters":3,
            "Medium":4, "High":5, "Very High":6
        }

        base_inputs = {
            "property_type"        : ia_property_type,
            "built_form"           : ia_built_form,
            "age_band"             : age_map[ia_age],
            "floor_area"           : float(ia_floor),
            "has_own_roof"         : 1 if ia_roof == "Yes" else 0,
            "wall_type"            : ia_wall_type,
            "wall_insulation"      : wall_insul_map[ia_wall_insul],
            "wall_insulation_label": ia_wall_insul,
            "roof_type"            : ia_roof_type,
            "roof_insulation"      : roof_insul_num.get(ia_roof_insul, 3),
            "roof_insulation_label": ia_roof_insul,
            "glazing"              : ia_glazing,
            "heating"              : ia_heating,
            "fuel"                 : ia_fuel,
            "hotwater"             : ia_hotwater,
            "solar"                : 1 if ia_solar == "Yes" else 0,
        }

        # Define possible upgrades
        upgrades = []

        if ia_wall_insul != "Insulated":
            upgrades.append(("Insulate Walls (fully)",
                             {**base_inputs,
                              "wall_insulation": 3,
                              "wall_insulation_label": "Insulated"}))
        if ia_roof_insul in ["None", "Low"]:
            upgrades.append(("Upgrade Roof Insulation to High (200mm+)",
                             {**base_inputs,
                              "roof_insulation": 5,
                              "roof_insulation_label": "High"}))
        if ia_glazing in ["Single", "Secondary"]:
            upgrades.append(("Upgrade to Double Glazing",
                             {**base_inputs, "glazing": "Double"}))
        if ia_glazing == "Double":
            upgrades.append(("Upgrade to Triple Glazing",
                             {**base_inputs, "glazing": "Triple"}))
        if ia_heating not in ["Heat Pump"]:
            upgrades.append(("Replace Heating with Heat Pump",
                             {**base_inputs,
                              "heating": "Heat Pump",
                              "fuel": "Electricity"}))
        if ia_solar == "No":
            upgrades.append(("Add Solar Hot Water",
                             {**base_inputs, "solar": 1}))

        ia_loading_strip.markdown("""
        <div class="predict-loading-strip" role="status" aria-live="polite">
          <div class="spin" aria-hidden="true"></div>
          <span>Scoring baseline and upgrade scenarios…</span>
        </div>
        """, unsafe_allow_html=True)

        with st.status("Improvement plan in progress…", expanded=True) as status:
            status.write("Running the model for your current property and each upgrade.")
            base_df              = build_feature_vector(base_inputs)
            base_pred            = int(model.predict(base_df)[0])
            base_label           = LABEL_NAMES.get(base_pred + 3, "?")

            results = []
            for upgrade_name, upgraded_inputs in upgrades:
                upg_df    = build_feature_vector(upgraded_inputs)
                upg_pred  = int(model.predict(upg_df)[0])
                upg_label = LABEL_NAMES.get(upg_pred + 3, "?")
                improvement = base_pred - upg_pred  # positive = better
                results.append({
                    "upgrade"    : upgrade_name,
                    "new_label"  : upg_label,
                    "new_class"  : upg_pred,
                    "improvement": improvement,
                })

            results.sort(key=lambda x: x["improvement"], reverse=True)
            status.update(label="Improvement plan ready", state="complete")

        ia_loading_strip.empty()

        # ── Results ───────────────────────────────────────────
        st.markdown('<p class="predictor-section-label">Summary</p>'
                    '<div class="predictor-section-title">Your Improvement Plan</div>',
                    unsafe_allow_html=True)

        cc1, cc2 = st.columns(2)
        with cc1:
            st.markdown("**Current Label**")
            st.markdown(render_label_badge(base_label, 90),
                        unsafe_allow_html=True)
            st.markdown(f"<p style='text-align:center; font-weight:700; "
                        f"color:{label_colour(base_label)};'>Label {base_label}</p>",
                        unsafe_allow_html=True)

        best = results[0] if results else None
        with cc2:
            if best and best["improvement"] > 0:
                st.markdown("**Best Single Upgrade**")
                st.markdown(render_label_badge(best["new_label"], 90),
                            unsafe_allow_html=True)
                st.markdown(f"<p style='text-align:center; font-weight:700; "
                            f"color:{label_colour(best['new_label'])};'>"
                            f"Label {best['new_label']} "
                            f"({best['improvement']:+d} grade{'s' if abs(best['improvement'])>1 else ''})"
                            f"</p>", unsafe_allow_html=True)
            else:
                st.success("Your property is already at or near its optimal rating!")

        st.markdown('<p class="predictor-section-label">Ranking</p>'
                    '<div class="predictor-section-title">All Recommended Upgrades</div>',
                    unsafe_allow_html=True)

        for i, res in enumerate(results, 1):
            improvement = res["improvement"]
            colour      = "#1a9641" if improvement > 0 else "#d73027" if improvement < 0 else "#888"
            arrow       = "⬆️" if improvement > 0 else "➡️" if improvement == 0 else "⬇️"
            grade_text  = (f"{improvement:+d} grade{'s' if abs(improvement)>1 else ''}"
                           if improvement != 0 else "No change")

            st.markdown(f"""
            <div class="upgrade-card" style="border-left-color:{colour};">
                <strong>#{i} — {res['upgrade']}</strong><br>
                <span style="color:{colour}; font-weight:600;">
                    {arrow} {base_label} → {res['new_label']} &nbsp;|&nbsp; {grade_text}
                </span>
            </div>""", unsafe_allow_html=True)

        # Improvement journey chart
        if any(r["improvement"] > 0 for r in results):
            st.markdown('<p class="predictor-section-label">Visualization</p>'
                        '<div class="predictor-section-title">Improvement Journey</div>',
                        unsafe_allow_html=True)

            journey_labels = [base_label] + [
                r["new_label"] for r in results if r["improvement"] > 0
            ]
            journey_names  = ["Current"] + [
                r["upgrade"][:30] + "..." if len(r["upgrade"]) > 30
                else r["upgrade"]
                for r in results if r["improvement"] > 0
            ]
            journey_colours = [label_colour(l) for l in journey_labels]
            journey_vals    = [7 - (ord(l) - ord("A")) for l in journey_labels]

            fig = go.Figure(go.Bar(
                x=journey_names,
                y=journey_vals,
                marker_color=journey_colours,
                text=journey_labels,
                textposition="outside",
                textfont=dict(size=16, color="#0f172a"),
            ))
            fig.update_layout(
                title=dict(
                    text="Energy Label Improvement Journey",
                    font=dict(color="#f8fafc", size=16),
                ),
                yaxis=dict(
                    tickvals=list(range(1, 8)),
                    ticktext=["G","F","E","D","C","B","A"],
                    title=dict(text="Energy Label", font=dict(color="#94a3b8")),
                    gridcolor="rgba(148,163,184,0.2)",
                ),
                xaxis=dict(
                    title=dict(font=dict(color="#94a3b8")),
                    tickfont=dict(color="#cbd5e1"),
                ),
                plot_bgcolor="#1e293b",
                paper_bgcolor="#0f172a",
                font=dict(color="#cbd5e1"),
                height=380,
                margin=dict(t=50, b=80),
                showlegend=False,
            )
            st.plotly_chart(fig, use_container_width=True)