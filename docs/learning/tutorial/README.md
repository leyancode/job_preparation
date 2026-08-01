# PETSc `ex2` Tutorial Path

This directory is a step-by-step learning track for understanding PETSc's `ex2` example from first principles.

The goal is not to replace the original reference source in `resources/`, but to make it easier to study:

- the mathematical model
- the five-point stencil
- the indexing scheme
- the PETSc matrix, vector, and solver API flow
- the difference between local learning runs and HPC benchmark runs

## Suggested Reading Order

1. `01_problem_definition.md`
2. `02_five_point_stencil.md`
3. `03_matrix_indexing.md`
4. `04_petsc_api_mapping.md`
5. `05_ksp_solver_basics.md`
6. `06_mpi_partitioning.md`
7. `07_running_ex2.md`
8. `08_benchmarking_basics.md`
9. `09_csv_bash_slurm.md`

For hands-on script-writing practice, use:

- `SCRIPT_WORKSHEET.md`: questions to answer in your own words
- `examples/local_size_grid_practice.sh`: a WSL-safe version of the size-grid control flow

## Source Files in This Tutorial

- `examples/ex2_annotated.c`: keeps the same overall logic as the reference example, but adds beginner-oriented English comments
- `examples/minimal_ex2.c`: strips the example down to the core flow needed to understand `Ax = b`, `KSPSolve`, and error checking

## Important Boundary

The original reference code is still kept separately in:

- [`resources/ex2`](/home/leyan/leyan/s2795693/resources/ex2:1)

This tutorial does not overwrite or replace it.
