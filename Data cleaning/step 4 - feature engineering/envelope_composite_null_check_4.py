import pyarrow.parquet as pq
import pandas as pd

pf = pq.ParquetFile("epc_script2_4.parquet")
null_counts = {"WALLS_ENERGY_EFF": 0, 
               "ROOF_ENERGY_EFF": 0, 
               "WINDOWS_ENERGY_EFF": 0}
total = 0

for batch in pf.iter_batches(batch_size=500_000,
        columns=["WALLS_ENERGY_EFF", 
                 "ROOF_ENERGY_EFF", 
                 "WINDOWS_ENERGY_EFF"]):
    df = batch.to_pandas()
    total += len(df)
    for col in null_counts:
        null_counts[col] += df[col].isnull().sum()

for col, nulls in null_counts.items():
    print(f"{col:<25} nulls: {nulls:>9,}  ({nulls/total*100:.3f}%)")
print(f"\nTotal rows: {total:,}")