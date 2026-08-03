# 简历目录说明

> 最后更新：2026-08-03 · 本目录为本地文件，不进入任何公开仓库

## 当前状态一句话

**Agent、HPC 详细版和 HPC+AI Infra 一页版均已完成。** 旧 `CV_hpc` 只保留作修改前基线，不要投递。

## 目录里有什么

| 文件 | 赛道 | 状态 |
|---|---|---|
| `agentCV_20260803.docx` / `.pdf` | Agent / LLM 应用（主投） | ✅ **一页版，投递用这份** |
| `agentCV_20260803_详细版.docx` / `.pdf` | 同上 | 三页，内容更全；面试前自己回读、或对方明确要长版时用 |
| `CV_hpc_ai_infra_20260803.docx` / `.pdf` | HPC + AI Infrastructure | ✅ **一页投递版**；性能平台、AI Infra、HPC 工具链与混合岗位 |
| `CV_hpc_20260803_详细版.docx` / `.pdf` | HPC / 科学软件 / 性能工程 | ✅ **两页技术版**；技术筛选、内推和面试前材料 |
| `CV_hpc.docx` / `.pdf` | 旧 HPC 草稿 | ❌ 有失效链接、未实现声称和 launcher-era 数字，只作基线 |
| `backup/` | — | 历史版本，只读留档，不要从这里取文件投递 |

**Agent 一页版与详细版的差别**（都只声称已实现的东西，一页版是详细版的子集，没有任何独有表述）：

- 项目一：8 条工作内容压成 4 条（分层架构与同构契约 / function calling 与防御式解析 / 评测与消融 / 工程化外围），砍掉的是规则 router 细节、字节级报告、工程纪律
- 项目二：5 条压成 2 条，只留根因诊断与负结果自我批判
- 技术能力：7 行并成 4 行；论文标题行内联
- 排版：去掉 `docGrid` 行网格（11pt 段落原本被吸附到两个网格行，行距凭空翻倍——这一项零内容损失就省了一整页）；正文统一 9.5pt；上下页边距 0.4cm

两份新 HPC 简历都不覆盖旧 `CV_hpc`。旧文件现在是可回溯的修改前基线，不应作为附件发送。

## 项目底稿的真实进度（简历口径的来源）

简历声称的内容必须能在以下三个仓库中找到对应实现或实验记录。

**hpc_benchmark_archer2**（github.com/leyancode/hpc_benchmark_archer2）

- 正式实验：2D/3D、约 5M-165M unknowns、1-32 个 ARCHER2 节点，最多 4096 个物理核
- 证据量：264 个 weak-scaling runs + 144 个 fixed-20M strong-scaling runs，共 **408 accepted formal runs**
- 正式结论：2D `64x2` 在 11 个 weak-scaling 点赢 8 个；165M/32 节点约 794.8M equations/s；3D 最大 throughput gain 33.2%
- MAP 数字来自 instrumented runs，只解释 MPI exposure 与 OpenMP waiting 的排序，不与非插桩 timing 混用

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

## 2026-08-03 这次改了什么（HPC 简历）

- 新增两页 HPC / 科学软件详细版和一页 HPC+AI Infrastructure 投递版；两份都通过 Microsoft Word PDF 导出和逐页视觉检查
- 项目链接统一为 `leyancode/hpc_benchmark_archer2`，教育日期和可入职时间与 Agent 简历一致
- 第二个项目改为已经实现的 Agent 系统；删除 Redis、FAISS/Chroma、LangChain/LlamaIndex、MySQL 优化和 Docker 健康检查等未实现声称
- HPC 数字改用经过审计的 Phase 3 正式结果；旧的 64 节点、8192 核、26.1x 和“`32x4` 始终最优”来自 launcher-era 数据，已被 process-count 审计推翻，禁止恢复
- 增加 `302/303` launcher 失配、408 个 accepted formal runs、weak/strong scaling 和 MAP instrumented-run 边界，突出实验纠错与证据管理能力

## 关键事实口径（两份简历必须一致）

| 项 | 口径 |
|---|---|
| 课程与毕业论文完成 | 2026.08 |
| **可入职时间** | **2026.09.01**（比多数海外硕士早，务必写出来） |
| 学位证书获得 | 2026.12 |
| GitHub | `leyancode`（`lionleepower` 是死链） |
| 评测数字 | 规则 router 83.3% · LLM router 100% · 无 system prompt 消融 63.3% |
| 评测条件 | qwen3.7-plus · temperature 0 · 单次运行 · 题量 30 |

被追问"100% 可信吗"时主动给局限：**题量 30、出题人即作者、单模型单次运行**。

被 HR 追问"12 月才发证怎么 9 月入职"时：课程和论文 8 月全部完成，9 月起可全职；入职提供成绩单 + 课程完成证明（Completion Letter），证书后补。学历认证需凭证书办理，因此在 12 月之后 —— 如某家公司明确要求入职前完成认证，那是硬门槛，提前问清楚。

## 投递前自查

- [ ] 全文搜"进行中""接入中" —— 应为 0 处
- [ ] 所有 GitHub 链接**在无痕窗口逐个点开**（无痕是为了避开自己的登录态：你能看见的 private 仓库，面试官看到的是 404）
- [ ] 简历声称的每个模块都能在仓库里指出对应实现 —— **不声称未实现的模块**是硬约束
- [ ] 毕业时间与可入职时间两个都在，缺一不可
- [ ] demo 三分钟可复现：clone → `pytest`（229 passed）→ `ask` → `report`
- [ ] 使用带日期的新文件名，不覆盖或误发旧 `CV_hpc` 基线
