# 简历目录说明

> 最后更新：2026-09-16 · 本文件讲「事实从哪来、怎么生成、不许写什么」
> 两条线的岗位与时间线分别在 `海外投递/README.md`（英国 / 欧洲）与 `国内投递/README.md`（秋招）

## 当前状态一句话

**两条线并行：海外（英国 / 欧洲英语岗）与国内秋招同等优先**（2026-09-12 调整，此前海外排在国内之后）。
两条线的方向一致：**主线 Agent 开发 / 后端开发，第二方向 AI Infra / HPC 性能工程**；
海外线多一档 **Research Software Engineer**（EPCC / STFC / 大学 RSE 组），那是 ARCHER2 项目最直接对口的岗位。

GPU 侧（推理引擎 / 训练框架 / 智算平台）仍然搁置：JD 要 CUDA / TensorRT / 分布式训练实操，短期补不上。
**解冻前提不变：`llm_inference_archer2` 跑出正式数字。**

十一个变体（中文七、英文四）由两个生成器从**同一套事实**生成，头条数字由 `build_cv_en.py` 的 `check()`
钉死——中英对照文件里的头条数字集合必须相等，否则 build 失败。

**已投 5 个（国内）**：华为 2、字节 1、快手 2，四个在 Agent / AI 应用侧。海外 **0 个**——四份英文简历 2026-09-12 刚出，
投之前先过 `海外投递/README.md` 的「投出去之前」清单（LinkedIn、签证措辞、Word 页数）。

## 先看哪个文件

| 文件 | 作用 |
|---|---|
| 本文件 | 事实口径、生成器用法、禁令清单、投递前自查、开放待办 |
| `海外投递/README.md` | **英国 / 欧洲线**：四份英文简历投什么、签证硬期限、中英简历差异、目标雇主、招聘节奏 |
| `国内投递/README.md` | 秋招：七份中文简历投什么、时间线、面试要讲的故事 |
| `../秋招投递_岗位清单.xlsx` | 国内 60+ 岗位 × 匹配度 / 优先级 / 建议简历 / 投递时间；「方向」列四档可筛 |

## 变体总表

### 海外 · 英文（`build_cv_en.py` → `海外投递/`，全部一页）

| 变体 | 输出 | 岗位 | 第一个项目 |
|---|---|---|---|
| `agent` | `CV_agent_EN_*.docx` | AI Engineer、Agent / LLM Application Engineer | HPC_Agent |
| `backend` | `CV_backend_EN_*.docx` | Backend / Software Engineer (Python) | HPC_Agent（分层与服务化打头） |
| `ai_infra` | `CV_ai_infra_EN_*.docx` | ML / AI Infrastructure、HPC Performance Engineer | ARCHER2 |
| `rse` | `CV_rse_EN_*.docx` | Research Software Engineer、Applications Consultant | ARCHER2（多一条可发布性 / 证据链 bullet） |

### 国内 · 中文（`build_cv.py` → `国内投递/`）

| 档 | 变体 | 输出 | 投什么 |
|---|---|---|---|
| 主线 · Agent | `agent` | `CV_agent_*.docx` | ✅ 默认主投：腾讯 / 字节 / 阿里 / 华为 Agent 岗，Coze、百炼、元宝… |
| 保底 · 后端 | `backend` | `CV_backend_*.docx` | 后端开发岗 |
| 保留 · CPU 侧 HPC | `hpc` | `CV_hpc_*.docx` | 超算中心、曙光、浪潮、计算所 / 软件所、Intel oneAPI、Arm |
| 保留 · 备用 | `ai_infra` | `CV_ai_infra_*.docx` | JD 同时要 HPC 与 AI 平台时；一页、信息密度最高 |
| 不投 · 回读 | `ai_infra_full` | `CV_ai_infra_详细版_*.docx` | 两页，面试前自己回读；一页版是它的子集 |
| 搁置 · 需 GPU | `perf` / `platform` | `CV_perf_*` / `CV_aiplatform_*` | 随事实一起更新，暂不投 |

中英同名变体（`agent` / `backend` / `ai_infra`）的**项目顺序、bullet 取舍与头条数字完全对应**；英文 `rse` 没有中文对应，
一致性检查对照中文 `ai_infra`。

## 目录结构

```
CV/
├── README.md          ← 你在这里
├── build_cv.py        ← 七个中文变体的唯一生成器；事实底稿（FACT 区）在这里
├── build_cv_en.py     ← 四个英文变体；import build_cv 共用排版原语、母版 package 与仓库链接表，
│                        底部 check() 做中英头条数字一致性检查
├── template/          ← 排版母版 agentCV_20260803.docx，构建输入，**不是投递件，不要删、不要改名**
├── 国内投递/           ← 中文简历（只放能投的）+ README
├── 海外投递/           ← 英文简历（只放能投的）+ README
├── preview/           ← 预览件，**不投递**：`CV_agent_v3预览_*` 是假设「审计后数据导入 Agent」做完后的样子
├── ref/ai_infra/      ← 一份已进面的 AI Infra 简历，排布的参照物
└── backup/            ← 历史版本与手改原件，只读。**不要从这里取文件投递**
```

## 生成器怎么用

```bash
python3 build_cv.py                # 七份中文 → 国内投递/
python3 build_cv_en.py             # 四份英文 → 海外投递/，并做中英一致性检查（要先跑上一条）
soffice --headless --convert-to pdf 国内投递/CV_*.docx --outdir 国内投递
soffice --headless --convert-to pdf 海外投递/CV_*_EN_*.docx --outdir 海外投递
```

- **事实只写一遍**。中文：技能在 `SKILL` / `SKILL_KW` / `SKILL_1P`，项目 bullet 在 `P1` / `P2` / `P3`。
  英文：`SK`、`P1` / `P2` / `P3`、`PROFILE`。英文是**重写不是翻译**，但数字必须一样——`check()` 会拦。
  **不要直接编辑 docx**（手改 docx 正是 8 月那批死链的来源）。
- 变体差别只在两个脚本各自的 `VARIANTS`：`projects` 顺序、技能行与 bullet 取舍，外加几个开关。
- 联系方式、仓库名、超链接目标全部在 `build_cv.py` 顶部（`EMAIL` / `PHONE` / `GITHUB_URL` / `REPOS` / `REL_REPO`），
  英文侧只覆盖 `UK_PHONE` / `LINKEDIN` / `LOCATION` / `WORK_AUTH`。**改仓库名只改 `REPOS` 这张表**，十一份同时生效。
- 改数字：两个脚本都跑，两边都过才算改完。

### 页数：LibreOffice 的分页只能看趋势

本机没装 Tahoma，LibreOffice 导出的字距与分页**不等于 Word**。经验值：一页大约装 70 行 LibreOffice 文本，
2026-09-12 四份英文版在 LibreOffice 下都恰好一页、余量 1–3 行——**投递前必须从 Word 重新导出并确认页数**，
目录里的 PDF 只能看排布。溢出时按 `海外投递/README.md` 的「砍法」顺序砍，**不动事实**。

### 七个容易写回去的坑

1. **技能段只写项目段证明不了的东西**（语言、工具面、了解性知识）。做过的事交给项目 bullet 用细节证明；
   同一句话在技能段和 bullet 里出现两次不增加可信度，只挤行数。
2. **中文 `service` 与 `eng` 两行会重复** FastAPI + Pydantic、SQLite / MySQL、Docker → `agent` / `backend` 用 `eng_lite`。
   英文同理：`service` + `eng_lite`，`eng` 只给 `ai_infra`。
3. **前向引用**：中文 `P2_TITLE`（"面向**该** benchmark 数据"）/ `P2_DESC`（"**上一项目**"）、英文 `P2_DESC`
   （"the benchmark data **above**"）都假定 ARCHER2 排在前面。HPC_Agent 排第一的变体自动换成 `*_STANDALONE`，
   逻辑在两个 `build()` 里——**改 `projects` 顺序时确认这一处仍生效**。
4. **exposure share 有长短两版**：带「MAP 扰动运行时间、只读占比排序」半句的（中文 `c_context` / 英文 `context`）
   给没有 MAP bullet 的 `agent` / `backend`；不带的（中文 `o_exposure` / 英文 `exposure`）给有 `map` bullet 的
   `ai_infra` / `rse`。同一份简历里不说两次。
5. **ARCHER2 三块内容各有位置**：「为什么值得做」在项目描述；「吞吐差 13.1% / 33.2%」在结论 bullet；
   「规模、两个后端、exposure share」在 context bullet。不要互相复述。
6. **`P3[2]`（中文）是一页版专用合并条**，与 `P3[0]` 重叠；英文对应 `P3["full"]` 与 `P3["short"]`。别在同一变体里两条都取。
7. **英文 `PROFILE` 是唯一写「投什么岗」的地方**，两行以内，不写形容词；改方向先改这里。

### 超链接：显示文字和跳转目标是两回事

母版包里原有的 `rId8` 指向已废弃的 `https://github.com/leyancode`，**不能复用**。`build_cv.py` 自建
`rId90`–`rId95`（主页 / 邮箱 / GitHub / 三个仓库），`build_cv_en.py` 再加 `rId96`（LinkedIn，设了才加）。
显示文字与目标由 `REPOS` / `REL_REPO` 一张表生成。手工 docx 会把 URL 拆进多个 run，按整串查找替换会漏——所以：

- [ ] 改完链接后不要只看 docx：**解包 `word/_rels/document.xml.rels` 取全部 `Target`，逐个 curl**（2026-09-12 四份英文版：全部 200）

### 项目标题排布

**中文（2026-09-16 起）：标题靠左、仓库链接右对齐在同一行，技术栈另起一行**

```
面向 ARCHER2 超算上 PETSc benchmark 数据的 Agent 式性能分析系统            lionleepower/HPC_Agent   ← 右对齐制表位
｜Python · SQLite · FastAPI · Pydantic · OpenAI SDK（function calling）· pytest
```

链接固定在每个项目第一行、三个项目纵向对齐，不多占一行（`title_link()`，制表位钉在正文右边缘 11338 twips）。
**标题 + 链接必须一行放下**，否则链接会被推到下一行右端、白丢一行——agent 变体的 ARCHER2 标题为此从
「……上一项目的数据来源与可信度基线」缩成「……上一项目的数据来源」。`ai_infra` 的 P1 标题在 LibreOffice 下仍折行，
Word 下（Tahoma 更窄）待确认；折行就缩标题，不动链接。

**英文（仍是 09-12 的排布）：标题一行，技术栈与链接另起一行**

```
Evaluable Tool-Calling LLM Agent over Real Supercomputer Benchmark Data          ← 加粗，独占一行
| Python · SQLite · FastAPI · Pydantic · OpenAI SDK (function calling) · pytest  lionleepower/HPC_Agent
```

链接文字去掉 `github.com/` 前缀（页头已写过一次）。**技术栈行要短到让链接留在同一行**——2026-09-12 为此把
`GitHub Actions` 缩成 `CI`、MARL 栈砍掉 `CTDE · PPO · MPE2`；链接单独占一行等于白丢一行。

### `agent` 变体的 bullet 写法（2026-09-16）

HR 的反馈：文字密、抓不住重点；企业想看「针对什么难点、用了什么策略、效果怎么样」。第一版把「难点 / 做法 / 效果」
三个词直接印进 bullet，本人否掉（没有哪家简历这么写，观感不专业）。现在的规矩：

- 标签仍是名词短语，正文是一句连贯的话，用「为了 / 由于 / 因此 / 使 / 以保」把难点→做法→效果串起来；
- 只有工程重点（同构契约、防御式解析、可观测性、自动化测试、词法检索）交代难点，其余条目沿用 0904 版原文；
- 事实与数字与 0904 版逐个相同，只是把可观测性 / 自动化测试 / 词法检索从「工程化外围」拆成各自可见的三条（`a_trace` / `a_tests` / `a_rag`），
  P1 多一条算力换算 `a_value`：11.6% = 1 − 1/1.131、24.9% = 1 − 1/1.332（仓库 README 原有）、26% = 1/3.81，逐个带范围，不许写成「平均节省」。
- 「（硕士毕业论文）」「（本科毕业设计）」标在技术栈行末尾（`STACK_TAG`），不占标题宽度。

HR 建议里的几个「效果百分比」（事故排查时间降低 X%、词法比向量准确率高 X%）**在这个项目里不存在**——没有线上事故，
也没做过词法 vs 向量的 A/B。写的是仓库里真有的东西：5 个 trace 事件可回放、三类异常各有测试、rag.py 文档串里的取舍理由。

## 关键事实口径（所有简历必须一致）

| 项 | 口径 |
|---|---|
| 课程与毕业论文完成 | 2026.08 |
| **可入职时间** | **立即**（今天已过 2026-09-01）。英文版写 `available immediately`；中文版目前不写入职时间（见开放待办），面试与 HR 沟通时必须主动讲 |
| 本科日期 | 中英都写 **`2021.09 – 2025.06` / `Sep 2021 – Jun 2025`**，两校并列、括号里「2+2」（2026-09-16 手改版改的口径；此前只写利物浦两年 2023.09 起） |
| 学位证书 | 2026.12（简历上「2025.09 – 2026.12（预计）」/ `Dec 2026 (expected)`）→ 国内属 **2027 届** |
| 英国签证 | **Student visa 在手，Graduate Route 尚未申请**（2026-09-12）。英文版 `WORK_AUTH` 写的是这个状态；批下来必须改（见 `海外投递/README.md`） |
| 电话 | 中文 `+86 18805506898`；英文 `+44 7887 930137` |
| 邮箱 | 中文版页头 gmail + `3073751449@qq.com` 两个都放（2026-09-04 手改版加的，09-16 收进生成器 `EMAIL_QQ`）；英文版只放 gmail |
| 主页 | `leyan-li.com`。**源码里的 `leyancode` 死链已于 2026-09-12 全部改为 `lionleepower` 并 commit，但还没部署**（开放待办 6） |
| GitHub | **`lionleepower`**（`leyancode` 已废弃，全部 404） |
| 仓库 | `HPC_PETSC_Benchmark` · `HPC_Agent` · `MARL_VALUE_FACTORISATION`——三个 README 2026-09-12 起以英文为默认，中文保留为 `README.zh-CN.md`；**本地已 commit，尚未 push** |
| 评测数字 | 规则 router 83.3% · LLM router 100% · 无 system prompt 消融 63.3% |
| 评测条件 | qwen3.7-plus · temperature 0 · 单次运行 · 题量 30 · **题目是中文** |
| 测试数 | **229 passed**（不是 165） |
| ARCHER2 规模 | **32 节点 / 4,096 核**、5M–165M unknowns、**408 个通过审计的 run**（264 weak + 144 strong） |
| 同步暴露占比 | 自建指标 = halo + 全局归约占 `KSPSolve` 的比例，逐 run 从 `-log_view` 算，覆盖 264 个 weak-scaling run；2D 32 节点中位数 `128×1` **48.2%** → `16×8` **26.4%** |
| 为什么可相加 | 事件嵌套使叶子事件直接相加达 `KSPSolve` 的 **116–372%**；halo（`VecScatterBegin/End`）与归约（`VecTDot`、`VecNorm`）在**互不相交的调用路径**上，只有这两者之和合法 |
| ARCHER2 头条数 | 2D weak +13.1%（794.8M eq/s）· 3D weak 最大 +33.2% · 2D fixed-20M **29.83× / 93.2%** · 3D `16×8` 比 flat MPI 快 3.81× |
| MAP 占比 | MPI 46.7%→6.2%、OpenMP 等待 48.3%→76.5%（8 节点 LibSci profiles）；LibSci BLAS ≤ 2.1% |
| 审计 | launcher 时代 **302 / 303** 份日志 process count 与文件名不符，整阶段作废 |

被追问「100% 可信吗」时**主动**给局限：题量 30、出题人即作者、单模型单次运行。
英国面试官问「为什么是中文评测集」：真实用户场景是中文；工具、schema、测试、架构与语言无关；评测方法可迁移，英文集是明确的下一步。

被 HR 追问「12 月才发证怎么现在入职」：课程和论文 8 月全部完成，可全职；入职提供成绩单 + Completion Letter，证书后补。
国内学历认证凭证书办理，12 月之后再花 1–2 个月——国企 / 银行 / 运营商这条线现在就该查流程。

## 项目底稿的真实进度

简历声称的内容都必须能在这三个仓库里找到对应实现。三个链接 2026-09-12 再次 curl 验证 200。

**HPC_PETSC_Benchmark** — 32 节点 / 4,096 核；408 audited runs；头条数如上表；Phase 2 302/303 失配作废；MAP 只读占比排序；
CI 跑公开数据 pytest + fake Slurm。README 英文（中文 `README.zh-CN.md`），`test_public_portfolio.py` 断言英文标题。

**HPC_Agent** — P1 确定性工具 + 中文规则 router + CLI、P2 LLM function calling + 30 问评测、P3 tracing + FastAPI + 词法 RAG，
**全部已完成**；229 passed，离线、不需要 key。README / WORKFLOW / 评测报告英文，如实标注「自然语言界面是中文」；
代码里的中文（测试问句、规则词表、CLI 回答）**没动也不能动**——那是功能本身。

**MARL_VALUE_FACTORISATION** — 本科毕设（COMP390，2025）；2026 整理为作品集：修正 Predator-Prey 合作边界、uv.lock 锁 CPU 版
PyTorch、pytest + CI。README 与 `results/thesis/README.md` 英文；核心文件（qmix.py、两个 learner）的中文注释已译成英文，
顺手修掉一条过期注释（写 `abs()` 保单调性，代码实际是 `softplus`）。

## 禁令清单：这些东西不许写回去

- **不声称未实现的模块**（硬约束）。曾写过又删掉的：Redis / TTL、FAISS / Chroma、LangChain / LlamaIndex、MySQL 查询优化、
  Docker 健康检查、缓存命中追踪、图表生成、Obsidian 报告。只能以「了解 / working knowledge」层级出现在技能段。
  英文 `llm` 技能行里的 `planning / memory / reflection patterns and LangGraph-style orchestration` **就是这一层级**，
  前面有 `working knowledge of`，不许升级成项目 bullet。
- **旧的 ARCHER2 数据禁止恢复**：64 节点、8,192 核、40.96M unknowns、26.1× 加速、「`32x4` 始终最优」——launcher-era 数据，已被审计推翻。
  `HPC_PETSC_Benchmark` 的测试明写 `"26.1" not in readme`、`"64 nodes" not in readme`。
- **不写 ePyMARL**。仓库 `UPSTREAM.md` 只记录 PyMARL。
- **GPU 技能条的「（课程与自学）/ coursework / self-study level」限定必须留着**——全篇唯一没有项目 bullet 背书的技能。也不要写成「尚无生产经验」。
- **教育日期不许自相矛盾**：`2025.09 – 2026.12（预计）` / `Sep 2025 – Dec 2026 (expected)`，与「证书 2026.12」一致。
- **英文版不放**照片、年龄、性别、婚姻状况、国籍；不写 referees 名单。
- **签证状态不许写超前**：Graduate Route 没批之前不写 `visa held` / 到期日。

## 投递前自查

- [ ] 全文搜「进行中」「接入中」/ `in progress` —— 应为 0 处
- [ ] **解包 docx 关系表逐个 curl 全部 `Target`**，再在无痕窗口点开一遍（你能看见的 private 仓库，面试官看到的是 404）
- [ ] 简历声称的每个模块都能在仓库里指出对应实现
- [ ] demo 三分钟可复现：clone → `pytest`（229 passed）→ `ask` → `report`
- [ ] 改事实改脚本再重新生成，**不要手改 docx**
- [ ] **从 Word 导出 PDF 并确认页数**——LibreOffice 的分页不作数
- [ ] 另存为新文件名（改 `DATE`），上一版移入 `backup/`
- [ ] **同一家公司只投一份**——十一个变体共用同一批仓库，多份一起投等于自曝口径差异
- [ ] 英文专有：`LINKEDIN` 已填；`WORK_AUTH` 与当天签证状态一致；`COURSEWORK` 逐条对过成绩单
- [ ] 主页 `leyan-li.com` 已部署新版（点开项目链接不是 404）；三个仓库的英文 README 已 push

## 开放待办

1. **中文版的可入职时间**（P0）。2026-09-03 手改版把「课程与论文 2026.08 完成｜可入职 2026.09.01｜证书 2026.12」整条删了。
   现在日期已过，要恢复的话措辞该是「**可立即入职**」，改 `build_cv.py` 的 `EDU_MSC` 注释行。英文版已写 `available immediately`。
   **这个决定还没做。**
2. ~~国内邮箱口径~~ —— 2026-09-16 起中文页头同时放 gmail 与 QQ（`EMAIL_QQ` / `REL_MAIL_QQ`），不再二选一。
3. **LinkedIn**（P0，海外）：`build_cv_en.py` 的 `LINKEDIN = None`，页头没有 LinkedIn。英国简历几乎都放，且 recruiter 先搜 LinkedIn 再看简历。
   建 / 填好 profile 后写进去，一行搞定。
4. **Graduate Route**（P0，硬期限）：**2026-12-31 前递交是 2 年，2027-01-01 起递交是 18 个月**。还没申请。
   要先向爱丁堡 Student Immigration Service 确认课程完成的上报时间；同时确认 Student visa 下「课程完成后可全职工作」
   这句在你这个课程上成立（`WORK_AUTH` 写的就是它）。详见 `海外投递/README.md`。
5. **三个仓库 push**：README 英文化已本地 commit（`HPC_PETSC_Benchmark` 7f8b6cb、`HPC_Agent` 26b6b96、`MARL_VALUE_FACTORISATION` db6b59c），
   看过 `git show --stat` 后 `git push`。push 后顺手把三个仓库的 GitHub description 填上（现在全是空的，搜索结果里只有一个名字）。
6. **主页部署**：`myProfile/leyan-li-homepage` 已 commit 4a79c72（死链改 `lionleepower`、「可入职 9 月」改「立即」），Vercel 需要你自己部署。
   **部署前决定**：`Basic_algorithm` / `linux_operation` / `script_basic` 三个卡片链到 `lionleepower/...` 但那里没有这三个仓库
   （本地 clone 的 remote 还是 `leyancode`）——要么先 push 这三个，要么删卡片。
7. **`COURSES` / `COURSEWORK` 逐条对成绩单。** 没修过的直接删。2026-09-12 为省行数把英文版的 `Parallel Design Patterns`
   删掉、`High-Performance Data Analytics` 缩成 `HPC Data Analytics`——如果成绩单上有前者且你想留，得腾别的行。
8. **Agent 框架缺口**（P0，国内外 JD 都点名 LangGraph / AutoGen / CrewAI；Planning / Memory / Reflection）。HPC_Agent 刻意手写
   function calling、不上框架。两条路选一条：用 LangGraph 重写一版，或把「为什么不用框架」讲扎实（确定性工具 + 可评测路由，框架会把这两层藏起来）。
9. **英文评测集**（P1，海外）：HPC_Agent 的 30 问是中文，英国面试官无法读题。加一套英文题 + 英文规则 router 是真正的工程量，
   会产生**新的**准确率数字，必须和中文那组分开写。做之前先想清楚要不要。
10. **③ 把审计后的 408 个 run 导进 HPC_Agent**（P1，做不做由本人对照 `preview/CV_agent_v3预览_*` 后决定）。
    现状：`HPC_Agent/examples/sample.csv` 是 2026-06 的 `scaling_grid` 导出——单节点、1M unknowns、36 行，README 写的数据范围
    1M–40.96M 属于 launcher-era 数据；`ask` 会答「128×1 最快、3.866 s」，与 `HPC_PETSC_Benchmark` 的 64×2 +13.1% 相反。
    简历现在的副标题「上一项目的数据来源」在「同一套 benchmark 代码、同一台机器」意义上成立，但 Agent 里查不到 408 run 的任何结果。
    要做的工程：导入器对齐审计后 CSV 的列（nodes / 2D-3D / weak-strong）、工具加 `nodes` 参数、CI 断言 Agent 回答与 benchmark README
    头条数一致。**代价**：30 问评测集问的是「100 万规模」那套数据，换数据要重出题、重跑——83.3% / 100% / 63.3% 会变成**新的**数字，
    必须和旧的分开写。做完之前 `a_pipeline_v3` 与 `P2_DESC_AGENT_V3` 不许进 `国内投递/`。
11. **`job_preparation` 本身在版本控制里、带手机号，remote 是已死的 `leyancode/job_preparation`。** 换 remote 到 `lionleepower`
    并 push 之前，**先决定 CV 目录要不要 `git rm --cached`**——否则手机号、邮箱、完整简历一起公开。`llm_inference_archer2` 的 remote 同样是 `leyancode`。

## 已了结的旧账（不要再翻出来重做）

- ~~agentCV「数据侧」括号里的 245.7s → 3.866s、效率 49.7% / 0.33~~ —— 与 `HPC_PETSC_Benchmark` README 直接矛盾，已从所有可投版本移除。
- ~~GitHub 链接是 `leyancode`~~ —— 简历 2026-09-03 全线改 `lionleepower`；主页源码 2026-09-12 改完（待部署）。
- ~~agentCV 是手工 docx~~ —— 已收进 `build_cv.py`。
- ~~测试数写成 165~~ —— 已改 229。
- ~~项目链接是纯文本~~ —— 全部是真超链接，目标由 `REPOS` 一张表生成。
- ~~母版混在 `国内投递/`~~ —— 已移到 `template/`。
- ~~英文只有 `ai_infra` 一份~~ —— 2026-09-12 起四份（`agent` / `backend` / `ai_infra` / `rse`），旧版 `CV_ai_infra_EN_20260903.*` 在 `backup/`。
- ~~英文版 `UK_PHONE = None` 回落到 +86~~ —— 已填 `+44 7887 930137`。
- ~~英文版 `available from 1 Sep 2026`~~ —— 日期已过，改 `available immediately`。
- ~~09-16 两次手改 `CV_agent_20260916*.docx`~~ —— 第一次三处改动（本科日期与两校并列、技能行加 RAG / 上下文压缩 / 并行 / LangChain、P2 技术栈加 RAG）已回填进两个生成器；原件在 `backup/CV_agent_20260916_手改原件.docx`。技能行里 RAG 有 `a_rag` 背书，其余三项挂在「了解」后面。
  第二次（`_update`）：去掉「难点 / 做法 / 效果」字样、毕业设计标注挪到技术栈行、P3 结尾改为论文对负结果的归结，全部回填；原件在 `backup/CV_agent_20260916_update_手改原件.docx`。
- ~~`国内投递/` 的 PDF 比 docx 旧~~ —— 09-12 改了 docx 没重出 PDF，09-16 全部重出；旧 0903 件与 0904 手改件已移入 `backup/`。
- ~~三个仓库 README 全中文~~ —— 2026-09-12 英文为默认、中文保留 `.zh-CN.md`（待 push）。
