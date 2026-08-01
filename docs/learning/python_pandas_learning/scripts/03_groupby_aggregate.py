#!/usr/bin/env python3
from __future__ import annotations

from common import aggregate_runtime_results, clean_runtime_results, ensure_output_dir, load_runtime_results


def main() -> None:
    raw = load_runtime_results()
    clean = clean_runtime_results(raw)
    aggregated = aggregate_runtime_results(clean)

    output_dir = ensure_output_dir()
    output_path = output_dir / "runtime_scaling_aggregated_pandas.csv"
    aggregated.to_csv(output_path, index=False)

    print(f"Clean rows: {len(clean)}")
    print(f"Aggregated rows: {len(aggregated)}")
    print(f"Wrote: {output_path}")

    print("\nAggregated sample:")
    print(aggregated.head(16).to_string(index=False))

    print("\nRepeat count summary:")
    print(aggregated["repeat_count"].describe().to_string())


if __name__ == "__main__":
    main()
