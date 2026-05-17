import time
import pyarrow.parquet as pq
import pandas as pd

INPUT      = "epc_script1_4.parquet"
BATCH_SIZE = 500_000

parquet_file = pq.ParquetFile(INPUT)
results = {}
total_rows = 0

for batch in parquet_file.iter_batches(
        batch_size=BATCH_SIZE, 
        columns=["PROPERTY_TYPE", "BUILT_FORM"]):
    df = batch.to_pandas()
    total_rows += len(df)
    counts = df.groupby(["PROPERTY_TYPE", "BUILT_FORM"]).size()
    for (prop, built), count in counts.items():
        key = (prop, built)
        results[key] = results.get(key, 0) + count

summary = pd.DataFrame([
    {"PROPERTY_TYPE": k[0], "BUILT_FORM": k[1], "count": v}
    for k, v in results.items()
])
summary["pct"] = (summary["count"] / total_rows * 100).round(3)
summary = summary.sort_values(["PROPERTY_TYPE", "count"], ascending=[True, False])
print(summary.to_string(index=False))