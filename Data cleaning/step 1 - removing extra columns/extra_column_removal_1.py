"""
BELDA — Step 1: Column Filtering
=================================
Reads epc_raw.parquet, keeps only the 29 CORE fields defined in
BELDA_Core_Fields_Mapping.pdf, and writes epc_core.parquet.

Uses batch streaming so the full dataset is never loaded into RAM —
processes 500,000 rows at a time regardless of total file size.

Usage
-----
    python step1_filter_columns.py

    # Optional overrides via CLI:
    python step1_filter_columns.py --input /path/to/epc_raw.parquet \
                                   --output /path/to/epc_core.parquet
"""

import argparse
import time
import pyarrow as pa
import pyarrow.parquet as pq

# ── Core fields from BELDA_Core_Fields_Mapping.pdf ────────────────────────────
CORE_FIELDS = [
    # Building Identity & Typology
    "PROPERTY_TYPE",
    "BUILT_FORM",
    "CONSTRUCTION_AGE_BAND",
    "TOTAL_FLOOR_AREA",
    # Thermal Envelope
    "WALLS_DESCRIPTION",
    "WALLS_ENERGY_EFF",
    "WALLS_ENV_EFF",
    "ROOF_DESCRIPTION",
    "ROOF_ENERGY_EFF",
    "ROOF_ENV_EFF",
    "WINDOWS_DESCRIPTION",
    "WINDOWS_ENERGY_EFF",
    "WINDOWS_ENV_EFF",
    # Heating System & Energy Carrier
    "MAINHEAT_DESCRIPTION",
    "MAINHEAT_ENERGY_EFF",
    "MAINHEAT_ENV_EFF",
    "MAIN_FUEL",
    "HOTWATER_DESCRIPTION",
    "HOT_WATER_ENERGY_EFF",
    "HOT_WATER_ENV_EFF",
    # Energy Performance Outcomes (target variables)
    "CURRENT_ENERGY_RATING",
    "POTENTIAL_ENERGY_RATING",
    "CURRENT_ENERGY_EFFICIENCY",
    "POTENTIAL_ENERGY_EFFICIENCY",
    "ENERGY_CONSUMPTION_CURRENT",
    "ENERGY_CONSUMPTION_POTENTIAL",
    "ENVIRONMENT_IMPACT_CURRENT",
    "CO2_EMISSIONS_CURRENT",
    "CO2_EMISS_CURR_PER_FLOOR_AREA",
]

BATCH_SIZE = 500_000   # rows per batch — tune down to 250_000 if still OOM


def parse_args():
    parser = argparse.ArgumentParser(description="BELDA Step 1 — Column Filtering")
    parser.add_argument(
        "--input",
        default="epc_raw.parquet",
        help="Path to the raw EPC parquet file (default: epc_raw.parquet)",
    )
    parser.add_argument(
        "--output",
        default="epc_core.parquet",
        help="Path for the filtered output (default: epc_core.parquet)",
    )
    return parser.parse_args()


def validate_columns(available_cols, required_cols):
    """Raise a clear error if any required column is missing from the file."""
    missing = [c for c in required_cols if c not in available_cols]
    if missing:
        raise ValueError(
            "\n[ERROR] The following CORE fields were not found in the parquet file:\n"
            + "\n".join(f"  - {c}" for c in missing)
            + "\n\nCheck the column names in your raw file with:"
            + "\n  import pyarrow.parquet as pq"
            + "\n  print(pq.read_schema('epc_raw.parquet').names)"
        )


def main():
    args = parse_args()

    print("=" * 60)
    print("  BELDA - Step 1: Column Filtering")
    print("=" * 60)
    print(f"\n  Input  : {args.input}")
    print(f"  Output : {args.output}")
    print(f"  Keeping: {len(CORE_FIELDS)} core fields")
    print(f"  Mode   : Batch streaming ({BATCH_SIZE:,} rows/batch)\n")

    # Step 1: Read schema only - zero rows loaded
    print("[1/3] Reading parquet schema...")
    schema = pq.read_schema(args.input)
    available_cols = schema.names
    print(f"      Columns in raw file : {len(available_cols)}")
    print(f"      Columns to drop     : {len(available_cols) - len(CORE_FIELDS)}")

    # Step 2: Validate all core fields exist
    print("\n[2/3] Validating core field availability...")
    validate_columns(available_cols, CORE_FIELDS)
    print("      All 29 core fields found")

    # Step 3: Stream batches and write output
    print(f"\n[3/3] Streaming to '{args.output}'...")
    print("      (progress updates every batch)\n")

    parquet_file = pq.ParquetFile(args.input)
    writer = None
    total_rows = 0
    t0 = time.time()

    for i, batch in enumerate(parquet_file.iter_batches(
            batch_size=BATCH_SIZE, columns=CORE_FIELDS)):

        table = pa.Table.from_batches([batch])

        if writer is None:
            writer = pq.ParquetWriter(
                args.output, table.schema, compression="snappy"
            )

        writer.write_table(table)
        total_rows += len(table)
        elapsed_so_far = time.time() - t0
        print(f"      Batch {i+1:>3} | {total_rows:>12,} rows | {elapsed_so_far:.0f}s elapsed")

    if writer:
        writer.close()

    total_time = time.time() - t0

    print("\n" + "=" * 60)
    print("  SUCCESS - Step 1 Complete")
    print("=" * 60)
    print(f"  Rows retained  : {total_rows:,}")
    print(f"  Cols retained  : {len(CORE_FIELDS)} / {len(available_cols)}")
    print(f"  Cols dropped   : {len(available_cols) - len(CORE_FIELDS)}")
    print(f"  Output file    : {args.output}")
    print(f"  Total time     : {total_time:.1f}s")
    print("\n  -> Ready for Step 2: Missing Value Analysis\n")


if __name__ == "__main__":
    main()