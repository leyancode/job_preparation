# PETSc `ex2` Learning Worksheet

This worksheet is designed for slow, hands-on learning. The recommended workflow is:

1. Read the referenced tutorial note.
2. Open the referenced code lines.
3. Write your answer by hand first.
4. Only then check `WORKSHEET_ANSWERS.md`.

## How To Use This Worksheet

For each section:

- read the concept summary
- inspect the mapped tutorial note
- inspect the mapped code lines
- answer the questions in your own words
- if useful, type the small code fragment yourself instead of copying

## Section 1: Problem Definition

### Concept Mapping

- Tutorial note: [01_problem_definition.md](/home/leyan/leyan/s2795693/tutorial/01_problem_definition.md:1)
- Reference source setup: [resources/ex2](/home/leyan/leyan/s2795693/resources/ex2:22)
- Annotated teaching source setup: [ex2_annotated.c](/home/leyan/leyan/s2795693/tutorial/examples/ex2_annotated.c:19)

### What You Should Understand

- what problem `ex2` is solving at a high level
- why the example is written as `Ax = b`
- why an exact solution vector is chosen first

### Questions

1. In your own words, what is the big goal of `ex2`?

Answer:

Test if the questuin computed correctly;

Feedback:
Partly correct idea, but this answer is too narrow and a bit off target.
`ex2` is not mainly a program that checks whether a question is computed correctly.
The bigger goal is:
- build a sparse linear system from a 2D finite-difference stencil
- solve `Ax = b` with a PETSc Krylov solver
- compare the computed solution with a known exact solution

Better answer:
`ex2` builds and solves a linear system coming from a 2D five-point stencil problem, then checks whether the computed solution is close to a known exact solution.



2. What does the equation `Ax = b` mean in this example?

Answer:
Transform the Partial Differential Equation(PDE) into the format like `Ax=b` to computing easily for computer.

Feedback:
This is mostly correct.
You correctly caught the big idea: the continuous PDE is turned into a discrete linear algebra problem that a computer can solve.
One thing to add is the meaning of each symbol:
- `A`: the sparse matrix built from the stencil
- `x`: the unknown numerical solution
- `b`: the right-hand side vector

Better answer:
In this example, `Ax = b` is the discrete linear system obtained from the PDE after finite-difference discretization. `A` is the sparse matrix from the stencil, `x` is the unknown solution vector, and `b` is the right-hand side vector.

3. Why is it useful to choose an exact solution `u` first, instead of starting from a hand-written `b`?

Answer:
Because the question A would be very huge, it is not realistic to compute x directly, we can guess one, then compute the error between them

Feedback:
You are close to an important intuition, but the wording needs correction.
The main reason is not that `A` is huge, and not exactly that we "guess one" in the ordinary sense.
What actually happens is:
- we deliberately choose a simple exact solution `u`
- then we compute `b = A u`
- now we know the true answer in advance
- after solving, we can compare the computed `x` with the known `u`

Better answer:
It is useful to choose an exact solution `u` first because then we can generate a consistent right-hand side with `b = A u`. That means we already know the true solution, so after solving we can directly measure the error and check correctness.

4. Which code lines create the known exact solution and which lines use it to construct `b`?

Answer:
u:
 PetscCall(VecSet(u, 1.0));


b:
PetscCall(MatMult(A, u, b));

Feedback:
This is correct.
You identified the two key lines exactly right.
If you want to make the answer stronger, add the line numbers:
- [resources/ex2](/home/leyan/leyan/s2795693/resources/ex2:133)
- [resources/ex2](/home/leyan/leyan/s2795693/resources/ex2:134)

Stronger answer:
The known exact solution is created by `PetscCall(VecSet(u, 1.0));` and the right-hand side is constructed by `PetscCall(MatMult(A, u, b));`.




## Section 2: Five-Point Stencil

### Concept Mapping

- Tutorial note: [02_five_point_stencil.md](/home/leyan/leyan/s2795693/tutorial/02_five_point_stencil.md:1)
- Reference stencil loop: [resources/ex2](/home/leyan/leyan/s2795693/resources/ex2:70)
- Annotated stencil loop: [ex2_annotated.c](/home/leyan/leyan/s2795693/tutorial/examples/ex2_annotated.c:64)

### What You Should Understand

- what a five-point stencil is
- why the diagonal is `4.0`
- why the neighbors are `-1.0`
- why boundary checks are needed

### Questions

1. Write the five-point stencil used in `ex2`.

Answer:
`4u(i,j) - u(i-1,j) - u(i+1,j) - u(i,j-1) - u(i,j+1)`


2. Why does the center coefficient become `4.0`?

Answer: It comes from combining the second-derivative terms in the 2D Laplacian. The contributions from the two coordinate directions add up to the center coefficient `4.0`.


3. Why do the direct neighbors use `-1.0`?

Answer: In the finite-difference stencil for the 2D Laplacian, each direct neighbor contributes with coefficient `-1.0`, so the off-diagonal entries are `-1.0`.


4. Why does the code need the four checks below?

```text
if (i > 0)
if (i < m - 1)
if (j > 0)
if (j < n - 1)
```

Answer:
These checks prevent the code from inserting neighbors outside the grid. Boundary points do not have all four neighbors.


5. Which line inserts the diagonal entry?

Answer:
`PetscCall(MatSetValues(A, 1, &Ii, 1, &Ii, &v, ADD_VALUES));`

This is the diagonal insertion line in the reference source:
- [resources/ex2:91](/home/leyan/leyan/jobSkill/petsc-benchmark-suite/s2795693/resources/ex2:91)


## Section 3: 2D to 1D Indexing

### Concept Mapping

- Tutorial note: [03_matrix_indexing.md](/home/leyan/leyan/s2795693/tutorial/03_matrix_indexing.md:1)
- Reference indexing lines: [resources/ex2](/home/leyan/leyan/s2795693/resources/ex2:72)
- Annotated indexing lines: [ex2_annotated.c](/home/leyan/leyan/s2795693/tutorial/examples/ex2_annotated.c:52)
- Minimal version: [minimal_ex2.c](/home/leyan/leyan/s2795693/tutorial/examples/minimal_ex2.c:26)

### What You Should Understand

- how `I = i * n + j` works
- how `i` and `j` are recovered from `Ii`
- why vertical neighbors use `±n`
- why horizontal neighbors use `±1`

### Questions

1. Write the formula that maps 2D coordinates `(i,j)` to the 1D index `I`.

Answer:
I = i * n + j

Feedback:
This is correct.
You wrote the exact mapping used in `ex2`.

Better answer:
`I = i * n + j`


2. Explain the meaning of:

```c
i = Ii / n;
j = Ii - i * n;
```

Answer:

Because the I = i*n + j;
so when we need to reverse the mapping, we need to compute like 
i = Ii / n;
j = Ii - i * n;

Feedback:
This is mostly correct.
You understood that these two lines reverse the mapping from the 1D index back to the 2D coordinates.
To make the answer stronger, explain what each line gives:
- `i = Ii / n` gives the row index
- `j = Ii - i * n` gives the column index left over after removing full rows

Better answer:
These two lines recover the 2D grid coordinates from the 1D index `Ii`. Integer division `i = Ii / n` gives the row index, and `j = Ii - i * n` gives the column index.


3. Why is the up neighbor `Ii - n`?

Answer:
(i - 1) * n + j = I - n
(i + 1) * n + j = I + n

Feedback:
This is partly correct.
You wrote both the up and down formulas, which shows the right idea, but the question only asks why the up neighbor is `Ii - n`.

Better answer:
The up neighbor keeps `j` the same and decreases `i` by 1. Using `I = i * n + j`, we get:
`(i - 1) * n + j = I - n`
So the up neighbor is `Ii - n`.



4. Why is the right neighbor `Ii + 1`?

Answer:
i * n + (j - 1) = I - 1
i * n + (j + 1) = I + 1

Feedback:
This is mostly correct.
You included both left and right formulas, so the idea is right. To match the question more directly, focus on the `j + 1` part.

Better answer:
The right neighbor keeps `i` the same and increases `j` by 1. Using `I = i * n + j`, we get:
`i * n + (j + 1) = I + 1`
So the right neighbor is `Ii + 1`.



5. Let `m = 3` and `n = 4`. 
Compute the 1D index of `(i,j) = (1,2)`.

Answer:
I = 3*1 +2 = 5

Feedback:
This is incorrect because the formula should use `n = 4`, not `3`.
The mapping is `I = i * n + j`, so for `(i,j) = (1,2)`:
`I = 1 * 4 + 2 = 6`

Better answer:
`I = i * n + j = 1 * 4 + 2 = 6`


6. For the same point, compute the indices of up, down, left, and right neighbors.

Answer:
Iup = 2
Idown = 8
Iright = 6
Ileft = 5

Feedback:
These are not correct because they were computed from the wrong center index.
For `(i,j) = (1,2)` with `n = 4`, the center index is `I = 6`.
Then:
- up: `6 - 4 = 2`
- down: `6 + 4 = 10`
- left: `6 - 1 = 5`
- right: `6 + 1 = 7`

Better answer:
`Iup = 2`
`Idown = 10`
`Ileft = 5`
`Iright = 7`



7. For that same point, list which matrix positions in that row receive `-1.0` and which receive `4.0`.

Answer:
4.0: (0,0),(1,1) ...(11,11)
-1: the neighbors that around the point of 4.0

Feedback:
This answer is not correct for the specific row asked in the question.
The question is about the row for the single point `(i,j) = (1,2)`, whose 1D index is `I = 6`.
In that row:
- the diagonal entry at `(6,6)` receives `4.0`
- the neighbor columns `(6,2)`, `(6,10)`, `(6,5)`, and `(6,7)` receive `-1.0`

Better answer:
For the row with index `6`:
- `4.0` goes to matrix position `(6,6)`
- `-1.0` goes to matrix positions `(6,2)`, `(6,10)`, `(6,5)`, and `(6,7)`


## Section 4: Matrix Assembly

### Concept Mapping

- Tutorial note: [04_petsc_api_mapping.md](/home/leyan/leyan/s2795693/tutorial/04_petsc_api_mapping.md:1)
- Reference matrix creation: [resources/ex2](/home/leyan/leyan/s2795693/resources/ex2:40)
- Reference ownership range: [resources/ex2](/home/leyan/leyan/s2795693/resources/ex2:55)
- Reference assembly: [resources/ex2](/home/leyan/leyan/s2795693/resources/ex2:100)
- Annotated source: [ex2_annotated.c](/home/leyan/leyan/s2795693/tutorial/examples/ex2_annotated.c:28)

### What You Should Understand

- how PETSc creates a distributed matrix
- why preallocation exists
- why each MPI rank only assembles its own rows
- why matrix assembly happens in two steps

### Questions

1. What is the role of `MatCreate` and `MatSetSizes`?

Answer:
- create the object
- define global dimensions

Feedback:
This is correct.
You captured the main purpose of both calls:
- `MatCreate` creates the PETSc matrix object
- `MatSetSizes` sets its local/global dimensions

Better answer:
`MatCreate` creates the matrix object, and `MatSetSizes` defines the matrix dimensions, including the global size of the linear system.



2. Why does the code preallocate roughly 5 nonzeros per row?

Answer:
 reserve storage

Feedback:
This is partly correct.
Preallocation does reserve storage, but the reason for about 5 entries per row is tied to the five-point stencil:
- one diagonal entry
- up to four neighbor entries

Better answer:
The code preallocates roughly 5 nonzeros per row because each row in the five-point stencil usually contains one diagonal entry and up to four neighbor entries. Preallocation reserves memory in advance and makes matrix assembly more efficient.


3. What does `MatGetOwnershipRange(A, &Istart, &Iend)` mean?

Answer:
Get the range that petsc assigned to each MPI

Feedback:
This is mostly correct.
The key point is that PETSc tells each MPI rank which contiguous block of matrix rows it owns locally.

Better answer:
`MatGetOwnershipRange(A, &Istart, &Iend)` returns the global row range owned by the current MPI rank. This tells the process which rows it is responsible for assembling locally.


4. Why does the loop run from `Ii = Istart` to `Ii < Iend`?

Answer:
Each MPI processes only need to be responsibility to its own assigned rows. 

Feedback:
This is correct in meaning.
Your answer identifies the main idea: each MPI rank works only on its own locally owned rows.

Better answer:
The loop runs from `Istart` to `Iend` because each MPI rank only assembles the rows that PETSc assigned to it. This avoids every process trying to build the whole matrix.


5. Why are `MatAssemblyBegin` and `MatAssemblyEnd` both required?

Answer:
Beginning the MPi processes and Wait for the MPI processes, confirm the structure of matrix

Feedback:
This is partly correct.
The main idea is not just "begin and wait," but that PETSc uses a two-step assembly process to communicate inserted values, complete any needed data exchange, and finalize the matrix.

Better answer:
Both `MatAssemblyBegin` and `MatAssemblyEnd` are required because PETSc finalizes matrix assembly in two steps. During this process, off-process entries can be communicated to the correct MPI ranks and the matrix structure is completed consistently.


## Section 5: Vectors and Right-Hand Side

### Concept Mapping

- Tutorial note: [04_petsc_api_mapping.md](/home/leyan/leyan/s2795693/tutorial/04_petsc_api_mapping.md:33)
- Reference vector creation: [resources/ex2](/home/leyan/leyan/s2795693/resources/ex2:122)
- Reference exact solution and RHS: [resources/ex2](/home/leyan/leyan/s2795693/resources/ex2:133)
- Annotated source: [ex2_annotated.c](/home/leyan/leyan/s2795693/tutorial/examples/ex2_annotated.c:108)

### What You Should Understand

- what `u`, `b`, and `x` mean
- why `VecDuplicate` is used
- why `VecSet(u, 1.0)` is a convenient teaching choice
- why `MatMult(A, u, b)` generates a consistent right-hand side

### Questions

1. What do the vectors `u`, `b`, and `x` represent?

Answer:

u: the exactly solution that made by human
b: the right hand side`s answer that we got by u
x: the numerical solution

Feedback:
This is mostly correct.
You identified the three roles correctly, but the wording can be more precise:
- `u` is the known exact solution
- `b` is the right-hand side vector computed from `u`
- `x` is the computed numerical solution

Better answer:
`u` is the known exact solution vector, `b` is the right-hand side vector, and `x` is the numerical solution computed by the solver.


2. Why is `VecDuplicate` used instead of creating every vector from scratch?

Answer:
Quick and convenient; it get the same structure of vector but dont copy the value.

Feedback:
This is correct.
You captured the important idea: `VecDuplicate` reuses the same layout and type, but does not copy the numerical entries.

Better answer:
`VecDuplicate` is used because it creates a new vector with the same parallel layout, size, and type as the original vector, without copying its values. This is easier and safer than rebuilding each vector from scratch.

3. What does `VecSet(u, 1.0)` do mathematically?

Answer:
let u = 1;

Feedback:
This is partly correct.
The key detail to add is that every entry of the vector is set to `1.0`, not just a single scalar variable.

Better answer:
`VecSet(u, 1.0)` sets every entry of the vector `u` to `1.0`. Mathematically, it makes `u` the all-ones vector.


4. What does `MatMult(A, u, b)` do mathematically?

Answer:
A*u = b

Feedback:
This is correct.
You stated the core mathematical operation exactly right.

Better answer:
`MatMult(A, u, b)` computes the matrix-vector product `b = A u`.


5. Why is this pattern useful for checking solver correctness?

Answer:
It is easy to validate

Feedback:
This is partly correct.
It is easy to validate because we already know the true solution in advance. That is the main reason this pattern is useful.

Better answer:
This pattern is useful because we choose a known exact solution `u` first, then compute `b = A u`. That means the true solution is already known, so after solving we can compare the computed `x` with `u` and directly measure the error.


## Section 6: KSP Solver Basics

### Concept Mapping

- Tutorial note: [05_ksp_solver_basics.md](/home/leyan/leyan/s2795693/tutorial/05_ksp_solver_basics.md:1)
- Reference solver setup: [resources/ex2](/home/leyan/leyan/s2795693/resources/ex2:146)
- Annotated source: [ex2_annotated.c](/home/leyan/leyan/s2795693/tutorial/examples/ex2_annotated.c:130)
- Minimal version solve call: [minimal_ex2.c](/home/leyan/leyan/s2795693/tutorial/examples/minimal_ex2.c:67)

### What You Should Understand

- what `KSP` is
- what `KSPSetOperators(ksp, A, A)` means
- what `KSPSolve(ksp, b, x)` means
- why runtime solver options are powerful

### Questions

1. What is `KSP` in PETSc?

Answer:
Krylov Subspace Methods

Feedback:
This is correct.
You identified the meaning of `KSP` exactly right.

Better answer:
`KSP` in PETSc stands for Krylov Subspace Methods, which are iterative solvers for linear systems such as `Ax = b`.


2. What does `KSPSetOperators(ksp, A, A)` tell the solver?

Answer:

- the matrix defining the linear system is `A`
- the matrix used to build the preconditioner is also `A`

Feedback:
This is correct.
You captured both roles of the two matrix arguments very clearly.

Better answer:
`KSPSetOperators(ksp, A, A)` tells PETSc that `A` is the matrix defining the linear system, and that the preconditioner should also be built using `A`.



3. What does `KSPSolve(ksp, b, x)` compute?

Answer:
To solve Ax = b

Feedback:
This is mostly correct.
The main idea is right, but it is better to say explicitly that the solution is stored in `x`.

Better answer:
`KSPSolve(ksp, b, x)` solves the linear system `Ax = b` and stores the computed numerical solution in `x`.


4. Why is `KSPSetFromOptions(ksp)` useful?

Answer: It allows the user to use command line to set the conditions by themselves

Feedback:
This is mostly correct.
The key idea is that solver and preconditioner settings can be changed at runtime from the command line, without recompiling the program.

Better answer:
`KSPSetFromOptions(ksp)` is useful because it lets the user change solver settings at runtime from the command line, such as solver type, preconditioner, tolerances, and monitoring options, without changing the source code.



5. Give two example runtime options you could pass to experiment with solver behavior.

Answer:
-ksp_type cg
-pc_type jacobi
-ksp_monitor
-ksp_converged_reason

Feedback:
This is correct.
You gave more than two valid PETSc runtime options, and all of them are relevant examples.

Better answer:
Two example runtime options are:
- `-ksp_type cg`
- `-pc_type jacobi`

Other valid examples include:
- `-ksp_monitor`
- `-ksp_converged_reason`


## Section 7: Error Computation

### Concept Mapping

- Tutorial note: [04_petsc_api_mapping.md](/home/leyan/leyan/s2795693/tutorial/04_petsc_api_mapping.md:64)
- Reference error check: [resources/ex2](/home/leyan/leyan/s2795693/resources/ex2:184)
- Annotated source: [ex2_annotated.c](/home/leyan/leyan/s2795693/tutorial/examples/ex2_annotated.c:143)
- Minimal version: [minimal_ex2.c](/home/leyan/leyan/s2795693/tutorial/examples/minimal_ex2.c:72)

### What You Should Understand

- what `VecAXPY(x, -1.0, u)` changes
- what `VecNorm(x, NORM_2, &norm)` measures
- why the final printed norm is a correctness signal

### Questions

1. After this line,

```c
VecAXPY(x, -1.0, u);
```

what does `x` contain?

Answer:

x = x - u

Feedback:
This is correct.
You identified exactly what `VecAXPY(x, -1.0, u)` does to the vector `x`.

Better answer:
After this line, `x` contains the error vector `x - u`.


2. What quantity is computed by:

```c
VecNorm(x, NORM_2, &norm);
```

Answer:
||x - u||_2

Feedback:
This is correct.
You wrote the exact mathematical quantity being computed.

Better answer:
`VecNorm(x, NORM_2, &norm)` computes the 2-norm of the vector `x`, which at this point is `||x - u||_2`.


3. Why do we want this norm to be small?

Answer:
let x ~ = u, proving that the results are reasonable

Feedback:
This is mostly correct.
The main idea is right: if the norm is small, then the computed solution `x` is close to the known exact solution `u`.

Better answer:
We want this norm to be small because it means the computed solution `x` is close to the known exact solution `u`. That is a direct correctness check for the solver result.


4. Which code lines print the final convergence summary?

Answer:
PetscCall(PetscPrintf(PETSC_COMM_WORLD, "Norm of error %g iterations %" PetscInt_FMT "\n", (double)norm, its));

Feedback:
This is correct.
You identified the exact line that prints the final summary.
If you want to make the answer stronger, you can also mention the nearby line that gets the iteration count first.

Better answer:
The final summary is printed by:
`PetscCall(PetscPrintf(PETSC_COMM_WORLD, "Norm of error %g iterations %" PetscInt_FMT "\n", (double)norm, its));`

Related nearby line:
- [resources/ex2:186](/home/leyan/leyan/jobSkill/petsc-benchmark-suite/s2795693/resources/ex2:186) gets the iteration count
- [resources/ex2:193](/home/leyan/leyan/jobSkill/petsc-benchmark-suite/s2795693/resources/ex2:193) prints the final summary



## Section 8: MPI Ownership and Parallel Thinking

### Concept Mapping

- Tutorial note: [06_mpi_partitioning.md](/home/leyan/leyan/s2795693/tutorial/06_mpi_partitioning.md:1)
- Reference ownership logic: [resources/ex2](/home/leyan/leyan/s2795693/resources/ex2:50)
- Annotated source: [ex2_annotated.c](/home/leyan/leyan/s2795693/tutorial/examples/ex2_annotated.c:43)

### What You Should Understand

- what rows an MPI rank owns
- why the code still uses global indices
- why PETSc can assemble distributed matrices without manual message passing in user code

### Questions

1. What is a matrix ownership range?

Answer:
it is the range that each MPI ranks be assigned, each rank builds its local chunk of the global matrix

Comment:
Your core idea is correct: each MPI rank is assigned part of the matrix to build. To make the answer more precise, you should say that the ownership range is usually a contiguous block of global rows owned by one MPI rank.

Reference answer:
It is the contiguous block of global matrix rows assigned to one MPI rank. Each rank is responsible for assembling its own local part of the global matrix.

2. Why can each MPI rank assemble only a subset of rows?

Answer:
The line

```c
MatGetOwnershipRange(A, &Istart, &Iend);
```

tells each MPI rank which global rows it owns.

Then each process only loops over:

```c
for (Ii = Istart; Ii < Iend; Ii++)
```

And even if the assemble is local, but the indices are still global, we can get the whole matrix

Comment:
You correctly used `MatGetOwnershipRange` and the loop bounds as evidence. The main idea still needs one clearer sentence: PETSc distributes the matrix across processes, so each rank only assembles the rows it owns rather than the whole matrix.

Reference answer:
`MatGetOwnershipRange(A, &Istart, &Iend)` tells each MPI rank which global rows it owns. PETSc distributes the matrix across processes, so each rank only assembles the rows in its ownership range. This splits the work across ranks, and PETSc later combines the local contributions into the full distributed matrix.

3. Even when building only local rows, why are column indices still global?

Answer:
Because we need to get the whole matrix, we divided them and let them be processed indivaully, but after that, we need to combined them globally to get the results

Comment:
This answer shows that you understand the matrix is global, which is a good start. To strengthen it, explain that one locally owned row may still connect to unknowns stored on other MPI ranks, so PETSc must keep the column numbering global.

Reference answer:
Column indices stay global because the matrix represents one global linear system. A row owned by one rank may still connect to unknowns stored on other ranks, so PETSc needs global column numbers to place entries in the correct positions.


4. In your own words, what PETSc convenience do we gain from this design?

Answer:

I still assemble the rows that i own
i still name the matrix in the global coordinates

Petsc takes cares of the distributed assembly details

Comment:
This is already very close to the ideal answer. The main improvements are grammar and one final sentence making the benefit explicit: PETSc hides the communication and distributed assembly details, so the user can focus on the mathematics instead of manual MPI message passing.

Reference answer:
I only assemble the rows that I own, but I can still describe matrix entries using global coordinates. PETSc takes care of the distributed assembly and communication details, so user code can focus on the mathematical structure instead of manual message passing.


## Section 9: Running and Observing

### Concept Mapping

- Tutorial note: [07_running_ex2.md](/home/leyan/leyan/s2795693/tutorial/07_running_ex2.md:1)
- Benchmark basics note: [08_benchmarking_basics.md](/home/leyan/leyan/s2795693/tutorial/08_benchmarking_basics.md:1)
- README run examples: [README.md](/home/leyan/leyan/s2795693/README.md:190)

### What You Should Understand

- how to start with a tiny run
- what `-ksp_converged_reason`, `-ksp_monitor`, and `-log_view` are for
- why correctness comes before benchmarking

### Questions

1. Why is a tiny run a better first step than a large benchmark sweep?

Answer:
quick feedback, fewer moving parts, readable output

Comment:
This is a good concise answer and it captures the main idea. If you want to make it stronger, add that a tiny run is also less likely to hide simple correctness mistakes under lots of output or long runtime.

Reference answer:
A tiny run is better first because it is faster, easier to inspect, and less likely to hide simple mistakes under lots of output.

2. What does `-ksp_converged_reason` help you learn?

Answer:
why the solver stopped

Comment:
This is correct and nicely direct. A slightly stronger version would mention that it helps distinguish real convergence from failure cases such as hitting the iteration limit or diverging.

Reference answer:
It tells us why the solver stopped, so we can tell whether it really converged or failed for some reason such as hitting the iteration limit or diverging.

3. What does `-ksp_monitor` help you learn?

Answer:
how the residual changes each iteration

Comment:
This is correct. You could improve it by adding why that matters: it lets you see whether the solver is actually converging and how fast the residual is decreasing.

Reference answer:
It shows how the residual changes during iterations, so we can observe whether the solver is converging and how fast it is improving.

4. What does `-log_view` help you learn?

Answer:
where PETSc spends times

Comment:
The idea is right. For cleaner wording, say that it shows timing and operation information, which helps identify where time is spent and supports performance analysis.

Reference answer:
It shows PETSc timing and operation information that helps us see where time is spent and supports performance analysis.


5. What are the minimum fields you should record in a simple benchmark table?

Answer:
ksp_converged_reason, because it tell us whether the results converged, according to that, we can judge that if the experiments succeed

Comment:
This answer explains why `ksp_converged_reason` is useful, but it does not answer the actual question. The question asks for the fields that should appear in a benchmark record. You can include convergence information as one field, but you also need the basic run configuration and result data.

Reference answer:
A simple benchmark table should at least record: timestamp, problem size, ranks, threads, total cores, runtime, iteration count, error norm, and log filename. If you want, you can also include `ksp_converged_reason` as an extra correctness field.

## Section 10: Hand-Typing Practice

### Concept Mapping

- Minimal teaching source: [minimal_ex2.c](/home/leyan/leyan/s2795693/tutorial/examples/minimal_ex2.c:1)
- Annotated teaching source: [ex2_annotated.c](/home/leyan/leyan/s2795693/tutorial/examples/ex2_annotated.c:1)

### Exercise A

Without copying, type the indexing and stencil part of the loop from memory:

```c
for (Ii = Istart; Ii < Iend; Ii++) {
  ...
}
```
After typing it, explain each line out loud.


 for (Ii = Istart; Ii < end; Ii++ ){
  i = Ii / n;
  j = Ii - i*n;
  v = -1.0

  /* up neighbor(Ii = i*n +j) */
  if (i>0){
    J = Ii - n;
    petscCall(Matsetvalues(A, 1, &Ii, 1, &J, &v, ADD_VALUES));
  }
  
  /* down neighbor(Ii = i*n +j) */
  if (i < m -1){
    J = Ii + n;
    petscCall(Matsetvalues(A, 1, &Ii, 1, &J, &v, ADD_VALUES));
  }
  
  /* left neighbor(Ii = i*n +j) */
  if (j > 0){
    J = Ii - 1;
    petscCall(Matsetvalues(A, 1, &Ii, 1, &J, &v, ADD_VALUES));
  }
  
  /* right neighbor(Ii = i*n +j) */
  if (j< n-1>){
    J = Ii +1 ;
    petscCall(Matsetvalues(A, 1, &Ii, 1, &J, &v, ADD_VALUES));
  }
  
  /* center (Ii = i*n +j) */

    J = j;
    v=4;
    petscCall(Matsetvalues(A, 1, &Ii, 1, &J, &v, ADD_VALUES));
 
  

 }

Comment:
This shows that you remember the overall structure very well: recover `i` and `j`, visit neighbors, then set the center value. The main issues are a few small but important details: `Iend` was written as `end`, `v = -1` should be `v = -1.0`, PETSc function names need exact spelling and capitalization, the right-neighbor condition should be `j < n - 1` rather than `i > 0`, and the center entry should use column `Ii` instead of `j` and should not be wrapped in `if (i > 0)`.

Reference answer:
```c
for (Ii = Istart; Ii < Iend; Ii++) {
  i = Ii / n;
  j = Ii - i * n;
  v = -1.0;

  if (i > 0) {
    J = Ii - n;
    PetscCall(MatSetValues(A, 1, &Ii, 1, &J, &v, ADD_VALUES));
  }
  if (i < m - 1) {
    J = Ii + n;
    PetscCall(MatSetValues(A, 1, &Ii, 1, &J, &v, ADD_VALUES));
  }
  if (j > 0) {
    J = Ii - 1;
    PetscCall(MatSetValues(A, 1, &Ii, 1, &J, &v, ADD_VALUES));
  }
  if (j < n - 1) {
    J = Ii + 1;
    PetscCall(MatSetValues(A, 1, &Ii, 1, &J, &v, ADD_VALUES));
  }

  v = 4.0;
  PetscCall(MatSetValues(A, 1, &Ii, 1, &Ii, &v, ADD_VALUES));
}
```



### Exercise B

Without copying, write the three-line logical flow that creates a known exact solution and then builds the right-hand side from it.

Answer:
PetscCall(VecSetSize(u, PETSC_DECIDE, m*n));
PetscCall(VecSet(u, 1.0));
PetscCall(MatMult(A, u, b));

Comment:
Your logic is very close: create or size the exact-solution vector, fill it with `1.0`, then compute `b = A u`. The main problem is function spelling: it should be `Vec...` and `MatMult`, not `Vet...` or `VetMult`. Also, the reference answer in this worksheet focuses on the core logical flow, so it usually keeps only the two essential lines after the vector already exists.

Reference answer:
```c
PetscCall(VecSet(u, 1.0));
PetscCall(MatMult(A, u, b));
```

### Exercise C

Without copying, write the two lines that convert the computed solution into an error vector and then measure its norm.

Answer:
PetscCall(VecAXPY(x, -1.0, u));
PetscCall(VecNorm(x, NORM_2, &norm));

Comment:
This is correct. You wrote the two key lines exactly right: first convert `x` into the error vector `x - u`, then measure its 2-norm.

Reference answer:
```c
PetscCall(VecAXPY(x, -1.0, u));
PetscCall(VecNorm(x, NORM_2, &norm));
```



### Reflection

Which part still feels least natural to you right now?

Answer:

Comment:
This reflection question does not have one fixed correct answer, so leaving it blank just means you have not chosen a focus yet. A strong reflection should name one specific sticking point rather than saying something broad like "MPI is hard".

Reference answer:
One good reflection would be: "The mapping between the 2D grid and the 1D global index still feels least natural to me, especially why moving up means subtracting `n` and why matrix rows use global indices even in parallel."
