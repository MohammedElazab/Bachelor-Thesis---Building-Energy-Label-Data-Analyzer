import pyarrow.parquet as pq
import pandas as pd
import numpy as np

pf = pq.ParquetFile("epc_script3_4.parquet")
values = []

for batch in pf.iter_batches(batch_size=500_000,
        columns=["CO2_EMISS_CURR_PER_FLOOR_AREA"]):
    df = batch.to_pandas()
    values.extend(df["CO2_EMISS_CURR_PER_FLOOR_AREA"].dropna().tolist())

s = pd.Series(values)
print(f"Count  : {len(s):>12,}")
print(f"Min    : {s.min():>12.2f} kg/m²/yr")
print(f"Max    : {s.max():>12.2f} kg/m²/yr")
print(f"Mean   : {s.mean():>12.2f} kg/m²/yr")
print(f"Median : {s.median():>12.2f} kg/m²/yr")
print(f"Std    : {s.std():>12.2f}")
print(f"\nPercentiles:")
for p in [5, 10, 25, 50, 75, 90, 95, 99]:
    print(f"  p{p:<3} : {np.percentile(s, p):>8.2f} kg/m²/yr")