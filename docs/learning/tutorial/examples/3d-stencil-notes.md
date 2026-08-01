# 3D Stencil Fix Notes

This note records issues found in `3d-stencil.c`, based on comparison with
`ex2_annotated.c`.

## Problems To Fix

1. `PetscInitialize` uses the wrong argument name.

   In `main`, the parameter is named `argv`, but `PetscInitialize` currently
   passes `args`. This will cause a compile error.

   Expected shape:

   ```c
   PetscCall(PetscInitialize(&argc, &argv, NULL, help));
   ```

2. The help text does not mention the z-direction option.

   The program has `p` for the third dimension, so the help string should also
   describe `-p <mesh_z>`.

3. The code does not read `-p` from command-line options.

   It reads `-m` and `-n`, but not `-p`, so the z dimension always stays at its
   default value.

   Expected shape:

   ```c
   PetscCall(PetscOptionsGetInt(NULL, NULL, "-p", &p, NULL));
   ```

4. The z-neighbor comments are reversed.

   The code itself is mathematically right:

   - `Ii - m * n` means `(i, j, k-1)`
   - `Ii + m * n` means `(i, j, k+1)`

   But the comments currently describe these in the opposite direction.

5. The KSP tolerance formula still looks like the 2D version.

   Current logic follows `ex2_annotated.c`, which uses `m` and `n`. For a 3D
   teaching version, consider including `p` too:

   ```c
   PetscCall(KSPSetTolerances(ksp, 1.e-2 / ((m + 1) * (n + 1) * (p + 1)), 1.e-50, PETSC_CURRENT, PETSC_CURRENT));
   ```

6. Preallocation is minimal compared with `ex2_annotated.c`.

   `MatMPIAIJSetPreallocation` and `MatSeqAIJSetPreallocation` are enough for
   the common AIJ case, but `ex2_annotated.c` also includes preallocation calls
   for other PETSc matrix formats. This is not the first correctness problem,
   but it is worth revisiting after the compile and command-line issues are
   fixed.

## Mathematical Check

The intended 3D indexing is:

```c
Ii = i + m * j + m * n * k;
```

So the coordinate recovery in `3d-stencil.c` is correct:

```c
i = Ii % m;
j = (Ii / m) % n;
k = Ii / (m * n);
```

The seven-point stencil is also conceptually correct:

- center coefficient: `6.0`
- six neighbor coefficients: `-1.0`

This represents a 3D finite-difference Laplacian-style operator on a structured
grid.

## Validation Commands

Local WSL/Linux environment checks:

```bash
command -v mpicc
pkg-config --cflags --libs petsc
```

If PETSc is available through `pkg-config`, compile and run a small test:

```bash
mpicc tutorial/examples/3d-stencil.c -o /tmp/3d-stencil $(pkg-config --cflags --libs petsc)
mpirun -np 1 /tmp/3d-stencil -m 3 -n 3 -p 3 -ksp_converged_reason
```
