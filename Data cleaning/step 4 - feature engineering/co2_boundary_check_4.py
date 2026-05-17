import pyarrow.parquet as pq
import pandas as pd

pf = pq.ParquetFile("epc_script3_4.parquet")
negative = []

for batch in pf.iter_batches(batch_size=500_000,
        columns=["CO2_EMISS_CURR_PER_FLOOR_AREA",
                 "MAINHEAT_DESCRIPTION",
                 "MAIN_FUEL",
                 "CURRENT_ENERGY_RATING"]):
    df = batch.to_pandas()
    negative.append(df[df["CO2_EMISS_CURR_PER_FLOOR_AREA"] < 0])

negative = pd.concat(negative)

print(f"Total negative CO2 rows: {len(negative):,}")
print(f"\nValue distribution:")
print(negative["CO2_EMISS_CURR_PER_FLOOR_AREA"].describe())
print(f"\nHeating system breakdown:")
print(negative["MAINHEAT_DESCRIPTION"].value_counts())
print(f"\nFuel breakdown:")
print(negative["MAIN_FUEL"].value_counts())
print(f"\nEnergy rating breakdown:")
print(negative["CURRENT_ENERGY_RATING"].value_counts().sort_index())