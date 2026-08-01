# 05 KSP Solver Basics

## What KSP Means

In PETSc, `KSP` is the interface for Krylov Subspace Methods, which are iterative solvers for linear systems such as:

```text
Ax = b
```

Common examples include:

- CG
- GMRES
- BiCGStab

## Why `ex2` Uses KSP

The matrix from a 2D five-point stencil is sparse and structured. Iterative solvers are a natural fit because:

- they avoid dense factorization
- they scale better for larger sparse systems
- they work well with PETSc preconditioners

## Operator vs Preconditioner Matrix

The example uses:

```c
KSPSetOperators(ksp, A, A);
```

This means:

- the matrix defining the linear system is `A`
- the matrix used to build the preconditioner is also `A`

Using the same matrix for both is common in introductory examples.

## Tolerances

The example sets a relative tolerance with:

```c
KSPSetTolerances(ksp, 1.e-2 / ((m + 1) * (n + 1)), 1.e-50, PETSC_CURRENT, PETSC_CURRENT);
```

The important beginner idea is:

- the solver stops when the residual is judged small enough
- PETSc allows absolute tolerance, relative tolerance, and iteration limits
- these defaults can be overridden from the command line

## Runtime Solver Selection

One of PETSc's most important ideas is that many solver details can be changed at runtime:

```bash
-ksp_type cg
-pc_type jacobi
-ksp_monitor
-ksp_converged_reason
```

This means you often do not need to recompile the code just to compare solver or preconditioner choices.
