from __future__ import annotations

from pathlib import Path

import pandas as pd


LEARNING_DIR = Path(__file__).resolve().parents[1]
ANALYSIS_DIR = LEARNING_DIR.parent
SOURCE_CSV = ANALYSIS_DIR / "size_grid_summary" / "runtime_results.csv"
OUTPUT_DIR = LEARNING_DIR / "outputs"

SCALE_ORDER = ["small", "medium-small", "medium", "large", "very-large"]
THREAD_ORDER = [1, 2, 4, 8]
TABLE_GROUP_COLUMNS = [
    "scale",
    "m",
    "n",
    "unknowns",
    "nodes",
    "ppn",
    "threads",
    "mpi_ranks",
    "total_cores",
    "unknowns_per_core",
    "matrix_type",
]


def load_runtime_results() -> pd.DataFrame:
    """Read the source CSV into a pandas DataFrame."""
    return pd.read_csv(SOURCE_CSV)


def clean_runtime_results(df: pd.DataFrame) -> pd.DataFrame:
    """Return rows suitable for the Runtime Scaling plot."""
    numeric_columns = [
        "m",
        "n",
        "unknowns",
        "nodes",
        "ppn",
        "threads",
        "mpi_ranks",
        "total_cores",
        "unknowns_per_core",
        "runtime_seconds",
    ]

    clean = df.copy()
    for column in numeric_columns:
        clean[column] = pd.to_numeric(clean[column], errors="coerce")

    clean = clean[clean["status"].eq("completed")]
    clean = clean[clean["threads"].isin(THREAD_ORDER)]
    clean = clean.dropna(subset=["scale", "unknowns", "threads", "total_cores", "runtime_seconds"])

    integer_columns = ["m", "n", "unknowns", "nodes", "ppn", "threads", "mpi_ranks", "total_cores"]
    for column in integer_columns:
        clean[column] = clean[column].astype(int)

    calculated_total_cores = clean["nodes"] * clean["ppn"] * clean["threads"]
    mismatches = clean[clean["total_cores"] != calculated_total_cores]
    if not mismatches.empty:
        raise ValueError(
            "Found rows where total_cores != nodes * ppn * threads. "
            f"Mismatch count: {len(mismatches)}"
        )

    scale_type = pd.CategoricalDtype(categories=SCALE_ORDER, ordered=True)
    thread_type = pd.CategoricalDtype(categories=THREAD_ORDER, ordered=True)
    clean["scale"] = clean["scale"].astype(scale_type)
    clean["threads"] = clean["threads"].astype(thread_type)

    return clean.sort_values(["scale", "total_cores", "threads", "runtime_seconds"]).reset_index(drop=True)


def clean_runtime_results_for_tables(df: pd.DataFrame) -> pd.DataFrame:
    """Return completed rows for report tables without filtering thread counts."""
    numeric_columns = [
        "m",
        "n",
        "unknowns",
        "nodes",
        "ppn",
        "threads",
        "mpi_ranks",
        "total_cores",
        "unknowns_per_core",
        "runtime_seconds",
    ]

    clean = df.copy()
    for column in numeric_columns:
        clean[column] = pd.to_numeric(clean[column], errors="coerce")

    clean["matrix_type"] = clean["matrix_type"].fillna("")
    clean = clean[clean["status"].eq("completed")]
    clean = clean.dropna(subset=["scale", "unknowns", "threads", "total_cores", "runtime_seconds"])

    integer_columns = ["m", "n", "unknowns", "nodes", "ppn", "threads", "mpi_ranks", "total_cores"]
    for column in integer_columns:
        clean[column] = clean[column].astype(int)

    calculated_total_cores = clean["nodes"] * clean["ppn"] * clean["threads"]
    mismatches = clean[clean["total_cores"] != calculated_total_cores]
    if not mismatches.empty:
        raise ValueError(
            "Found rows where total_cores != nodes * ppn * threads. "
            f"Mismatch count: {len(mismatches)}"
        )

    scale_type = pd.CategoricalDtype(categories=SCALE_ORDER, ordered=True)
    clean["scale"] = clean["scale"].astype(scale_type)

    return clean.sort_values(["scale", "total_cores", "nodes", "ppn", "threads"]).reset_index(drop=True)


def aggregate_runtime_tables(clean: pd.DataFrame) -> pd.DataFrame:
    """Aggregate raw runs into report-ready runtime scaling table rows."""
    aggregated = (
        clean.groupby(TABLE_GROUP_COLUMNS, observed=True, dropna=False, as_index=False)
        .agg(
            runtime_mean_s=("runtime_seconds", "mean"),
            runtime_std_s=("runtime_seconds", "std"),
            runtime_min_s=("runtime_seconds", "min"),
            runtime_max_s=("runtime_seconds", "max"),
            n_runs=("runtime_seconds", "count"),
        )
        .sort_values(["scale", "total_cores", "nodes", "ppn", "threads", "mpi_ranks"])
        .reset_index(drop=True)
    )

    baseline = aggregated[
        (aggregated["nodes"] == 1)
        & (aggregated["ppn"] == 1)
        & (aggregated["threads"] == 1)
        & (aggregated["total_cores"] == 1)
    ][["scale", "runtime_mean_s"]].rename(columns={"runtime_mean_s": "baseline_runtime_s"})

    aggregated = aggregated.merge(baseline, on="scale", how="left")
    aggregated["speedup"] = aggregated["baseline_runtime_s"] / aggregated["runtime_mean_s"]
    aggregated["efficiency"] = aggregated["speedup"] / aggregated["total_cores"]
    aggregated["cu"] = aggregated["nodes"] * aggregated["runtime_mean_s"] / 3600
    aggregated = aggregated.drop(columns=["baseline_runtime_s"])

    return aggregated


def aggregate_runtime_results(clean: pd.DataFrame) -> pd.DataFrame:
    """Aggregate repeated runs into one row per scale/core/thread configuration."""
    aggregated = (
        clean.groupby(["scale", "unknowns", "m", "n", "total_cores", "threads"], observed=True, as_index=False)
        .agg(
            median_runtime_seconds=("runtime_seconds", "median"),
            mean_runtime_seconds=("runtime_seconds", "mean"),
            min_runtime_seconds=("runtime_seconds", "min"),
            max_runtime_seconds=("runtime_seconds", "max"),
            repeat_count=("runtime_seconds", "count"),
        )
        .sort_values(["scale", "total_cores", "threads"])
        .reset_index(drop=True)
    )

    return aggregated


def ensure_output_dir() -> Path:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    return OUTPUT_DIR


def problem_size_label(unknowns: int) -> str:
    if unknowns >= 1_000_000:
        value = unknowns / 1_000_000
        return f"{value:.2f}M unknowns"
    return f"{unknowns:,} unknowns"
