# Ch6 草稿：Profiling and Bottleneck Analysis（框架 + 可写部分成稿）

> 6.1 和 6.2 数据已齐，是成稿；6.3/6.4 是带 TODO 的框架，等 MAP 矩阵（缺口 G3）
> 跑完填充。`【批注】` 搬运时删除。

---

## 6.1 Isolating the Solve Phase: a Repeated-Solve Driver

Interpreting profiles of the unmodified `ex2` benchmark proved misleading. In a
representative run at $4500 \times 4500$ (16 ranks $\times$ 8 threads), the `-log_view`
summary attributes 45% of total wall-clock time to `PCSetUp` — the one-off construction
of the GAMG hierarchy — and only 10% to `KSPSolve`. A profile of this run therefore
describes the cost of *setting up* the preconditioner far more than the cost of
*solving* with it, whereas in realistic applications a preconditioner is constructed
once and reused across many solves. Early Linaro MAP sessions confirmed the problem:
the timeline was dominated by setup activity, and solver-phase behaviour was too short
to sample reliably.

The driver was therefore modified (`ex2_repeat`) to execute the solve repeatedly under
a dedicated PETSc logging stage:

```c
PetscCall(PetscLogStageRegister("RepeatedSolves", &stage));
PetscCall(PetscLogStagePush(stage));
for (s = 1; s < nsolves; s++) {
  /* zero the initial guess, otherwise the previous solution satisfies the
     tolerance immediately and the solve exits at iteration 0 */
  PetscCall(VecSet(x, 0.0));
  PetscCall(KSPSolve(ksp, b, x));
}
PetscCall(PetscLogStagePop());
```

Two details matter. First, the initial guess must be re-zeroed before each solve;
otherwise the converged solution of the previous iteration satisfies the tolerance
immediately and every subsequent "solve" terminates at iteration zero, silently
measuring nothing. Second, the preconditioner must actually be reused, which is
enforced with `-ksp_reuse_preconditioner -pc_gamg_reuse_interpolation true`; this was
verified in the log output, where `PCSetUp` appears only in the main stage and the
repeated-solves stage contains no setup events.

With 20 solves, the repeated stage accounts for 69% of total wall-clock time and 93%
of all floating-point work, and within the stage `KSPSolve` is 100% of time. Each of
the 19 repeated solves converges in exactly 11 iterations, identical to the first,
confirming that preconditioner reuse does not alter convergence for this
constant-matrix problem. The measurement target — the steady-state cost of the
preconditioned CG iteration — is thereby isolated cleanly from one-off costs.

【批注】这节的数字全部来自你贴的 before/after 两份 log_view，已核对。
可加一张小表（before/after 的 stage 时间分布），素材现成。

## 6.2 Analysis Methodology: MAP Timelines and log_view Cross-Reference

Bottleneck identification combines two complementary sources.

**Linaro MAP** (version 25.0.4) samples the whole application and attributes time to
source lines, distinguishing main-thread computation, OpenMP regions, OpenMP overhead,
and MPI time. Its timeline view shows *when* threads are active or idle, which
`-log_view` cannot; in particular it exposes whether nominally OpenMP-enabled kernels
actually execute on worker threads (Section 3.4 of the feasibility study showed ~70%
of time on the main thread for an early configuration).

**PETSc `-log_view`** provides exact per-event counts, times, flops and message
statistics. Its per-event columns %T (share of stage time) and %F (share of stage
flops) support a simple diagnostic: an event whose share of time far exceeds its share
of useful arithmetic is spending that time on something other than computation —
communication, synchronisation or memory traffic — and is a bottleneck candidate.
The achieved rate column (Mflop/s) and the max/min time ratio across ranks (load
imbalance) refine the diagnosis.

Applying this to the repeated-solves stage of the $4500\times4500$ run
(16 ranks $\times$ 8 threads) already yields a clear picture:

| Event | %T | %F | Achieved GF/s | Reading |
|---|---|---|---|---|
| `MatMult` | 39 | 55 | 30.5 | healthy: fine-grid SpMV, bandwidth-bound but efficient |
| `MatMultTranspose` | 18 | 6 | 6.7 | **suspect**: 3× the time share of its flop share; restriction on coarse levels, 4.6× slower per flop than `MatMult` |
| `VecTDot` + `VecNorm` | 8 | 6 | — | 50% + 25% of all stage reductions: CG's global synchronisation points |
| `VecCopy` + `VecPointwiseMult` | 10 | 4 | 9.7 | pure memory traffic in the smoother |
| `PCApply` (aggregate) | 82 | 82 | 21.6 | the preconditioner dominates the iteration, as expected for multigrid |

【批注】表里的数字全部出自你贴的改进后 log_view 的 RepeatedSolves stage
（Stage 列），可直接核对。写成正文时建议保留表 + 每行一句解读的形式，
这正是你想要的"T%/F% 对照分析怎么写"的模板。

Together the two tools cover each other's blind spots: `-log_view` says *which
operation* is expensive and whether the cost is arithmetic or not; MAP says *where the
threads were* while it was expensive.

## 6.3 Profiling Matrix Results 🏃 TODO（等 G3 数据）

【批注】以下为写作框架。6 个格子对应 problemDesign.md 的矩阵：
20.25M × {2, 8, 16 节点} × {128×1 MPI-heavy, 16×8 OpenMP-heavy}，
全部用 ex2_repeat + PC 复用跑，MAP + log_view 双输出。

预定叙事结构（每个小节一张 MAP 截图 + 一张 log_view 摘要表）：

- **6.3.1 MPI-heavy vs OpenMP-heavy at 2 nodes** —
  基线对比：TODO MPI 时间占比、主线程串行占比、OpenMP 区域利用率各是多少。
  预期（写作时验证）：128×1 的 MPI 占比高但核全忙；16×8 的 MPI 占比低但
  worker 线程在通信段闲置。
- **6.3.2 Scaling the two extremes to 8 and 16 nodes** —
  随节点数增长，两种布局的 MPI 时间增长斜率对比。
  预期：这里能直接解释 Ch5 的两个现象——
  ①16×8 大规模崩溃（worker idle 时间随通信占比放大）；
  ②1→2 节点悬崖在 profile 里的对应物（VecScatter/allreduce 时间跳变）。
- **6.3.3 Where the OpenMP backend does and does not parallelise** —
  对照 MAP 的 per-function 视图，列出哪些 PETSc 事件真正跑在 worker 线程上
  （预期 MatMult 系）、哪些仍在主线程（预期 VecTDot/VecNorm 的 reduction 部分、
  MatMultTranspose）。这直接回答 RQ3。

## 6.4 Bottleneck Identification 🏃 TODO（依赖 6.3）

【批注】综合 6.2 的单点分析 + 6.3 的矩阵，预期锁定三个瓶颈（按现有证据排序）：

1. **Halo exchange / `VecScatter`**（跨节点后的主要 MPI 成本，1→2 悬崖主嫌）
2. **CG + GAMG 的全局归约**（`VecTDot`/`VecNorm` + 粗层级 allreduce，
   随节点数线性增多的同步点）
3. **`MatMultTranspose`（GAMG restriction）的低效率**（6.7 vs 30.5 GF/s，
   且 OpenMP 化程度存疑——若 MAP 显示其主线程执行，则是 backend 覆盖不全的实锤）

每个瓶颈给：证据（log_view 数字 + MAP 截图）→ 机理 → 可能的缓解措施
（如 `-pc_gamg_*` 参数、telescope 到更少 rank 的粗网格、kernel 级优化）。
若时间允许做了任一缓解实验，放 6.5；否则在 Future Work 交代。

## 6.5 [占位] Preconditioner Reuse and Solve-Only Scaling

【批注】占位节（缺口 G8）：如果 8 月前有余量，用 ex2_repeat 重跑 20.25M 的
32×4 和 128×1 各节点数，报告 solve-only 的 scaling 与 Ch5 total-time scaling
的差异（预期：去掉 setup 后 1→2 悬崖形态改变 → 反推 setup 在悬崖中的贡献）。
没时间就整节删除，Ch5 的方法学保护伞（3.3 末段）已经把 total-time 口径立住了。
