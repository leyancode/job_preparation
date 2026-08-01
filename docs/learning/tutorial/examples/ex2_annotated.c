static char help[] = "Solves a linear system in parallel with KSP.\n\
Input parameters include:\n\
  -view_exact_sol   : write exact solution vector to stdout\n\
  -m <mesh_x>       : number of mesh points in x-direction\n\
  -n <mesh_y>       : number of mesh points in y-direction\n\n";

#include <petscksp.h>

int main(int argc, char **args)
{
  Vec         x, b, u; /* x: computed solution, b: RHS, u: exact solution */
  Mat         A;       /* Sparse matrix for the 2D five-point stencil */
  KSP         ksp;     /* Krylov solver object */
  PetscReal   norm;    /* ||x - u||_2 after the solve */
  PetscInt    i, j, Ii, J, Istart, Iend, m = 8, n = 7, its;
  PetscBool   flg;
  PetscScalar v;

  PetscFunctionBeginUser;
  PetscCall(PetscInitialize(&argc, &args, NULL, help));
  PetscCall(PetscOptionsGetInt(NULL, NULL, "-m", &m, NULL));
  PetscCall(PetscOptionsGetInt(NULL, NULL, "-n", &n, NULL));

  /*
    Create a distributed sparse matrix A of global size (m*n) x (m*n).
    Each unknown u(i,j) becomes one row and one column in this matrix.
  */
  PetscCall(MatCreate(PETSC_COMM_WORLD, &A));
  PetscCall(MatSetSizes(A, PETSC_DECIDE, PETSC_DECIDE, m * n, m * n));
  PetscCall(MatSetFromOptions(A));

  /*
    Preallocate up to 5 nonzeros per row:
    one diagonal entry and up to four nearest neighbors.
  */
  PetscCall(MatMPIAIJSetPreallocation(A, 5, NULL, 5, NULL));
  PetscCall(MatSeqAIJSetPreallocation(A, 5, NULL));
  PetscCall(MatSeqSBAIJSetPreallocation(A, 1, 5, NULL));
  PetscCall(MatMPISBAIJSetPreallocation(A, 1, 5, NULL, 5, NULL));
  PetscCall(MatMPISELLSetPreallocation(A, 5, NULL, 5, NULL));
  PetscCall(MatSeqSELLSetPreallocation(A, 5, NULL));

  /*
    Each MPI rank owns a contiguous block of global rows [Istart, Iend).
    We assemble only the rows we own.
  */
  PetscCall(MatGetOwnershipRange(A, &Istart, &Iend));

  /*
    Natural-order indexing used here:

      I = i * n + j

    Recover 2D coordinates from the global 1D index Ii:

      i = Ii / n
      j = Ii - i * n

    The five-point stencil adds:

      diagonal      ->  4.0
      each neighbor -> -1.0
  */
  for (Ii = Istart; Ii < Iend; Ii++) {
    v = -1.0;
    i = Ii / n;
    j = Ii - i * n;

    /* Up neighbor: (i-1, j) -> Ii - n */
    if (i > 0) {
      J = Ii - n;
      PetscCall(MatSetValues(A, 1, &Ii, 1, &J, &v, ADD_VALUES));
    }

    /* Down neighbor: (i+1, j) -> Ii + n */
    if (i < m - 1) {
      J = Ii + n;
      PetscCall(MatSetValues(A, 1, &Ii, 1, &J, &v, ADD_VALUES));
    }

    /* Left neighbor: (i, j-1) -> Ii - 1 */
    if (j > 0) {
      J = Ii - 1;
      PetscCall(MatSetValues(A, 1, &Ii, 1, &J, &v, ADD_VALUES));
    }

    /* Right neighbor: (i, j+1) -> Ii + 1 */
    if (j < n - 1) {
      J = Ii + 1;
      PetscCall(MatSetValues(A, 1, &Ii, 1, &J, &v, ADD_VALUES));
    }

    /* Center coefficient of the stencil */
    v = 4.0;
    PetscCall(MatSetValues(A, 1, &Ii, 1, &Ii, &v, ADD_VALUES));
  }

  PetscCall(MatAssemblyBegin(A, MAT_FINAL_ASSEMBLY));
  PetscCall(MatAssemblyEnd(A, MAT_FINAL_ASSEMBLY));

  /* The matrix is symmetric for this stencil. */
  PetscCall(MatSetOption(A, MAT_SYMMETRIC, PETSC_TRUE));

  /*
    Create distributed vectors compatible with A.
    u will store the exact solution, b the right-hand side, and x the result.
  */
  PetscCall(VecCreate(PETSC_COMM_WORLD, &u));
  PetscCall(VecSetSizes(u, PETSC_DECIDE, m * n));
  PetscCall(VecSetFromOptions(u));
  PetscCall(VecDuplicate(u, &b));
  PetscCall(VecDuplicate(b, &x));

  /*
    Choose a simple exact solution:

      u = [1, 1, 1, ..., 1]^T

    Then define the RHS by applying the matrix:

      b = A u
  */
  PetscCall(VecSet(u, 1.0));
  PetscCall(MatMult(A, u, b));

  flg = PETSC_FALSE;
  PetscCall(PetscOptionsGetBool(NULL, NULL, "-view_exact_sol", &flg, NULL));
  if (flg) PetscCall(VecView(u, PETSC_VIEWER_STDOUT_WORLD));

  PetscCall(KSPCreate(PETSC_COMM_WORLD, &ksp));
  PetscCall(KSPSetOperators(ksp, A, A));

  /*
    Set a default relative tolerance. PETSc runtime options can still
    override this later with KSPSetFromOptions().
  */
  PetscCall(KSPSetTolerances(ksp, 1.e-2 / ((m + 1) * (n + 1)), 1.e-50, PETSC_CURRENT, PETSC_CURRENT));
  PetscCall(KSPSetFromOptions(ksp));

  /* Solve A x = b */
  PetscCall(KSPSolve(ksp, b, x));

  /*
    Reuse x to store the error:

      x <- x - u

    Then compute ||x - u||_2.
  */
  PetscCall(VecAXPY(x, -1.0, u));
  PetscCall(VecNorm(x, NORM_2, &norm));
  PetscCall(KSPGetIterationNumber(ksp, &its));

  PetscCall(PetscPrintf(PETSC_COMM_WORLD, "Norm of error %g iterations %" PetscInt_FMT "\n", (double)norm, its));

  PetscCall(KSPDestroy(&ksp));
  PetscCall(VecDestroy(&u));
  PetscCall(VecDestroy(&x));
  PetscCall(VecDestroy(&b));
  PetscCall(MatDestroy(&A));

  PetscCall(PetscFinalize());
  return 0;
}
