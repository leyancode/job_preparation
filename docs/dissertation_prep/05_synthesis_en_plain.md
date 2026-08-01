# Study Summary (plain English, for supervisor discussion)

A synthesis of the current drafts (methodology, single-node results, multi-node results,
profiling). Numbers come from `analysis/` and the drafts and can be checked. Written in
plain declarative form; adjectives kept to a minimum. Open questions are listed at the end.

## Scope

The study measures PETSc rank-thread configurations for a Poisson problem on ARCHER2:
flat MPI against hybrid MPI+OpenMP, in 2D and 3D, at four problem sizes, from 1 to 64
nodes. It asks whether hybrid execution reduces runtime, which configuration gives the
lowest runtime, and where the time goes.

## Platform and setup

- ARCHER2. Each node has two AMD EPYC 7742 processors, 128 physical cores, and 8 NUMA
  regions of 16 cores each.
- PrgEnv-gnu 8.4.0, gcc 11.2.0, cray-mpich 8.1.27. PETSc 3.24.4 built from source as
  `arch-omp-opt` (`--with-openmp=1 --with-openmp-kernels=1 -O3`). One thread per rank is
  used as the MPI-only baseline.
- Benchmarks: 2D uses PETSc `ex2` (5-point stencil); 3D uses a driver written for this
  project (7-point stencil), added because the surface-to-volume ratio differs from 2D.
  Profiling uses `ex2_repeat` (see Profiling).

## Solver choice

The default `ex2` solver is GMRES with block Jacobi — one block per MPI rank, each block
factorised with incomplete Cholesky (ICC; the log events are `MatICCFactorSym` and
`MatCholFctrNum`, so it is ICC, not the ILU an earlier draft assumed. Verified from the
raw logs on 16 July). At 2240x2240 (5.0M unknowns) and above, every run hit PETSc's
default limit of 10,000 iterations without converging (`DIVERGED_ITS`), with final error
norms between order 10^0 and order 10^3 (up to 3.8e3 at 6400x6400). An earlier draft said
"order 10^10"; that came from an unparseable column in the now-deleted derived CSVs and
is refuted by the logs. The solver was changed rather than the tolerance relaxed.

Production runs use:
```
-ksp_type cg -pc_type gamg -ksp_rtol 1e-5 -ksp_atol 1e-10
```
CG applies because the discretised Laplacian is symmetric positive definite. GAMG is used
because multigrid convergence is close to mesh-independent for elliptic problems. Across
5.0M to 41.0M unknowns the solver takes 10-13 iterations with an error norm of order
10^-2 (0.026 at 4500x4500). Near-constant iteration counts mean runtime differences
reflect per-iteration and setup cost, not iteration count.

### Why the solver had to change (revised 16 July; this is the main change since the last version)

Non-convergence is the surface reason. The load-bearing reason is that block Jacobi builds
one block per MPI rank, so the preconditioner is a function of the rank decomposition:
changing the rank-thread layout changes the operator being applied.

The single-node sweep data shows this. Iteration count tracks the rank count and does not
depend on the thread count at all:

| ranks | 1 | 2 | 4 | 8 | 16 | 32 | 64 | 128 |
|---|---|---|---|---|---|---|---|---|
| iterations | 6700 | 3715 | 2825 | 4085 | 8179 | 6460 | 7181 | 10000 (limit) |

One rank takes 6700 iterations whether it runs 1 thread or 128. So two layouts with
different rank counts apply different preconditioners to the same system, and a wall-clock
difference between them reflects that difference as much as any property of the layout.
**Cross-rank-count runtime under this solver is indicative only**, and the question "which
rank-thread layout is fastest?" is not well posed.

Note the dependence is **not monotonic** in rank count: 1 rank is not the fastest to
converge, despite discarding no coupling at all. So it cannot be read as a clean trade-off
between preconditioner strength and parallelism either. I have not established why, and
have not written a mechanism into the text — candidates are restarted GMRES behaving
erratically this far from convergence, and PETSc's default left preconditioning making the
stopping test itself depend on the preconditioner. The argument does not need the reason:
it needs only that iteration count is a function of the rank decomposition and not of the
thread count, which the table shows. If anything, the non-monotonicity strengthens the
point — there is not even a coherent trade-off to reason about.

GAMG removes the coupling: its iteration count is set by the multigrid hierarchy, not the
rank decomposition. At a fixed size the four layouts differ by at most one iteration. That
is what makes the layout comparison in the multi-node chapter admissible.

Evidence (re-verified 16 July from the raw logs in `analysis/data/size_grid/logs/*/`; the derived CSVs
are deleted): of 213 logs, 4 are empty failed jobs; 149 of the 209 with results end in
`DIVERGED_ITS iterations 10000` = PETSc's default `max_it`. Only the 1M size converges
(and not at 128 ranks); at 5.0M and above no run converges at all. The iteration series
in the table is identical across every thread count and both job IDs, and two campaigns
run four months apart at 800x800 give identical iteration counts for every shared rank
count (5052/4173/5150/6567 for 16/32/64/128 ranks). This closed gap G2 without machine
time.

GAMG cost has two phases: setup (`PCSetUp`, building the coarse hierarchy) and solve
(`KSPSolve`). In a single-solve run, setup is about 45% of runtime; in applications the
preconditioner is reused across solves. The multi-node chapter reports total time including
setup; the profiling chapter isolates the solve phase.

## Configuration space

Three rules reduce the space:
1. Threads per rank in {1, 2, 4, 8}. A single-node sweep showed that 16 or more threads
   per rank were slower at every core count, and a single rank (pure OpenMP) reduced
   runtime by under 20% from 1 to 128 threads. At 8 threads or fewer a rank stays within
   one or two NUMA regions.
2. `ppn x threads = 128` (full nodes). Four layouts: 128x1, 64x2, 32x4, 16x8. Same node
   count means same core count, so the comparison isolates rank-thread balance from core
   count.
3. `1e4 < N/C < 1e6` unknowns per core. This sets which node counts are valid per size.
   Four sizes: 5.0M, 10.0M, 20.25M, 41.0M. 2D and 3D grid dimensions are matched per
   nominal size (e.g. 4500^2 ~ 273^3 ~ 20.25M).

Placement uses `OMP_PLACES=cores`, `OMP_PROC_BIND=close`, `--hint=nomultithread`,
`--distribution=block:block`, `--exact`, so a rank and its threads occupy a contiguous
set of cores. Runtime is the maximum `Time (sec)` over ranks from `-log_view`, median
over repetitions. Scaling is computed per layout against that layout's smallest node
count (node-relative, not single-core; this differs from the feasibility study).

## Single-node exploration (was Chapter 4; now folded into Chapter 3)

The single-node chapter has been dissolved and the study is now 7 chapters. The sweep is
exploratory work that bounds the configuration space, which makes it methodology rather
than results. Its data is default-solver data, so by the argument above it cannot rank
layouts with different rank counts. Two findings survive, because both hold at a fixed
rank count, where the preconditioner is also fixed:

All figures below come from one campaign and one build (`analysis/data/size_grid/logs/small`, 1000x1000
= 1M unknowns, `arch-omp-opt`; the 800x800 campaign cited in an earlier version of this
document has been deleted, and these numbers were re-extracted from the raw logs on 16
July). The pure-OpenMP and MPI-only lines share the same baseline: one rank on one
thread, 245.7 s at 6700 iterations. Combinations with 8 threads or fewer have two
repetitions; larger thread counts have one.

| cores | MPI-only (N ranks x 1 thread) | | pure OpenMP (1 rank x N threads) | |
|---|---|---|---|---|
| | time | speedup | time | speedup |
| 1 | 245.7 s | 1.0x | 245.7 s | 1.00x |
| 8 | 60.1 s | 4.1x | 225.5 s | 1.09x |
| 32 | 29.8 s | 8.2x | 216.5 s | 1.13x |
| 64 | 8.1 s | **30.3x** | 195.6 s | 1.26x |
| 128 | (hit iteration limit; excluded) | | 208.4 s | **1.18x** |

- Pure OpenMP does not scale. One rank takes 6700 iterations at every thread count, so
  these runtimes are directly comparable. The best case is 1.26x at 64 threads; beyond
  that more threads cost time. 128 threads return 1.18x for 128x the cores.
- MPI-only from the same baseline reaches 30x on 64 ranks. Its rank counts differ, so that
  figure is indicative rather than a measurement of parallel efficiency — but the 64-rank
  run performs *more* iterations than the baseline (7181 against 6700), so iteration count
  explains none of the gap. The 128-rank run terminates at the 10,000-iteration limit and
  is excluded. Distributing this problem across the node works; threading it does not.
- Cost per iteration falls monotonically as ranks replace threads at fixed cores. On a full
  node: 31.05 ms/iteration at 1x128, 14.36 at 2x64, 7.20 at 4x32, 3.65 at 8x16, 1.88 at
  16x8, 0.98 at 32x4, 0.60 at 64x2, 0.38 at 128x1 (the last measured over its
  non-converged 10,000 iterations). This excludes 16+ threads per rank and leaves
  {1, 2, 4, 8}.

Two claims were removed:

- "Moderate thread counts beat MPI-only" (8x4 at 23.0 s against 32x1 at 29.8 s). Per
  iteration the ordering reverses: 32x1 is 4.61 ms/iteration against 5.6-5.7 for 8x4; at
  16 cores 16x1 (10.4) and 4x4 (9.6-12.0 across two repetitions) are equal within
  run-to-run spread. The wall-clock margin came from 8x4 running fewer iterations (4085
  against 6460), not from hybrid parallelism.
- "Effect of solver choice" / the layout-order reversal. Both numbers it cited (128x1 at
  64.0 s, 32x4 at 76.0 s, 5.0M on one node) terminate at the 10000-iteration limit without
  converging, and the two sides use different preconditioners. Keeping it would have
  contradicted this document's own statement that non-converged runtimes are meaningless.

Consequence: the hybrid question is answered on CG+GAMG data in the multi-node chapter,
and nowhere else. The {1, 2, 4, 8} restriction is a pragmatic bound taken from a sweep that
cannot rank layouts, vindicated after the fact by the multi-node results.

## Multi-node results, 2D

- 32x4 had the lowest median runtime at every size and at almost every node count. For
  41.0M unknowns it was faster than 128x1 by 11.3% on 1 node (105.0 s vs 118.4 s), 11.7%
  on 16 nodes, and 12.0% on 64 nodes. 64x2 was a few percent behind 32x4.
- 1 to 2 nodes: speedup was 0.93-0.99 for every layout and size (2 nodes did not beat
  1 node). From 2 nodes on, each doubling gave speedups near 2.0 (2.00, 1.99, 2.00, 2.01
  for 32x4 at 41.0M). Efficiency relative to 1 node settled at 45-48%.
- 16x8 at scale: efficiency 33% at 20.25M on 32 nodes (32x4: 48%), and 18% at 41.0M on
  64 nodes, with runtime 9.19 s against 4.03 s for 32x4.

## Multi-node results, 3D

- Layout order matched 2D (32x4 fastest, 128x1 slowest of the four, 16x8 weakest at
  scale), with two differences.
- 1 to 2 nodes: 2 nodes were never slower than 1 (speedup 1.00-1.10; the smallest gain,
  0.1%, is at 5.0M with 64x2); efficiency at 2 nodes was 50-55% (2D: 47-49%). The 3D
  7-point stencil exchanges a larger halo relative to subdomain interior than the 2D
  5-point stencil. (Numbers re-checked 16 July against the updated 3D aggregation, which
  added 5.0M multi-node rows; note every 3D multi-node row is a single run, n_runs=1.)
- 16x8 at 41.0M on 64 nodes kept 35% efficiency (34.8%; 2D: 18%) and was 11% slower than
  32x4 (7.75 s against 6.99 s; 2D: 128% slower).

## Profiling

- In a single solve at 20.25M with 16x8, `-log_view` gave `PCSetUp` 45% of time and
  `KSPSolve` 10%. `ex2_repeat` runs the solve inside a `RepeatedSolves` log stage, zeroes
  the initial guess before each solve, and reuses the preconditioner
  (`-ksp_reuse_preconditioner -pc_gamg_reuse_interpolation true`). With 20 solves the
  stage held 69% of time and 93% of flops; within the stage `KSPSolve` was 100% of time;
  each of the 19 repeats took 11 iterations.
- Method: MAP 25.0.4 timelines plus `-log_view` %T (share of stage time) and %F (share of
  stage flops). An event whose %T exceeds its %F spends the difference on communication,
  synchronisation, or memory traffic.
- Single-point data (20.25M, 16x8, RepeatedSolves stage):

  | Event | %T | %F | GF/s |
  |---|---|---|---|
  | MatMult | 39 | 55 | 30.5 |
  | MatMultTranspose | 18 | 6 | 6.7 |
  | VecTDot + VecNorm | 8 | 6 | -- |
  | PCApply (aggregate) | 82 | 82 | 21.6 |

  `MatMultTranspose` (GAMG restriction) has a %T three times its %F and a rate 4.6x below
  `MatMult`. `VecTDot`/`VecNorm` are the CG global reductions.

## Pending data

Machine time needed (ARCHER2):

| ID | Task | Blocks |
|---|---|---|
| G3 | MAP matrix: 20.25M x {2, 8, 16 nodes} x {128x1, 16x8} | profiling chapter — the only large item left |
| G1 | Table: default vs CG+GAMG (error, iterations, runtime) | Ch 3.3; now half-done from the size_grid `iterations` column |

No machine time needed:

| ID | Task | Blocks |
|---|---|---|
| G11 | Run `lscpu`/`hwloc-ls` on a compute node to fix the CCX/L3/NUMA topology | the mechanism claims in Ch 3 (see question 3 below) |
| G4 | log_view forensics, 1 node vs 2 nodes (VecScatter, PCSetUp) | the 1-to-2-node step |
| G7 | Repeat counts | every 3D multi-node row is a single run (n_runs=1); 1-node baselines have 3-7 |
| G5, G9, G10 | 2D-vs-3D plot, ms/iteration plot, %T/%F table | figures only, data exists |

Closed on 16 July, without machine time:

- **G2** (was: confirm the size-grid solver). Closed from the local CSVs — it is the default
  solver and mostly non-converged. Consequences are in the solver section above.
- **G6** (was: 3D 5.0M multi-node rows). The data is there: `ksp_3d_aggregated.csv`
  has 5.0M at 1/2/4/8 nodes x 4 layouts. Only the repeat count remains (G7).
- **G12** (was: explain or discard `analysis/data/mpi_only/logs`). Resolved on 16 July; see question 7,
  which is now a report rather than an open question.

## Open questions for discussion

1. **Chapter structure.** Chapter 4 has been dissolved into Chapter 3 and the study is now
   7 chapters, because once the artefacts were removed the single-node work was two
   negative results plus "the default solver cannot support a layout study" — which reads
   as methodology, not results. Is a 7-chapter structure acceptable, or do you want the
   single-node exploration kept as its own chapter?
2. **Where the block Jacobi argument belongs.** Right now it sits in Chapter 3 as
   justification for the solver choice. It is arguably a contribution in its own right: a
   rank-dependent preconditioner makes a rank-thread layout study ill-posed, and GAMG's
   layout-independent iteration count is what makes the whole comparison valid. Should it
   be lifted into the Discussion as a contribution, or stay as methodology?
3. **Mechanism claims.** The draft attributes the 16+ thread penalty to crossing NUMA
   boundaries, but 16 threads exactly fills one 16-core NUMA region — the boundary crossed
   above 4 threads is the CCX/L3 one (Rome shares 16 MB of L3 per 4-core CCX). Under
   `block:block` + `close` this also gives a candidate explanation for 32x4 winning
   everywhere: it is the only layout where one rank maps to exactly one L3 domain. How much
   verification do you want before that goes in the text (G11 is one `lscpu` away)?
4. **The 1-to-2-node step** in 2D and its absence in 3D are stated with proposed mechanisms
   (network vs shared-memory communication; surface-to-volume ratio). How much log evidence
   (G4) do you expect before these move from "proposed" to "shown"?
5. **Total time includes GAMG setup.** Is that acceptable for the scaling claims, given the
   profiling chapter reports solve-only separately, or should the multi-node chapter also
   report solve-only for the headline configurations?
6. **Scope against the deadline.** G3 is now the only large item outstanding, four weeks
   before 14 August. Does the current scope hold, or should something be cut?
7. **The 1.53x anomaly: now confirmed indirectly, cause still open.** The early
   `analysis/data/mpi_only/logs` campaign is labelled `arch-mpi-opt`, but all 24 of its logs report
   `on a arch-omp-opt`: the MPI-only build was never actually run, and the draft sentence
   claiming one has been removed (the configure recipe exists; no results from it
   survive). The slowdown claim survives the deletion of its original baseline: scaling
   the 1M serial run from `analysis/data/size_grid/logs/small` by the iteration and problem-size ratios
   predicts 101.2 s for the 800x800 serial case, matching the deleted baseline's 101.3 s,
   against the campaign's measured 154.7 s — 1.53x slower per unit of work. A direct
   same-configuration check at 128 ranks against the July `fixed128_multinode` campaign
   gives 1.25x (KSPSolve 2.076 s vs 1.659 s). So that campaign is systematically
   1.25-1.5x slower than newer equivalents; iteration counts, by contrast, match the new
   campaign exactly, so within-campaign ratios are sound. The cause is still unestablished
   (candidates: CPU frequency, 3.4/2.25 = 1.51; unbound memory on a remote NUMA node). A
   cheap decisive experiment exists — rerun the 800x800 serial case a few times while
   recording `srun` binding and `--cpu-freq` — and is on the weekend list. Is that worth
   the queue time, or should the campaign simply carry a caveat?
