# 08 Benchmarking Basics

## Learning Before Benchmarking

Before running large parameter sweeps, make sure you can explain:

- what `m` and `n` mean
- what one MPI rank does
- what `OMP_NUM_THREADS` changes
- what output fields you want to capture

If those are still unclear, benchmarking will produce data faster than understanding.

## Benchmark Variables

The most common variables in this repository are:

- number of MPI ranks
- number of OpenMP threads per rank
- total cores
- problem size
- repeat count

## Why Repeat Runs

Single timing runs can be noisy. Repeating runs helps you see:

- whether timings are stable
- whether outliers exist
- whether one configuration is consistently better

## What to Record

A minimal benchmark record should include:

- timestamp
- problem size
- ranks
- threads
- total cores
- runtime
- iteration count
- error norm
- log filename

That matches the general shape of the existing Slurm scripts in `scripts/`.

## Good Beginner Benchmark Habit

Use this progression:

1. Verify a tiny local run.
2. Verify a small MPI run.
3. Verify one small Slurm run.
4. Only then automate rank-thread sweeps.

This prevents you from collecting many broken logs caused by one simple environment mistake.
