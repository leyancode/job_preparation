# 01 Problem Definition

## Big Picture

PETSc `ex2` is a linear solver example. It builds a matrix `A`, a right-hand side vector `b`, solves

```text
Ax = b
```

and compares the computed answer `x` with a known exact solution `u`.

## The Continuous Idea

The example is based on a 2D elliptic problem on a rectangular grid. A standard way to describe the model is:

```text
-Delta u = f
```

where:

- `u` is the unknown field we want to solve for
- `f` is the forcing term
- `Delta` is the Laplacian operator

In two dimensions,

```text
Delta u = d^2u/dx^2 + d^2u/dy^2
```

so

```text
-Delta u = -(d^2u/dx^2 + d^2u/dy^2)
```

## Why `ex2` Is Good for Learning

This example is small enough to understand but still contains the main PETSc ideas:

- distributed matrix creation
- distributed vector creation
- matrix assembly
- Krylov solver setup
- runtime options
- error checking

## What the Code Actually Does

At a high level, the example:

1. reads problem dimensions `m` and `n`
2. builds a sparse matrix for a 2D five-point stencil
3. creates an exact solution vector `u`
4. computes `b = A * u`
5. solves `Ax = b`
6. measures the error between `x` and `u`

## Why the Exact Solution Is Chosen First

Instead of starting from a hand-written `f`, the example first chooses a convenient exact solution:

```text
u = [1, 1, 1, ..., 1]^T
```

Then it computes:

```text
b = A u
```

This is a very practical teaching pattern because:

- the exact answer is already known
- the computed error is easy to interpret
- we can test the solver without deriving a custom forcing function first
