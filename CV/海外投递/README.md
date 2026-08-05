# 海外投递

> 最后更新：2026-08-05

## 现状

`CV_ai_infra_EN_20260805.docx` / `.pdf` —— **英文一页版，由 `../build_cv_en.py` 生成**。
内容是重写而非翻译（动词开头、过去式、impact 打头），排版原语与母版 package 直接复用 `build_cv.py`，
所以中英两版的字号、边距、项目符号完全一致。

**投出去之前有两项必须先填**（`build_cv_en.py` 顶部，build 时会打印警告）：

1. `UK_PHONE` —— 现在是 `None`，回落到 +86 号码。**只有 +86 会显著降低回复率。**
2. `WORK_AUTH` —— 现在写的是最弱、也最站得住的一句：
   `eligible for the UK Graduate Route on completion of my MSc — no sponsorship needed to start`。
   **拿到签证批复前不要写死到期日。** 批下来后改成 `Graduate Route visa held, valid until <日期>`。

### 中英事实不漂移的机制

中英是两份手写文本，最大风险是改了一边忘了另一边。`build_cv_en.py` 底部的 `check()`
把 20 个头条数字（`794.8` / `29.83` / `93.2` / `302` / `303` / `408` / `83.3` / `63.3` / `229` …）钉死：
每一个都必须同时出现在中文一页版和英文版里，**否则 build 直接失败**。
改数字时先跑 `python3 build_cv.py && python3 build_cv_en.py`，两边都过才算改完。

## 中英简历的实际差异（不是翻译问题）

| 项 | 国内投递 | 海外（英国 / 欧洲） |
|---|---|---|
| 长度 | 一页（大厂 HR 首屏）或两页详细版 | 工业界一页；学术 / 国家实验室可两页 |
| 照片、年龄、性别、婚姻 | 一般不放，放了也无妨 | **绝对不要放**——反歧视法规下 HR 会因此弃件 |
| 学历 | 写学校 + 学位 + 荣誉等级 | 同上，`First-Class Honours` 要写全称 |
| 工作许可 | 不涉及 | **必须主动写一行**（见下），不写会被默认需要 sponsorship 而直接过滤 |
| Referees | 不写 | 写 `References available on request` 即可，别列人 |
| 项目叙述 | 可以密 | 更强调 impact 与 ownership，动词开头、过去式 |
| 电话 | +86 | 在英期间用英国号码；只有 +86 会显著降低回复率 |

**工作许可那一行是最重要的一处**，措辞取决于你届时的签证状态，例如：
`Work authorisation: eligible for the UK Graduate Route (no sponsorship required until <到期日>)`。
**在拿到签证批复之前不要写死日期。**

## 英国招聘时间线（2026-08 视角）

**Graduate scheme 对你不适用。** 英国的 graduate scheme 每年 9–11 月开放，
招的是**下一年**秋季入职的人——2026 年 9 月开的 scheme 是 2027 年 9 月入职，
而你 2026.09.01 就能全职，中间空一年。而且多数 scheme 是 rolling、招满即关。

**你该投的是 direct entry / experienced hire 的常规岗位**，这类全年滚动招聘，
通常提前 1–3 个月开始招。以 2026.09 可入职算，**现在（8 月）投正合适，再晚就偏晚了。**

HPC / AI infra 方向在英国的雇主，多在 [jobs.ac.uk](https://www.jobs.ac.uk) 和各自官网滚动发布：
EPCC（就在爱丁堡，你本校，ARCHER2 的运营方——你的项目就跑在他们机器上，这是最强的叙事优势）、
STFC Hartree Centre、UKAEA、Met Office、Diamond Light Source；
工业界 Arm、NVIDIA UK、以及 AWS / Microsoft / Google 的英国 office。

### ⚠️ 一个有硬期限的签证问题

Graduate Route（PSW）的时长在 2027 年初变短：
**2026 年 12 月 31 日**（含）之前提交申请是 **2 年**，2027 年 1 月 1 日起提交是 **18 个月**（博士不受影响，仍是 3 年）。

你的课程与论文 2026.08 完成、学位证书 2026.12 才发——**关键问题是能否在 12 月 31 日前递交申请**。
Graduate Route 通常在**学校向内政部上报课程完成**之后即可申请，不必等证书或毕业典礼，
但这取决于爱丁堡上报的时间，且申请时人必须在英国境内、持有效学生签证。

**这半年之差值得专门去问一次**，越早越好：
- 问爱丁堡 Student Immigration Service：课程完成上报的具体时间，以及能否赶在 12 月 31 日前申请
- 政策以 [gov.uk/graduate-visa](https://www.gov.uk/graduate-visa) 为准，上面这些数字请自己复核一遍再做决定

## 目标雇主（2026-08 整理，**每一家投前都要自己核对当前是否在招、是否有 sponsor licence**）

分档依据是「你现有材料与 JD 的距离」，不是公司名气。

### 主投 —— 你的 ARCHER2 项目基本就是这些岗位的日常工作

| 雇主 | 岗位名怎么搜 | 备注 |
|---|---|---|
| **EPCC / 爱丁堡大学** | Applications Consultant、Research Software Engineer | **最强的一家**：ARCHER2 的运营方，你的项目跑在他们机器上，你的学位也是他们发的 |
| STFC（Hartree Centre / Daresbury / RAL） | RSE、HPC Application Developer | 公共部门，招人节奏慢但对 MSc 友好 |
| 各大学 RSE 组（剑桥 / 牛津 / UCL / Imperial / 布里斯托 / 谢菲尔德） | Research Software Engineer | 集中在 [jobs.ac.uk](https://www.jobs.ac.uk)，滚动发布 |
| Diamond Light Source、Alan Turing Institute | Scientific Software / Research Engineer | 同上 |
| ⚠️ Met Office、UKAEA | HPC / Computational Scientist | 技术上极其对口，**但常有国籍或安全审查限制**，投前先看 eligibility 那一段，别白花时间 |

### 冲刺 —— 技术方向对口，但门槛在你目前缺的那一格（GPU / 生产经验）

| 雇主 | 岗位名怎么搜 | 你的差距 |
|---|---|---|
| Arm（剑桥） | HPC / Compiler / Performance Engineer | 最接近的一家「工业界冲刺」，你的 profiling 与体系结构叙事直接对得上 |
| AMD（剑桥 / 布里斯托）、NVIDIA UK | ROCm / CUDA / HPC Solutions | 要 GPU 实操，`llm_inference_archer2` 的数据能补一部分 |
| AWS、Microsoft、Google 的英国 office | HPC / Azure Batch / Infra Engineer | 流程长、竞争激烈，但正经招 new grad |
| Google DeepMind、Anthropic（伦敦） | Research Infrastructure | 门槛最高的一档，投了不亏但别当计划 |
| Jane Street、Optiver、IMC、Citadel Securities（伦敦） | Low-latency / Performance Engineer | **别忽略这条路**：C/C++ + profiling + 体系结构正是他们要的，按裸能力招人、给 sponsorship；难在笔试与心算轮 |

### 保底 —— 更宽的口子，或对新人容忍度更高

| 雇主 | 岗位名怎么搜 | 备注 |
|---|---|---|
| Eviden / Atos UK、HPE UK、Dell UK | HPC Solutions / Benchmark Engineer | 集成商与厂商侧，正好吃你「跑 benchmark + 出可信报告」这套 |
| Siemens（STAR-CCM+）、Ansys UK | CFD / Simulation Software Engineer | 科学软件厂商，PETSc / 求解器背景直接可用 |
| Rolls-Royce、Airbus UK 的仿真组 | CFD / HPC Engineer | ⚠️ 国防相关的同样有国籍与 clearance 限制 |
| 伦敦 / 剑桥的 AI 基础设施小公司 | Platform / Infra Engineer | ⚠️ 小公司常**没有 sponsor licence**——你在 Graduate Route 期内不受影响，但两年后要换签证 |
| 一般后端 / 数据工程岗 | Backend / Data Engineer | FastAPI + Python + SQL 是真的，作为兜底成立 |

**Graduate Route 期内你不需要 sponsorship，这是你现在最大的一张牌**——所以英文简历第一屏那句
work authorisation 必须写，而且要趁这两年（或 18 个月）把 Skilled Worker 的转换谈成。

## 要做的事

1. [ ] 先把签证时长那件事问清楚（决定你要不要留英，进而决定这个目录的优先级）
2. [x] ~~生成英文一页版~~ —— 已完成，`CV_ai_infra_EN_20260805`
3. [ ] 填 `UK_PHONE`；签证状态确定后改 `WORK_AUTH`
4. [ ] **从 Word 导出 PDF 并确认还是一页**（本机无 Tahoma，现有 PDF 是 LibreOffice 导出的，只能看排布）
5. [ ] 单独准备一份 EPCC / ARCHER2 相关岗位的求职信——你的项目跑在他们的机器上，这一点值得单独写一段
