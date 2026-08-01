# 02 Five-Point Stencil

## Grid View

Imagine a 2D grid of unknown values:

```text
u(i,j)
```

where:

- `i` is the row-like grid coordinate
- `j` is the column-like grid coordinate

Each interior point interacts with four direct neighbors:

- up
- down
- left
- right

## Stencil Formula

The core algebraic pattern used in `ex2` is:

```text
4u(i,j) - u(i-1,j) - u(i+1,j) - u(i,j-1) - u(i,j+1)
```

This is called a five-point stencil:

- one center point
- four nearest neighbors

## Why the Center Coefficient Is `4`

The finite-difference approximation of the 2D Laplacian combines two second derivatives:

```text
-Delta u approx 4u(i,j) - u(i-1,j) - u(i+1,j) - u(i,j-1) - u(i,j+1)
```

up to a scaling by the mesh spacing. In `ex2`, the focus is the sparse linear algebra structure, so the matrix entries are written using the simple pattern:

- diagonal: `4.0`
- neighbor entries: `-1.0`

## Boundary vs Interior Points

Interior points usually have all four neighbors.

Boundary points do not. That is why the code checks conditions such as:

```text
if (i > 0)
if (i < m - 1)
if (j > 0)
if (j < n - 1)
```

These conditions prevent invalid neighbors from being inserted outside the grid.

## From Local Stencil to Sparse Matrix

Each grid point contributes one row of the sparse matrix `A`.

That row contains:

- one diagonal value `4.0`
- up to four off-diagonal values `-1.0`

This is why the matrix is sparse: most entries are zero, and each row only stores a small number of nonzeros.
