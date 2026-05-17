import pandas as pd

df = pd.read_parquet("epc_script1_4.parquet")

negative = df[df["improvement_potential"] < 0][[
    "CURRENT_ENERGY_RATING",
    "POTENTIAL_ENERGY_RATING", 
    "improvement_potential",
    "label_gap_readable",
    "PROPERTY_TYPE",
    "CONSTRUCTION_AGE_BAND",
    "MAINHEAT_DESCRIPTION"
]]

print(negative.to_string())
print(f"\nTotal: {len(negative)} rows")