# 研究综述（中英混杂 · 自用版）

> 当前事实基线：2026-07-30。正式 scaling 结论只采用已经审计的 2D/3D
> repeated-fullnode campaigns。更早的 launcher-era 多节点结果已经作废，不能再用于
> layout 排名、效率或跨维度比较。

## 一句话定位

在 ARCHER2 上比较 PETSc 求解结构化 Poisson 问题时的 flat MPI 与 hybrid
MPI+OpenMP。正式实验覆盖 2D 和 3D、六种问题规模、1--32 个满载节点以及四种
rank-thread layout，重点回答 steady-state repeated solve 中 moderate hybridisation
是否有效、哪种 layout 更稳定，以及哪些机理仍需 profiling 证据。

## 1. 平台、构建和 driver

- ARCHER2 每节点有 2 个 AMD EPYC 7742、128 个 physical cores；所有正式运行关闭
  SMT，并使用全部 128 个物理核。
- 软件环境为 PrgEnv-gnu 8.4.0、gcc 11.2.0、cray-mpich 8.1.27 和 PETSc 3.24.4。
- 早期 single-node/default-solver 探索使用 `arch-omp-opt`。正式 2D/3D
  repeated-fullnode campaigns 使用 `arch-omp-libsci-rome-opt`，配置记录指向
  `libsci_gnu_mp.so.5.0`。两种构建都使用 `-O3`。
- 2D 正式 driver 是 `drivers/ex2_repeat.arch-omp-libsci-rome-opt`，来自 PETSc
  `ex2` 的 five-point stencil；3D 正式 driver 是
  `drivers/3d_repeat.arch-omp-libsci-rome-opt`，使用 seven-point stencil。
- `128x1` 表示 OpenMP-enabled binary 上每 rank 一个线程，是本文的 flat-MPI
  baseline；它不是独立的 `arch-mpi-opt` 构建。

LibSci linkage 只说明 executable 链接到了 threaded LibSci，不能证明 repeated sparse
solve 调用了 BLAS，也不能把 layout 差异归因于 LibSci。该归因需要 call-path 或 event
证据。

## 2. Solver 选择和比较合法性

默认 `ex2` 使用 GMRES + block Jacobi，每个 MPI rank 对应一个 block，子块使用 ICC。
在 5.0M unknowns 及以上，原始日志中的 run 全部达到 10,000 iteration limit 而未收敛。
更重要的是，block 数随 MPI rank 数变化，所以更换 rank-thread layout 同时改变了
preconditioner。默认 solver 下的跨-rank runtime 不能单独解释为并行性能。

单节点数据给出的 iteration series 是：

```text
MPI ranks:   1    2    4    8    16    32    64    128
iterations: 6700 3715 2825 4085 8179 6460 7181 10000
```

在固定 rank 数时，thread 数不改变 iteration count；跨 rank 数时，iteration count
非单调变化。因此早期“某个 hybrid layout wall time 更短”的结果不能用来排序 layout。

正式 campaigns 使用：

```text
-ksp_type cg -pc_type gamg -ksp_rtol 1e-5 -ksp_atol 1e-10
```

CG 适用于离散 Laplacian 的 SPD 系统，GAMG 使 iteration count 远低于默认配置，且
不再直接等于 MPI rank 数对应的 block-Jacobi 分解。正式数据中：

- 2D 为 9--13 iterations，同一 size/node 点的 layouts 最多差 2 次；
- 3D 为 6--7 iterations，同一 size/node 点的 layouts 最多差 1 次；
- 2D error norm 为约 `8.5e-3`--`1.34e-1`，3D 为约
  `6.0e-3`--`8.59e-2`。

论文同时报告实际吞吐率和 seconds per KSP iteration。后者消除了外层 iteration
count 的差异，但 GAMG hierarchy、coarse-grid work 和通信量仍可能随分解变化，因此
不能把 iteration-normalised time 描述成完全相同的底层工作量。

## 3. 正式 experiment matrix

布局固定为四种满节点配置：

```text
128 MPI ranks/node x 1 OpenMP thread/rank
 64 MPI ranks/node x 2 OpenMP threads/rank
 32 MPI ranks/node x 4 OpenMP threads/rank
 16 MPI ranks/node x 8 OpenMP threads/rank
```

问题规模为 5m、10m、20m、41m、82m 和 165m。2D 与 3D 使用接近的 unknown counts，
例如 `4500^2 = 20,250,000` 和 `273^3 = 20,346,417`。size/node 点必须满足：

```text
25,000 <= unknowns / (nodes * 128) <= 100,000
```

这个窗口在 1、2、4、8、16、32 节点上产生 11 个 `(scale,nodes)` 点。每点包含四种
layout 和三次 formal repeats，所以每个维度各有 44 个正式配置、132 份正式日志。
每个维度另保留八份 one-repeat 20m pilot logs，但 pilots 不进入 median、best-layout
table 或 figures。

所有 run 使用：

```text
OMP_PLACES=cores
OMP_PROC_BIND=close
srun --hint=nomultithread --distribution=block:block --exact
```

论文必须区分 nodes、MPI process count 和 total cores。节点数相同时，四种 layout
都使用相同的 `nodes * 128` physical cores；NPROC 图的横轴只能使用 PETSc header
报告的 MPI process count。

## 4. Measurement contract 和审计结果

每次程序调用执行 20 次收敛的 KSP solves。第一次在 Main Stage 中 warm up 并支付
`PCSetUp`；其余 19 次位于 `RepeatedSolves`，并复用 preconditioner 和 GAMG
interpolation。正式吞吐率只使用该 stage：

```text
equations_per_sec = unknowns * 19 / RepeatedSolves_KSPSolve_max_time
seconds_per_iteration = RepeatedSolves_KSPSolve_max_time / (19 * iterations)
```

2D 和 3D 各 140 份日志均通过 content-based audit：arch、actual process/thread
counts、20 次收敛、19 个 timed events、positive timing 和 threaded LibSci path 均正确；
`RepeatedSolves` 中没有 exact `PCSetUp`，也没有 PETSc/MPI/Slurm/LibSci failure
marker。3D 的 140 个 source-CSV rows 还与独立解析的日志逐行一致。

正式 repeats 按 median 聚合，error bars 表示三次运行的 observed minimum--maximum，
不是 confidence interval。2D 最大 throughput spread 为 4.71%，3D 为 3.83%；三次
重复不足以支持 statistical-significance claim。

## 5. 单节点探索的可用结论

早期 `size_grid/small` 数据仍能支持两个边界结论，但不参与正式 layout 排名：

- Pure OpenMP 不 scale：一个 rank 在 1--128 threads 下始终需要 6700 iterations，
  64 threads 的最佳 speedup 约 1.26，128 threads 回落到约 1.18。
- 在 128 cores 上，以更多 MPI ranks 替代大 OpenMP teams 会降低 time per iteration。
  该结果支持把正式 sweep 限制在 1、2、4、8 threads/rank，但不能把某个 NUMA 或
  CCX 机制写成已证实原因。

这组探索使用默认 block-Jacobi solver，而且 `t>=16` 的组合只有一次运行。正文应把
它定位为 configuration-space selection evidence，不应据此回答哪个 production layout
最快。

## 6. 2D repeated-fullnode 结果

- Raw throughput：`64x2` 在 11 点中赢 8 点，`128x1` 赢 3 点；`16x8` 在 11 点
  全部最低。
- Iteration-normalised：`64x2` 在 11 点全部具有最低 median seconds/iteration。
- 三个 flat-MPI raw wins 中有两个伴随少一次 iteration。41m/8 nodes 的 `128x1`
  与 `64x2` medians 只差约 0.4%，observed ranges 重叠。
- 165m/32 nodes：`64x2` 为约 794.8 million equations/s，比 `128x1` 高 13.1%。
- 五个 size 各提供一个 local node-doubling step。Raw speedup 为 2.00--3.08，包含
  repeatable superlinear observations。Cache capacity、GAMG hierarchy 和 system
  variation 都是可能解释，现有数据不能确认其中任何一个。

因此 2D 的 practical default 是 `64x2`。5m/1 node 和 10m/1 node 的实际 raw
throughput 仍由 flat MPI 获胜；差距小或 observed ranges 重叠时应同时测试两者。

## 7. 3D repeated-fullnode 结果

- Raw-throughput winners：`32x4` 六点、`64x2` 四点、`128x1` 一点、`16x8`
  零点。
- Iteration-normalised winners：`32x4` 七点、`64x2` 三点、`128x1` 一点。
- `16x8` 没有赢过，但 raw throughput 只在 8/11 点最低，不能写成每点最慢。
- 165m/32 nodes：`64x2` 为约 510.4 million equations/s，比 `128x1` 高 30.1%。
- 在该最大规模，16->32 nodes 的 speedup 为 `64x2` 约 1.91（95.5% doubling
  efficiency），`128x1` 约 1.46（73.0%）。
- 全部 local node-doubling speedups 为约 1.46--2.39。20m/4 nodes 的 flat-MPI
  near-tie 伴随 6 iterations，而其他 layouts 为 7，需同时查看 per-iteration time。

3D 支持 moderate hybridisation，但不支持单一固定最优 layout。`32x4` 更常获胜，
`64x2` 在最大 concurrency 表现最好。

## 8. 跨维度结论

两个维度都支持 2--4 threads/rank 通常优于两个极端，但 exact ranking 不一致：

- 2D 明确偏向 `64x2`；
- 3D 更常偏向 `32x4`，在 165m/32 nodes 切换为 `64x2`；
- `16x8` 在两个维度均未赢任何 raw-throughput point；
- flat MPI 在少数小问题或特定分解仍可获胜。

可以安全写成“moderate hybridisation is useful across both stencil dimensions, while
the preferred balance remains dimension- and scale-dependent”。不能写“layout ranking
跨维度完全一致”，也不能仅凭 surface-to-volume ratio 把差异归因于通信。

2D five-point 和 3D seven-point stencil 每个 equation 的工作量不同，因此 absolute
equations/s 不适合直接作为跨维度算法速度比较；应比较 relative layout gain、winner
pattern 和 scaling step。

## 9. Profiling 现状

Repeated-solve driver 的目的仍成立：single solve 的 `PCSetUp` 可占大量时间，而本文
要分析 hierarchy 已建立后的 steady-state solve。Baseline `arch-omp-opt` MAP campaign
已经覆盖 20.25M、nodes `{2,8,16}` 和 layouts `{128x1,32x4,16x8}`。MAP 无法可靠
launch 128 ranks/node，因此 `128x1` 只能使用 `-log_view`，MAP 只能解释 hybrid
layouts 内部行为。

已有单点 `RepeatedSolves` event evidence：

| Event | %T | %F | GF/s | 可支持的读法 |
|---|---:|---:|---:|---|
| `MatMult` | 39 | 55 | 30.5 | 细网格 SpMV 占主要 flops |
| `MatMultTranspose` | 18 | 6 | 6.7 | 时间占比相对 flop 占比较高，是 bottleneck candidate |
| `VecTDot+VecNorm` | 8 | 6 | -- | CG global reductions |
| `PCApply` aggregate | 82 | 82 | 21.6 | repeated solve 主要花在 multigrid apply |

MAP instrumentation overhead 已测得不均匀，不能把 MAP-run timing 混入正式 scaling
curves。LibSci MAP campaign 仍待 retrieval；smoke evidence 指向 repeated solve 不调用
BLAS，这个 null result 应如实报告。

## 10. 剩余工作和论文措辞边界

需要完成的正文工作：

1. 把已审计的 3D matrix、三张 figures 和 cross-dimensional comparison 写入
   `draft.tex`。
2. 分析现有 baseline MAP matrix，并在可用时取回 LibSci MAP evidence，以回答
   “where the time goes”。在此之前，halo、global reduction、OpenMP overhead、cache
   和 NUMA 都只能写成候选机制。
3. 若要保留 default-vs-CG+GAMG 的完整方法学对照表，再补齐相同规模的对照点；否则
   使用现有日志只陈述已验证的 convergence failure 和 rank-dependent preconditioner。
4. 核实 compute-node CCX/L3/NUMA topology 后再写 placement 的硬件机制。
5. 若要对小于约 2% 的 layout gap 做显著性陈述，需要增加重复或采用预先规定的统计
   设计；当前正文只报告 median 和 observed range。

当前 scaling evidence 足以回答“哪类 layout 在该 repeated CG+GAMG workload 上更好”，
并支持有限的跨维度建议。它不支持 three-run significance、LibSci causality、end-to-end
single-solve performance，也不支持已经确认的硬件 bottleneck mechanism。
