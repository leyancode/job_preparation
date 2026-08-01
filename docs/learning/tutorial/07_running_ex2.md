# 07 Running `ex2`

## Small Local Runs First

When learning, start small. You want:

- quick feedback
- readable output
- fewer moving parts

Recommended first run:

```bash
./ex2 -m 8 -n 7 -ksp_converged_reason
```

## Useful Runtime Options

Try these one at a time:

```bash
./ex2 -m 8 -n 7 -ksp_converged_reason
./ex2 -m 8 -n 7 -ksp_monitor
./ex2 -m 8 -n 7 -log_view
./ex2 -m 8 -n 7 -view_exact_sol
```

What they help you learn:

- `-ksp_converged_reason`: why the solver stopped
- `-ksp_monitor`: how the residual changes each iteration
- `-log_view`: where PETSc spends time
- `-view_exact_sol`: what the known exact solution vector looks like

## Small MPI Test

Once the serial-style run works, try:

```bash
mpirun -n 2 ./ex2 -m 8 -n 7 -ksp_converged_reason
```

Then compare:

- the final error norm
- the iteration count
- whether output formatting changes with multiple ranks

For a correct run, the mathematical answer should still be consistent.
