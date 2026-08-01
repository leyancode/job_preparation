#include <petscksp.h>

int main(int argc, char **argv)
{
  Mat         A;
  Vec         u, b, x;
  KSP         ksp;
  PetscInt    m = 4, n = 4;
  PetscInt    Istart, Iend, Ii, i, j, J;
  PetscScalar v;
  PetscReal   norm;

  PetscCall(PetscInitialize(&argc, &argv, NULL, NULL));

  /*
    Build an (m*n) x (m*n) sparse matrix for the five-point stencil.
  */
  PetscCall(MatCreate(PETSC_COMM_WORLD, &A));
  PetscCall(MatSetSizes(A, PETSC_DECIDE, PETSC_DECIDE, m * n, m * n));
  PetscCall(MatSetFromOptions(A));
  PetscCall(MatMPIAIJSetPreallocation(A, 5, NULL, 5, NULL));
  PetscCall(MatSeqAIJSetPreallocation(A, 5, NULL));

  PetscCall(MatGetOwnershipRange(A, &Istart, &Iend));

  for (Ii = Istart; Ii < Iend; Ii++) {
    i = Ii / n;
    j = Ii - i * n;
    v = -1.0;

    if (i > 0) {
      J = Ii - n;
      PetscCall(MatSetValues(A, 1, &Ii, 1, &J, &v, INSERT_VALUES));
    }
    if (i < m - 1) {
      J = Ii + n;
      PetscCall(MatSetValues(A, 1, &Ii, 1, &J, &v, INSERT_VALUES));
    }
    if (j > 0) {
      J = Ii - 1;
      PetscCall(MatSetValues(A, 1, &Ii, 1, &J, &v, INSERT_VALUES));
    }
    if (j < n - 1) {
      J = Ii + 1;
      PetscCall(MatSetValues(A, 1, &Ii, 1, &J, &v, INSERT_VALUES));
    }

    v = 4.0;
    PetscCall(MatSetValues(A, 1, &Ii, 1, &Ii, &v, INSERT_VALUES));
  }

  PetscCall(MatAssemblyBegin(A, MAT_FINAL_ASSEMBLY));
  PetscCall(MatAssemblyEnd(A, MAT_FINAL_ASSEMBLY));

  PetscCall(VecCreate(PETSC_COMM_WORLD, &u));
  PetscCall(VecSetSizes(u, PETSC_DECIDE, m * n));
  PetscCall(VecSetFromOptions(u));
  PetscCall(VecDuplicate(u, &b));
  PetscCall(VecDuplicate(u, &x));

  /*
    Pick the exact solution u = 1 and build b = A*u.
  */
  PetscCall(VecSet(u, 1.0));
  PetscCall(MatMult(A, u, b));

  PetscCall(KSPCreate(PETSC_COMM_WORLD, &ksp));
  PetscCall(KSPSetOperators(ksp, A, A));
  PetscCall(KSPSetFromOptions(ksp));
  PetscCall(KSPSolve(ksp, b, x));

  /*
    Compute the error norm ||x - u||_2.
  */
  PetscCall(VecAXPY(x, -1.0, u));
  PetscCall(VecNorm(x, NORM_2, &norm));
  PetscCall(PetscPrintf(PETSC_COMM_WORLD, "Minimal ex2 error norm: %g\n", (double)norm));

  PetscCall(KSPDestroy(&ksp));
  PetscCall(VecDestroy(&u));
  PetscCall(VecDestroy(&b));
  PetscCall(VecDestroy(&x));
  PetscCall(MatDestroy(&A));
  PetscCall(PetscFinalize());
  return 0;
}
