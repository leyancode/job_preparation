# Dissertation outline and live evidence gaps

Last updated: 2026-08-01.

This file is a compact planning index. The live manuscript is
`docs/dissertation_latex/draft.tex`; numerical claim status is maintained in
`07_claim_evidence_map.md`; campaign state lives in `AGENTS.md` and the two
`analysis/data/nproc_*_libsci/reports/README.md` records.

## Evidence boundary

- The completed 2D and 3D `repeated_fullnode` formal campaigns are audited
  Phase 3 evidence. Their 11 size–node points form `~40k` and `~80k`
  unknowns/core weak-scaling chains.
- The old `ksp_2d_scaling` and `ksp_3d_scaling` launcher-era campaigns are
  invalid for runtime, speedup, efficiency, layout ranking, and cross-dimension
  comparison: 302/303 inspected logs mismatch the requested process count.
  Retain them only for methodological history and solver-event inspection.
- The fixed-20m strong-scaling extension is **audited in both dimensions**
  (72/72 selected logs each). It supports matched 1–32-node runtime, speedup,
  and efficiency curves while remaining separate from the weak-scaling data.
- Raw logs and retrieved source CSVs are immutable. Derived outputs are rebuilt
  from scripts; never repair a generated table or report by hand.

## Current manuscript structure

1. **Introduction** — motivation, questions, contributions.
2. **Background and Related Work** — PETSc, CG/GAMG, MPI/OpenMP, ARCHER2.
3. **Experimental Platform and Methodology** — topology, drivers, repeated
   solves, configuration-space reduction, binding, metrics, and validation.
4. **Full-Node Scaling Results** — audited formal weak-scaling chains and
   layout-relative results plus the audited matched 2D/3D fixed-20m curves.
5. **Profiling and Bottleneck Analysis** — `log_view` exposure evidence and
   future MAP call-path analysis.
6. **Discussion** — 2D/3D differences, limits, and mechanism boundaries.
7. **Conclusion and Future Work**.
8. **Reproducibility: Repository and Scripts**.
9. **Appendix** — selected full `log_view` excerpts.

## Completed evidence

### Single-node methodology

- Default GMRES + block Jacobi/ICC couples the preconditioner to MPI rank
  decomposition; cross-rank layout timing is therefore ill-posed.
- The 1M size-grid sweep supports the clean fixed-rank thread comparison and
  shows pure OpenMP scaling is poor.
- `analysis/scripts/size_grid/analyze_single_node_sweep.py` regenerates the
  table and figure and asserts constant iteration counts across threads at each
  fixed rank count.

### Formal repeated-fullnode campaigns

- Each dimension has 132 formal logs plus eight excluded one-repeat 20m pilots.
- All 140 logs per dimension passed arch, process/thread, convergence,
  repeated-stage, timing, and failure-marker checks.
- Current figures use unknowns/core weak-scaling panels, medians of three formal
  runs, and observed min–max bars.
- 2D: 64×2 is lowest in seconds/iteration at all 11 points; 165m/32 nodes is
  about 794.8 M equations/s, 13.1% above 128×1.
- 3D: 32×4 wins seconds/iteration at seven points and 64×2 at three; 165m/32
  nodes 64×2 is about 510.4 M equations/s, 30.1% above 128×1.
- Three repeats quantify observed spread, not statistical significance.

### Launcher-era diagnosis — G14 closed

The earlier requested strong-scaling campaigns did not launch their requested
layouts. The PETSc header disagrees with the filename for 141/142 2D logs and
161/161 non-smoke 3D logs, usually reporting one process. Their previous
“fastest layout”, node-efficiency, and 1→2-node-cliff narratives are withdrawn.

## Live gaps

### G13 — Phase 1 tolerance

Determine whether PETSc accepted the double-dash `--ksp_rtol 1e-5` in the
default-solver jobs. This affects only the Ch3 default-versus-GAMG narrative,
not the Phase 3 formal campaigns, which use single-dash `-ksp_rtol 1e-5`.

### G11 — hardware topology confirmation

Run `lscpu` and `hwloc-ls` on an ARCHER2 compute node and cite the result.
Current safe interpretation: a CCX is four cores sharing 16 MB L3; a NUMA
region is 16 cores; eight threads/rank crosses an L3 boundary but not a NUMA
boundary.

### Fixed-20m strong scaling — both dimensions audited

Design:

```text
2D             4500² = 20,250,000 unknowns
3D             273³  = 20,346,417 unknowns
nodes          1, 2, 4, 8, 16, 32
layouts/node   128×1, 64×2, 32×4, 16×8
repeats        3
timing         1 warm-up + 19 RepeatedSolves
```

Each pipeline generates runtime, speedup, and efficiency figures from 72 valid
same-session logs. In 2D, new 2/4-node medians agree with the earlier formal
anchors within 2.2%; at 32 nodes, 64×2 reaches 29.83× speedup and 93.2%
cumulative efficiency, but only 62.9% efficiency for the final 16→32 doubling.
In 3D, 16×8 is fastest at 32 nodes with 0.0681 s/solve, 14.24× speedup, 44.5%
cumulative efficiency, and 74.6% final-doubling efficiency. The 3D best layout
changes with node count, and flat MPI plus 64×2 turn upward by 32 nodes.

### Profiling

The baseline MAP artefacts exist but lack a complete analysis pipeline. MAP
timings remain separate from uninstrumented curves; use profiles only for
mechanism evidence. Do not attribute layout rankings to LibSci merely because
the executable links threaded LibSci.

### Writing and administration

- Finish contributions, limitations, profiling discussion, and appendix.
- Resolve remaining citations and confirm the official dissertation template.
- Compile the live draft with `tectonic docs/dissertation_latex/draft.tex`.

## Next order of work

1. Add the audited matched 2D/3D fixed-20m figures and endpoint table to the
   manuscript, explicitly separating strong scaling from the weak-scaling bands.
2. Run G13 and G11 checks.
3. Complete MAP analysis and finish the manuscript.

## Memory discipline

Use **prepared**, **collected**, and **audited** literally. Remove superseded
instructions instead of appending another “latest” paragraph. A script, job
name, plot, or derived CSV is not proof that the requested configuration ran;
the raw log header is authoritative.
