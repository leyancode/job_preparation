# Ch4 + Ch5 草稿：Results

> ## ⛔ 2026-08-01：本文件整体仅作历史存档，不得再搬运性能结论
>
> 后续发现旧 `ksp_2d_scaling` / `ksp_3d_scaling` campaign 的 302/303 份日志实际
> process count 与文件名不符，大多只启动一个 MPI process。因此本文件下半部此前标成
> “数据和结论都成立”的 launcher-era runtime、speedup、efficiency 和 layout ranking
> 也已全部撤回。唯一权威正文是 `../dissertation_latex/draft.tex`；当前有效结果来自
> audited `nproc_{2d,3d}_libsci/repeated_fullnode` weak-scaling chains。固定 20m 的 long
> strong scaling 仍处于 prepared、未收集状态。

> ## ⛔ 2026-07-16：本文件的 **Ch4 部分整章作废** —— 搬运前先读这里
>
> **权威版本是 `../dissertation_latex/draft.tex`。** G2 结案后(size_grid 是默认 solver 且大面积未收敛):
>
> ### Ch4 部分(本文件上半)
> - **整章已解散,并入 Ch3**,全文改为 7 章。幸存内容已重写为 `draft.tex` §3.5 *Single-Node Exploration*。
> - ❌ **4.1 发现②"中等线程数优于 MPI-only"是假象,已删**。按迭代归一化后反转(2026-07-16 晚
>   从原始 log 复算):32 核 8×4 = 5.6–5.7 ms/it vs 32×1 = **4.61** ms/it;16 核 4×4(9.6–12.0,
>   两 rep 波动)与 16×1(10.4)在波动内打平。墙钟优势全部来自迭代数少(block Jacobi 块数 =
>   rank 数),与 hybrid 并行无关。
> - ❌ **4.2 "Effect of Solver Choice"(排名翻转)整节已删**。引用的 128×1 64.0s / 32×4 76.0s
>   **都顶在 10000 迭代上限、都没收敛**,且两边预条件子不同。留着会和 §3.3"未收敛 runtime 无意义"自相矛盾。
> - ✅ 幸存:发现①纯 OpenMP 不 scale(1 rank 全程 6700 iters,是干净对比);发现③≥16 threads
>   劣化(归一化后仍成立,但**机理别再说跨 NUMA**,见 G11)。
>
> ### Ch5 部分(本文件下半)
> - **数据和结论都成立**(GAMG 迭代数与 layout 无关,同规模差 ≤1 次 —— 这是它成立的前提)。
> - 章号变了:**原 Ch5 → 现 Ch4**。四张图已放入 `draft.tex`(`figures/ksp2d_*`、`ksp3d_*`)。
> - ⚠️ **3D 数据 2026-07-16 更新过**(新增 small 多节点行 + 1 节点第 7 个 rep):本文件里的
>   3D 数字以 `draft.tex` §4.3 和新 `ksp_3d_aggregated.csv` 为准 —— 1→2 节点 speedup 现为
>   **1.00–1.10**(不是 1.02–1.10)、2 节点效率 **50–55%**(不是 51–55%);16×8@64 节点 34.8%、
>   慢 32×4 11% 不变。迭代数范围:2D 10–13、3D 6–8(别写 11–12)。
> - ~~G6(3D small 多节点)~~ **已结案**:数据本来就在,不用补跑。剩 `n_runs=1` 的重复问题 → G7
>   (且 3D **所有**多节点行都是 n_runs=1,不只 small)。

> 英文正文 + `【批注】`。所有数字都来自
> `analysis/data/ksp_2d_scaling/tables/plot_reference_tables.md`、
> `analysis/data/ksp_3d_scaling/tables/plot_reference_tables.md` 和
> `docs/private/updateResults.md`，可直接核对。

---

# Ch4 Single-Node Performance Evaluation

## 4.1 Exhaustive Rank–Thread Sweep

The first stage of the experimental campaign evaluated every rank–thread combination
on a single node, in order to identify which region of the configuration space merits
systematic multi-node study. All combinations with
$\text{ranks} \times \text{threads} \le 128$ were run at a fixed problem size of
$1000 \times 1000$ (one million unknowns), and the sweep was then repeated at larger
sizes up to 41.0M unknowns for the subset of configurations permitted by the
unknowns-per-core rule.

Three consistent patterns emerge (Figure \ref{fig:single_node_sweep}).

First, **pure OpenMP execution does not scale**. With a single MPI rank, increasing
the thread count from 1 to 128 reduces runtime by less than 20% (from 246 s to 208 s at
one million unknowns), despite a 128-fold increase in cores. This is direct evidence
that the OpenMP backend parallelises only part of the execution path: the assembly
phase and several solver kernels run serially on the main thread, so Amdahl's law caps
the achievable speedup at a small factor. 【批注】这里可以 forward-ref Ch6 的 MAP
证据（~70% main thread），呼应非常好。

Second, **moderate thread counts are competitive with, and sometimes better than,
MPI-only execution at equal core count**. At 32 cores, for example, $8\times4$
(23.0 s) outperforms the MPI-only $32\times1$ (29.8 s) at one million unknowns; at 16
cores, $4\times4$ and $8\times2$ both beat $16\times1$ by more than a factor of two.
The advantage is not universal — at a fully populated node the MPI-only layout is
fastest at this problem size — but hybrid layouts with 2–4 threads are never far
behind.

Third, **large thread counts degrade performance consistently**. Configurations with
16 or more threads per rank are slower at every core count tested, and the degradation
grows with thread count. On the ARCHER2 node architecture a team of 16 or more threads
necessarily spans multiple 16-core NUMA regions, so the shared data structures of a
rank are striped across NUMA domains and every iteration pays remote-access costs.

Together these observations justify the reduced configuration set used in the
remainder of this work: threads per rank restricted to $\{1, 2, 4, 8\}$, with
$\text{ppn} \times \text{threads} = 128$ on fully populated nodes.

【批注】图 \ref{fig:single_node_sweep} 还没有——缺口 G9：
从 updateResults.md / size_grid CSV 画：
①runtime vs total cores（log-log，每 layout 一条线，纯 OpenMP 那条平线视觉冲击力强）；
②128 核满节点下四 layout 的柱状对比。

## 4.2 Effect of Solver Choice on Configuration Ranking

【批注】⚠️ 本节写之前必须完成 G2 验证（确认 size-grid 那批数据确实是默认 GMRES+
block Jacobi 跑的）。验证通过的话，这是全文最"有意思"的发现之一，值得单独一节；
验证不通过就删掉本节。以下按"验证通过"预写。

The single-node sweep was initially performed with the default `ex2` solver
configuration (GMRES with block Jacobi). After the switch to CG with GAMG
preconditioning (Section 3.3), the sweep was partially repeated, and the comparison
reveals that solver choice affects not only absolute runtime but also the *ranking* of
rank–thread layouts. At 5.0M unknowns on one fully populated node, the default solver
runs fastest in the MPI-only layout ($128\times1$: 64.0 s, versus 76.0 s for
$32\times4$), whereas under CG+GAMG the ordering reverses ($32\times4$: 12.3 s, versus
13.8 s for $128\times1$). A plausible explanation is that the two solvers stress
different resources: the default configuration is dominated by GMRES orthogonalisation
(`VecMDot`), which is bandwidth-bound and scales well with rank count, while GAMG
introduces coarse-grid levels whose small operators and frequent global reductions
penalise high rank counts — a penalty that fewer, threaded ranks partially avoid.
Conclusions about optimal hybrid configurations are therefore solver-dependent, and
the multi-node results that follow should be read as specific to CG+GAMG.
【批注】机理解释我给的是合理假设，写论文时降格为 "one plausible explanation"
（已经是这个语气），有 G3 profiling 数据后可以坐实或修正。

---

# Ch5 Multi-Node Scaling

## 5.1 Setup

The multi-node campaign runs the four per-node layouts ($128\times1$, $64\times2$,
$32\times4$, $16\times8$) at four problem sizes in both 2D and 3D, over the node
counts admitted by the unknowns-per-core window: up to 8 nodes at 5.0M unknowns,
16 at 10.0M, 32 at 20.25M and 64 at 41.0M. All runs use CG+GAMG with the tolerances of
Section 3.3; iteration counts are constant (11–12) across sizes and node counts, so
runtime differences reflect per-iteration and setup cost only.

## 5.2 2D Results

Figures \ref{fig:2d_runtime}–\ref{fig:2d_efficiency} show median runtime, speedup and
parallel efficiency; the underlying values are tabulated in
Appendix \ref{app:tables}. 【批注】图直接用
`analysis/plots/ksp_2d_scaling/*.png`（重新出一版嵌入 LaTeX 的尺寸即可），
附录表用 `tables/plot_reference_tables.md` 转 LaTeX。

Three findings stand out.

**The $32\times4$ layout is the fastest at every problem size and almost every node
count.** Its advantage over MPI-only execution is consistent but moderate: for the
largest problem, $32\times4$ is faster than $128\times1$ by 11.3% on one node
(105.0 s vs 118.4 s), 11.7% on 16 nodes and 12.0% on 64 nodes. The $64\times2$ layout
tracks $32\times4$ closely, a few percent behind, so the practical recommendation is
robust: on ARCHER2, replacing pure MPI with 2–4 threads per rank yields a
reliable 5–12% improvement for this workload at no cost in scalability.
【批注】H2（2–4 threads 最优）在这里被正面证实，Discussion 记得回收。

**Crossing from one node to two costs one full doubling of resources.** For every
layout and every problem size, two nodes (256 cores) perform no better than one node
(128 cores): speedups at 2 nodes range from 0.93 to 0.99. From 2 nodes onward, however,
each further doubling yields close to ideal improvement (e.g. for 41.0M unknowns,
$32\times4$ improves by factors of 2.00, 1.99, 2.00 and 2.01 across successive
doublings up to 32 nodes). The overall parallel efficiency of roughly 45–48% relative
to the 1-node baseline is therefore not a gradual decay but a single step: the entire
loss is incurred when the job first spans the network. The likely cause is that
intra-node MPI communication proceeds through shared memory, while inter-node halo
exchange and the global reductions in CG and GAMG setup must traverse the Slingshot
network; once that cost is paid, it grows only slowly with node count.
【批注】"likely cause" 需要 G4 的日志取证支撑：对比 nodes1/nodes2 log_view 里
VecScatter 和 PCSetUp 事件时间。取证后把措辞升级为 "this is confirmed by…"，
并给一张小表。这是审稿人最可能追问的点。

**Eight threads per rank collapses at scale.** The $16\times8$ layout is competitive
at small node counts but degrades sharply as the job grows: at 20.25M unknowns on 32
nodes its efficiency drops to 33% (versus 48% for $32\times4$), and at 41.0M on 64
nodes to 18%, with runtime 9.19 s against 4.03 s for $32\times4$ — more than a factor
of two slower on identical resources. With only 16 ranks per node, each rank holds a
large subdomain whose halo exchange is serialised through one MPI process per 8 cores,
and the partially threaded solver kernels leave threads idle during the growing
communication phases. 【批注】这个解释同样可用 G3 的 MAP（16 节点 × 16×8 那格）
直接验证——OpenMP-heavy 大规模正是矩阵里安排好的配置，写作时留好接口。

## 5.3 3D Results

The 3D benchmark reproduces the headline findings — $32\times4$ fastest overall,
$128\times1$ slowest of the four layouts, $16\times8$ weakest at scale — but differs
in two instructive ways.

First, **the one-to-two-node step is absent**. In 3D, two nodes are consistently
*faster* than one (speedups of 1.02–1.10 across layouts and sizes), and parallel
efficiency at two nodes is 51–55%, compared with 47–49% in 2D. Relative to its own
communication volume, the 3D problem loses less when it first crosses the network.
A seven-point stencil on a 3D subdomain exchanges a larger halo relative to its
interior than the 2D five-point stencil, so the single-node 3D baseline already pays a
substantial intra-node communication and memory-traffic cost; distributing the same
problem over two nodes then adds proportionally less new overhead, and the doubled
aggregate memory bandwidth compensates.
【批注】这个解释是我给的候选机理，建议同样用 nodes1 vs nodes2 的 log_view
（3D 侧）取证后再定稿；也可以只陈述现象 + "we attribute this to…" 的谨慎措辞。

Second, **the 8-thread degradation is milder in 3D**: at the largest size on 64 nodes,
$16\times8$ retains 35% efficiency (2D: 18%) and is 11% slower than $32\times4$
(2D: 128% slower). Where communication is a larger fraction of total work, reducing
the number of ranks — and hence the number of messages — recovers more of the cost of
idle threads.

【批注】5.3 缺 3D small (5M) 的 2/4/8 节点行（缺口 G6）。目前草稿刻意不引用
3D small 的 multi-node 数字，补跑后可以加一句覆盖；不补则在 5.1 里声明
"the 5.0M 3D case was run on a single node only"。

## 5.4 Cross-Dimension Comparison

【批注】写作素材已在 5.2/5.3 的对比句里，本节做成一张并排图（缺口 G5：
同规模同 layout 的 2D/3D 效率曲线双栏图）+ 一段总结：
- 相同点：layout 排名一致 → 配置建议跨维度稳健（回答 RQ4 的 generality）
- 不同点：3D 无 1→2 悬崖、8 线程劣化更温和 → 通信占比越高，hybrid 越有利（支撑 H1）

## 5.5 Summary

Across both dimensions, four problem sizes and node counts from 1 to 64, the results
give a consistent answer to RQ2: the best configurations concentrate at 2–4 threads
per rank, with $32\times4$ the single best layout in every setting tested, delivering
a 5–12% improvement over MPI-only execution without sacrificing scalability. The
benefit of hybrid execution is real but bounded; its magnitude, and the penalty for
over-threading, both depend on the communication intensity of the problem.
