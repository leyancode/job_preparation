# 简历目录说明

> 最后更新：2026-08-05 · 本目录为本地文件，不进入任何公开仓库

## 当前状态一句话

**主投 `国内投递/CV_ai_infra_20260805`（AI Infra，一页）**，另有性能优化 / AI 平台 / HPC / Agent 四个赛道变体备用。
`海外投递/` 目前是空的——**英文简历还没有**，那边的时间线与签证硬期限见该目录下的 README。
`backup/` 只作留档，**不要从那里取文件投递**。
投递日原定 2026-08-02，截至 8/5 尚未投出；国内 2027 届秋招提前批已过大半，**这条待办的成本每天都在涨**。

## 目录结构

```
CV/
├── README.md          ← 你在这里：事实口径、生成器用法、投递前自查
├── build_cv.py        ← 全部中文变体的唯一生成器
├── 国内投递/           ← 中文简历（含自己的 README：投哪份 + 秋招时间线）
├── 海外投递/           ← 空；英文简历待建（含自己的 README：中英差异 + 英国时间线 + 签证期限）
├── ref/ai_infra/      ← 一份已进面的 AI Infra 简历，排布的参照物
└── backup/            ← 历史版本，只读
```

两个子目录各有自己的 README，讲「投哪一份、什么时候投」；本文件讲「事实从哪来、怎么生成、不许写什么」。

### 变体怎么维护（`build_cv.py`）

五份不是五个独立文档，而是**同一套事实底稿的五种排布**：

```bash
python3 build_cv.py
soffice --headless --convert-to pdf 国内投递/CV_*.docx --outdir 国内投递
```

| 变体 | 输出 | 用途 |
|---|---|---|
| `ai_infra` | `CV_ai_infra_*.docx` | ✅ **一页，主投** |
| `ai_infra_full` | `CV_ai_infra_详细版_*.docx` | 两页，面试前回读用，不投 |
| `perf` / `platform` / `hpc` | 各自 `CV_*.docx` | 两页，对应赛道 |

- 排版直接复用 `国内投递/agentCV_20260803.docx` 的 package（styles / numbering / sectPr），只换 `word/document.xml`。
  **这个文件既是投递件又是排版母版，不要删、不要改名**
- **事实只写一遍**：技能条目在 `SKILL` / `SKILL_KW` / `SKILL_1P`，项目 bullet 在 `P1` / `P2` / `P3`。
  改一个数字，五份同时生效——**不要直接编辑 docx**
- 变体差别只在 `VARIANTS`：技能段顺序、bullet 取舍、项目一标题，外加四个开关
  `courses`（关联课业段）、`skills_kw` / `skills_1p`（换技能段写法）、`stack_inline`（技术栈并进标题）、`onepage`（换短描述）
  - `perf`：技能以并行/剖析/深度学习打头，项目一先给 scaling 结论和 MAP 机理，再给审计
  - `platform`：技能以工程/调度/服务化打头，项目一先给设计与审计管线，性能结论压成一条摘要
  - `hpc`：技能含数值方法与求解器，项目一八条全给（含「局限如实标注」）
  - `ai_infra`：见下方 8/5 那节
- ⚠️ `P3[2]` 是一页版专用的合并条，与 `P3[0]` 内容重叠。`p3` 默认取 `[0, 1]`，**加新变体时别写成 `range(len(P3))`**
- ⚠️ **本机没装 Tahoma**，LibreOffice 导出的 PDF 字距与分页不等于 Word。**投递前从 Word 重新导出并确认页数**

**Agent 一页版与详细版的差别**（都只声称已实现的东西，一页版是详细版的子集，没有任何独有表述）：

- 项目一：8 条工作内容压成 6 条（分层架构与同构契约 / 中文规则 router / 确定性工具与字节级报告 / function calling 与防御式解析 / 评测与消融 / 工程化外围），只砍掉工程纪律那条
- 项目二：5 条压成 2 条，只留根因诊断与负结果自我批判
- 技术能力：7 行并成 4 行
- 排版：去掉 `docGrid` 行网格（11pt 段落原本被吸附到两个网格行，行距凭空翻倍——这一项零内容损失就省了一整页）；正文统一 9.5pt；上下页边距 0.4cm；论文标题行内联

### 技术能力段的写法（8/3 修正，容易写回去的坑）

技能段一度把项目 bullet 里做过的事又复述一遍——"实做 FastAPI 接口层""实现 IDF 加权词法检索并刻意未引入向量检索""防御式解析与依赖注入""离线评测集设计与消融实验"，全都在项目 bullet 里逐字出现过。

**规则：技能段只写项目段证明不了的东西**（语言、工具、了解性知识、概念理解），做过的事交给项目段用细节去证明。重复不增加可信度，只挤占本该写实现的行数。同理，"规则 83.3%、LLM 100%"只在项目描述里出现一次，评测 bullet 里承接消融的 63.3% 即可。

## 项目底稿的真实进度（简历口径的来源）

简历声称的内容都必须能在这三个仓库里找到对应实现。

**hpc_benchmark_archer2**（github.com/leyancode/hpc_benchmark_archer2，已公开）

- ARCHER2 上 PETSc hybrid MPI+OpenMP 布局对照，2D/3D、5M–165M unknowns、**最多 32 节点 / 4,096 核**
- 正式结论只用 **408 个通过内容审计的 run**（264 weak-scaling + 144 fixed-size strong-scaling）
- 头条数：2D weak `64×2` 在 11 个点赢 8 个、165M/32 节点 **794.8M eq/s（+13.1%）**；3D weak `32×4` 最大 **+33.2%**；
  2D fixed-20M `64×2` **0.0277 s/solve、29.83×、93.2%**；3D fixed-20M `16×8` **0.0681 s/solve、14.24×**，比 flat MPI 快 3.81×
- 方法论卖点：Phase 2 的 **302 / 303** 份日志 process count 与文件名失配 → 整阶段性能曲线作废；MAP 占比 MPI 46.7%→6.2%、OpenMP 等待 48.3%→76.5%
- MAP 数字来自 instrumented runs，**只解释布局之间的排序，不与未插桩 timing 混用**
- CI：GitHub Actions 跑公开数据 pytest + fake Slurm 执行提交脚本

**hpc-benchmark-agent**（github.com/leyancode/hpc-benchmark-agent）

- P1 确定性分析工具 + 中文规则 router + CLI · **已完成**
- P2 LLM function calling + 30 问五类中文评测集 · **已完成**
- P3 结构化 tracing + FastAPI `POST /ask` + 最小 RAG（词法检索）· **已完成（RAG 于 2026-08-03 合入 main）**
- 测试：**229 passed**，全程离线、不需要 API key

**marl-value-factorisation**（github.com/leyancode/marl-value-factorisation）

- 本科毕业设计（COMP390，利物浦大学，2025 年完成）
- 2026 年整理为作品集仓库：修正 Predator-Prey 合作边界、uv.lock 锁 CPU 版 PyTorch、补 pytest、接入 GitHub Actions CI

## 2026-08-03 这次改了什么（agentCV）

**修事实**

- 教育背景自相矛盾修掉：学历行原写 `2025.09 – 2026.11`，同一行末尾却写"学位证书 2026.12 获得"。已统一为 **2026.12**
- 测试数 165 → **229**
- 技术栈删掉 `ePyMARL`：仓库 `UPSTREAM.md` 只记录基于 Oxford WhiRL 的 **PyMARL**，写 ePyMARL 会被追问到答不上

**补 P3 两项实做**（新增两条 bullet）

- FastAPI 薄封装 `POST /ask`：只做协议转换、约束写进类型（非法 router 由 Pydantic 拦为 422）、缺 key 映射 503 而非 500、与 CLI 的退出码 2 各自独立
- 最小 RAG（词法检索）：IDF 加权词重叠、中文取相邻 bigram、纯标准库零新依赖、**刻意不用向量库**、检索不到返回空不注入、未开启检索时 messages 与评测时逐字节一致并由测试锁死

**技术能力段**

- 「RAG 与向量检索」→「**RAG 与检索**」：原文写"因此未引入"，RAG 落地后这句就成了假话。改为"实现了词法检索，并刻意未引入向量检索"，并说明两者在可解释性 / 冷启动 / 同义词召回上的取舍
- 「后端与系统设计基础」：从纯"了解"改为"实做了 FastAPI 接口层"

**MARL 项目整段重写**（改动最大的一处）

原来 7 条全是"探索…""评估…""分析…"这类没有结论的动词，一个数字都没有。换成 5 条有结论的，全部扣着仓库 README 的真实实验：

- 三种 critic 变体**对齐成单变量对照**（共用 runner / buffer / actor 与全部 PPO 超参，只换 critic 分支）
- 反直觉结论：Predator-Prey 上 VDN 唯一转正（≈150），单体 critic 始终为负（−300 → −30），QMIX critic loss 起手 5.4×10⁴、200k 步后二次发散
- 根因诊断：QMIX 的 TD 目标沿用 `max_a Qᵢ` 而 actor 是 on-policy，td_error 不是合法 advantage 而是系统性偏乐观
- 负结果与自我批判：non-monotonic mixer 梯度爆炸如实写进论文；三个 learner 其实都只产出共享标量 advantage，收益来自表示与梯度路径而非真正的 per-agent credit assignment
- 2026 作品集化的工程动作

## 2026-08-03 这次改了什么（HPC 简历，另一台机器 · 已由 8/4 版取代，留作记录）

- 新增两页 HPC / 科学软件详细版和一页 HPC+AI Infrastructure 投递版；两份都通过 Microsoft Word PDF 导出和逐页视觉检查
- 项目链接统一为 `leyancode/hpc_benchmark_archer2`，教育日期和可入职时间与 Agent 简历一致
- 第二个项目改为已经实现的 Agent 系统；删除 Redis、FAISS/Chroma、LangChain/LlamaIndex、MySQL 优化和 Docker 健康检查等未实现声称
- HPC 数字改用经过审计的 Phase 3 正式结果；旧的 64 节点、8192 核、26.1x 和「`32x4` 始终最优」来自 launcher-era 数据，已被 process-count 审计推翻，**禁止恢复**
- 增加 `302/303` launcher 失配、408 个 accepted formal runs、weak/strong scaling 和 MAP instrumented-run 边界

## 2026-08-04 这次做了什么（三个岗位变体）

旧 `CV_hpc.docx` 的四条待办**全部处理完毕**，文件已移入 `backup/`：

1. ~~第二个项目整段是未实现声称~~ —— Redis / TTL、FAISS / Chroma、LangChain / LlamaIndex、MySQL 查询优化、Docker、健康检查、缓存命中追踪、图表生成、Obsidian 报告，一条都没留。改用 agentCV 已验证的口径重写成 3–4 条
2. ~~GitHub 链接是 `lionleepower`~~ —— 全改 `leyancode`，两个仓库都已 curl 验证 200（公开）
3. ~~教育背景 `2025.09 – 2026.09 预计`~~ —— 改成 2026.12 + 课程 2026.08 完成 + 可入职 2026.09.01
4. ~~petsc 项目规模被严重低估~~ —— 注意：**这条待办本身写错了**。它记的是"64 节点 / 8,192 核、40.96M unknowns、26.1× 加速"，而仓库现在的真实数据是 **32 节点 / 4,096 核、5M–165M unknowns、29.83× 加速**。现按仓库 README 重写，见上方「项目底稿的真实进度」

另外把 `hpc_benchmark_archer2` 从"一个 benchmark 项目"改写成 **AI infra 听得懂的语言**：集合通信开销（halo exchange / CG global reduction ≈ allreduce）、通信暴露与线程空转的权衡、每核工作量下降后的收益递减与饱和点、拓扑亲和与线程绑定。不虚构任何 GPU 经历，GPU 相关只出现在技能段的"了解"层面。

### 仍未解决的一条：agentCV 的「数据侧」括号

`agentCV_20260803` 项目描述里那句 —— **「数据侧：单核 245.7s → 128 核 3.866s、并行效率 49.7%，并识别出 2 / 4 核超线性加速与 32 核 hybrid 的效率坍缩至 0.33」** —— 与 `hpc_benchmark_archer2` 自相矛盾：

- 这批数是 agent 仓库 `examples/sample.csv` 的 Phase 1 `scaling_grid` 数据
- 而 archer2 README 明写 Phase 1「default GMRES + block Jacobi/ICC 会随 MPI rank 数改变 preconditioner」「**128-rank 点没有收敛**」，只能当每迭代成本的线索，**不做跨 rank 布局排名**
- CSV 里也能直接看出来：迭代数随 rank 从 6700 跳到 2825，`error_norm` 字段是 `error`

**两份简历投同一家公司，面试官交叉读会撞上这一处。** 建议把括号整段删掉或改成中性表述（例如"数据来自 ARCHER2 上 PETSc scaling 实验的真实导出"）—— agent 项目的卖点是评测与工程，不是那个加速比。三个新变体里都没有复述这个数字。

## 2026-08-05：新增 ai_infra 变体（对标 `ref/ai_infra` 的进面简历）

参照物是 `ref/ai_infra/CV-reference.jpg`——佐治亚理工硕士、三段 ML Infra 实习。
**不去模仿它的经历**（那是三段大厂实习，抄不来），只搬它的**排布与信息密度**。四处结构性差异：

| 差异 | 原来 | 现在 |
|---|---|---|
| 关联课业 | 没有这一段 | 教育背景下加一行主题名，把 MPI / OpenMP / HPC 体系结构 / **GPU 编程** / 机器学习 提到第一屏 |
| 技能段 | 4–6 条散文，每条 3–4 行，关键词埋在句子中间 | `SKILL_KW`：工具关键词打头 + 一句能力边界，六行扫得完 |
| 技术栈 | 每个项目一整行「技术栈：…」 | 内联进项目标题（`｜C · PETSc · MPI · …`），三个项目省三行 |
| bullet | 标签 + 3–4 行叙述，数字散在中后段 | 数字前置：第一条 bullet 开头就是 794.8M eq/s / +13.1% / 29.83× / 93.2% |

**参考简历真正赢在哪**（看清楚，别只学表面）：每条 bullet 都是「做了什么 + 量化结果 —— 机制是什么」，
**结果在破折号前面，机制在后面**，一条里塞 2–3 个数字（`eager −51%`、`torch.compile −25%`、`28%→<5%`、`55%→94%`）。
你的 ARCHER2 数字密度其实不输它，问题只是被散文稀释了、且数字埋在句子中后段——
所以这次是重排，不是重写，**一个事实都没新增**。

**一页版怎么砍的**（`ai_infra`，投递用这份）：不是每个项目都对齐参考简历的条数，而是每个项目只留最核心的：

- 技能六行 → 四行（`SKILL_1P`）：并行与剖析并成一条，深度学习与 GPU 并成一条
- 项目描述只交代「问题是什么」，**所有结论一律下放到 bullet**
- 项目一 6 条 → 3 条：布局选型（数字）/ 机理归因（MAP）/ 可信度门禁（302-303 审计 + 工程化）
- 项目二 4 条 → 2 条：可评测的路由（83.3% / 100% / 63.3%）/ 防御式解析与工程化
- 项目三 2 条 → 1 条：反直觉结论 + 根因 + 负结果压成一条
- 两页详细版留作 `ai_infra_full`，**一页版是它的子集，无任何独有表述**

**GPU 那条技能的写法**：`GPU 与推理服务（课程与自学）：CUDA 编程模型…NCCL…数据 / 张量并行…KV cache 与量化`。
`（课程与自学）` 这个限定必须留着——它是全篇唯一没有项目 bullet 背书的技能，不标层级就是超范围声称。
但也**不要写成「尚无生产经验」**，那是在简历上自我淘汰。

⚠️ **投递前必须核对 `COURSES`**：里面的课程主题名是按「修过 MPI/线程/HPC 架构类 + GPU/加速器类 + 数据科学/ML 类」
这个口径写的，**没有逐条对过成绩单**。没修过的直接删，不要为了关键词留着——这一段最容易在面试里被追问细节。

**这份的短板（已知，不要自欺）**：参考简历有三段 ML Infra 实习，你没有实习；
它有 vLLM / DeepSpeed / Triton / Nsight / H100 的实操，你的 GPU 只到「了解」层。
唯一能真正补上这一格的是 `llm_inference_archer2`——管线和 34 项测试已完成、仓库已公开，但 `runs/` 还是空的，
**一个正式数字都没有，所以这次没放进简历**。跑完 `docs/PLAN.md` 的阶段一（STREAM 带宽基线）+ 阶段二（布局扫描）
就能加一个带数字的 LLM 推理项目，那是目前投产出比最高的一步。

## 关键事实口径（所有简历必须一致）

| 项 | 口径 |
|---|---|
| 课程与毕业论文完成 | 2026.08 |
| **可入职时间** | **2026.09.01**（比多数海外硕士早，务必写出来） |
| 学位证书获得 | 2026.12 |
| GitHub | `leyancode`（`lionleepower` 是死链） |
| 评测数字 | 规则 router 83.3% · LLM router 100% · 无 system prompt 消融 63.3% |
| 评测条件 | qwen3.7-plus · temperature 0 · 单次运行 · 题量 30 |
| ARCHER2 实验规模 | **32 节点 / 4,096 核**、5M–165M unknowns、**408 个通过审计的 run** |
| ARCHER2 头条数 | 2D weak +13.1%（794.8M eq/s）· 3D weak 最大 +33.2% · 2D fixed-20M **29.83× / 93.2%** · 3D `16×8` 比 flat MPI 快 3.81× |

被追问"100% 可信吗"时主动给局限：**题量 30、出题人即作者、单模型单次运行**。

被 HR 追问"12 月才发证怎么 9 月入职"时：课程和论文 8 月全部完成，9 月起可全职；入职提供成绩单 + 课程完成证明（Completion Letter），证书后补。学历认证需凭证书办理，因此在 12 月之后 —— 如某家公司明确要求入职前完成认证，那是硬门槛，提前问清楚。

## 投递前自查

- [ ] 全文搜"进行中""接入中" —— 应为 0 处
- [ ] 所有 GitHub 链接**在无痕窗口逐个点开**（无痕是为了避开自己的登录态：你能看见的 private 仓库，面试官看到的是 404）
- [ ] 简历声称的每个模块都能在仓库里指出对应实现 —— **不声称未实现的模块**是硬约束
- [ ] 毕业时间与可入职时间两个都在，缺一不可
- [ ] demo 三分钟可复现：clone → `pytest`（229 passed）→ `ask` → `report`
- [ ] 另存为新文件名，不覆盖上一版；上一版移入 `backup/`
- [ ] 五个变体：**改事实改 `build_cv.py` 再重新生成，不要手改 docx**（手改会让五份漂移）
- [ ] ai_infra 专有：`COURSES` 逐条对过成绩单；GPU 技能条的「（课程与自学）」限定还在
- [ ] **从 Word 导出 PDF 并确认页数**——本机无 Tahoma，LibreOffice 的分页不作数
- [ ] 同一家公司只投一份 —— 所有简历的 Agent 项目都是同一个仓库，多份一起投等于自曝口径差异
