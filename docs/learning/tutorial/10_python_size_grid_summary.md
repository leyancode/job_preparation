# Python Notes: Building the Size-Grid Summary

This note records the Python commands used to turn the raw size-grid CSV files into summary tables. It is written as a learning reference, so the examples are deliberately small and explicit.

The mathematical quantity used throughout the summary is:

```text
N = m * n
C = nodes * ppn * threads
unknowns per core = N / C
```

For PETSc `ex2`, `N` is the number of unknowns in the 2D finite-difference grid. The supervisor's suggested validity criterion was:

```text
10,000 < N/C < 1,000,000
```

## 1. Inspect All Raw CSV Files

Local WSL command:

```bash
python3 - <<'PY'
import csv
import glob
from collections import Counter

rows = []

# Find every CSV file directly under analysis/data/size_grid/logs.
for path in sorted(glob.glob("analysis/data/size_grid/logs/*.csv")):
    with open(path, newline="") as f:
        for row in csv.DictReader(f):
            row["_source_file"] = path
            rows.append(row)

print("number of rows:", len(rows))
print("job ids:", sorted(set(row["jobid"] for row in rows)))
print("scales:", Counter(row["scale"] for row in rows))
print("total core counts:", sorted({int(row["total_cores"]) for row in rows}))
PY
```

What this teaches:

- `glob.glob("analysis/data/size_grid/logs/*.csv")` finds matching files.
- `csv.DictReader(f)` reads each CSV row as a dictionary.
- `Counter(...)` counts how many rows belong to each problem size.
- `set(...)` removes duplicates.

## 2. Read Problem Sizes

Local WSL command:

```bash
python3 - <<'PY'
import csv

problem_sizes = []

with open("scripts/ex2_problem_sizes.csv", newline="") as f:
    for row in csv.DictReader(f):
        row["m"] = int(row["m"])
        row["n"] = int(row["n"])
        row["unknowns"] = int(row["unknowns"])
        problem_sizes.append(row)

for row in problem_sizes:
    print(row["scale"], row["m"], row["n"], row["unknowns"])
PY
```

Important idea:

CSV fields are read as strings. Convert numeric fields with `int(...)` or `float(...)` before doing arithmetic.

## 3. Compute `N/C` and Classify Each Cell

Local WSL command:

```bash
python3 - <<'PY'
def classify(unknowns_per_core):
    if unknowns_per_core <= 10_000:
        return "too_small_per_core"
    if unknowns_per_core >= 1_000_000:
        return "too_large_per_core"
    return "valid"

unknowns = 1_000_000

for total_cores in [1, 2, 4, 8, 16, 32, 64, 128]:
    unknowns_per_core = unknowns / total_cores
    print(total_cores, unknowns_per_core, classify(unknowns_per_core))
PY
```

For the 1M case, this shows why `C=128` is too small per core:

```text
1,000,000 / 128 = 7,812.5
```

That is below `10,000`.

## 4. Produce the Validity Table

This is the core idea behind `analysis/size_grid_summary/validity_table.md`.

Local WSL command:

```bash
python3 - <<'PY'
import csv

def classify(unknowns_per_core):
    if unknowns_per_core <= 10_000:
        return "too_small_per_core"
    if unknowns_per_core >= 1_000_000:
        return "too_large_per_core"
    return "valid"

def fmt_number(x):
    return f"{x:,.0f}"

problem_sizes = []
with open("scripts/ex2_problem_sizes.csv", newline="") as f:
    for row in csv.DictReader(f):
        row["unknowns"] = int(row["unknowns"])
        problem_sizes.append(row)

total_core_counts = [1, 2, 4, 8, 16, 32, 64, 128]

print("| scale | unknowns | " + " | ".join(f"C={c}" for c in total_core_counts) + " |")
print("| --- | ---: | " + " | ".join("---:" for _ in total_core_counts) + " |")

for row in problem_sizes:
    cells = []
    for c in total_core_counts:
        npc = row["unknowns"] / c
        cells.append(f"{fmt_number(npc)} {classify(npc)}")

    print(f"| {row['scale']} | {fmt_number(row['unknowns'])} | " + " | ".join(cells) + " |")
PY
```

This prints Markdown table text to the terminal. To write it to a file in a normal script, use `open(..., "w")` and `f.write(...)`.

## 5. Build Clean Runtime Rows

This is the main pattern used for `runtime_results.csv`.

Local WSL command:

```bash
python3 - <<'PY'
import csv
import glob

clean_rows = []

for path in sorted(glob.glob("analysis/data/size_grid/logs/*.csv")):
    with open(path, newline="") as f:
        for row in csv.DictReader(f):
            nodes = int(row["nodes"])
            mpi_ranks = int(row["ranks"])
            threads = int(row["threads"])
            total_cores = int(row["total_cores"])
            unknowns = int(row["unknowns"])

            # In the current runs, nodes=1, so ppn is the same as mpi_ranks.
            ppn = mpi_ranks // nodes

            clean_rows.append({
                "scale": row["scale"],
                "m": row["m"],
                "n": row["n"],
                "unknowns": unknowns,
                "nodes": nodes,
                "ppn": ppn,
                "threads": threads,
                "mpi_ranks": mpi_ranks,
                "total_cores": total_cores,
                "unknowns_per_core": unknowns / total_cores,
                "matrix_type": "",
                "runtime_seconds": float(row["time_sec"]),
                "memory_mb": "",
                "status": "completed",
                "source_file": path,
            })

print("clean rows:", len(clean_rows))
print(clean_rows[0])
PY
```

Fields left blank:

- `matrix_type`: not recorded in the available CSV files.
- `memory_mb`: not recorded in the available CSV files.

## 6. Sort Rows in a Stable Order

The summary uses this order:

```text
scale -> total cores -> threads -> matrix type
```

Local WSL command:

```bash
python3 - <<'PY'
scale_order = ["small", "medium-small", "medium", "large", "very-large"]
scale_rank = {scale: i for i, scale in enumerate(scale_order)}

example_rows = [
    {"scale": "medium", "total_cores": 64, "threads": 1, "matrix_type": ""},
    {"scale": "small", "total_cores": 128, "threads": 1, "matrix_type": ""},
    {"scale": "small", "total_cores": 64, "threads": 2, "matrix_type": ""},
]

example_rows.sort(
    key=lambda row: (
        scale_rank.get(row["scale"], 99),
        row["total_cores"],
        row["threads"],
        row["matrix_type"],
    )
)

for row in example_rows:
    print(row)
PY
```

The `key=lambda row: (...)` expression tells Python how to compare rows.

## 7. Write a New CSV File

Local WSL command:

```bash
python3 - <<'PY'
import csv

rows = [
    {
        "scale": "small",
        "m": 1000,
        "n": 1000,
        "unknowns": 1000000,
        "nodes": 1,
        "ppn": 128,
        "threads": 1,
        "mpi_ranks": 128,
        "total_cores": 128,
        "unknowns_per_core": 7812.5,
        "matrix_type": "",
        "runtime_seconds": 3.844,
        "memory_mb": "",
        "status": "completed",
        "source_file": "analysis/data/size_grid/logs/example.csv",
    }
]

fields = [
    "scale", "m", "n", "unknowns", "nodes", "ppn", "threads",
    "mpi_ranks", "total_cores", "unknowns_per_core", "matrix_type",
    "runtime_seconds", "memory_mb", "status", "source_file",
]

with open("/tmp/runtime_results_example.csv", "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=fields)
    writer.writeheader()
    writer.writerows(rows)

print("wrote /tmp/runtime_results_example.csv")
PY
```

This example writes to `/tmp`, so it is safe for practice.

## 8. Estimate a 128M Runtime

This is the simple extrapolation discussed with the supervisor.

Local WSL command:

```bash
python3 - <<'PY'
base_unknowns = 40_960_000
target_unknowns = 128_000_000
scale_factor = target_unknowns / base_unknowns

slow_40m_seconds = 15_420
fast_40m_seconds = 846.9

slow_estimate = slow_40m_seconds * scale_factor
fast_estimate = fast_40m_seconds * scale_factor

print("scale factor:", scale_factor)
print("slow estimate seconds:", slow_estimate)
print("slow estimate hours:", slow_estimate / 3600)
print("fast estimate seconds:", fast_estimate)
print("fast estimate minutes:", fast_estimate / 60)
PY
```

Interpretation:

- The slow estimate uses the `C=1` 40.96M result.
- The fast estimate uses the fastest `C=128` 40.96M result.
- This is only a rough estimate. It assumes runtime grows linearly with `N`, which may be optimistic or pessimistic depending on solver behaviour, memory effects, and communication cost.

## 9. ARCHER2 Note

The Python commands above are local WSL analysis commands. They inspect existing CSV files and write summaries.

They are not Slurm submission commands. On ARCHER2, the benchmark itself is launched with `sbatch`, for example:

```bash
sbatch scripts/run_ex2_size_grid.sbatch
```

Use the Python analysis only after the raw CSV results have been copied back into the repository under `analysis/data/size_grid/logs/`.
