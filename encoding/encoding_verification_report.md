# BELDA — Encoding Verification Report
**Generated:** 2026-05-09 12:32:08
**Source file:** `epc_encoded.parquet`
**Total rows:** 24,498,358
**Total columns:** 51

---
## 1. Overall Shape Check

| Check | Expected | Actual | Status |
|---|---|---|---|
| Row count | 24,498,358 | 24,498,358 | ✅ PASS |
| Column count | 51 | 51 | ✅ PASS |

---
## 2. Dropped Columns Verification
These columns should NOT exist in the encoded file.

| Column | Present in file | Status |
|---|---|---|
| `WALLS_DESCRIPTION` | No | ✅ PASS |
| `ROOF_DESCRIPTION` | No | ✅ PASS |
| `HOTWATER_DESCRIPTION` | No | ✅ PASS |
| `label_gap_readable` | No | ✅ PASS |

---
## 3. Text Column Check
There should be zero text (object) columns remaining.

| Check | Result | Status |
|---|---|---|
| Text columns remaining | 0 | ✅ PASS |

---
## 4. Ordinal Encoded Columns

### `CONSTRUCTION_AGE_BAND`
| Item | Detail |
|---|---|
| Status | ✅ PASS |
| Data type | `int32` |
| Allowed values | [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11] |
| Actual unique values | [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11] |
| Unexpected values | None |
| Null count | 0 (0.00%) |

**Value distribution:**

| Value | Count | % of Total |
|---|---|---|
| 1 | 2,375,693 | 9.7% |
| 2 | 3,602,040 | 14.7% |
| 3 | 3,277,674 | 13.4% |
| 4 | 4,193,137 | 17.1% |
| 5 | 2,876,975 | 11.7% |
| 6 | 1,502,175 | 6.1% |
| 7 | 1,620,245 | 6.6% |
| 8 | 949,651 | 3.9% |
| 9 | 1,239,189 | 5.1% |
| 10 | 1,030,797 | 4.2% |
| 11 | 1,830,782 | 7.5% |

### `co2_intensity_category`
| Item | Detail |
|---|---|
| Status | ✅ PASS |
| Data type | `int32` |
| Allowed values | [0, 1, 2, 3] |
| Actual unique values | [0, 1, 2, 3] |
| Unexpected values | None |
| Null count | 0 (0.00%) |

**Value distribution:**

| Value | Count | % of Total |
|---|---|---|
| 0 | 1,214,090 | 5.0% |
| 1 | 6,210,577 | 25.4% |
| 2 | 12,308,949 | 50.2% |
| 3 | 4,764,742 | 19.4% |

---
## 5. Efficiency Score Columns (Expected Range: 1–5)

| Column | Dtype | Min | Max | Nulls | Unexpected Values | Status |
|---|---|---|---|---|---|---|
| `WALLS_ENERGY_EFF` | `Int64` | 1 | 5 | 0 (0.0%) | 0 | ✅ PASS |
| `WALLS_ENV_EFF` | `Int64` | 1 | 5 | 0 (0.0%) | 0 | ✅ PASS |
| `ROOF_ENERGY_EFF` | `Int64` | 1 | 5 | 4,097,630 (16.7%) | 0 | ✅ PASS |
| `ROOF_ENV_EFF` | `Int64` | 1 | 5 | 4,097,630 (16.7%) | 0 | ✅ PASS |
| `WINDOWS_ENERGY_EFF` | `Int64` | 1 | 5 | 0 (0.0%) | 0 | ✅ PASS |
| `WINDOWS_ENV_EFF` | `Int64` | 1 | 5 | 0 (0.0%) | 0 | ✅ PASS |
| `MAINHEAT_ENERGY_EFF` | `Int64` | 1 | 5 | 0 (0.0%) | 0 | ✅ PASS |
| `MAINHEAT_ENV_EFF` | `Int64` | 1 | 5 | 0 (0.0%) | 0 | ✅ PASS |
| `HOT_WATER_ENERGY_EFF` | `Int64` | 1 | 5 | 0 (0.0%) | 0 | ✅ PASS |
| `HOT_WATER_ENV_EFF` | `Int64` | 1 | 5 | 0 (0.0%) | 0 | ✅ PASS |

---
## 6. Binary Columns (Expected Values: 0 and 1 only)

| Column | Dtype | Unique Values | Count of 1s | Count of 0s | Nulls | Status |
|---|---|---|---|---|---|---|
| `HAS_OWN_ROOF` | `int8` | [0, 1] | 20,400,728 | 4,097,630 | 0 (0.0%) | ✅ PASS |
| `glazing_upgrade_flag` | `int32` | [0, 1] | 1,139,217 | 23,359,141 | 0 (0.0%) | ✅ PASS |
| `PROPERTY_TYPE_Flat` | `int32` | [0, 1] | 6,172,886 | 18,325,472 | 0 (0.0%) | ✅ PASS |
| `PROPERTY_TYPE_House` | `int32` | [0, 1] | 15,513,238 | 8,985,120 | 0 (0.0%) | ✅ PASS |
| `PROPERTY_TYPE_Maisonette` | `int32` | [0, 1] | 597,872 | 23,900,486 | 0 (0.0%) | ✅ PASS |
| `PROPERTY_TYPE_Park home` | `int32` | [0, 1] | 12,885 | 24,485,473 | 0 (0.0%) | ✅ PASS |
| `BUILT_FORM_Enclosed End-Terrace` | `int32` | [0, 1] | 383,166 | 24,115,192 | 0 (0.0%) | ✅ PASS |
| `BUILT_FORM_Enclosed Mid-Terrace` | `int32` | [0, 1] | 328,090 | 24,170,268 | 0 (0.0%) | ✅ PASS |
| `BUILT_FORM_End-Terrace` | `int32` | [0, 1] | 3,540,983 | 20,957,375 | 0 (0.0%) | ✅ PASS |
| `BUILT_FORM_Mid-Terrace` | `int32` | [0, 1] | 7,180,718 | 17,317,640 | 0 (0.0%) | ✅ PASS |
| `BUILT_FORM_Semi-Detached` | `int32` | [0, 1] | 7,845,155 | 16,653,203 | 0 (0.0%) | ✅ PASS |
| `built_form_simplified_End-Terrace` | `int32` | [0, 1] | 3,924,149 | 20,574,209 | 0 (0.0%) | ✅ PASS |
| `built_form_simplified_Mid-Terrace` | `int32` | [0, 1] | 7,508,808 | 16,989,550 | 0 (0.0%) | ✅ PASS |
| `built_form_simplified_Semi-detached` | `int32` | [0, 1] | 7,845,155 | 16,653,203 | 0 (0.0%) | ✅ PASS |
| `MAIN_FUEL_Electricity` | `int32` | [0, 1] | 2,101,856 | 22,396,502 | 0 (0.0%) | ✅ PASS |
| `MAIN_FUEL_LPG` | `int32` | [0, 1] | 163,104 | 24,335,254 | 0 (0.0%) | ✅ PASS |
| `MAIN_FUEL_Mains gas` | `int32` | [0, 1] | 21,345,223 | 3,153,135 | 0 (0.0%) | ✅ PASS |
| `MAIN_FUEL_Oil` | `int32` | [0, 1] | 771,982 | 23,726,376 | 0 (0.0%) | ✅ PASS |
| `MAINHEAT_DESCRIPTION_Community` | `int32` | [0, 1] | 640,833 | 23,857,525 | 0 (0.0%) | ✅ PASS |
| `MAINHEAT_DESCRIPTION_Electric storage` | `int32` | [0, 1] | 2,344,238 | 22,154,120 | 0 (0.0%) | ✅ PASS |
| `MAINHEAT_DESCRIPTION_Gas boiler` | `int32` | [0, 1] | 20,061,980 | 4,436,378 | 0 (0.0%) | ✅ PASS |
| `MAINHEAT_DESCRIPTION_Heat pump` | `int32` | [0, 1] | 269,472 | 24,228,886 | 0 (0.0%) | ✅ PASS |
| `MAINHEAT_DESCRIPTION_LPG` | `int32` | [0, 1] | 182,856 | 24,315,502 | 0 (0.0%) | ✅ PASS |
| `MAINHEAT_DESCRIPTION_Oil boiler` | `int32` | [0, 1] | 904,080 | 23,594,278 | 0 (0.0%) | ✅ PASS |
| `WINDOWS_DESCRIPTION_Secondary glazing` | `int32` | [0, 1] | 215,861 | 24,282,497 | 0 (0.0%) | ✅ PASS |
| `WINDOWS_DESCRIPTION_Single glazing` | `int32` | [0, 1] | 1,139,217 | 23,359,141 | 0 (0.0%) | ✅ PASS |
| `WINDOWS_DESCRIPTION_Triple glazing` | `int32` | [0, 1] | 1,023,089 | 23,475,269 | 0 (0.0%) | ✅ PASS |

---
## 7. Target Variable Columns

| Column | Dtype | Min | Max | Unique Values | Nulls | Status |
|---|---|---|---|---|---|---|
| `CURRENT_ENERGY_RATING` | `Int64` | 3 | 9 | [3, 4, 5, 6, 7, 8, 9] | 0 (0.0%) | ❌ FAIL |
| `POTENTIAL_ENERGY_RATING` | `Int64` | 3 | 9 | [3, 4, 5, 6, 7, 8, 9] | 0 (0.0%) | ❌ FAIL |
| `improvement_potential` | `Int64` | 0 | 6 | [0, 1, 2, 3, 4, 5, 6] | 0 (0.0%) | ✅ PASS |

---
## 8. Continuous / Numeric Columns

| Column | Dtype | Min | Max | Mean | Nulls | Status |
|---|---|---|---|---|---|---|
| `TOTAL_FLOOR_AREA` | `float64` | 10.0 | 1000.0 | 88.24 | 0 (0.0%) | ✅ PASS |
| `CURRENT_ENERGY_EFFICIENCY` | `int64` | 1 | 13060 | 64.8 | 0 (0.0%) | ✅ PASS |
| `POTENTIAL_ENERGY_EFFICIENCY` | `int64` | 1 | 13071 | 79.35 | 0 (0.0%) | ✅ PASS |
| `ENERGY_CONSUMPTION_CURRENT` | `int64` | 10 | 500 | 247.13 | 0 (0.0%) | ✅ PASS |
| `ENERGY_CONSUMPTION_POTENTIAL` | `float64` | -46498.0 | 996.0 | 143.72 | 0 (0.0%) | ✅ PASS |
| `ENVIRONMENT_IMPACT_CURRENT` | `int64` | 1 | 224 | 62.11 | 0 (0.0%) | ✅ PASS |
| `CO2_EMISSIONS_CURRENT` | `float64` | -15.9 | 250.0 | 3.88 | 0 (0.0%) | ✅ PASS |
| `CO2_EMISS_CURR_PER_FLOOR_AREA` | `int64` | -134 | 545 | 44.3 | 0 (0.0%) | ✅ PASS |
| `envelope_composite_score` | `float64` | 1.0 | 5.0 | 3.12 | 0 (0.0%) | ✅ PASS |

---
## 9. Full Column Inventory

Every column in the final encoded file.

| # | Column | Dtype | Null Count | Null % |
|---|---|---|---|---|
| 1 | `CONSTRUCTION_AGE_BAND` | `int32` | 0 | 0.00% |
| 2 | `TOTAL_FLOOR_AREA` | `float64` | 0 | 0.00% |
| 3 | `WALLS_ENERGY_EFF` | `Int64` | 0 | 0.00% |
| 4 | `WALLS_ENV_EFF` | `Int64` | 0 | 0.00% |
| 5 | `ROOF_ENERGY_EFF` | `Int64` | 4,097,630 | 16.73% |
| 6 | `ROOF_ENV_EFF` | `Int64` | 4,097,630 | 16.73% |
| 7 | `WINDOWS_ENERGY_EFF` | `Int64` | 0 | 0.00% |
| 8 | `WINDOWS_ENV_EFF` | `Int64` | 0 | 0.00% |
| 9 | `MAINHEAT_ENERGY_EFF` | `Int64` | 0 | 0.00% |
| 10 | `MAINHEAT_ENV_EFF` | `Int64` | 0 | 0.00% |
| 11 | `HOT_WATER_ENERGY_EFF` | `Int64` | 0 | 0.00% |
| 12 | `HOT_WATER_ENV_EFF` | `Int64` | 0 | 0.00% |
| 13 | `CURRENT_ENERGY_RATING` | `Int64` | 0 | 0.00% |
| 14 | `POTENTIAL_ENERGY_RATING` | `Int64` | 0 | 0.00% |
| 15 | `CURRENT_ENERGY_EFFICIENCY` | `int64` | 0 | 0.00% |
| 16 | `POTENTIAL_ENERGY_EFFICIENCY` | `int64` | 0 | 0.00% |
| 17 | `ENERGY_CONSUMPTION_CURRENT` | `int64` | 0 | 0.00% |
| 18 | `ENERGY_CONSUMPTION_POTENTIAL` | `float64` | 0 | 0.00% |
| 19 | `ENVIRONMENT_IMPACT_CURRENT` | `int64` | 0 | 0.00% |
| 20 | `CO2_EMISSIONS_CURRENT` | `float64` | 0 | 0.00% |
| 21 | `CO2_EMISS_CURR_PER_FLOOR_AREA` | `int64` | 0 | 0.00% |
| 22 | `HAS_OWN_ROOF` | `int8` | 0 | 0.00% |
| 23 | `improvement_potential` | `Int64` | 0 | 0.00% |
| 24 | `glazing_upgrade_flag` | `int32` | 0 | 0.00% |
| 25 | `envelope_composite_score` | `float64` | 0 | 0.00% |
| 26 | `co2_intensity_category` | `int32` | 0 | 0.00% |
| 27 | `PROPERTY_TYPE_Flat` | `int32` | 0 | 0.00% |
| 28 | `PROPERTY_TYPE_House` | `int32` | 0 | 0.00% |
| 29 | `PROPERTY_TYPE_Maisonette` | `int32` | 0 | 0.00% |
| 30 | `PROPERTY_TYPE_Park home` | `int32` | 0 | 0.00% |
| 31 | `BUILT_FORM_Enclosed End-Terrace` | `int32` | 0 | 0.00% |
| 32 | `BUILT_FORM_Enclosed Mid-Terrace` | `int32` | 0 | 0.00% |
| 33 | `BUILT_FORM_End-Terrace` | `int32` | 0 | 0.00% |
| 34 | `BUILT_FORM_Mid-Terrace` | `int32` | 0 | 0.00% |
| 35 | `BUILT_FORM_Semi-Detached` | `int32` | 0 | 0.00% |
| 36 | `built_form_simplified_End-Terrace` | `int32` | 0 | 0.00% |
| 37 | `built_form_simplified_Mid-Terrace` | `int32` | 0 | 0.00% |
| 38 | `built_form_simplified_Semi-detached` | `int32` | 0 | 0.00% |
| 39 | `MAIN_FUEL_Electricity` | `int32` | 0 | 0.00% |
| 40 | `MAIN_FUEL_LPG` | `int32` | 0 | 0.00% |
| 41 | `MAIN_FUEL_Mains gas` | `int32` | 0 | 0.00% |
| 42 | `MAIN_FUEL_Oil` | `int32` | 0 | 0.00% |
| 43 | `MAINHEAT_DESCRIPTION_Community` | `int32` | 0 | 0.00% |
| 44 | `MAINHEAT_DESCRIPTION_Electric storage` | `int32` | 0 | 0.00% |
| 45 | `MAINHEAT_DESCRIPTION_Gas boiler` | `int32` | 0 | 0.00% |
| 46 | `MAINHEAT_DESCRIPTION_Heat pump` | `int32` | 0 | 0.00% |
| 47 | `MAINHEAT_DESCRIPTION_LPG` | `int32` | 0 | 0.00% |
| 48 | `MAINHEAT_DESCRIPTION_Oil boiler` | `int32` | 0 | 0.00% |
| 49 | `WINDOWS_DESCRIPTION_Secondary glazing` | `int32` | 0 | 0.00% |
| 50 | `WINDOWS_DESCRIPTION_Single glazing` | `int32` | 0 | 0.00% |
| 51 | `WINDOWS_DESCRIPTION_Triple glazing` | `int32` | 0 | 0.00% |

---
## 10. Summary Scorecard

| Check | Result |
|---|---|
| Correct row count | ✅ PASS |
| Correct column count | ✅ PASS |
| No text columns remaining | ✅ PASS |
| Dropped columns removed | ✅ PASS |
| CONSTRUCTION_AGE_BAND in range | ✅ PASS |
| co2_intensity_category in range | ✅ PASS |
| CURRENT_ENERGY_RATING in range | ❌ FAIL |
| All efficiency cols present | ✅ PASS |
| All binary cols are 0/1 | ✅ PASS |

**8/9 checks passed.**

> ⚠️ Some checks failed. Review the sections above for details.

---
*BELDA Encoding Verification — auto-generated by verification_script.py*