import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import os

# --- Configuration ---
INPUT_CSV  = r"d:\Programming\Uni code\BELDA - Bachelor Thesis\step 0 - raw data\certificates.csv"
OUTPUT_PQ  = r"d:\Programming\Uni code\BELDA - Bachelor Thesis\step 0 - raw data\certificates.parquet"
CHUNK_SIZE = 500_000

# --- Chunked Conversion ---
writer = None
total  = 0

print(f"Converting {INPUT_CSV} in chunks of {CHUNK_SIZE:,} rows ...")

for i, chunk in enumerate(pd.read_csv(
        INPUT_CSV,
        chunksize=CHUNK_SIZE,
        low_memory=False,
        encoding="latin-1",
)):
    table = pa.Table.from_pandas(chunk, preserve_index=False)

    if writer is None:
        writer = pq.ParquetWriter(OUTPUT_PQ, table.schema, compression="snappy")

    writer.write_table(table)
    total += len(chunk)
    print(f"  Chunk {i+1}: {total:,} rows written")

if writer:
    writer.close()

size_mb = os.path.getsize(OUTPUT_PQ) / 1e6
print(f"\nDone. Saved → {OUTPUT_PQ}  ({size_mb:.1f} MB)  |  Total rows: {total:,}")