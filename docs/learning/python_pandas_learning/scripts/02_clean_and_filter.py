#!/usr/bin/env python3
from __future__ import annotations

from common import THREAD_ORDER, clean_runtime_results, load_runtime_results


def main() -> None:
    raw = load_runtime_results()
    clean = clean_runtime_results(raw)

    print(f"Raw rows: {len(raw)}")
    print(f"Rows after status/thread/runtime filtering: {len(clean)}")
    print(f"Thread values kept: {list(THREAD_ORDER)}")

    print("\nRows by scale:")
    print(clean["scale"].value_counts(sort=False).to_string())

    print("\nRows by thread count:")
    print(clean["threads"].value_counts(sort=False).to_string())

    print("\nTotal core values:")
    print(sorted(clean["total_cores"].unique()))

    print("\nCheck total_cores formula:")
    calculated = clean["nodes"] * clean["ppn"] * clean["threads"].astype(int)
    print((clean["total_cores"] == calculated).value_counts().to_string())

    print("\nClean sample:")
    columns = ["scale", "unknowns", "nodes", "ppn", "threads", "total_cores", "runtime_seconds"]
    print(clean[columns].head(12).to_string(index=False))


if __name__ == "__main__":
    main()
