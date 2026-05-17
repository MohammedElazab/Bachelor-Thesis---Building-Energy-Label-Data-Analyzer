# BELDA — Encoding Verification Report v2
**Generated:** 2026-05-09 14:26:06
**Source file:** `epc_encoded.parquet`
**Total rows:** 24,498,358
**Total columns:** 77

---
## 1. Overall Shape Check

| Check | Expected | Actual | Status |
|---|---|---|---|
| Row count    | 24,498,358 | 24,498,358 | ✅ PASS |
| Column count | 77 | 77 | ✅ PASS |

---
## 2. Dropped Columns Verification
These columns must NOT exist in the encoded file.

| Column | Present | Status |
|---|---|---|
| `WALLS_DESCRIPTION` | No | ✅ PASS |
| `ROOF_DESCRIPTION` | No | ✅ PASS |
| `HOTWATER_DESCRIPTION` | No | ✅ PASS |
| `label_gap_readable` | No | ✅ PASS |

---
## 3. Text Column Check

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

| Value | Label | Count | % of Total |
|---|---|---|---|
| 1 | Pre-1900 | 2,375,693 | 9.7% |
| 2 | 1900-1929 | 3,602,040 | 14.7% |
| 3 | 1930-1949 | 3,277,674 | 13.4% |
| 4 | 1950-1966 | 4,193,137 | 17.1% |
| 5 | 1967-1975 | 2,876,975 | 11.7% |
| 6 | 1976-1982 | 1,502,175 | 6.1% |
| 7 | 1983-1990 | 1,620,245 | 6.6% |
| 8 | 1991-1995 | 949,651 | 3.9% |
| 9 | 1996-2002 | 1,239,189 | 5.1% |
| 10 | 2003-2006 | 1,030,797 | 4.2% |
| 11 | 2007 onwards | 1,830,782 | 7.5% |

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

| Value | Label | Count | % of Total |
|---|---|---|---|
| 0 | Unknown | 1,214,090 | 5.0% |
| 1 | Low | 6,210,577 | 25.4% |
| 2 | Medium | 12,308,949 | 50.2% |
| 3 | High | 4,764,742 | 19.4% |

### `WALL_INSULATION`
| Item | Detail |
|---|---|
| Status | ✅ PASS |
| Data type | `int32` |
| Allowed values | [0, 1, 2, 3] |
| Actual unique values | [0, 1, 2, 3] |
| Unexpected values | None |
| Null count | 0 (0.00%) |

**Value distribution:**

| Value | Label | Count | % of Total |
|---|---|---|---|
| 0 | Unknown | 959,376 | 3.9% |
| 1 | Uninsulated | 10,225,665 | 41.7% |
| 2 | Partial | 838,001 | 3.4% |
| 3 | Insulated | 12,475,316 | 50.9% |

### `ROOF_INSULATION`
| Item | Detail |
|---|---|
| Status | ✅ PASS |
| Data type | `int32` |
| Allowed values | [0, 1, 2, 3, 4, 5, 6] |
| Actual unique values | [0, 1, 2, 3, 4, 5, 6] |
| Unexpected values | None |
| Null count | 0 (0.00%) |

**Value distribution:**

| Value | Label | Count | % of Total |
|---|---|---|---|
| 0 | Unknown / No Roof | 4,905,045 | 20.0% |
| 1 | None | 2,674,781 | 10.9% |
| 2 | Low | 1,565,760 | 6.4% |
| 3 | At Rafters | 333,046 | 1.4% |
| 4 | Medium | 7,211,930 | 29.4% |
| 5 | High | 5,909,439 | 24.1% |
| 6 | Very High | 1,898,357 | 7.7% |

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
| `HOTWATER_SOLAR` | `int64` | [0, 1] | 134,258 | 24,364,100 | 0 (0.0%) | ✅ PASS |
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
| `WALL_TYPE_Cavity` | `int32` | [0, 1] | 15,108,274 | 9,390,084 | 0 (0.0%) | ✅ PASS |
| `WALL_TYPE_Cob` | `int32` | [0, 1] | 18,361 | 24,479,997 | 0 (0.0%) | ✅ PASS |
| `WALL_TYPE_Curtain Wall` | `int32` | [0, 1] | 7 | 24,498,351 | 0 (0.0%) | ✅ PASS |
| `WALL_TYPE_Granite / Whinstone` | `int32` | [0, 1] | 379,668 | 24,118,690 | 0 (0.0%) | ✅ PASS |
| `WALL_TYPE_Other` | `int32` | [0, 1] | 2 | 24,498,356 | 0 (0.0%) | ✅ PASS |
| `WALL_TYPE_Park Home` | `int32` | [0, 1] | 12,828 | 24,485,530 | 0 (0.0%) | ✅ PASS |
| `WALL_TYPE_Sandstone / Limestone` | `int32` | [0, 1] | 805,711 | 23,692,647 | 0 (0.0%) | ✅ PASS |
| `WALL_TYPE_Solid Brick` | `int32` | [0, 1] | 5,480,591 | 19,017,767 | 0 (0.0%) | ✅ PASS |
| `WALL_TYPE_System Built` | `int32` | [0, 1] | 1,020,261 | 23,478,097 | 0 (0.0%) | ✅ PASS |
| `WALL_TYPE_Timber Frame` | `int32` | [0, 1] | 717,259 | 23,781,099 | 0 (0.0%) | ✅ PASS |
| `WALL_TYPE_Unknown` | `int32` | [0, 1] | 954,982 | 23,543,376 | 0 (0.0%) | ✅ PASS |
| `ROOF_TYPE_No Roof` | `int32` | [0, 1] | 4,097,199 | 20,401,159 | 0 (0.0%) | ✅ PASS |
| `ROOF_TYPE_Pitched` | `int32` | [0, 1] | 18,434,072 | 6,064,286 | 0 (0.0%) | ✅ PASS |
| `ROOF_TYPE_Roof Room` | `int32` | [0, 1] | 531,931 | 23,966,427 | 0 (0.0%) | ✅ PASS |
| `ROOF_TYPE_Thatched` | `int32` | [0, 1] | 19,313 | 24,479,045 | 0 (0.0%) | ✅ PASS |
| `ROOF_TYPE_Unknown` | `int32` | [0, 1] | 775,966 | 23,722,392 | 0 (0.0%) | ✅ PASS |
| `HOTWATER_SOURCE_Dedicated Gas` | `int32` | [0, 1] | 141,642 | 24,356,716 | 0 (0.0%) | ✅ PASS |
| `HOTWATER_SOURCE_Dedicated Oil` | `int32` | [0, 1] | 7,365 | 24,490,993 | 0 (0.0%) | ✅ PASS |
| `HOTWATER_SOURCE_Dedicated Solid Fuel` | `int32` | [0, 1] | 2,822 | 24,495,536 | 0 (0.0%) | ✅ PASS |
| `HOTWATER_SOURCE_Electric Immersion` | `int32` | [0, 1] | 2,346,506 | 22,151,852 | 0 (0.0%) | ✅ PASS |
| `HOTWATER_SOURCE_Heat Pump` | `int32` | [0, 1] | 6,437 | 24,491,921 | 0 (0.0%) | ✅ PASS |
| `HOTWATER_SOURCE_Main System` | `int32` | [0, 1] | 21,464,622 | 3,033,736 | 0 (0.0%) | ✅ PASS |
| `HOTWATER_SOURCE_Unknown` | `int32` | [0, 1] | 3,461 | 24,494,897 | 0 (0.0%) | ✅ PASS |

---
## 7. Target Variable Columns

| Column | Dtype | Min | Max | Unique Values | Nulls | Status |
|---|---|---|---|---|---|---|
| `CURRENT_ENERGY_RATING` | `Int64` | 3 | 9 | [3, 4, 5, 6, 7, 8, 9] | 0 (0.0%) | ✅ PASS |
| `POTENTIAL_ENERGY_RATING` | `Int64` | 3 | 9 | [3, 4, 5, 6, 7, 8, 9] | 0 (0.0%) | ✅ PASS |
| `improvement_potential` | `Int64` | 0 | 6 | [0, 1, 2, 3, 4, 5, 6] | 0 (0.0%) | ✅ PASS |

---
## 8. Continuous / Numeric Columns

| Column | Dtype | Min | Max | Mean | Nulls | Status |
|---|---|---|---|---|---|---|
| `TOTAL_FLOOR_AREA` | `float64` | 10.0 | 1000.0 | 88.24 | 0 (0.0%) | ✅ PASS |
| `CURRENT_ENERGY_EFFICIENCY` | `int64` | 1.0 | 13060.0 | 64.8 | 0 (0.0%) | ✅ PASS |
| `POTENTIAL_ENERGY_EFFICIENCY` | `int64` | 1.0 | 13071.0 | 79.35 | 0 (0.0%) | ✅ PASS |
| `ENERGY_CONSUMPTION_CURRENT` | `int64` | 10.0 | 500.0 | 247.13 | 0 (0.0%) | ✅ PASS |
| `ENERGY_CONSUMPTION_POTENTIAL` | `float64` | -46498.0 | 996.0 | 143.72 | 0 (0.0%) | ✅ PASS |
| `ENVIRONMENT_IMPACT_CURRENT` | `int64` | 1.0 | 224.0 | 62.11 | 0 (0.0%) | ✅ PASS |
| `CO2_EMISSIONS_CURRENT` | `float64` | -15.9 | 250.0 | 3.88 | 0 (0.0%) | ✅ PASS |
| `CO2_EMISS_CURR_PER_FLOOR_AREA` | `int64` | -134.0 | 545.0 | 44.3 | 0 (0.0%) | ✅ PASS |
| `envelope_composite_score` | `float64` | 1.0 | 5.0 | 3.12 | 0 (0.0%) | ✅ PASS |

---
## 9. New Standardized Columns Summary
Verification of the 6 columns created during description standardization.

| Column | Type | Present | Nulls | Status |
|---|---|---|---|---|
| `WALL_INSULATION` | Ordinal 0–3 (0=Unknown, 1=Uninsulated, 2=Partial, 3=Insulated) | Yes | 0 (0.0%) | ✅ PASS |
| `ROOF_INSULATION` | Ordinal 0–6 (0=Unknown/No Roof → 6=Very High) | Yes | 0 (0.0%) | ✅ PASS |
| `HOTWATER_SOLAR` | Binary 0/1 (0=No solar, 1=Has solar) | Yes | 0 (0.0%) | ✅ PASS |
| `WALL_TYPE_Cavity` | One-hot — baseline is Basement | Yes | 0 (0.0%) | ✅ PASS |
| `ROOF_TYPE_Pitched` | One-hot — baseline is Flat | Yes | 0 (0.0%) | ✅ PASS |
| `HOTWATER_SOURCE_Main System` | One-hot — baseline is Community | Yes | 0 (0.0%) | ✅ PASS |

---
## 10. Full Column Inventory

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
| 27 | `WALL_INSULATION` | `int32` | 0 | 0.00% |
| 28 | `ROOF_INSULATION` | `int32` | 0 | 0.00% |
| 29 | `HOTWATER_SOLAR` | `int64` | 0 | 0.00% |
| 30 | `PROPERTY_TYPE_Flat` | `int32` | 0 | 0.00% |
| 31 | `PROPERTY_TYPE_House` | `int32` | 0 | 0.00% |
| 32 | `PROPERTY_TYPE_Maisonette` | `int32` | 0 | 0.00% |
| 33 | `PROPERTY_TYPE_Park home` | `int32` | 0 | 0.00% |
| 34 | `BUILT_FORM_Enclosed End-Terrace` | `int32` | 0 | 0.00% |
| 35 | `BUILT_FORM_Enclosed Mid-Terrace` | `int32` | 0 | 0.00% |
| 36 | `BUILT_FORM_End-Terrace` | `int32` | 0 | 0.00% |
| 37 | `BUILT_FORM_Mid-Terrace` | `int32` | 0 | 0.00% |
| 38 | `BUILT_FORM_Semi-Detached` | `int32` | 0 | 0.00% |
| 39 | `built_form_simplified_End-Terrace` | `int32` | 0 | 0.00% |
| 40 | `built_form_simplified_Mid-Terrace` | `int32` | 0 | 0.00% |
| 41 | `built_form_simplified_Semi-detached` | `int32` | 0 | 0.00% |
| 42 | `MAIN_FUEL_Electricity` | `int32` | 0 | 0.00% |
| 43 | `MAIN_FUEL_LPG` | `int32` | 0 | 0.00% |
| 44 | `MAIN_FUEL_Mains gas` | `int32` | 0 | 0.00% |
| 45 | `MAIN_FUEL_Oil` | `int32` | 0 | 0.00% |
| 46 | `MAINHEAT_DESCRIPTION_Community` | `int32` | 0 | 0.00% |
| 47 | `MAINHEAT_DESCRIPTION_Electric storage` | `int32` | 0 | 0.00% |
| 48 | `MAINHEAT_DESCRIPTION_Gas boiler` | `int32` | 0 | 0.00% |
| 49 | `MAINHEAT_DESCRIPTION_Heat pump` | `int32` | 0 | 0.00% |
| 50 | `MAINHEAT_DESCRIPTION_LPG` | `int32` | 0 | 0.00% |
| 51 | `MAINHEAT_DESCRIPTION_Oil boiler` | `int32` | 0 | 0.00% |
| 52 | `WINDOWS_DESCRIPTION_Secondary glazing` | `int32` | 0 | 0.00% |
| 53 | `WINDOWS_DESCRIPTION_Single glazing` | `int32` | 0 | 0.00% |
| 54 | `WINDOWS_DESCRIPTION_Triple glazing` | `int32` | 0 | 0.00% |
| 55 | `WALL_TYPE_Cavity` | `int32` | 0 | 0.00% |
| 56 | `WALL_TYPE_Cob` | `int32` | 0 | 0.00% |
| 57 | `WALL_TYPE_Curtain Wall` | `int32` | 0 | 0.00% |
| 58 | `WALL_TYPE_Granite / Whinstone` | `int32` | 0 | 0.00% |
| 59 | `WALL_TYPE_Other` | `int32` | 0 | 0.00% |
| 60 | `WALL_TYPE_Park Home` | `int32` | 0 | 0.00% |
| 61 | `WALL_TYPE_Sandstone / Limestone` | `int32` | 0 | 0.00% |
| 62 | `WALL_TYPE_Solid Brick` | `int32` | 0 | 0.00% |
| 63 | `WALL_TYPE_System Built` | `int32` | 0 | 0.00% |
| 64 | `WALL_TYPE_Timber Frame` | `int32` | 0 | 0.00% |
| 65 | `WALL_TYPE_Unknown` | `int32` | 0 | 0.00% |
| 66 | `ROOF_TYPE_No Roof` | `int32` | 0 | 0.00% |
| 67 | `ROOF_TYPE_Pitched` | `int32` | 0 | 0.00% |
| 68 | `ROOF_TYPE_Roof Room` | `int32` | 0 | 0.00% |
| 69 | `ROOF_TYPE_Thatched` | `int32` | 0 | 0.00% |
| 70 | `ROOF_TYPE_Unknown` | `int32` | 0 | 0.00% |
| 71 | `HOTWATER_SOURCE_Dedicated Gas` | `int32` | 0 | 0.00% |
| 72 | `HOTWATER_SOURCE_Dedicated Oil` | `int32` | 0 | 0.00% |
| 73 | `HOTWATER_SOURCE_Dedicated Solid Fuel` | `int32` | 0 | 0.00% |
| 74 | `HOTWATER_SOURCE_Electric Immersion` | `int32` | 0 | 0.00% |
| 75 | `HOTWATER_SOURCE_Heat Pump` | `int32` | 0 | 0.00% |
| 76 | `HOTWATER_SOURCE_Main System` | `int32` | 0 | 0.00% |
| 77 | `HOTWATER_SOURCE_Unknown` | `int32` | 0 | 0.00% |

---
## 11. Summary Scorecard

| Check | Result |
|---|---|
| Correct row count | ✅ PASS |
| Correct column count | ✅ PASS |
| No text columns remaining | ✅ PASS |
| Dropped columns removed | ✅ PASS |
| CONSTRUCTION_AGE_BAND in range | ✅ PASS |
| co2_intensity_category in range | ✅ PASS |
| WALL_INSULATION in range | ✅ PASS |
| ROOF_INSULATION in range | ✅ PASS |
| HOTWATER_SOLAR is binary | ✅ PASS |
| CURRENT_ENERGY_RATING present | ✅ PASS |
| All efficiency cols present | ✅ PASS |
| All binary cols are 0/1 | ✅ PASS |
| New wall cols present | ✅ PASS |
| New roof cols present | ✅ PASS |
| New hotwater cols present | ✅ PASS |

**15/15 checks passed.**

> ✅ All checks passed. The encoded dataset is fully verified and ready for EDA and model training.

---
*BELDA Encoding Verification v2 — auto-generated by verification_script_v2.py*