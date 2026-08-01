# PETSc `ex2` Learning Worksheet Answers

Use this file only after you have attempted the worksheet yourself.

## Section 1: Problem Definition

1. `ex2` builds and solves a sparse linear system arising from a 2D finite-difference stencil problem, then checks the numerical answer against a known exact solution.
2. `Ax = b` means the matrix `A` represents the discrete operator, `x` is the unknown numerical solution, and `b` is the right-hand side vector.
3. Choosing `u` first makes correctness checking easy because we already know the exact answer and can generate a perfectly consistent `b`.
4. The exact solution is created by [resources/ex2](/home/leyan/leyan/s2795693/resources/ex2:133), and the right-hand side is built by [resources/ex2](/home/leyan/leyan/s2795693/resources/ex2:134).

## Section 2: Five-Point Stencil

1. The stencil is:

```text
4u(i,j) - u(i-1,j) - u(i+1,j) - u(i,j-1) - u(i,j+1)
```

2. The center coefficient is `4.0` because the discrete 2D Laplacian combines contributions from two spatial directions, giving one center term against four direct neighbors.
3. The direct neighbors use `-1.0` because each neighboring grid point enters the stencil with a negative coefficient.
4. The boundary checks prevent invalid neighbors outside the grid from being inserted into the matrix.
5. The diagonal entry is inserted at [resources/ex2](/home/leyan/leyan/s2795693/resources/ex2:91).

## Section 3: 2D to 1D Indexing

1. The mapping is:

```text
I = i * n + j
```

2. `i = Ii / n` recovers the row index using integer division. `j = Ii - i * n` recovers the remaining column offset inside that row.
3. The up neighbor is `Ii - n` because moving from row `i` to row `i - 1` changes the 1D index by one whole row width `n`.
4. The right neighbor is `Ii + 1` because moving from column `j` to `j + 1` changes only the local horizontal position by one.
5. For `m = 3`, `n = 4`, and `(i,j) = (1,2)`:

```text
I = 1 * 4 + 2 = 6
```

6. The neighbors are:

```text
up = 2
down = 10
left = 5
right = 7
```

7. In row `6`, the entries at columns `2`, `10`, `5`, and `7` get `-1.0`, and the entry at column `6` gets `4.0`.

## Section 4: Matrix Assembly

1. `MatCreate` creates the matrix object, and `MatSetSizes` tells PETSc the global dimensions of the linear system.
2. The code preallocates about 5 nonzeros per row because each stencil row has one diagonal and up to four neighbor entries.
3. `MatGetOwnershipRange(A, &Istart, &Iend)` tells one MPI rank which global rows it owns.
4. The loop only runs over locally owned rows so each rank assembles its part of the distributed matrix.
5. `MatAssemblyBegin` and `MatAssemblyEnd` finalize all inserted values and allow PETSc to complete any required communication and internal setup.

## Section 5: Vectors and Right-Hand Side

1. `u` is the exact solution, `b` is the right-hand side, and `x` is the computed solution.
2. `VecDuplicate` creates new vectors with a layout compatible with the existing vector, which avoids repeating size and distribution setup.
3. `VecSet(u, 1.0)` makes every entry of `u` equal to `1.0`.
4. `MatMult(A, u, b)` computes:

```text
b = A u
```

5. This is useful because the solver can later be judged against a known exact answer.

## Section 6: KSP Solver Basics

1. `KSP` is PETSc's Krylov Subspace Solver interface for iterative linear system methods.
2. `KSPSetOperators(ksp, A, A)` tells the solver to use `A` as both the system matrix and the matrix used to build the preconditioner.
3. `KSPSolve(ksp, b, x)` computes an approximate solution `x` to `Ax = b`.
4. `KSPSetFromOptions(ksp)` allows runtime command-line options to override defaults without recompiling.
5. Example runtime options:

```text
-ksp_type cg
-pc_type jacobi
-ksp_monitor
-ksp_converged_reason
```

## Section 7: Error Computation

1. After `VecAXPY(x, -1.0, u)`, the vector `x` contains:

```text
x - u
```

2. `VecNorm(x, NORM_2, &norm)` computes the Euclidean norm:

```text
||x - u||_2
```

3. We want this norm to be small because it means the computed solution is close to the known exact solution.
4. The final printed summary is at [resources/ex2](/home/leyan/leyan/s2795693/resources/ex2:193).

## Section 8: MPI Ownership and Parallel Thinking

1. A matrix ownership range is the contiguous block of global rows assigned to one MPI rank.
2. Each MPI rank can assemble only a subset of rows because PETSc distributes the matrix across processes.
3. Column indices stay global because the matrix itself is a global mathematical object, even if assembly work is split across ranks.
4. PETSc handles the distributed assembly details for us, so user code can stay focused on mathematical entries rather than explicit message passing.

## Section 9: Running and Observing

1. A tiny run is better first because it is faster, easier to inspect, and less likely to hide simple mistakes under lots of output.
2. `-ksp_converged_reason` tells you why the solver stopped.
3. `-ksp_monitor` shows how the residual changes during iterations.
4. `-log_view` shows PETSc timing and operation information that helps with performance analysis.
5. A minimal benchmark table should record:

- timestamp
- problem size
- ranks
- threads
- total cores
- runtime
- iteration count
- error norm
- log filename

## Section 10: Hand-Typing Practice

### Exercise A

A correct core loop should include:

```c
for (Ii = Istart; Ii < Iend; Ii++) {
  i = Ii / n;
  j = Ii - i * n;
  v = -1.0;

  if (i > 0) {
    J = Ii - n;
  }
  if (i < m - 1) {
    J = Ii + n;
  }
  if (j > 0) {
    J = Ii - 1;
  }
  if (j < n - 1) {
    J = Ii + 1;
  }

  v = 4.0;
}
```

### Exercise B

One clean answer is:

```c
PetscCall(VecSet(u, 1.0));
PetscCall(MatMult(A, u, b));
```

If you also mention that `u` must already exist as a PETSc vector, that is even better.

### Exercise C

The two core lines are:

```c
PetscCall(VecAXPY(x, -1.0, u));
PetscCall(VecNorm(x, NORM_2, &norm));
```

### Reflection

There is no single correct reflection answer. A good reflection identifies one exact sticking point, for example:

- mapping between 2D and 1D indices
- why `b = A u` is used
- what PETSc assembles locally vs globally
- what `KSPSetOperators` really means
