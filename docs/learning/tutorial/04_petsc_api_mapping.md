# 04 PETSc API Mapping

## Core PETSc Objects in `ex2`

The example introduces four main PETSc object types:

- `Mat`: sparse matrix
- `Vec`: vector
- `KSP`: Krylov linear solver
- PETSc runtime options and initialization helpers

## Matrix Construction Flow

The matrix part of the code follows this pattern:

1. `MatCreate(...)`
2. `MatSetSizes(...)`
3. `MatSetFromOptions(...)`
4. preallocation calls
5. `MatSetValues(...)` in a loop
6. `MatAssemblyBegin(...)`
7. `MatAssemblyEnd(...)`

Conceptually:

- create the object
- define global dimensions
- let PETSc choose a matrix type if needed
- reserve storage
- insert stencil values
- finalize assembly

## Vector Construction Flow

The vector part is:

1. `VecCreate(...)`
2. `VecSetSizes(...)`
3. `VecSetFromOptions(...)`
4. `VecDuplicate(...)`

This creates:

- `u`: exact solution
- `b`: right-hand side
- `x`: numerical solution

## Right-Hand Side Construction

The example uses:

```c
VecSet(u, 1.0);
MatMult(A, u, b);
```

Meaning:

- first set every entry of `u` to `1.0`
- then compute `b = A * u`

This gives a consistent test problem with a known exact solution.

## Solver Flow

The solver part is:

1. `KSPCreate(...)`
2. `KSPSetOperators(ksp, A, A)`
3. `KSPSetTolerances(...)`
4. `KSPSetFromOptions(...)`
5. `KSPSolve(ksp, b, x)`

Conceptually:

- create a solver context
- tell it which matrix defines the system
- set defaults
- allow command-line overrides
- solve the system

## Error Check Flow

The example checks the solution with:

```c
VecAXPY(x, -1.0, u);
VecNorm(x, NORM_2, &norm);
```

This means:

1. replace `x` by `x - u`
2. compute the 2-norm of that error vector

So the final printed `norm` is:

```text
||x - u||_2
```
