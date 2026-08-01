# 09 CSV, Bash, and Slurm Size-Grid Scripts

## Learning Goal

The goal is to understand enough Bash to write and explain
`scripts/run_ex2_size_grid.sbatch` yourself.

Do not begin by memorizing the entire Slurm script. Learn it as four smaller
layers:

1. describe benchmark inputs in a CSV file
2. read and filter those inputs with Bash
3. generate valid rank-thread combinations
4. replace a local command with an `srun` command on ARCHER2

The first three layers can be practiced safely in WSL. Slurm directives,
modules, and `srun` must be tested on ARCHER2.

## The Two Important Input Files

The problem-size table is:

```text
scripts/ex2_problem_sizes.csv
```

Each row describes one named problem:

```text
scale,m,n,unknowns
small,1000,1000,1000000
```

For `small`:

- `scale` is a human-readable name
- `m` and `n` are the two grid dimensions passed to `ex2`
- `unknowns` should equal `m * n`

The production job script is:

```text
scripts/run_ex2_size_grid.sbatch
```

It combines every selected problem size with valid MPI-rank and OpenMP-thread
configurations, runs `ex2`, parses the log, and writes one results CSV.

## Layer 1: Read a CSV Row

This Bash pattern reads four comma-separated fields:

```bash
while IFS=, read -r scale m n unknowns; do
  printf '%s: %s x %s = %s unknowns\n' \
    "${scale}" "${m}" "${n}" "${unknowns}"
done < scripts/ex2_problem_sizes.csv
```

Important pieces:

- `IFS=,` tells `read` that commas separate fields
- `read -r` prevents backslash interpretation
- the four variable names receive the four columns
- `< file.csv` sends the file into the loop

The production script skips the header with:

```bash
[[ "${SCALE}" == "scale" ]] && continue
```

`continue` skips the rest of the current loop iteration.

## Layer 2: Defaults That Users Can Override

This pattern gives a variable a default while allowing an environment override:

```bash
SCALES="${SCALES:-small}"
REPEAT="${REPEAT:-1}"
```

For example:

```bash
SCALES="small medium" REPEAT=3 bash tutorial/examples/local_size_grid_practice.sh
```

The values before `bash` become environment variables for that command.

This is the local equivalent of submitting an overridden Slurm job:

```bash
SCALES="small medium" REPEAT=3 sbatch scripts/run_ex2_size_grid.sbatch
```

## Layer 3: Build a Valid Rank-Thread Grid

Suppose one machine has at most eight cores:

```bash
MAX_CORES=8
RANKS_LIST=(1 2 4 8)
THREADS_LIST=(1 2 4 8)
```

For each rank count `R`, the largest valid thread count is:

```bash
MAX_T=$(( MAX_CORES / R ))
```

Then invalid configurations are skipped:

```bash
(( T > MAX_T )) && continue
```

The total requested cores are:

```bash
P=$(( R * T ))
```

For example, `R=2` and `T=4` gives `P=8`.

## Layer 4: Local Command vs Slurm Command

In WSL, a small MPI command may look like:

```bash
export OMP_NUM_THREADS=2
mpirun -n 2 /path/to/ex2 -m 8 -n 8 -ksp_converged_reason -log_view
```

On ARCHER2, Slurm launches the same conceptual configuration:

```bash
export OMP_NUM_THREADS=2
srun --nodes=1 --ntasks=2 --cpus-per-task=2 --exact \
  /path/to/ex2 -m 1000 -n 1000 -ksp_converged_reason -log_view
```

The key mapping is:

| Concept | Bash variable | Slurm option |
| --- | --- | --- |
| MPI ranks | `R` | `--ntasks="${R}"` |
| threads per rank | `T` | `--cpus-per-task="${T}"` |
| OpenMP threads | `T` | `OMP_NUM_THREADS="${T}"` |
| total cores | `P=R*T` | validated by the script |

## What the `#SBATCH` Lines Do

Lines beginning with `#SBATCH` are read by `sbatch`, not by ordinary Bash:

```bash
#SBATCH --nodes=1
#SBATCH --time=06:00:00
#SBATCH --output=%x.%j.out
```

They request resources and define job-level output files.

When the same file is run with `bash` in WSL, those lines are only comments.
However, the script will still fail later because WSL normally does not provide
ARCHER2 commands such as `module` and `srun`.

## Why the Production Script Uses `set -euo pipefail`

```bash
set -euo pipefail
```

This enables useful safety checks:

- `-e`: stop when a command fails
- `-u`: stop when an unset variable is used
- `pipefail`: fail a pipeline if an earlier command fails

These checks help prevent a failed benchmark from quietly producing misleading
result rows.

## Why Logs and Result CSVs Are Separate

The log contains the complete PETSc output for one run. The result CSV contains
only the fields needed for comparison.

The production script extracts values with `awk`, for example:

```bash
ITER="$(awk '/Norm of error/{iter=$NF} END{print iter}' "${LOG}")"
```

This means:

- find lines containing `Norm of error`
- save the final field as `iter`
- print the last saved value after reading the file

Keeping the raw log makes it possible to investigate parsing mistakes or failed
runs later.

## WSL Practice Sequence

Run all commands from the repository root:

```bash
cd ~/leyan/jobSkill/petsc-benchmark-suite/s2795693
```

### Exercise 1: Syntax Check

```bash
bash -n tutorial/examples/local_size_grid_practice.sh
```

No output means the Bash syntax is valid.

### Exercise 2: Generate a Tiny Plan

```bash
bash tutorial/examples/local_size_grid_practice.sh
```

The script defaults to dry-run mode. It prints commands and writes a small plan
CSV without launching PETSc.

### Exercise 3: Override Inputs

```bash
SCALES="small medium" \
RANKS="1 2" \
THREADS="1 2 4" \
MAX_CORES=4 \
REPEAT=2 \
bash tutorial/examples/local_size_grid_practice.sh
```

Before running it, predict which rank-thread combinations will be skipped.

### Exercise 4: Trace Bash Execution

```bash
bash -x tutorial/examples/local_size_grid_practice.sh
```

`-x` prints commands after variable expansion. Use it when a loop or condition
does not behave as expected.

### Exercise 5: Optional Real Local Run

Only after a small `ex2` executable works locally:

```bash
DRY_RUN=0 \
EX2_BIN=/absolute/path/to/ex2 \
SCALES="tiny" \
SIZE_TABLE=tutorial/examples/local_problem_sizes.csv \
RANKS="1 2" \
THREADS="1" \
MAX_CORES=2 \
bash tutorial/examples/local_size_grid_practice.sh
```

Use tiny local sizes for learning. Do not run the production million-unknown
table accidentally on WSL.

## Reading the Production Script in Order

When studying `run_ex2_size_grid.sbatch`, annotate it in this order:

1. resource request: `#SBATCH` lines
2. failure behavior: `set -euo pipefail`
3. ARCHER2 environment: `module`, paths, PETSc variables
4. user-controlled inputs: `SCALES`, `REPEAT`, `RANKS`, `THREADS`
5. output locations and CSV header
6. problem-size CSV loop
7. rank-thread loops and core-limit checks
8. `srun` launch
9. `awk` parsing and result-row output
10. final validation and completion message

If you can explain each block in one sentence, you are ready to recreate a
smaller version without copying.
