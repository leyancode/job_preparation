#!/usr/bin/env python3
from __future__ import annotations

from io import StringIO

from common import SOURCE_CSV, load_runtime_results


def main() -> None:
    df = load_runtime_results()

    print(f"Source CSV: {SOURCE_CSV}")
    print(f"Shape: {df.shape[0]} rows x {df.shape[1]} columns")

    print("\nColumns:")
    for column in df.columns:
        print(f"- {column}")

    print("\nFirst 5 rows:")
    print(df.head().to_string(index=False))

    print("\nDataFrame info:")
    buffer = StringIO()
    df.info(buf=buffer)
    print(buffer.getvalue())

    print("Important unique values:")
    for column in ["scale", "status", "threads", "total_cores"]:
        values = sorted(df[column].dropna().unique())
        print(f"- {column}: {values}")

    print("\nNumeric summary for runtime_seconds:")
    print(df["runtime_seconds"].describe().to_string())


if __name__ == "__main__":
    main()
