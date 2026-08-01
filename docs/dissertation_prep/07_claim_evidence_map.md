# 论点–图表对照表（Step 0）

> 更新日期：2026-08-01。现有正式数字从
> `analysis/data/nproc_{2d,3d}_libsci/csv/derived/repeated_fullnode_formal_summary.csv`
> （2026-07-30 审计版，各 44 行 = 11 size–node 点 × 4 layout）重新算出，已与
> `draft.tex` 逐条核对。
>
> **用途**：先定论点，再定图表，最后写字。任何不在本表里的图都不要生成；任何在本表
> 里但状态不是 ✅ 的论点，都还不能写进正文。
>
> 状态图例：✅ 证据齐全可写 · 🔧 数据齐全但图/表需重生成 · 🆕 需新建 · ❌ 无证据，
> 不得断言

---

## A. 图表清单

### A.1 图

| ID | 章 | 内容 | 数据源 | 状态 |
| --- | --- | --- | --- | --- |
| **F1** | Ch2 | ARCHER2 节点层次结构 | `figures/archer2.png` | ✅ 已在正文 |
| **F2** | Ch3 §3.5 | 共同基线出发的两条线：pure OpenMP vs MPI-only（speedup vs cores） | `data/size_grid/logs/small/*.log` | 🆕 TODO(G9) |
| **F3** | Ch5 | 2D 吞吐 vs 节点数，**按 unknowns/core 双波段分面板** | 2D formal summary | 🔧 PNG 已有，缺 PDF |
| **F4** | Ch5 | **2D 每迭代时间 / 128×1 基线，双波段** | 2D formal summary | 🔧 PNG 已有，缺 PDF |
| **F5** | Ch5 | 2D 吞吐 vs NPROC | 2D formal summary | 🔧 旧图，需决定去留 |
| **F6** | Ch5 | 3D 吞吐 vs 节点数，双波段 | 3D formal summary | 🔧 PNG 已有，缺 PDF |
| **F7** | Ch5 | **3D 每迭代时间 / 128×1 基线，双波段** | 3D formal summary | 🔧 PNG 已有，缺 PDF |
| **F8** | Ch5 | 3D 吞吐 vs NPROC | 3D formal summary | 🔧 旧图，需决定去留 |
| **F9** | Ch6 | MAP 时间线 / OpenMP 线程活动 | `analysis/maps/nproc_2d_libsci/profiled/` | ❌ 未分析 |
| **F10** | Ch5 | 2D 固定 20m、1–32 节点 strong scaling：runtime / speedup / efficiency | `nproc_2d_libsci` strong summary（24 行） | ✅ PNG/PDF 已生成，72/72 log 审计通过 |
| **F11** | Ch5 | 3D 固定 20m、1–32 节点 strong scaling：runtime / speedup / efficiency | `nproc_3d_libsci` strong summary（24 行） | ✅ PNG/PDF 已生成，72/72 selected log 审计通过 |

**F4 是全文最强的一张图**，它是 Ch5 和 Ch7 的论证主轴。F7 是它的 3D 对照，两张必须并排出现，因为结论相反。

**F5/F8 的去留建议：删。** NPROC 轴在双波段重构后是冗余的——同一节点数下四个 layout 用相同的核，NPROC 差 8 倍这件事，F4/F7 的比值图已经表达得更直接。保留会稀释论证。若要保留，只留 2D 一张放附录。

### A.2 表

| ID | 章 | 内容 | 数据源 | 状态 |
| --- | --- | --- | --- | --- |
| **T1** | Ch5 | 已验证实验矩阵（scale × 2D/3D 网格 × 未知数 × 节点数） | 手写 | ✅ 已在正文 `tab:fullnode-matrix` |
| **T2** | Ch3 §3.3 | default solver vs CG+GAMG：error norm / 迭代数 / 收敛与否 | `size_grid` + `ksp_2d_scaling` 原始 log | 🆕 缺口 G1 |
| **T3** | Ch3 §3.3 | 迭代数 vs rank 数（默认 solver，证明预条件子随 rank 变） | `data/size_grid/logs/small/*.log` | 🆕 正文现为八个数字的散文 |
| **T4** | Ch3 §3.5 | 满节点每迭代成本 vs layout（1×128 … 128×1） | 同上 | 🆕 正文现为八个数字的散文 |
| **T5** | Ch5 | **2D 双波段端点比值表**（F4 的配套证明表） | 2D formal summary | 🆕 |
| **T6** | Ch5 | **3D 双波段端点比值表**（F7 的配套证明表） | 3D formal summary | 🆕 |
| **T7** | Ch5 | 每点最优 layout + 相对 flat MPI 增益 + 三次重复实测幅度 | `tables/repeated_fullnode_best_layouts.csv` | 🔧 CSV 已有 |
| **T8** | Ch5 | 节点翻倍 speedup（按 scale × layout） | formal summary | 🔧 |
| **T9** | Ch6 | 单点 %T / %F / GF/s per event | 单份 log_view | ✅ 已在正文 `tab:tf`（仅单点） |
| **T10** | Ch5 | 固定 20m strong-scaling 端点、speedup 与 efficiency | F10/F11 的已审计 aggregate | 🔧 2D/3D endpoint CSV 均已有，需排入正文 |

**T3/T4 必须补。** 正文现在把八个数字排成散文（`draft.tex` 第 418–422、523–527 行），这是全文可读性最差的两处，且 §3.3 那个"默认 solver 下问题 ill-posed"的核心论证完全压在 T3 上。draft 里已有 `% TODO` 承认这一点。

---

## B. 按章论点表

### Ch3 方法学

| # | 论点 | 支撑 | 关键数字（已核验） | 状态 |
| --- | --- | --- | --- | --- |
| C3.1 | 默认 solver 在 5.0M 及以上全部不收敛，因此必须换 | T2 | 209 份有结果的 log 中 149 份 `DIVERGED_ITS 10000`；error norm 10⁰–10³ | 🔧 数字已验，缺表 |
| C3.2 | block Jacobi 块数 = rank 数 ⇒ 换 layout 即换预条件子 ⇒ "哪个 layout 最快"ill-posed | **T3** | 迭代数只随 rank 变、与线程无关：1→6700（1/2/4/128 线程皆然），2→3715，4→2825，8→4085，16→8179，32→6460，64→7181，128→顶 10000 上限 | 🔧 数字已验，缺表 |
| C3.3 | GAMG 解除该耦合，使 Ch5 的跨 layout 比较成立 | 正文 + T1 | 2D 9–13 次，3D 6–7 次；同点跨 layout 最多差 2 次（2D）/ 1 次（3D） | ✅ |
| C3.4 | 纯 OpenMP 不 scale | **F2** | 1 rank 全程 6700 次迭代：245.7 s(1t) → 195.6 s(64t, 峰值 1.26×) → 208.4 s(128t) | 🔧 数字已验，缺图 |
| C3.5 | 每迭代成本随 rank 数单调下降 ⇒ 排除 ≥16 线程/rank | **T4** | 满节点 ms/it：31.05(1×128) / 14.36 / 7.20 / 3.65 / 1.88 / 0.98 / 0.60 / 0.38(128×1) | 🔧 数字已验，缺表 |
| C3.6 | 绑核方案（`OMP_PLACES=cores` + `close` + `block:block` + `--exact`）由拓扑推出 | 正文 | — | 🆕 draft 现为 TODO |

> ⚠️ **C3.5 的机制解释仍不可写。** draft 现有措辞暗示 NUMA，但 16 线程恰好**填满**一个
> 16 核 NUMA 区而非跨越两个；真正跨越的是 CCX/L3 边界（4 核 / 16 MB）。见
> `TODO(G11)`。在计算节点上跑一次 `lscpu` / `hwloc-ls` 即可解决，不排队。

### Ch5 结果（**主要改动集中在这里**）

| # | 论点 | 支撑 | 关键数字（已核验） | 状态 |
| --- | --- | --- | --- | --- |
| C5.1 | 11 个 size–node 点恰好构成两条固定 unknowns/core 的弱扩展链 | T1 + F3 | ~40k 链：5m/1→10m/2→20m/4→41m/8→82m/16→165m/32（6 点）；~80k 链：10m/1→20m/2→41m/4→82m/8→165m/16（5 点） | 🆕 **新论点** |
| C5.2 | **2D：hybrid 优势沿弱扩展线随节点数单调增长** | **F4 + T5** | 见下方 §C | 🆕 **新论点，最强结果** |
| C5.3 | 2D：64×2 是全程最优 layout | F4 + T7 | 每迭代时间在 11/11 点最低；原始吞吐 8/11 点最高（128×1 占其余 3 点） | ✅ |
| C5.4 | 2D：16×8 从不获胜，但劣势随规模收窄 | F4 | 比值从 1.674(5m/1n) 收窄到 1.294(165m/32n) | 🆕 收窄趋势是新的 |
| C5.5 | 2D 最大并发点 | T7 | 165m/32 节点：64×2 = 794.8 M eq/s，比 flat MPI 高 **13.1%** | ✅ |
| C5.6 | **3D：优势大得多但非单调** | **F7 + T6** | 六条序列全部非单调；最大增益 33.2%（32×4 @ 41m/4n）远超 2D 的 14.7% | 🆕 **新论点** |
| C5.7 | 3D：32×4 略优于 64×2，但最大并发点反转 | F7 + T7 | 原始吞吐 32×4 赢 6 点 / 64×2 赢 4 点 / 128×1 赢 1 点；每迭代 7/3/1 | ✅ |
| C5.8 | 3D 最大并发点 | T7 | 165m/32 节点：64×2 = 510.4 M eq/s，比 flat MPI 高 **30.1%** | ✅ |
| C5.9 | 节点翻倍 speedup | T8 | 2D 2.00–3.08（含超线性）；3D 1.46–2.39 | ✅ |
| C5.10 | 三次重复只支持实测幅度，不支持显著性 | F3–F7 误差棒 | 最大三次重复幅度：2D **4.71%**，3D **3.83%** | ✅ |
| C5.11 | 固定 20m 可形成 1→32 节点的长 strong-scaling 曲线 | F10/F11 + T10 | 2D：64×2 @32n = 0.0277 s/solve、29.83×、累计 93.2%、16→32 为 62.9%；3D：16×8 @32n = 0.0681 s/solve、14.24×、累计 44.5%、16→32 为 74.6% | ✅ **匹配曲线可写；不得把 32n 饱和点泛化为机器极限** |

### C5.2 / C5.6 的证据（T5 / T6 的内容）

每迭代时间 ÷ 128×1 基线，`< 1` 表示 hybrid 更快：

**2D ~40k unknowns/core**

| layout | 5m/1n | 10m/2n | 20m/4n | 41m/8n | 82m/16n | 165m/32n | 趋势 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 64×2 | 0.957 | 0.946 | 0.931 | 0.913 | 0.872 | 0.885 | 5 步中 4 步下降 |
| 32×4 | 1.096 | 1.093 | 1.059 | 1.003 | 0.944 | 0.937 | **完全单调** |
| 16×8 | 1.674 | 1.619 | 1.529 | 1.462 | 1.341 | 1.294 | **完全单调** |

**2D ~80k unknowns/core**

| layout | 10m/1n | 20m/2n | 41m/4n | 82m/8n | 165m/16n | 趋势 |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| 64×2 | 0.995 | 0.993 | 0.978 | 0.954 | 0.949 | **完全单调** |
| 32×4 | 1.074 | 1.055 | 1.055 | 1.027 | 1.004 | 一次持平 |
| 16×8 | 1.420 | 1.391 | 1.377 | 1.351 | 1.296 | **完全单调** |

六条序列中四条完全单调，另两条各只有一次微小反转（64×2 的 0.872→0.885；32×4 的
1.055→1.055）。**32×4 在 ~40k 链上于 41m/8 节点处穿过 1.0 线**，这是"何时该开始用
hybrid"的可引用阈值。

**3D ~40k unknowns/core**

| layout | 5m/1n | 10m/2n | 20m/4n | 41m/8n | 82m/16n | 165m/32n |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 64×2 | 0.877 | 0.795 | 0.915 | 1.022 | 0.908 | 0.768 |
| 32×4 | 0.893 | 0.781 | 0.844 | 0.958 | 1.070 | 0.837 |
| 16×8 | 1.097 | 0.914 | 0.973 | 1.085 | 1.122 | 1.064 |

**3D ~80k unknowns/core**

| layout | 10m/1n | 20m/2n | 41m/4n | 82m/8n | 165m/16n |
| --- | ---: | ---: | ---: | ---: | ---: |
| 64×2 | 0.852 | 0.788 | 0.818 | 1.008 | 1.005 |
| 32×4 | 0.843 | 0.784 | **0.751** | 0.863 | 1.047 |
| 16×8 | 1.035 | 0.919 | 0.899 | 0.993 | 1.082 |

3D 六条序列**全部非单调**：优势在 2–4 节点处最大（最低 0.751 = 快 33.2%），到 8–16
节点退回 ~1.0，165m/32 节点又回落到 0.768。

### Ch7 讨论 / Ch8 结论

| # | 论点 | 依赖 | 状态 |
| --- | --- | --- | --- |
| C7.1 | 2D 与 3D 的**趋势形状**不同，不只是最优 layout 不同 | C5.2 + C5.6 | 🆕 替换现有"两者都偏好适度混合"的弱表述 |
| C7.2 | 实用建议：2D 用 64×2；3D 在 32×4 / 64×2 之间按规模选 | C5.3 + C5.7 | ✅ |
| C7.3 | 16×8 在任一维度都不获胜，采用需工作负载专属证据 | C5.4 | ✅ |
| C7.4 | 单调趋势**提示**通信占比机制，但未证明 | C5.2 | ⚠️ 只能写"consistent with"，不能写因果 |
| C7.5 | 链接 LibSci ≠ 该路径调用了 BLAS ≠ LibSci 造成了 layout 排序 | — | ✅ 现有措辞已正确 |
| C7.6 | 早期 launcher-era campaign 为何作废 | Ch3/附录 | 🆕 建议新增小节，是加分项 |

---

## C. 因 Ch5 重构而必须改动的现有正文

| 位置 | 现状 | 处理 |
| --- | --- | --- |
| `draft.tex` §5.4 `sec:strong-steps` | "Each size spans only one doubling, so these results establish a local scaling step rather than a long strong-scaling curve." | **删**。双波段重构后有 6 点和 5 点的完整链条，这句自我设限不再成立 |
| `draft.tex` §5.7 `sec:mn-interp` | "no monotonic relation links fewer MPI endpoints to higher throughput" | **改**。跨 layout 在单点上确实非单调；但**沿弱扩展线每个 layout 的比值在 2D 单调**。两件事要分开说 |
| §5.2 / §5.5 的"11 点里赢 N 点" | 数点式论证 | **降级**为 T7 的表注，正文改用 C5.2/C5.6 的趋势论证 |
| §5.3 `sec:iteration-normalised` | 独立成节 | **并入** F4 的讨论——比值图已经内含迭代归一化 |
| Abstract | "highest raw throughput at eight of 11 size–node points" | 改为趋势表述 + 保留 13.1% / 30.1% 两个端点数字 |
| Ch8 §8.1 | 同上 | 同上 |
| §5.2 NPROC 段 + F5/F8 | 两张 NPROC 图 | 建议删，理由见 A.1 |
| `draft.tex` 第 393 行 `% VERIFIED` 注释 | "KSPGMRESOrthog => GMRES" | **改**。该事件在 140/140 份已确认 CG 的 libsci log 中同样出现（GAMG setup 内部用 GMRES 估特征值）。判别式应为 `MatICCFactorSym`（size_grid 209/209，GAMG 组 0），且外层 solver 必须限定在 `RepeatedSolves` stage 内读 |

---

## D. 执行进度

**已完成（2026-07-31）**

1. ✅ 路径常量指向 `analysis/data/nproc_{2d,3d}_libsci/logs/repeated_fullnode/`，
   新版落到文档化位置 `scripts/nproc_{2d,3d}_libsci/`。逐位复现验证通过：
   2D 44×24、3D 44×23 列与已审计 CSV 完全一致，只多 `upc_band` 和
   `weak_scaling_efficiency`。`analysis/.venv` 已重建。
2. ✅ plots/scripts 半迁移状态清理完毕，重复项移入 `.trash/2026-07-31/`。
3. ✅ 12 张图重新生成（PNG+PDF 成对），`sync_figures.sh` 建立，
   `\graphicspath` 改为只指 `figures/`，6 处 `\includegraphics` 改名。
4. ✅ Ch5 重写：波段弱扩展框架 + vs-MPI 比值图主导 + 新增 T2（波段表）、
   T3（弱扩展效率表）。F5/F8（vs-NPROC）已删除并入回收站。
5. ✅ Abstract / Ch7 / Ch8 同步改写为趋势论证。
6. ✅ `\listoffigures` / `\listoftables` 启用（7 图 4 表）。构建：31 页，0 错误。

7. ✅ **T3/T4/F2 完成**（表 3.1 迭代数 8×8 三角表、表 3.2 满节点每迭代成本、
   图 3.2 单节点双线图）。生成脚本
   `analysis/scripts/size_grid/analyze_single_node_sweep.py` 会在
   「固定 rank 数下迭代数不恒定」时直接报错，把 §3.3 的核心论证变成可执行断言。

8. ✅ **固定 20m strong scaling（2026-08-01）**：2D 与 3D 均为 72/72 selected
   log 审计通过，F10/F11 及两维端点 CSV 均已生成。2D 的 2/4 节点新旧中位数
   最大差 2.2%；3D 为 0.3–3.1%，且 8/8 组 min–max 区间不重叠，因此旧行只作
   temporal check，不与同场六节点曲线合并。

**✅ G14 已了结 —— 这就是 "launcher-era" 的具体含义**

我一度认为 `ksp_{2d,3d}_scaling` 与正式 campaign 构成 BLAS 单变量对照，并据此提出
"线程化 LibSci 可能翻转全部布局结论"。**该结论错误，已撤回。**

真实原因：那两批 campaign 的 **layout 从未生效**。每份 PETSc 日志都自述
`on a <arch> named <node> with <N> process`；把 N 与文件名里的 rank 数对照：

| campaign | 不一致 / 总数 |
| --- | --- |
| `ksp_2d_scaling` | **141 / 142** |
| `ksp_3d_scaling` | **161 / 161** |
| `nproc_2d_libsci`（正式） | 0 / 140 |
| `nproc_3d_libsci`（正式） | 0 / 140 |

绝大多数只跑了 **1 个 MPI 进程**，而文件名写着 16/32/64/128。所以那两批数据里
任何跨 layout 的比较都无意义——所谓"线程越多越快"只是"实际起了几个进程"的映射。
它们比正式运行慢 20–50 倍也与此吻合。

**教训**：`petsc-campaign-provenance` skill 已经写明"信日志内容不信文件名"，但我
只核对了 arch 和 solver，**没核对进程数**。这一条现在补进了 skill 和 AGENTS.md，
且被列为分析任何 campaign 的第一步。

正式 campaign 的结论不受影响，反而更稳固：`draft.tex` §3.8 已改用这个更强也更简单的
理由，并接上 §3.9 的验证契约（280/280 全部通过进程/线程数核对）。

**⛔ 阻塞项：TODO(G13) 容差问题**

四个 driver 都从上游 ex2 继承 `rtol = 1e-2/((m+1)(n+1))`（3D 再乘 `(p+1)`），
在 `KSPSetFromOptions` 之前设置。Phase 1 的作业脚本
`run_ex2_size_grid.sbatch:137` 用**双横线** `--ksp_rtol 1e-5` 覆盖，而同一命令
前一行的单横线选项确认生效。

间接证据指向双横线被忽略：800²（无 rtol，mesh rtol 1.56e-8）r16/32/64 =
5052/4173/5150、r128 = 6567 收敛；1000²（有双横线）= 8179/6460/7181、r128 顶死
10000。真的 1e-5 比 1.56e-8 松三个数量级，迭代数应大跌，实测反升 39–62%。

**判定方法**（几秒，不排队）：
`ex2 -m 1000 -n 1000 --ksp_rtol 1e-5 -options_left -ksp_view`

**影响范围**：只影响 Ch3 的「默认 solver vs GAMG」叙事（若成立，两者差异同时包含
solver 和容差两个变量，是 confound，须写进 §7.2）。**不影响 Ch5** —— Phase 3 全部
用单横线 `-ksp_rtol 1e-5`，四种布局容差一致。

正文中 "The solver was changed rather than the tolerance relaxed" 一句已删除，
待判定后再决定措辞。**T2（default vs GAMG 对比表）押后到这个问题解决之后**，
因为它的全部内容就是这个对比。

**其余待办**
- ❌ **Ch6 §6.4 Bottleneck Identification** 目前为空，依赖 MAP 矩阵分析。
- ⚠️ **TODO(G11) 拓扑核实**：在计算节点跑 `lscpu` / `hwloc-ls`，不排队。
  这是唯一挡住机制论证的廉价实验。
- ✍️ Ch1 Contributions / Ch3 §3.6 §3.7 / 附录。
- ✍️ 新增"早期 launcher-era campaign 为何作废"小节（C7.6，加分项）。
