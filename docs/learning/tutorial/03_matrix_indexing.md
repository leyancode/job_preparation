# 03 Matrix Indexing

## Why We Need Index Mapping

The mathematical problem is naturally written on a 2D grid:

```text
u(i,j)
```

But PETSc vectors and matrices are indexed in 1D:

```text
x[I]
```

So we need a mapping between 2D grid coordinates and a 1D global index.

## The Ordering Used in `ex2`

The example uses this relation:

```text
I = i * n + j
```

where:

- `i` is the grid row index
- `j` is the grid column index
- `n` is the number of points in the second grid direction

## Recovering `i` and `j`

The code reverses this mapping with:

```c
i = Ii / n;
j = Ii - i * n;
```

This works because:

- integer division gives the row number
- subtracting `i * n` leaves the column offset

## Why Vertical Neighbors Are `Ii - n` and `Ii + n`

Moving one row up or down changes `i` by `1` while keeping `j` fixed.

Using

```text
I = i * n + j
```

we get:

```text
(i - 1) * n + j = I - n
(i + 1) * n + j = I + n
```

So:

- up neighbor: `Ii - n`
- down neighbor: `Ii + n`

## Why Horizontal Neighbors Are `Ii - 1` and `Ii + 1`

Moving left or right changes `j` by `1` while keeping `i` fixed:

```text
i * n + (j - 1) = I - 1
i * n + (j + 1) = I + 1
```

So:

- left neighbor: `Ii - 1`
- right neighbor: `Ii + 1`

## Small Example

If `m = 3` and `n = 4`, then the grid indices map like this:

```text
(0,0) -> 0
(0,1) -> 1
(0,2) -> 2
(0,3) -> 3
(1,0) -> 4
(1,1) -> 5
(1,2) -> 6
(1,3) -> 7
(2,0) -> 8
(2,1) -> 9
(2,2) -> 10
(2,3) -> 11
```

From `I = 5`, we recover:

- `i = 5 / 4 = 1`
- `j = 5 - 1 * 4 = 1`

and the neighbors are:

- up: `5 - 4 = 1`
- down: `5 + 4 = 9`
- left: `5 - 1 = 4`
- right: `5 + 1 = 6`
