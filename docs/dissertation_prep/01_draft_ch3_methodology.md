# Ch3 草稿：Experimental Platform and Methodology

> ## ⛔ 2026-07-16：本文件已部分过期 —— 搬运前先读这里
>
> **权威版本是 `../dissertation_latex/draft.tex`,不是本文件。** `draft.tex` 的 TODO 里写着
> "expand from 01 §3.1" 之类,但本文件仍带着以下已被推翻的内容,**照搬会把错误搬回去**:
>
> 1. **§3.3 的 "11–12 iterations" 是错的** → 实测 10–13(small 10–11 → very-large 12–13),
>    且随规模轻微增长,所以是 "near mesh-independent" 而非 "constant"。
> 2. **§3.4 的 "16 或更多线程必然跨 NUMA 边界" 站不住** → 16 线程恰好**填满**一个 16 核 NUMA 区。
>    Rome 的 L3 按 CCX(4 核/16MB)共享,>4 线程跨的是 **CCX/L3 边界**,>16 才跨 NUMA。见缺口 G11。
> 3. **§3.1 把 "Core Complex Die"(CCD,8 核)和 "Core Complex"(CCX,4 核)混用了** → 一并修。
> 4. **缺了换 solver 的真正论证**:block Jacobi 块数 = MPI rank 数 → 改 layout = 换预条件子 →
>    默认 solver 下 layout 比较 ill-posed。这段已在 `draft.tex` §3.3 成稿,本文件没有。
> 5. **§3.4 的单节点扫描证据**已重写为 `draft.tex` §3.5 *Single-Node Exploration*(原 Ch4 并入)。
>    数据源(2026-07-16 晚定稿):`analysis/data/size_grid/logs/small/`(1000²=1M;之前短暂改用的
>    rank_thread_grid 已删)。基线 245.7s/6700 iters,两条线共用。
> 6. 🔴 **§3.1 的 "reference MPI-only build (`arch-mpi-opt`)" 那句是假的(已从 log 坐实)—— 见下面 G12。**
> 7. **§3.3 的 "block Jacobi (ILU(0) on each block)" 是错的** → 原始 log 事件是
>    `MatICCFactorSym`/`MatCholFctrNum`,子块因子化是 **ICC(0)(不完全 Cholesky),不是 ILU(0)**。
> 8. **§3.3 的 "error norm reached order 10^10" 是错的** → 原始 log 实测未收敛 norm 是
>    **10⁰–10³ 量级**(6400² 最高 ~3.8×10³);正确表述是"5.0M 及以上全部 `DIVERGED_ITS`@10000"。
>    "10^10" 是已删 CSV 解析失败的产物。draft.tex 已按 log 改写。
>
> 未受影响、仍可直接搬的:§3.1 硬件参数(**除了 arch-mpi-opt 那句**)、§3.2 benchmark、
> §3.5 placement、§3.6 metrics、§3.7 repro。

> ## ~~🔴 G12~~ ✅ 已结案(2026-07-16 晚,从原始 log 重验坐实):`arch-mpi-opt` 这个 build 根本没被用过
>
> 本文件 §3.1 写着:
>
> > *"A reference MPI-only build with identical optimisation flags but without OpenMP
> > kernels (`arch-mpi-opt`) was used for the baseline comparison in the early single-node study."*
>
> **这句话作为对数据的描述是错的(已坐实)。** `analysis/data/mpi_only/logs/` 里 **24 份 log 全部**自报
> `on a arch-omp-opt` —— 文件名里的 `arch-mpi-opt` 是 job 脚本贴的标签,不是实际二进制。
> `scripts/petsc_configure_archer2.sh` 确实定义了这个 build("drop the two `--with-openmp*` lines"),
> 所以**配方存在,但没有任何留存结果出自它**。
>
> **1.53× 异常也站住了(间接重建;直接基线 rank_thread_grid 已删)**:同配置(1 rank×1 thread、
> 800×800、4311 迭代)`analysis/data/mpi_only/logs/` 要 **154.7s**;用 `analysis/data/size_grid/logs/small/` 的 1M 串行
> (245.7s/6700 it)按迭代比×规模比外推 = **101.2s**,与已删基线的 101.3s 严丝合缝 →
> 确实慢 ~1.53×/单位工作量。同配置直接对比:r128_t1 KSPSolve 2.076s(mpi_only)vs
> 1.659s(`fixed128_multinode` nodes1)= **1.25×**。→ 该批次**系统性偏慢 1.25–1.5×**,
> 根因仍未知(候选:CPU 频率 3.4/2.25=1.51;或没绑核、内存落远端 NUMA)。
>
> **现行规则(放宽)**:①§3.1 那句保持删除(draft.tex 有 G12 VERIFIED 注释);
> ②mpi_only 的**迭代数**与新 campaign 逐一相同,campaign **内部**相对值(如 r1→r128=72×)可用;
> ③**绝对时间**必须带"该批次系统性偏慢"脚注,跨批次绝对比较仍禁止;
> ④周末可选实验:重跑 800² 串行 3 reps、记录 `srun` 绑核与 `--cpu-freq`,一锤定音。

> 英文正文可直接搬进 LaTeX；`【批注】` 是给你的中文说明，搬运时删除。
> 图表引用用 `\ref{}` 占位名标出。

---

## 3.1 Hardware and Software Environment

All experiments were carried out on ARCHER2, the UK national supercomputing service, a
HPE Cray EX system consisting of 5,860 compute nodes. Each node contains two AMD EPYC
7742 (Rome) processors, providing 128 physical cores per node at a base frequency of
2.25 GHz. Each processor comprises eight Core Complex Dies, and each node is organised
into eight NUMA regions of 16 cores; cores within a Core Complex share an L3 cache. This
hierarchical memory organisation means that the cost of a memory access depends strongly
on the placement of the accessing thread relative to the data, which motivates the
thread-placement policy described in Section 3.5.

The Cray Programming Environment with the GNU toolchain (`PrgEnv-gnu/8.4.0`) was used
throughout, with `gcc/11.2.0` as the compiler and `cray-mpich/8.1.27` as the MPI
implementation. PETSc release 3.24.4 was built from source with OpenMP support enabled:

```
--with-openmp=1 --with-openmp-kernels=1
--with-debugging=0 COPTFLAGS=-O3 CXXOPTFLAGS=-O3 FOPTFLAGS=-O3
```

The resulting build (`PETSC_ARCH=arch-omp-opt`) enables OpenMP parallelism inside
selected PETSc computational kernels while retaining the standard MPI-based
distributed-memory execution model. A reference MPI-only build with identical
optimisation flags but without OpenMP kernels (`arch-mpi-opt`) was used for the
baseline comparison in the early single-node study.

【批注】如果最终正文只用 arch-omp-opt 一个 build（threads=1 当作 MPI-only），
把最后一句删掉或改为脚注，避免审稿人追问两个 build 的差异。

## 3.2 Benchmark Problems and Drivers

Three benchmark drivers are used in this work.

**2D Poisson benchmark (`ex2`).** The primary benchmark is the PETSc KSP tutorial
`ex2`, which assembles the sparse linear system arising from a five-point finite
difference discretisation of the Laplace operator on an $m \times n$ structured grid,
and solves it with a Krylov subspace method. The matrix is distributed row-wise across
MPI ranks in PETSc's MPIAIJ format, so that each rank owns a contiguous block of rows
and halo exchange is required for the off-process part of each matrix–vector product.

**3D Poisson benchmark.** Because the communication behaviour of a stencil code is
governed by its surface-to-volume ratio, conclusions drawn from a 2D problem do not
necessarily transfer to three dimensions, where each subdomain exchanges larger halos
with more neighbours. A 3D driver was therefore implemented for this project, following
the structure of `ex2` but assembling the seven-point stencil on an
$m \times n \times p$ grid, with the grid dimensions exposed as runtime options. This
allows the same solver configuration and job infrastructure to be reused unchanged for
the 3D study.

**Repeated-solve driver.** For profiling purposes a modified driver, `ex2_repeat`, was
developed; its motivation and design are described in Section 6.1.
【批注】如果 Ch6 结构改了，记得同步这里的 forward reference。

## 3.3 Solver Configuration

Initial experiments used the default `ex2` solver settings, namely restarted GMRES
preconditioned with block Jacobi (ILU(0) on each block). While adequate for small
grids, this combination did not converge to an acceptable solution at the problem sizes
targeted in this study: at $4500 \times 4500$ and above, the reported error norm reached
order $10^{10}$, indicating that the iteration had effectively stagnated within the
default iteration limit. Since runtime measurements of a non-converging solver are
meaningless, the solver configuration was changed rather than the tolerances relaxed.

All production runs therefore use the conjugate gradient method preconditioned with
PETSc's native algebraic multigrid, GAMG:

```
-ksp_type cg -pc_type gamg -ksp_rtol 1e-5 -ksp_atol 1e-10
```

CG is applicable because the discretised Laplacian is symmetric positive definite, and
multigrid preconditioning is the natural choice for elliptic problems because its
convergence rate is essentially independent of the mesh resolution. This is confirmed in
practice: across all problem sizes from 5.0M to 41.0M unknowns, the solver converges in
11–12 iterations with a final error norm of order $10^{-2}$
(e.g. 0.026 at $4500\times4500$), compared with the divergent behaviour of the default
configuration. Mesh-independent iteration counts are also methodologically important
for a scaling study: they ensure that runtime differences between configurations
reflect the cost per iteration rather than differences in iteration count.

【批注】① "order 10^10" 那句用的是你口述的"十位数"——G1 补跑后换成表格引用：
"Table \ref{tab:solver_choice} compares the two configurations."
② error norm ~0.05/0.026 是离散化误差层面的量，如果导师追问可加一句
"the residual tolerance, not the discretisation error, is the stopping criterion"。

An important structural property of this solver is that its cost divides into two
phases: a setup phase (`PCSetUp`), in which GAMG constructs the coarse-grid hierarchy,
prolongation operators and Galerkin coarse matrices, and a solve phase (`KSPSolve`), in
which the preconditioned CG iteration is applied. In a single-solve benchmark the setup
phase accounts for a substantial fraction of total runtime (approximately 45% in the
profiled configuration of Section 6.1), whereas in realistic applications the same
preconditioner is typically reused across many solves. The benchmark measurements in
Chapters 4 and 5 report total time including setup; the profiling study in Chapter 6
isolates the solve phase explicitly. 【批注】这段是"旧数据如实用"的方法学保护伞，务必保留。

## 3.4 Configuration Space and Selection Rules

The space of possible experiments is large: it spans problem size, node count, MPI
ranks per node (ppn), and OpenMP threads per rank. Three rules were used to reduce it
to a tractable and interpretable subset.

**Thread counts restricted to 1, 2, 4 and 8.** An exhaustive single-node sweep
(Chapter 4) evaluated every rank–thread combination with
$\text{ranks} \times \text{threads} \le 128$ and both factors drawn from
$\{1,2,\dots,128\}$. Configurations with 16 or more threads per rank were consistently
and substantially slower, while pure OpenMP execution (a single rank) barely scaled at
all. The multi-node study therefore retains only 1, 2, 4 and 8 threads per rank; with
one thread per rank this includes the MPI-only baseline. This choice also aligns with
the ARCHER2 topology: up to 8 threads, a rank's threads fit within one or two 16-core
NUMA regions, whereas larger thread teams necessarily span NUMA boundaries.

**Fully populated nodes.** All multi-node experiments satisfy
$\text{ppn} \times \text{threads} = 128$, so that every allocated node is fully
occupied and every configuration with the same node count uses the same number of
cores. Comparisons between the four resulting per-node layouts
($128\times1$, $64\times2$, $32\times4$, $16\times8$) therefore isolate the effect of
the rank–thread balance from that of core count. This also reflects realistic usage,
since ARCHER2 allocates and charges by full node.

**Unknowns-per-core window.** A configuration at problem size $N$ on $C$ total cores is
included only if $10^4 < N/C < 10^6$. Below the lower bound, per-core subdomains are so
small that runtime is dominated by communication latency and measurement noise; above
the upper bound, runs become prohibitively long and risk exceeding queue limits, without
adding information about parallel behaviour. The window determines which node counts
are valid for each problem size, giving the experiment matrix in
Table \ref{tab:experiment_matrix}.

【批注】Table \ref{tab:experiment_matrix} 直接用 problemDesign.md 里
"5.02M: 1,2,4,8 nodes …" 那张表 + 2D/3D 网格尺寸对照表（两张可合成一张）。

Four problem sizes are used, chosen so that the largest single-node case and the
smallest 64-node case both remain inside the unknowns-per-core window:
approximately 5.0M, 10.0M, 20.25M and 41.0M unknowns. For each nominal size the 2D and
3D grid dimensions are chosen to give closely matching totals
(e.g. $4500 \times 4500 = 20{,}250{,}000$ and $273^3 = 20{,}346{,}417$), so that 2D and
3D results at the same nominal size are directly comparable.

## 3.5 Job Configuration and Thread Placement

All runs were submitted through Slurm. Each configuration is launched as

```
srun --nodes=$NODES --ntasks-per-node=$PPN --cpus-per-task=$THREADS \
     --exact --hint=nomultithread --distribution=block:block ...
```

with `OMP_NUM_THREADS=$THREADS`, `OMP_PLACES=cores` and `OMP_PROC_BIND=close`.
`--hint=nomultithread` disables simultaneous multithreading so that each thread maps to
a physical core; `--distribution=block:block` assigns consecutive ranks to consecutive
sets of cores; and the combination of `OMP_PLACES=cores` with `OMP_PROC_BIND=close`
binds each rank's threads to adjacent physical cores. Together these settings ensure
that a rank and its threads occupy a contiguous region of the node, so that for up to 8
threads per rank all threads of a rank share at most two NUMA regions and remote memory
accesses are minimised. Without explicit binding, thread migration across NUMA regions
introduces both performance degradation and run-to-run variance.

Each configuration was executed multiple times, and the median runtime is reported.
【批注】重复次数各批不一（部分 rep1，部分 rep2/rep3）。定稿前统计一下真实值，
把这句改成准确表述，例如 "between one and three times depending on cost; see the
raw logs in the accompanying repository"。对应缺口 G7。

## 3.6 Metrics

Runtime is taken from the PETSc `-log_view` summary as the maximum wall-clock time
over all ranks (`Time (sec)`), which includes matrix assembly, preconditioner setup and
the solve itself. For each (problem size, node count, layout) triple the median over
repetitions is used.

Scaling metrics are computed per layout. For a layout $\ell$ at node count $n$,

$$S_\ell(n) = \frac{T_\ell(n_0)}{T_\ell(n)}, \qquad
  E_\ell(n) = \frac{S_\ell(n)}{n / n_0},$$

where $n_0$ is the smallest node count at which that layout was run for the given
problem size (normally $n_0 = 1$). Because all layouts satisfy
$\text{ppn} \times \text{threads} = 128$, node count is proportional to core count and
$E_\ell$ is the conventional strong-scaling parallel efficiency. Note that this
definition differs from the single-core baseline used in the preliminary study of
Chapter 4: here each layout is normalised against itself, so the metric measures how
well a layout scales, while absolute runtime comparisons between layouts are made
directly on $T_\ell(n)$.

【批注】这个"和 feasibility 不同的基线定义"一定要点明，不然两章的 speedup 数字
互相矛盾会被抓。上面这段已经处理了，别删。

## 3.7 Reproducibility

All job scripts, the 3D and repeated-solve drivers, the raw PETSc logs and the analysis
pipeline (log parsing, aggregation, and figure generation in Python) are preserved in a
public repository. Every figure and table in Chapters 4–6 can be
regenerated from the raw logs with a single script invocation per analysis.
【批注】如果学校规定匿名评审，仓库链接放附录或脚注；答辩时可以现场演示。
