# 原始 log 重验记录(2026-07-16 晚)+ 周末补跑清单

> **2026-08-01 provenance update:** 本文件是 7 月 16 日历史快照。其后 G14 证明
> `ksp_2d_scaling` / `ksp_3d_scaling` 的 302/303 份日志实际 process count 与文件名
> 不符，因此其中任何 launcher-era runtime、speedup、efficiency 或 layout ranking
> 均已撤回。`KSPGMRESOrthog` 也不能单独证明 outer solver 是 GMRES，因为 GAMG setup
> 内部会产生该事件。当前状态以 `AGENTS.md`、`07_claim_evidence_map.md` 和
> `draft.tex` 为准。

> 背景:上一会话的数据结论全部基于**已删除的衍生 CSV**。本次从 ARCHER2 拉回的**原始 log**
> 逐条重验六个结论,全部一手推导、不继承旧会话。docs(draft.tex、00/01/02/04/05)已按本记录改完,
> `tectonic draft.tex` 编译通过。论文里引用相关数字时,以本文件的证据路径为准。

---

## 第一部分:六条结论的判定

### 1. size_grid 是默认 solver 且大面积未收敛 — **CONFIRMED(一处修正:子块是 ICC 不是 ILU)**

- 证据:`analysis/data/size_grid/logs/*/` 共 213 份 log,4 份 0 字节(作业失败):
  `large/...r1_t4...job13997046`、`medium/...r2_t8...job13997044`、
  `very-large/...r2_t8...job13998765`、`very-large/...r1_t2...job13997063`。
- Option table(每份 log 尾部)只有 `-ksp_converged_reason -log_view -m -n` → ex2 默认 solver。
- 事件表:`KSPGMRESOrthog` → **GMRES**;多 rank 有 `PCSetUpOnBlocks`/`PCApplyOnBlocks` →
  **block Jacobi(每 rank 一块)**;因子化事件是 `MatICCFactorSym`+`MatCholFctrNum` →
  **子块 ICC(0)(不完全 Cholesky),不是 ILU** ⚠️(串行 = 全矩阵一次 ICC)。
- 收敛:209 份有结果的 log 中 **149 份 `DIVERGED_ITS iterations 10000`**;
  **只有 small(1M)收敛**(60/62,r128 也未收敛);2240² 及以上**无一收敛**。
- ⚠️ 附带修正:未收敛 error norm 实测 **10⁰–10³**(medium-small 7.2–65 → very-large 2109–3768),
  **不是**旧稿的 "10^10"(那是已删 CSV `error_norm` 解析失败的产物)。

### 2. 迭代数只随 rank 数变、与 thread 无关且非单调 — **CONFIRMED(逐字复现)**

- @1M(`analysis/data/size_grid/logs/small/*.log` 第 1 行 "Linear solve"):
  r1=6700, r2=3715, r4=2825, r8=4085, r16=8179, r32=6460, r64=7181, r128=10000(未收敛)。
  同 rank 数下所有 thread 数(1–128)、两个 jobid(13996330/13997004)**完全相同**。
- 跨 campaign 互证 @800²:`analysis/data/mpi_only/logs/`(2026-02,job12590513)与
  `analysis/data/fixed128_multinode/logs/` nodes1(2026-07)的 r16/32/64/128 = **5052/4173/5150/6567,逐一相同**。
- 新细节:同 rank 数**跨节点摆放**漂移 <1%(r128:6567@1n / 6571@2n / 6615@4n,浮点归约顺序),
  不影响论证。
- 措辞纪律不变:非单调;跨 rank 数 runtime 只做参考;不写"块越少收敛越快"。

### 3. 纯 OpenMP 不 scale / MPI-only 对照 — **MODIFIED(定性确认;数字全部换源到 1M)**

- 旧数字(101.3s / 4311 it / 1.16× / 58.6×)出自已删的 `runs/rank_thread_grid/`,不可直接复验。
- 新来源 `analysis/data/size_grid/logs/small/`(1M,共享基线 r1_t1 = 245.7s/6700 it):
  - 纯 OpenMP(迭代恒 6700,干净对比):t8 225.5s → t32 216.5 → **t64 195.6(峰值 1.26×)** →
    t128 208.4(**1.18×**)。
  - 纯 MPI:r64 = 8.1s ≈ **30.3×**(迭代还比基线多:7181 vs 6700);r128 未收敛,剔除。
  - 满节点对角线 ms/it(KSPSolve/iters,单调):31.05(1×128)/14.36/7.20/3.65/1.88/0.98/0.60/**0.38**(128×1)。
- "中等线程优于 MPI-only" 假象维持删除:32 核 8×4 = 5.6–5.7 ms/it vs 32×1 = 4.61(两 rep 同值);
  16 核 4×4(9.6–12.0,rep 波动)与 16×1(10.4)打平。
- rep 数:t≤8 组合 2 reps,t≥16 组合 1 rep(引用时声明)。

### 4. mpi_only 贴错标签 + 1.53× 异常 — **标签 CONFIRMED;1.53× MODIFIED(间接重建)**

- 标签:`grep 'on a arch' analysis/data/mpi_only/logs/*.log` → **24/24 自报 `arch-omp-opt`**,
  `Using 1 OpenMP threads`。arch-mpi-opt 无任何留存结果 → 01 §3.1 那句保持删除。
- 1.53×:r1 实测 154.7s/4311 it(3 reps,154.2–154.7)。间接重建已删基线:
  245.7 × (4311/6700) × 0.64 = **101.2s** ≈ 已删的 101.3s → 确实慢 ~1.53×/单位工作量。
  直接同配置对比:r128_t1 KSPSolve **2.076s vs 1.659s**(fixed128 nodes1)= 1.25×。
- 规则(放宽):campaign 内部相对值可用(r1→r128 = 72×);绝对时间加"系统性偏慢 1.25–1.5×"脚注;
  跨批次绝对比较仍禁止。根因(频率 vs 绑核)待周末实验。

### 5. ksp_2d(CG+GAMG)迭代数 10–13、同规模四 layout 差 ≤1 — **CONFIRMED**

- `analysis/data/ksp_2d_scaling/logs/`(58 份单节点 log):option table 确认 `-ksp_type cg -pc_type gamg`;
  迭代数 small=11(一个 rep 10)、medium=11、large=12、very-large=12,同规模四 layout **完全相同**
  (唯一例外差 1)。
- 含多节点行的 `ksp_2d_aggregated.csv`:范围 **10–13**(13 出现在 very-large@4 节点)→
  草稿的 10–13 成立。error norm:0.012/0.031/**0.026(4500²)**/0.064 → "order 10⁻²" 成立。

### 6. ksp_3d 全部数字 — **CONFIRMED(新数据重算)**

- 从更新后的 `analysis/data/ksp_3d_scaling/csv/derived/ksp_3d_aggregated.csv` 重算,并抽查原始 log
  (64 节点 16×8:`analysis/data/ksp_3d_scaling/logs/very-large/nodes64/...job14245947_rep1.log` = 7.753s/7 it,与 CSV 一致):
  - 2 节点效率:**50.1–55.0%**(small 50.1–51.7 → very-large 53.9–55.0);旧 "51–55" 微调下界。
  - 1→2 节点:所有规模/layout **无回退**(speedup 1.00–1.10;small 64×2 最低 1.001)。
    措辞:是"无回退",**不是**"有收益"。2 节点之后每翻倍近乎理想。
  - 16×8@41M/64 节点:**34.8%≈35%**,比 32×4 慢 **10.9%≈11%**(7.75 vs 6.99s)。
  - small 有 1/2/4/8 节点(新 job 14256743–46);**所有规模的 3D 多节点行 n_runs=1**,
    1 节点基线 n_runs=3–7(新增第 7 rep 含 ~29–31s 离群值:**mean 失真,median 稳**,pipeline 用 median 无碍)。
  - 3D 迭代数范围 **6–8**(2D 是 10–13;draft 旧句 "11–12" 两边都不对,已改)。

---

## 第二部分:docs 已改动清单(2026-07-16 晚)

- `draft.tex`:§3.3 默认 solver 句(ICC + DIVERGED_ITS + 实测 norm)、迭代段加跨 campaign 互证、
  §3.4 G2 注释结案、§3.5 整节换 1M 数据源、G12 两处注释结案、§4.1 迭代范围句(10–13/6–8)、
  §4.3 3D 数字(1.00–1.10、50–55%)、G6/G7 注释。**编译通过**。
- `figures/ksp3d_*.png`:checksum 与新 plots 一致,**无需重拷**(交接文档说是旧图,实际已换过)。
- `00`:§3.3/§3.5 素材句、G1/G2/G12 行。`01`:横幅加 7/8 两条(ILU→ICC、10^10→10⁰–10³)、G12 结案。
- `02`:横幅补 3D 新数字与 ms/it 修正。`04`/`05`:solver 段、单节点表(1M)、3D 数字、缺口表、Open Q7。
- 记忆文件:两条 ⛔ 已改为"已验证+证据"。

---

## 第三部分:周末补跑清单(按优先级)

### 必跑

| # | 实验 | 配置 | 成本 | 卡住谁 |
|---|------|------|------|--------|
| **W1 = G3** | **MAP profiling 矩阵**(唯一大项) | 20.25M × {2, 8, 16 节点} × {128×1, 16×8},`ex2_repeat` + `-ksp_reuse_preconditioner -pc_gamg_reuse_interpolation true`,MAP 采样 + `-log_view` 双输出,共 6 jobs | 中 | Ch5(Profiling)§6.3–6.4 整章主体;也是解释 16×8 崩溃和 1→2 台阶的唯一手段 |
| **W2 = G1** | **default vs CG+GAMG 对照表的 GAMG 侧** | default 侧原始 log 已够(迭代+norm 都有)。补:同规模同配置的 CG+GAMG 点 —— 建议 1000² 和 4500²,各 128×1 与 32×4,2 reps ≈ 8 个短 job | 极低 | Ch3.3 的 G1 表(把"未收敛 vs 收敛"变成可引用的表) |
| **W3 = G7** | **3D 多节点重复补齐(关键行)** | 正文引用的行优先:41M@64 节点 ×{16×8, 32×4, 128×1} 各 +2 reps;每个规模的 2 节点行 ×4 layout 各 +2 reps(支撑 50–55% 和 1.00–1.10 两个区间) ≈ 20 个 job,多数很短 | 低–中 | Ch4 §4.3 所有单跑数字;Threats §7.2 |
| **W4 = G11** | **计算节点拓扑核实** | 任一作业里加一行 `lscpu; hwloc-ls --of console`(或单独 1 分钟 job) | ~0 | Ch3 的 CCX/L3/NUMA 机理论断;32×4 = "1 rank 恰好 1 个 L3" 的强解释 |

### 可选(时间富余再跑)

| # | 实验 | 配置 | 值什么 |
|---|------|------|--------|
| W5 | **1.53× 一锤定音** | 800²、1 rank×1 thread、3 reps,job 脚本里显式记录 `srun` 绑核参数与 `--cpu-freq`,再各跑一版 `--cpu-freq=2250000` 与不设频率 | 把 05 Open Q7 从"带脚注"升级为"已解释";若复现 ~101s 则坐实 mpi_only 批次环境异常 |
| W6 | **真跑一次 arch-mpi-opt** | 按 `scripts/petsc_configure_archer2.sh` 去掉两个 `--with-openmp*` 重配,800² r1–r128 各 1 rep | 让"OpenMP 构建的 t1 = MPI-only 基线"从假设变成实测(检验 `--with-openmp-kernels` 是否有 t1 开销);不跑也不伤论文,框架已改 |
| W7 = G8 | ex2_repeat solve-only scaling | 20.25M 各节点数 × {32×4, 128×1} | Ch5 §6.5 占位节;检验"含 setup 的 total time"结论对 solve-only 是否成立(回应 05 Open Q5) |

### 不用上机(平日可做,列这里防遗漏)

- **G4**:`analysis/data/ksp_2d_scaling/logs/` nodes1 vs nodes2 的 log_view 取证(VecScatter/PCSetUp)→ 1→2 台阶机理。
- **G5/G9/G10**:2D-3D 并排图、单节点 **ms/iteration** 图(数据源 `analysis/data/size_grid/logs/small/`;
  别画原始 runtime,会把迭代数假象带回来)、%T/%F 表。
