# 06 MPI Partitioning

## Why MPI Matters Here

Even though `ex2` looks small in source code, PETSc is built for distributed-memory computation. The matrix rows and vector entries can be split across MPI ranks.

## Ownership Range

The line

```c
MatGetOwnershipRange(A, &Istart, &Iend);
```

tells each MPI rank which global rows it owns.

Then each process only loops over:

```c
for (Ii = Istart; Ii < Iend; Ii++)
```

So each rank builds only its local chunk of the global matrix.

## Local Work, Global Indices

Even though each rank only owns some rows, the inserted column indices are still global:

```c
MatSetValues(A, 1, &Ii, 1, &J, &v, ADD_VALUES);
```

This is important:

- `Ii` is a global row index
- `J` is a global column index
- PETSc handles communication during assembly

## Why This Is Good for Beginners

You can start by thinking:

- "I only assemble the rows I own."
- "I still name matrix entries using global coordinates."
- "PETSc takes care of the distributed assembly details."

That lets you learn distributed sparse assembly without writing explicit send and receive calls first.
