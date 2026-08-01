# Bash and Slurm Script Learning Worksheet

Use this worksheet with:

- `09_csv_bash_slurm.md`
- `examples/local_size_grid_practice.sh`
- `../scripts/ex2_problem_sizes.csv`
- `../scripts/run_ex2_size_grid.sbatch`

Keep your original answers when receiving feedback.

## Section 1: Problem-Size CSV

1. What does each column in `ex2_problem_sizes.csv` mean?

Answer:

2. For the `medium` row, verify that `unknowns = m * n`.

Answer:

3. Why is a CSV table better than repeatedly editing `M` and `N` inside the
   job script?

Answer:

## Section 2: Bash Inputs

1. Explain the meaning of:

```bash
SCALES="${SCALES:-small}"
```

Answer:

2. What values do `RANKS_LIST` and `THREADS_LIST` contain after:

```bash
RANKS="1 2 4"
THREADS="1 2"
read -r -a RANKS_LIST <<< "${RANKS}"
read -r -a THREADS_LIST <<< "${THREADS}"
```

Answer:

3. Why is quoting `"${VARIABLE}"` a good Bash habit?

Answer:

## Section 3: Reading the CSV

1. Explain each part of:

```bash
while IFS=, read -r SCALE M N UNKNOWNS; do
```

Answer:

2. Why does the script skip the row where `SCALE` equals `scale`?

Answer:

3. What does `continue` do inside a loop?

Answer:

## Section 4: Rank-Thread Grid

1. What do `R`, `T`, and `P` represent?

Answer:

2. If `MAX_CORES=8` and `R=4`, what is `MAX_T`?

Answer:

3. With `MAX_CORES=8`, which of these configurations are valid:
   `(R=1,T=8)`, `(R=2,T=8)`, `(R=4,T=2)`, `(R=8,T=2)`?

Answer:

4. Why does the script skip configurations where `R * T > MAX_CORES`?

Answer:

## Section 5: WSL vs ARCHER2

1. Why can you practice the CSV and Bash loops in WSL?

Answer:

2. Why can you not properly test the `#SBATCH`, `module`, and `srun` parts in a
   normal WSL environment?

Answer:

3. Match these concepts:

```text
MPI ranks
OpenMP threads per rank
total cores
```

to:

```text
R
T
P = R * T
```

Answer:

## Section 6: Logs and Results

1. Why does the script keep one raw log per benchmark run?

Answer:

2. What does this command extract?

```bash
awk '/Norm of error/{iter=$NF} END{print iter}' logfile
```

Answer:

3. Why does the script stop if it cannot parse `Time (sec):`?

Answer:

4. Why should benchmark results include both runtime and error norm?

Answer:

## Section 7: Write It Yourself

Without copying, write a small Bash loop that:

1. reads `scale`, `m`, `n`, and `unknowns` from a CSV file
2. skips the header
3. prints only the `small` row

Answer:

Then write nested loops that print all valid `R`, `T`, and `P` combinations for
`MAX_CORES=4`.

Answer:
