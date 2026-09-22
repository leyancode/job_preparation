# 海外投递（英国 / 欧洲英语岗）

> 最后更新：2026-09-12 · **与国内秋招同等优先**（此前排在国内之后）
> 四份英文一页简历由 `../build_cv_en.py` 生成，事实口径与禁令见 `../README.md`

## 投哪一份

| 文件 | 岗位名怎么搜 | 第一屏 | 典型雇主 |
|---|---|---|---|
| `CV_agent_EN_20260912` | AI Engineer · Agent Engineer · LLM Application Engineer · Applied AI Engineer · Forward Deployed Engineer | HPC_Agent（评测 / 消融 / 防御式解析） | 伦敦 AI 应用公司与 scale-up、大厂 applied AI 组、咨询 / 金融的 GenAI 团队 |
| `CV_backend_EN_20260912` | Software Engineer (Python) · Backend Engineer · Graduate / Junior Software Engineer · Platform Engineer | HPC_Agent（分层架构 / 进程边界 / 可观测） | fintech、SaaS、数据平台、任何 Python 后端 |
| `CV_ai_infra_EN_20260912` | ML Infrastructure Engineer · ML Platform · HPC Performance Engineer · Performance / Systems Engineer | ARCHER2（布局选型 / MAP 归因 / 自建指标 / 审计） | Arm、AMD / NVIDIA UK、云厂商英国 office、量化公司、HPC 厂商 |
| `CV_rse_EN_20260912` | Research Software Engineer · Applications Consultant · Scientific Software Developer · HPC Application Developer | ARCHER2（多一条证据链 / 可发布性 bullet） | **EPCC**、STFC（Hartree / Daresbury / RAL）、大学 RSE 组、Turing、Diamond |

**同一家只投一份。** 拿不准时：JD 里 LLM / agent 出现 ≥ 2 次投 `agent`；写 "research software" / "scientific computing" 投 `rse`；
写 "performance" / "HPC" / "GPU" / "infrastructure" 投 `ai_infra`；其他 Python 岗投 `backend`。

## 投出去之前必须先做的四件事

1. **LinkedIn**（`build_cv_en.py` 顶部 `LINKEDIN = None`）。英国 recruiter 的流程是先搜 LinkedIn 再点简历，没有会显得不真实。
   建好 profile、URL 写进去，页头自动多一项，链接自动加 `rId96`。
2. **签证措辞与当天状态一致**（`WORK_AUTH`）。现状 2026-09-12：Student visa 在手、课程 2026-08 完成、Graduate Route **未申请**。
   现在写的是 `Student visa (full-time work permitted post-course); applying for the 2-year Graduate Route — no sponsorship required.`
   - 递交申请后可改成 `Graduate Route application submitted <月>`；
   - **批下来必须改成** `Graduate Route visa held, valid until <日期>; no sponsorship required.`——这是最强的一句；
   - 批之前**不许写** `visa held` 或到期日。
3. **向爱丁堡 Student Immigration Service 确认两件事**：(a) 课程完成向内政部上报的日期——决定 Graduate Route 最早何时能递；
   (b) 你这个课程在 Student visa 下「课程结束后至签证到期前可全职工作」是否成立——`WORK_AUTH` 第一句写的就是它。
4. **从 Word 导出 PDF 并确认还是一页。** 本机无 Tahoma，目录里的 PDF 是 LibreOffice 导出的，四份在 LibreOffice 下恰好一页、余量 1–3 行。

## 一件有硬期限的事：Graduate Route

**2026 年 12 月 31 日（含）前递交是 2 年，2027 年 1 月 1 日起递交是 18 个月**（博士不受影响，3 年）。

课程 2026-08 完成、证书 2026-12 才发。Graduate Route 通常在学校向内政部上报课程完成后即可申请，不必等证书或毕业典礼，
但取决于爱丁堡上报的时间，且申请时人须在英国境内、持有效 Student visa。

- [ ] 问 Student Immigration Service 上报时间（第 3 件事的 (a)）
- [ ] 政策以 [gov.uk/graduate-visa](https://www.gov.uk/graduate-visa) 为准，数字自己复核
- [ ] 申请费 + IHS 两年的钱先备好

**Graduate Route 期内不需要 sponsorship，这是现在最大的一张牌。** 很多没有 sponsor licence 的小公司只能招不需要 sponsor 的人——
这反而是你的独占池子。两年后要换 Skilled Worker 才需要 sponsor，届时有两年英国工作经验，是另一个问题。

## 简历里几处英国 / 欧洲的惯例（不是翻译问题）

| 项 | 国内 | 英国 / 欧洲英语岗 | 生成器里对应 |
|---|---|---|---|
| 长度 | 一页或两页 | 工业界一页；学术 / 国家实验室可两页 | 四份都是一页 |
| Profile / Summary | 一般不写 | **几乎都写**，两三行，说清投什么岗 | `PROFILE[variant]` |
| 照片、年龄、性别、婚姻、国籍 | 有时放 | **绝对不放**（Equality Act 下 HR 会因此弃件） | 无 |
| 工作许可 | 不涉及 | **必须一行**，不写默认需要 sponsorship 直接过滤 | `WORK_AUTH` |
| 所在地 | 城市 | 城市 + 是否可搬迁 | `LOCATION` |
| 学历 | 学校 + 学位 | 同上，荣誉等级写全称 `First-Class Honours` | `EDU` |
| 电话 | +86 | 英国号码，`+44 7xxx xxxxxx` 分组 | `UK_PHONE` |
| Referees | 不写 | 不列人，需要时对方会要 | 无 |
| 项目叙述 | 可以密 | 动词开头、过去式、结果前置、机制在后 | bullet 写法 |
| 拼写 | — | 英式：`optimisation` / `factorisation` / `sanitised` | 全文已统一英式；仓库名里的 `FACTORISATION` 也是 |

**德国 / 法国的本地格式（Lebenslauf 带照片与出生日期、CV français）不做**，除非明确投德语 / 法语岗；
荷兰、爱尔兰、北欧、德国的英语团队用同一份英文简历。

## 招聘节奏

**Graduate scheme 不适用**：9–11 月开放、招**下一年**秋季入职，且多数 rolling、招满即关。你现在就能全职，等一年不划算。
**该投的是 direct entry / experienced hire 的常规岗位**，全年滚动，通常提前 1–3 个月招。以「立即可入职」算，现在正好。

| 渠道 | 投什么 |
|---|---|
| [jobs.ac.uk](https://www.jobs.ac.uk) | RSE、Applications Consultant、HPC——`rse` / `ai_infra` |
| EPCC / STFC / Turing 官网 | 同上；EPCC 的岗位 jobs.ac.uk 有时不同步，直接看 [epcc.ed.ac.uk](https://www.epcc.ed.ac.uk) |
| LinkedIn Jobs、Otta（现 Welcome to the Jungle）、Workable / Ashby 的公司页 | `agent` / `backend`——伦敦 AI 公司基本都在这些 |
| Hiring Cafe、Welcome to the Jungle EU | 欧洲英语岗 |
| 公司官网 careers 页 | Arm、AMD、NVIDIA、量化公司只看这里 |

## 目标雇主

分档依据是「现有材料与 JD 的距离」，不是公司名气。**每一家投前核对：是否在招、是否有 sponsor licence（两年后才用得上，但先记着）。**

### `rse` —— ARCHER2 项目基本就是这些岗位的日常

| 雇主 | 岗位名 | 备注 |
|---|---|---|
| **EPCC / 爱丁堡大学** | Applications Consultant、RSE、HPC Systems | **最强的一家**：ARCHER2 的运营方，项目跑在他们机器上，学位也是他们发的。**单独写求职信**，项目在他们机器上这一点值得一段 |
| STFC（Hartree / Daresbury / RAL） | RSE、HPC Application Developer | 公共部门，节奏慢但对 MSc 友好 |
| 各大学 RSE 组（剑桥 / 牛津 / UCL / Imperial / 布里斯托 / 谢菲尔德 / 曼城） | Research Software Engineer | 集中在 jobs.ac.uk |
| Diamond Light Source、Alan Turing Institute | Scientific Software / Research Engineer | 同上 |
| ⚠️ Met Office、UKAEA、AWE | HPC / Computational Scientist | 极其对口，**但常有国籍或安全审查限制**，投前看 eligibility |

### `ai_infra` —— 方向对口，门槛在缺的那一格（GPU / 生产经验）

Arm（剑桥，最接近的一家，profiling 与体系结构叙事直接对得上）、AMD / NVIDIA UK（要 GPU 实操）、
AWS / Microsoft / Google 英国 office 的 infra 组、Graphcore（布里斯托）、
Jane Street / Optiver / IMC / Citadel Securities / G-Research（**别忽略这条**：C/C++ + profiling + 体系结构正是他们要的，
按裸能力招人、给 sponsorship，难在笔试与心算轮）。
保底：Eviden / Atos UK、HPE UK、Dell UK（HPC Solutions / Benchmark Engineer，正好吃「跑 benchmark + 出可信报告」这套）；
Siemens STAR-CCM+、Ansys UK（PETSc / 求解器背景直接可用）。

### `agent` —— 伦敦是欧洲 AI 应用公司最密的地方

| 档 | 雇主 | 备注 |
|---|---|---|
| 大厂 applied AI | Google DeepMind / Anthropic / OpenAI 伦敦 | 别当计划，但 applied / solutions 类岗位比 research 岗门槛低得多 |
| 有 sponsor 的 scale-up | ElevenLabs、Synthesia、Wayve、PolyAI、Humanloop、Robin AI、Builder.ai 之类 | 看当下是否在招；JD 里 "evaluation" / "evals" 出现的岗位是你的 |
| 金融 / 咨询 GenAI 团队 | 各大行 & Big 4 的 AI 组、Revolut / Monzo / Wise 的 AI 岗 | 后端 + LLM 混合岗，`agent` 与 `backend` 二选一，看 JD 权重 |
| ⚠️ 无 sponsor licence 的小公司 | 伦敦 / 剑桥 / 爱丁堡的 AI 小公司 | Graduate Route 期内不受影响，是你的独占池子 |

面 `agent` 岗必讲的一格：**Agent 评测与质量体系**（规则 baseline / 同构输出 / 30 问 / 消融 63.3%→100%）——大多数应届生讲不出来。
必答的一问：**为什么是中文评测集**——真实用户场景；工具、schema、测试与语言无关；英文集是明确的下一步（`../README.md` 待办 9）。

### `backend` —— 兜底成立

FastAPI + Python + SQL + 测试 + 可观测是真的。fintech（Revolut、Monzo、Wise、Checkout.com）、SaaS、数据平台、
爱丁堡本地（Skyscanner、FanDuel、Cirrus Logic、Wood Mackenzie）。支付域会问一致性 / 幂等 / 对账——幂等目前只在技能段的 `working knowledge` 层。

### 欧洲（英语岗）

阿姆斯特丹（Booking、Adyen、Optiver、IMC、ASML 在 Veldhoven）、都柏林（各大厂欧洲总部）、柏林（Zalando、大量 AI 初创）、
苏黎世（Google、ETH 相关）、北欧（Spotify、Klarna）。**签证各国不同**，多数需要雇主 sponsor 但流程比英国 Skilled Worker 轻；
荷兰有 Orientation Year（zoekjaar）给国际毕业生——英国学位也算，值得查。

## 溢出时怎么砍（不动事实）

四份在 LibreOffice 下余量 1–3 行，Word 里若溢出按此顺序：

1. `agent` / `backend`：`P3["short"]` 删掉最后一句 `Repackaged in 2026…`（已删）→ 再砍 `P2["ops"]` 的 RAG 半句
2. `ai_infra`：`P3["full"]` 换成 `P3["short"]`
3. `rse`：`COURSEWORK` 整行删（RSE 岗看项目不看课）
4. 所有变体：`PUBLICATION` 那行（EMITI 2024 是弱会议，英国岗价值很低，删了不心疼）
5. **不要**砍 `WORK_AUTH`、`PROFILE`、任何带数字的 bullet

## 求职信（cover letter）

英国的 RSE / 公共部门岗**几乎都要**，且 HR 真的看；工业界可选。三段够了：
(1) 投什么岗、为什么是这家；(2) 一个项目、三个数字、一个方法论卖点（302/303 作废那件事对 RSE 是满分故事）；
(3) 可入职时间 + 工作许可 + 感谢。EPCC 那封单独写：项目跑在 ARCHER2 上，你读过他们的 hardware docs 并用 `lscpu` / `hwloc` 核对过——这是他们自己的机器。

## 要做的事

1. [ ] LinkedIn 建好、URL 填进 `build_cv_en.py`
2. [ ] 问 Student Immigration Service：课程完成上报时间；Student visa 下课程后全职工作是否成立
3. [ ] 递交 Graduate Route（**12 月 31 日前**）；递交 / 获批各改一次 `WORK_AUTH`
4. [ ] Word 导出四份 PDF，确认一页
5. [ ] EPCC 求职信
6. [ ] 三个仓库 `git push`；主页部署（见 `../README.md` 待办 5、6）——**投出去之前**，因为简历上的链接会被点
7. [ ] 第一批：EPCC / STFC（`rse`）、Arm（`ai_infra`）、3–5 家伦敦 AI 公司（`agent`）、2–3 家 fintech（`backend`）
