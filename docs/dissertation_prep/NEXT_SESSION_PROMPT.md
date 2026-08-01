# Current hand-off prompt (2026-08-01)

I am writing an EPCC MSc dissertation on PETSc MPI/OpenMP scaling on ARCHER2.
The repository is `~/leyan/local_data_analysis/local_data_analysis`.

Read these state sources before making a performance claim:

1. `AGENTS.md` for current rules, open gaps, and campaign states;
2. `analysis/data/nproc_2d_libsci/reports/README.md` and the matching 3D record;
3. `docs/dissertation_prep/07_claim_evidence_map.md`;
4. `.agents/skills/petsc-campaign-provenance/SKILL.md`.

## Evidence that is currently valid

- The formal 2D and 3D `repeated_fullnode` campaigns each contain 132
  three-repeat formal logs plus eight excluded one-repeat pilots. All 140 logs
  per dimension passed content-based audit.
- Their matrix is window-filtered by unknowns/core. The current figures are two
  weak-scaling chains (`~40k` and `~80k` unknowns/core), not long fixed-size
  strong-scaling curves.
- The old `ksp_2d_scaling` and `ksp_3d_scaling` launcher-era campaigns are
  invalid for runtime, speedup, efficiency, layout ranking, and 2D/3D
  comparison: 302 of 303 inspected logs report a different process count from
  the filename, usually one process.
- Trust raw log contents before filenames. Read the PETSc-reported arch,
  process count, thread count, stage-scoped solver events, and convergence.

## Current fixed-20m strong-scaling state

A matched fixed-20m strong-scaling extension now exists for both dimensions:

```text
2D: 4500² = 20,250,000 unknowns
3D: 273³  = 20,346,417 unknowns
nodes: 1, 2, 4, 8, 16, 32
layouts: 128×1, 64×2, 32×4, 16×8
repeats: 3
solves: 1 warm-up + 19 timed RepeatedSolves
```

Submission wrappers:

```text
scripts/ksp/2d/lib/2Dlib_strong_scaling_20m.sh
scripts/ksp/3d/lib/3Dlib_strong_scaling_20m.sh
```

New logs are isolated under
`analysis/data/nproc_{2d,3d}_libsci/logs/strong_scaling_20m/`.

Each dimension uses only one submit `.sh` and one self-contained `.sbatch`, with
no sourced helper, size-table dependency, or job-side validation. The scripts
passed local syntax, submission-matrix, and fake-launch tests. Cluster evidence
is now audited in both dimensions.

- 2D: 72/72 logs valid. Generated outputs are under
  `csv/derived/strong_scaling_20m/`, `tables/strong_scaling_20m/`, and
  `analysis/plots/nproc_2d_libsci/strong_scaling_20m/`. At 32 nodes, 64×2 is
  fastest at 0.0277 s/solve with 29.83× cumulative speedup, 93.2% cumulative
  efficiency, and 62.9% 16→32 doubling efficiency.
- 3D: 72/72 selected logs valid. Outputs are under the matching 3D derived,
  table, and plot paths. At 32 nodes, 16×8 is fastest at 0.0681 s/solve with
  14.24× cumulative speedup, 44.5% cumulative efficiency, and 74.6% 16→32
  doubling efficiency. The largest three-repeat runtime spread is 11.09%.
  Replacement jobs at nodes 1, 2, and 32 are selected; older attempts remain
  retained but excluded from the formal matrix.

## Next evidence workflow

1. Add the audited 2D and 3D fixed-20m figures/tables to the manuscript, keeping
   them separate from the unknowns/core weak-scaling figures.
2. Interpret saturation with both cumulative one-node efficiency and the local
   16→32 doubling efficiency; do not treat the 32-node point as a machine limit.
3. Keep the prior 2/4-node formal rows as temporal checks, not pooled repeats.
   In 3D the new medians are 0.3–3.1% slower and none of eight ranges overlap.

## Remaining external checks

- G13: determine whether the Phase 1 double-dash `--ksp_rtol` override was
  accepted by PETSc.
- G11: confirm ARCHER2 topology on a compute node with `lscpu` and `hwloc-ls`.

## Memory hygiene

After changing campaign scripts, collecting data, changing analysis semantics,
or revising a dissertation result, proactively update `AGENTS.md`, both durable
campaign records where applicable, this hand-off, and the affected PETSc
skills. Remove superseded instructions and label state explicitly as
**prepared**, **collected**, or **audited**. A script's existence is never proof
that its campaign ran.
