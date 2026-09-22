#!/usr/bin/env python3
"""
从同一套事实底稿生成三个岗位变体的简历 docx。

两个求职方向，七个变体：

  方向一 · AI Infra（三种排布，按公司类型选，见 国内投递/README.md）
    ai_infra       一页主投；对标 ref/ai_infra 那份进面简历的排布（关联课业段、
                   关键词式技能段、技术栈内联进标题、bullet 压到两行内且数字前置）
    ai_infra_full  两页详细版，面试前回读用，一页版是它的子集
    hpc            芯片 / 超算中心 / HPC 原生岗
    perf           推理引擎 / 训练性能优化岗
    platform       互联网 AI 平台 / 智算平台岗

  方向二 · Agent 开发 / 后端开发（把 HPC_Agent 提到第一个项目）
    agent          Agent / 大模型应用岗
    backend        后端开发岗（分层架构 / 服务化 / 测试打头，ARCHER2 作为工程可信度佐证）

项目出场顺序由变体的 projects 决定，默认 ARCHER2 → HPC_Agent → MARL。

排版沿用 agentCV_20260803.docx 的 package（styles / numbering / sectPr 全部复用），
只替换 word/document.xml。改事实只改本文件顶部的 FACT 区，三份同时生效。

用法：
    python3 build_cv.py
    soffice --headless --convert-to pdf CV_*.docx --outdir .
"""
import zipfile, re, os
from xml.sax.saxutils import escape

HERE = os.path.dirname(os.path.abspath(__file__))
CN = os.path.join(HERE, "国内投递")                  # 中文简历的输出目录
# 排版母版：只借 package（styles / numbering / sectPr），内容整份换掉。
# 它不是投递件，所以 2026-09-03 从 国内投递/ 移到了 template/——**不要删、不要改名**。
SRC = os.path.join(HERE, "template", "agentCV_20260803.docx")
DATE = "20260916"

# ============================================================ 排版原语
RF = '<w:rFonts w:ascii="Tahoma" w:hAnsi="Tahoma" w:cs="Tahoma"/>'
NUM_A, NUM_B = 7, 8          # agentCV numbering.xml 里已有的两个项目符号列表


def rpr(sz=19, bold=False):
    b = '<w:b/><w:bCs/>' if bold else ''
    return f'<w:rPr>{RF}{b}<w:sz w:val="{sz}"/><w:szCs w:val="{sz}"/></w:rPr>'


def run(text, sz, bold):
    return f'<w:r>{rpr(sz, bold)}<w:t xml:space="preserve">{escape(text)}</w:t></w:r>'


def para(segs, sz=19, numid=None, border=False, ind=None):
    if isinstance(segs, str):
        segs = [(segs, False)]
    ppr = '<w:pPr>'
    if numid:
        ppr += f'<w:numPr><w:ilvl w:val="0"/><w:numId w:val="{numid}"/></w:numPr>'
    if border:
        ppr += '<w:pBdr><w:bottom w:val="single" w:sz="6" w:space="1" w:color="auto"/></w:pBdr>'
    if ind:
        ppr += f'<w:ind w:left="{ind}"/>'
    ppr += rpr(sz) + '</w:pPr>'
    return f'<w:p>{ppr}{"".join(run(t, sz, b) for t, b in segs)}</w:p>'


def spacer(sz=12):
    return f'<w:p><w:pPr><w:rPr><w:sz w:val="{sz}"/></w:rPr></w:pPr></w:p>'


def link(rid, text, sz=19, bold=False):
    """外部超链接。样式与正文一致——不加蓝色下划线，避免页头变花。"""
    return f'<w:hyperlink r:id="{rid}">{run(text, sz, bold)}</w:hyperlink>'


def para_link(segs, rid, link_text, sz=19):
    """普通文本段，尾部挂一个外链。
    显示文字与跳转目标必须成对改——只改文字会留下「看着对、点开 404」的链接。"""
    body = "".join(run(t, sz, b) for t, b in segs) + link(rid, link_text, sz, False)
    return f'<w:p><w:pPr>{rpr(sz)}</w:pPr>{body}</w:p>'


def bullet(head, body, numid=NUM_A):
    return para([(head, True), (body, False)], sz=19, numid=numid)


# 页面 A4 11906 twips，左右边距各 284 → 正文宽 11338；右对齐制表位钉在正文右边缘
TEXT_W = 11906 - 284 * 2


def title_link(text, rid, link_text, sz=20):
    """项目标题行：标题靠左加粗，仓库链接经右对齐制表位顶到行尾。
    2026-09-16 起用：链接固定在每个项目的第一行、三个项目纵向对齐，不多占一行。
    标题 + 链接超过一行宽时制表位会把链接推到下一行右端——见 README「项目标题排布」。"""
    # 左对齐：标题过长折行时，母版的两端对齐会把第一行的字距拉开，很难看
    ppr = f'<w:pPr><w:jc w:val="left"/><w:tabs><w:tab w:val="right" w:pos="{TEXT_W}"/></w:tabs>{rpr(sz)}</w:pPr>'
    return (f'<w:p>{ppr}{run(text, sz, True)}<w:r>{rpr(sz)}<w:tab/></w:r>'
            f'{link(rid, link_text, sz, False)}</w:p>')


# ============================================================ FACT：事实底稿
NAME = "李乐岩"
SITE = "https://leyan-li.com/resume.html"
EMAIL = "leyanpower@gmail.com"
EMAIL_QQ = "3073751449@qq.com"     # 2026-09-04 手改版加进页头的第二邮箱，中文版专用；英文版不放
PHONE = "+86 18805506898"
GITHUB = "github.com/lionleepower"
GITHUB_URL = "https://github.com/lionleepower"

# 项目链接。2026-09-03 手改版把它们从纯文本改成了真超链接，显示文字去掉 github.com/ 前缀
# （页头已经写过一次 github.com/lionleepower，项目行再写一遍是浪费横向空间）。
REPOS = {"p1": "HPC_PETSC_Benchmark", "p2": "HPC_Agent", "p3": "MARL_VALUE_FACTORISATION"}
REL_REPO = {"p1": "rId93", "p2": "rId94", "p3": "rId95"}
HOMEPAGE = "leyan-li.com"

# ⚠️ agentCV package 里原有的 rId8 指向 https://github.com/leyancode —— 该账号已废弃（404），
#    所以不能再复用 rId8。rId90 / rId91 / rId92 都是本脚本自己加的关系：
#    个人主页、本简历用的 gmail（agentCV 的 rId7 指向 QQ 邮箱，不能复用）、以及现在的 GitHub 主页。
#    GitHub 链接的显示文字和跳转目标必须一起改——只改文字会留下一个点开是 404 的超链接。
HYPERLINK = "http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink"
REL_GH, REL_SITE, REL_MAIL = "rId92", "rId90", "rId91"
REL_MAIL_QQ = "rId97"              # rId93–95 是三个仓库，rId96 是英文版的 LinkedIn
EXTRA_RELS = (f'<Relationship Id="{REL_SITE}" Type="{HYPERLINK}" Target="{SITE}" TargetMode="External"/>'
              f'<Relationship Id="{REL_MAIL}" Type="{HYPERLINK}" Target="mailto:{EMAIL}" TargetMode="External"/>'
              f'<Relationship Id="{REL_GH}" Type="{HYPERLINK}" Target="{GITHUB_URL}" TargetMode="External"/>'
              f'<Relationship Id="{REL_MAIL_QQ}" Type="{HYPERLINK}" Target="mailto:{EMAIL_QQ}" TargetMode="External"/>'
              + "".join(f'<Relationship Id="{REL_REPO[k]}" Type="{HYPERLINK}" '
                        f'Target="{GITHUB_URL}/{REPOS[k]}" TargetMode="External"/>' for k in REPOS))
# ⚠️ 2026-09-03 手改版删掉了第三段「课程与毕业论文 2026.08 完成｜可入职时间 2026.09.01｜
#    学位证书 2026.12 获得」，并给日期加了「（预计）」。可入职时间是这份简历最强的一张牌
#    （比同届早、对缺实习是有效对冲），删掉它是一个有代价的取舍——要恢复就把下面那行取消注释。
EDU_MSC = [("爱丁堡大学 University of Edinburgh 英国 | 2025.09 – 2026.12（预计）  ", False),
           ("高性能计算与数据科学 硕士", True),
           # ("  课程与毕业论文 2026.08 完成｜可入职时间 2026.09.01｜学位证书 2026.12 获得", False),
           ]
# 2026-09-16 手改版：两校并列、日期写整个本科（2021.09 起），「2+2」留在括号里解释为什么是两校
EDU_BSC = [("利物浦大学 University of Liverpool 英国 / 西交利物浦大学 | 2021.09 – 2025.06  ", False),
           ("计算机科学 本科", True),
           ("（2+2），一等荣誉学位", False)]
PAPER = ("论文发表：", "Li, Leyan. Convolutional Neural Networks Based Medical Image Analysis. "
         "International Conference on Engineering Management, Information Technology and Intelligence, EMITI 2024.")

# 关联课业：写主题名而非课程代码，逐项须能在成绩单上找到对应课。
# ⚠️ 投递前按成绩单核对一遍；没修过的直接删，不要为了关键词留着。
COURSES = ("关联课业：", "消息传递并行编程（MPI）、线程并行编程（OpenMP）、HPC 体系结构、"
           "性能编程与优化、GPU / 加速器编程、并行设计模式、高性能数据分析、机器学习")

# ---------------- 技能条目 ----------------
SKILL = {
"parallel": ("并行与分布式性能工程：",
    "MPI、OpenMP、hybrid MPI+OpenMP、PETSc、Slurm；在英国国家超算 ARCHER2 上完成最多 32 节点 / 4,096 核的正式对照实验。"
    "理解 strong / weak scaling、parallel efficiency 与饱和点判定，以及 halo exchange、CG global reduction（allreduce）"
    "等集合通信开销与 surface-to-volume ratio 对通信暴露的影响。"),

"profiling": ("性能剖析与体系结构：",
    "Linaro MAP call-tree profiling；可从 NUMA / CCX / 共享 L3、memory bandwidth、线程绑定（OMP_PLACES、OMP_PROC_BIND）"
    "与负载均衡角度解释瓶颈，并把开销拆成计算、通信、同步等待三类分别归因。"),

"dl": ("深度学习与推理基础设施：",
    "熟悉 PyTorch，实现过多智能体 actor-critic 训练流程并诊断过训练不收敛的根因；"
    "熟悉 LLM function calling / tool schema 设计与离线评测方法；"
    "了解 GPU 上的分布式并行策略（数据并行、张量并行）与 NCCL 集合通信模式，以及推理服务的吞吐 / 时延 / batching 取舍。"),

"eng": ("编程与工程：",
    "C/C++、Python、Bash、SQL；Linux、Git、pytest、GitHub Actions CI，了解 Docker。"
    "习惯把实验做成可复现管线：参数化提交脚本 → 基于内容的日志审计 → pandas 聚合 → 图表与回归测试。"),

"sched": ("作业调度与集群：",
    "Slurm 作业提交、资源申请与满节点 placement 策略（--distribution、--hint=nomultithread、--exact）；"
    "用 lscpu / numactl / hwloc 核对节点内 NUMA 与 CCX 边界并验证线程绑定实际生效；"
    "有把整批实验参数化成提交脚本、并用 fake Slurm 在 CI 里跑通提交路径的经验。"),

"service": ("服务化与可观测性：",
    "FastAPI + Pydantic 的接口层与异常到 HTTP 语义的映射（依赖未就绪 503、参数非法 422）；"
    "trace_id 贯穿的 JSON Lines 结构化事件流与可回放执行链路；脱敏收敛在单一出口点并由扫描测试强制。"
    "了解 REST / HTTP、限流、幂等性；SQLite / MySQL 的索引与查询优化，了解 Redis 缓存场景与 TTL。"),

"numeric": ("数值方法与求解器：",
    "PETSc KSP / PC 栈：CG + GAMG 代数多重网格、GMRES + block Jacobi/ICC，理解 preconditioner 随分区变化对可比性的破坏；"
    "2D five-point / 3D seven-point stencil 离散与已知解误差校验；理解迭代数、每迭代成本与总吞吐三者需要分开看。"),

"data": ("数据分析与可视化：",
    "pandas、NumPy、Matplotlib；实验日志解析、指标计算、中位数与观测区间的误差表达，"
    "以及把关键数值锁进测试以防图表与结论漂移。"),
}

# ---------------- 技能条目：关键词式（ai_infra 变体用） ----------------
# 参考简历的技能段是 5 行纯列表，一眼扫得完；上面的 SKILL 是散文段，每条 3–4 行。
# 这里改成「工具关键词打头 + 一句能力边界」，行数减半而关键词密度更高。
# 规则不变：技能段只写项目段证明不了的东西，做过的事交给项目 bullet 用细节证明。
SKILL_KW = {
"lang": ("编程语言：", "C / C++、Python、Bash、SQL"),

"parallel": ("并行与分布式：",
    "MPI、OpenMP、hybrid MPI+OpenMP、PETSc、Slurm、numactl / hwloc / lscpu；"
    "strong / weak scaling、parallel efficiency 与饱和点判定；"
    "halo exchange、CG global reduction（allreduce）等集合通信开销与 surface-to-volume ratio 对通信暴露的影响"),

"profiling": ("性能剖析与体系结构：",
    "Linaro MAP call-tree profiling、STREAM 内存带宽基线、roofline / 访存墙估算；"
    "把开销拆成计算、通信、同步等待三类分别归因；"
    "从 NUMA / CCX / 共享 L3、memory bandwidth、线程绑定（OMP_PLACES、OMP_PROC_BIND）与负载均衡角度解释瓶颈"),

# 2026-09-16 手改版加了 RAG / 上下文压缩 / 并行处理 / LangChain。RAG 有项目 bullet（a_rag）背书，写在做过的那一截；
# 其余三项没有项目背书，只能挂在「了解」后面——与英文 llm 行的 working knowledge of ... 同一层级，不许升级成 bullet。
"dl": ("深度学习与大模型：",
    "PyTorch、NumPy、pandas；多智能体 actor-critic 训练与不收敛根因诊断；"
    "LLM function calling / tool schema 设计、离线评测集与消融实验、最小 RAG；"
    "了解上下文压缩、并行处理与 LangChain / LangGraph 等框架"),

# 「（课程与自学）」这个限定必须留着：它是这段唯一没有项目 bullet 背书的技能，
# 不标层级就是超范围声称。但也不必写成「尚无生产经验」——那是在简历上自我淘汰。
"gpu": ("GPU 与推理服务（课程与自学）：",
    "CUDA 编程模型与 GPU 存储层次、NCCL 集合通信、数据并行 / 张量并行；"
    "推理服务的 batching 与吞吐-时延取舍、KV cache 与量化档位对每 token 访存量的影响"),

"eng": ("工程与工具链：",
    "Linux、Git、pytest、GitHub Actions CI、FastAPI + Pydantic、SQLite / MySQL，了解 Docker；"
    "习惯把实验做成可复现管线：参数化提交脚本 → 基于内容的日志审计 → pandas 聚合 → 图表与回归测试"),

# ⚠️ 上面的 eng 行含 FastAPI + Pydantic、SQLite / MySQL、Docker，与下面的 service 行重复。
# 同时用这两行的变体（agent / backend）请改用 eng_lite，把这三项留给 service 那行。
"eng_lite": ("工程与工具链：",
    "Linux、Git、pytest、GitHub Actions CI；"
    "习惯把工作做成可复现管线：参数化脚本 → 基于内容的输入校验 → 聚合与回归测试，把关键数值锁进测试以防结论漂移"),

# agent / backend 变体用。同样守 8/3 那条规则：只写项目 bullet 证明不了的东西
# （了解性知识与工具面），做过的事交给项目段用细节去证明。
"service": ("后端与服务化：",
    "FastAPI + Pydantic、SQLite / MySQL（索引、事务与查询优化）、REST / HTTP、JSON Lines 结构化日志；"
    "异常到 HTTP 语义的映射（依赖未就绪 503、参数非法 422）；"
    "了解限流、幂等性、Redis 缓存场景与 TTL、Docker"),
}

# ---------------- 技能条目：一页版（四行） ----------------
# 一页纸放不下六行技能。合并原则：把「并行 + 剖析」并成一条、「深度学习 + GPU」并成一条，
# GPU 的「课程与自学」限定必须跟着走——它是全篇唯一没有项目 bullet 背书的技能。
SKILL_1P = {
"lang": ("编程语言：", "C / C++、Python、Bash、SQL"),

"hpc": ("并行与性能工程：",
    "MPI、OpenMP、hybrid MPI+OpenMP、PETSc、Slurm、numactl / hwloc、Linaro MAP；"
    "strong / weak scaling、parallel efficiency 与饱和点判定，halo exchange、global reduction（allreduce）等集合通信开销，"
    "roofline / 访存墙估算，NUMA 与线程绑定"),

"ml": ("深度学习与大模型：",
    "PyTorch、NumPy、pandas；LLM function calling / tool schema 设计、离线评测集构建与消融实验。"
    "GPU 与推理服务为课程与自学层面：CUDA 编程模型、NCCL 集合通信、数据 / 张量并行、"
    "batching 与吞吐-时延取舍、KV cache 与量化对每 token 访存量的影响"),

"eng": ("工程与工具链：",
    "Linux、Git、pytest、GitHub Actions CI、FastAPI + Pydantic、SQLite / MySQL，了解 Docker；"
    "把实验做成可复现管线：参数化提交脚本 → 基于内容的日志审计 → pandas 聚合 → 回归测试"),
}

# ---------------- agent 变体的 bullet 写法（2026-09-16）----------------
# HR 的反馈：企业想看「针对什么难点、用了什么策略、效果怎么样」。第一版把「难点 / 做法 / 效果」三个词直接印在
# bullet 里，本人看过后否掉：没有哪家简历这么写，观感不专业。现在的规矩——
#   · 标签仍是名词短语，正文是一句连贯的话，用「由于 / 为了 / 因此 / 使得 / 以保」这类词把难点→做法→效果串起来；
#   · 只有工程重点（同构契约、防御式解析、可观测性、自动化测试、词法检索）需要交代难点，其余条目沿用 0904 版的写法；
#   · 事实与数字与 0904 版逐个相同，只是把可观测性 / 自动化测试 / 词法检索从「工程化外围」拆成各自可见的三条。
# ---------------- 项目一：ARCHER2 ----------------
P1_TITLE = {
"perf":     "项目经历：ARCHER2 超算上 4,096 核规模的 hybrid MPI+OpenMP 布局对照实验——通信暴露与线程空转的权衡",
"platform": "项目经历：ARCHER2 超算上 4,096 核规模的可审计 benchmark 实验管线（408 runs）",
"hpc":      "项目经历：ARCHER2 超算上 PETSc hybrid MPI+OpenMP 布局的可审计性能实验（32 节点 / 4,096 核）",
"ai_infra": "ARCHER2 超算上 4,096 核规模的并行布局选型与性能归因——通信暴露与线程空转的权衡",
# Agent / 后端赛道里这个项目不是主角，标题只交代「数据从哪来、为什么可信」
# 2026-09-16 缩短：链接右对齐在标题行，标题 + 链接必须一行放下（旧题 45 字 + 32 字链接会折行）
"agent":    "ARCHER2 超算上 4,096 核的 PETSc 布局对照实验——上一项目的数据来源",
"backend":  "ARCHER2 超算上 4,096 核规模的可审计 benchmark 实验管线（408 runs）",
}
P1_DESC = ("项目描述：",
    "在英国国家超算 ARCHER2（HPE Cray EX，双路 AMD EPYC 7742、128 核/节点，Slingshot 互连）上研究一个受约束的配置问题："
    "总核数固定时，减少 MPI rank 数、增大每 rank 的 OpenMP 线程数，能否用省下的通信与进程开销抵消线程组创建、barrier 与空转成本。"
    "负载为 2D five-point / 3D seven-point stencil + CG+GAMG，规模 5M–165M unknowns，比较四种满节点布局（128×1 / 64×2 / 32×4 / 16×8）。"
    "正式结论只使用 408 个通过内容审计的 run（264 weak-scaling + 144 fixed-size strong-scaling）。")
P1_STACK = ("技术栈：",
    "C、PETSc、MPI、OpenMP、Slurm、Bash、Python、pandas、Matplotlib、Linaro MAP、GitHub Actions、Linux")

# 内联进标题行的短技术栈（ai_infra 变体用，每个项目省一整行）
P1_STACK_INLINE = "C · PETSc · MPI · OpenMP · Slurm · Linaro MAP · Python / pandas · GitHub Actions"
P2_STACK_INLINE = "Python · SQLite · FastAPI · Pydantic · OpenAI SDK（function calling）· pytest · RAG"
P3_STACK_INLINE = "Python · PyTorch · PyMARL · MAPPO · VDN · QMIX · CTDE · PPO · PettingZoo / MPE2"

# ai_infra 变体的项目描述：比通用版短一截，把行数让给带数字的 bullet
P1_DESC_SHORT = ("项目描述：",
    "在英国国家超算 ARCHER2（HPE Cray EX，双路 AMD EPYC 7742、128 核/节点，Slingshot 互连）上研究一个受约束的配置问题："
    "总核数固定时，减少 MPI rank 数、增大每 rank 的 OpenMP 线程数，能否用省下的通信与进程开销抵消线程组创建、barrier 与空转成本。"
    "负载为 2D/3D stencil + CG+GAMG，5M–165M unknowns，比较四种满节点布局；正式结论只用 408 个通过内容审计的 run。")

# 一页版的项目描述：只交代问题是什么，结论一律留给 bullet
P1_DESC_1P = ("项目描述：",
    "在英国国家超算 ARCHER2（双路 AMD EPYC 7742、128 核/节点，Slingshot 互连）上研究一个受约束的配置问题："
    "总核数固定时，如何在 MPI rank 数与每 rank 的 OpenMP 线程数之间切分——"
    "这两个值在真实作业里几乎都由提交脚本的默认值决定，很少有人量过默认值的代价。"
    "负载为 2D/3D stencil + CG+GAMG，5M–165M unknowns，四种满节点布局（128×1 / 64×2 / 32×4 / 16×8）。")
# agent 变体（2026-09-16）：描述只交代问题与设定，「默认值的代价」这个难点挪进 a_results 的难点句，
# 否则三段式 bullet 会把描述里的话再说一遍。
P1_DESC_AGENT = ("项目描述：",
    "在英国国家超算 ARCHER2（AMD EPYC 7742、128 核/节点，Slingshot 互连）上研究一个受约束的配置问题："
    "总核数固定时，MPI rank 数与每 rank 的 OpenMP 线程数怎么切分——真实作业里这两个值几乎都由提交脚本默认值决定，"
    "默认值的代价很少被量化。负载 2D/3D stencil + CG+GAMG，5M–165M unknowns，四种满节点布局 128×1 / 64×2 / 32×4 / 16×8。")
P2_DESC_1P = ("项目描述：",
    "把上一项目的 PETSc benchmark 数据结构化为 SQLite，性能分析任务封装为确定性工具："
    "让 LLM 只负责「选哪个工具、参数是什么」，数值一律由确定性代码算，从而让 Agent 的正确性变成可评测量。")
P3_DESC_1P = ("项目描述：",
    "在 MAPPO 的 critic 上分别接入 VDN 加性分解与 QMIX 单调 mixing 做单变量对照——"
    "三个变体共用同一套 runner / buffer / shared RNN actor 与全部 PPO 超参，差异只在 critic 分支。")

P1 = {
"design": ("实验设计：",
    "2D/3D 按 unknown 数对齐而非按网格边长，使同一线性系统规模下可比较两种 stencil 的通信暴露；"
    "weak scaling 以 25,000 ≤ unknowns/core ≤ 100,000 的准入规则组织出 ~40k（6 点）与 ~80k（5 点）两条固定本地工作量的链，"
    "fixed-20M 则有意越过该窗口降到 ~4.9k unknowns/core 以观察布局何时饱和。"
    "计时只读 PETSc RepeatedSolves stage（1 次 warm-up 建 GAMG 层次、19 次复用 preconditioner），不把 setup 与稳态求解混为一谈；"
    "每个正式配置 3 次重复，取中位数、误差线为观测 min–max。"),

"retract": ("主动作废不可信结果：",
    "审计发现 launcher 时代的日志有 302 / 303 份的实际 MPI process 数与文件名不符（一份文件名请求 2048 ranks，PETSc header 只报 32），"
    "据此废弃该阶段全部性能曲线，并把「从日志内容而非文件名解析 process / thread 数」写成分析入口的硬校验；"
    "另发现 default GMRES + block Jacobi/ICC 会随 rank 数改变 preconditioner、一次 --ksp_rtol override 被 PETSc 静默忽略，"
    "因此禁止用该批数据做跨 rank 布局排名。"),

"pipeline": ("可审计聚合管线：",
    "每份日志须通过 PETSc 自报 architecture、实际 ranks × threads、20 次 solve 全部收敛、timed stage 恰好 19 个 KSPSolve 且无 PCSetUp、"
    "链接库与 solver signature 共六项检查才进入聚合；未通过的标为 superseded，只解释方法如何改进，永不混进中位数。"),

"weak": ("Weak-scaling 结论：",
    "2D 上 64×2 在 11 个 size/node 点中赢 8 个，165M / 32 节点达 794.8M equations/s，比 flat-MPI 128×1 高 13.1%；"
    "3D 上 32×4 赢 6 个，最大吞吐增益 33.2%（41M / 4 节点，对应 24.9% 时间节省）。"
    "结论是最佳布局随维度与规模改变，不存在单一「最优线程数」；由于 GAMG 迭代数会随分区小幅变化，同时比较吞吐量与 seconds per KSP iteration。"),

"strong": ("Strong-scaling 结论：",
    "固定 20M、1→32 节点：2D 最快为 64×2，0.0277 s/solve、29.83× 加速、93.2% 累积效率；"
    "3D 最快为 16×8，0.0681 s/solve、14.24× 加速、比 flat MPI 快 3.81×。"
    "各布局饱和点不同（128×1 在 8 节点后变慢，64×2 与 32×4 在 16 节点后变慢，16×8 到 32 节点仍在下降）——"
    "即每核工作量下降到一定程度后，更粗的进程粒度才开始有回报；这与固定 batch 继续扩机器时的收益递减是同一类问题。"),

"map": ("Profiling 定位机理：",
    "Linaro MAP call tree 显示 threads/rank 上升时，solve window 内 MPI 占比从 46.7%（64×2）降到 6.2%（16×8），"
    "而 OpenMP runtime 等待从 48.3% 升到 76.5%——布局排序即「通信暴露」与「线程空转」两条曲线的交点；"
    "同时排除 threaded BLAS 的解释（LibSci 最多只占 solve-window core-time 的 2.1%）。"
    "因 MAP 插桩会不均匀扰动运行时间，只读布局之间的占比排序，绝不与未插桩的 scaling timing 混用。"),

"ops": ("工程化与可发布性：",
    "Slurm 提交脚本参数化生成全部正式配置，分析侧 16 个 Python 脚本配 pytest 断言公开矩阵行数、头条数值、README 图片与跨维度换算，"
    "GitHub Actions 跑公开数据测试并用 fake Slurm 执行提交脚本；对外发布的 5 份代表日志经脚本脱敏"
    "（去用户、allocation、node name、job ID 与个人路径），并附私有原件与公开副本的 SHA-256 manifest。"),

"limits": ("局限如实标注：",
    "3 次重复的误差线是观测 min–max 而非置信区间；结论绑定给定 stencil / solver / PETSc build / placement policy，"
    "不代表所有 PETSc 应用都有相同最佳布局；样本中可重复观察到的 superlinear speedup 未能确定硬件原因，写为未解释项而非卖点。"),

# ---- ai_infra 压缩版：数字前置、每条控制在两行内 ----
"c_layout": ("布局选型结论：",
    "固定总核数扫描 128×1 / 64×2 / 32×4 / 16×8 四种满节点布局。2D weak scaling 上 64×2 在 11 个 size/node 点赢 8 个"
    "（165M unknowns / 32 节点 794.8M equations/s，比 flat MPI 高 13.1%），3D 上 32×4 最大增益 33.2%；"
    "fixed-20M strong scaling 上 2D 最快为 64×2（0.0277 s/solve、29.83× 加速、93.2% 累积效率），3D 最快为 16×8（比 flat MPI 快 3.81×）。"
    "最佳并行度随维度与规模改变，不存在单一「最优线程数」。"),

"c_map": ("Profiling 归因：",
    "Linaro MAP call tree 显示 threads/rank 上升时，solve window 内 MPI 占比从 46.7% 降到 6.2%、OpenMP runtime 等待从 48.3% 升到 76.5%——"
    "布局排序即「通信暴露」与「线程空转」两条曲线的交点；同时排除 threaded BLAS 的解释（LibSci ≤ 2.1% solve-window core-time）。"
    "因插桩会不均匀扰动运行时间，只读布局之间的占比排序，绝不与未插桩的 scaling timing 混用。"),

"c_saturate": ("饱和点与收益递减：",
    "各布局饱和点不同——128×1 在 8 节点后变慢，64×2 与 32×4 在 16 节点后变慢，16×8 到 32 节点仍在下降："
    "每个计算单元的工作量降到一定程度后，更粗的进程粒度才开始有回报。"
    "这与固定 batch 继续扩机器时的收益递减、以及并行切分粒度的选型是同一类问题。"),

"c_retract": ("主动作废不可信结果：",
    "审计发现 launcher 时代 303 份日志中有 302 份的实际 MPI process 数与文件名不符（文件名请求 2048 ranks，PETSc header 只报 32），"
    "据此废弃该阶段全部性能曲线，并把「从日志内容而非文件名解析 process / thread 数」写成分析入口的硬校验。"),

"c_pipeline": ("可审计管线与工程化：",
    "每份日志须通过 PETSc 自报 architecture、实际 ranks × threads、20 次 solve 全部收敛、timed stage 恰好 19 个 KSPSolve 且无 PCSetUp 等六项检查才进聚合，"
    "未通过标为 superseded、永不混进中位数；Slurm 提交脚本参数化生成全部正式配置，16 个分析脚本配 pytest 锁死头条数值，"
    "GitHub Actions 跑公开数据测试并用 fake Slurm 执行提交路径。"),

# ---- 一页版：每个项目只留最核心的三条，结果打头、机制跟在破折号后 ----
"o_layout": ("布局选型：",
    "2D weak scaling 上 64×2 比 flat MPI 高 13.1%（165M unknowns / 32 节点、794.8M equations/s），"
    "fixed-20M strong scaling 达 29.83× 加速、93.2% 累积效率；3D 上最佳布局改为 32×4（最大增益 33.2%）"
    "与 16×8（比 flat MPI 快 3.81×）——最佳并行度随维度、规模与每核工作量改变，不存在单一「最优线程数」；"
    "这与固定 batch 继续扩机器时的收益递减是同一类问题。"),

"o_map": ("机理归因：",
    "Linaro MAP 把布局排序解释为两条曲线的交点——threads/rank 上升时 solve window 内 MPI 占比 46.7%→6.2%、"
    "OpenMP 等待 48.3%→76.5%，即「通信暴露」与「线程空转」的权衡；排除 threaded BLAS 的解释（LibSci ≤ 2.1% core-time），"
    "并因插桩扰动运行时间而只读占比排序、不与未插桩 timing 混用。"),

# 一页版专用的短版门禁：加了 o_exposure 之后一页放不下四条长 bullet，
# 这里砍掉工程化那半句（参数化提交脚本 / pytest / CI），只留审计与硬校验。
# 内容仍是 o_audit 的子集，不含任何独有表述。
"o_audit_short": ("可信度门禁：",
    "审计出 303 份日志中有 302 份的实际 MPI process 数与文件名不符，据此废弃整阶段性能曲线，"
    "正式结论只用 408 个通过内容审计的 run——并把「从日志内容而非文件名解析 process / thread 数」写成分析入口硬校验。"),

"o_audit": ("可信度门禁：",
    "审计出 303 份日志中有 302 份的实际 MPI process 数与文件名不符，据此废弃整阶段性能曲线，"
    "正式结论只用 408 个通过内容审计的 run——把「从日志内容而非文件名解析 process / thread 数」写成分析入口硬校验；"
    "提交脚本参数化生成全部正式配置，pytest 锁死头条数值，GitHub Actions 用 fake Slurm 跑通提交路径。"),

# 背景与方法创新版：给 ARCHER2 不是主角的变体（agent / backend）用。
# 数字出处：13.1% / 33.2% 见 results_merged；264 = weak-scaling run 数（= 408 − 144 strong）；
# 116–372% 与「halo 与归约在互不相交调用路径上、故可相加」见仓库分析脚本与论文的事件嵌套一节；
# 48.2% → 26.4% 为 2D 32 节点各布局 sync_pct 的中位数，
# 出自 analysis/data/nproc_2d_libsci/tables/repeated_fullnode_event_shares.csv。
# ⚠️ 现实意义写在项目描述里、吞吐差写在 results_merged 里，这一条都不要再重复一遍。
"c_context": ("研究口径与自建指标：",
    "规模推到 32 节点 / 4,096 核才看得到饱和点。测量用两个后端：Linaro MAP 会扰动运行时间，只用于读布局间的占比排序；"
    "PETSc -log_view 零插桩、覆盖全部 264 个 weak-scaling run，在它上面自建了可累加的「同步暴露占比」——"
    "事件嵌套使叶子事件直接相加会达到 KSPSolve 的 116–372%，而 halo 交换与全局归约位于互不相交的调用路径，二者之和才是合法指标。"
    "该占比在 32 节点上从 flat MPI 的 48.2% 降到 16×8 的 26.4%，使「布局为什么更快」成为可逐点度量的量，而不是事后解释。"),

# ai_infra 系列用的 exposure share 短版。c_context 里那句「MAP 扰动运行时间、只读占比排序」
# 在这里必须去掉——o_map / c_map 已经说过一次，同一份简历里不重复。
"o_exposure": ("自建的可累加指标：",
    "在 PETSc -log_view 上定义「同步暴露占比」：事件嵌套使叶子事件直接相加会达到 KSPSolve 的 116–372%，"
    "而 halo 交换与全局归约位于互不相交的调用路径，二者之和才是合法指标；"
    "该指标零插桩、覆盖全部 264 个 weak-scaling run，在 32 节点上从 flat MPI 的 48.2% 降到 16×8 的 26.4%。"),

# ---- agent 变体三段式（2026-09-16）。数字与 c_context / results_merged 逐个相同 ----
"a_metric": ("自建可累加的同步指标：",
    "-log_view 零插桩、覆盖 264 个 weak-scaling run，但事件嵌套使叶子事件直接相加达 KSPSolve 的 116–372%；"
    "由于 halo 交换与全局归约在互不相交的调用路径上，取二者之和定义「同步暴露占比」（MAP 扰动运行时间，只读占比排序）。"
    "32 节点上从 flat MPI 的 48.2% 降到 16×8 的 26.4%，使「为什么更快」可逐点度量而非事后解释。"),

"a_results": ("性能结论（摘要）：",
    "weak scaling 上 2D 最佳布局 64×2（165M / 32 节点 794.8M equations/s，比 flat MPI 高 13.1%）、3D 最佳 32×4（最大增益 33.2%）；"
    "fixed-20M strong scaling 上 2D 达 29.83× 加速 / 93.2% 累积效率，3D 的 16×8 比 flat MPI 快 3.81×。"
    "最佳布局随维度、规模与每核工作量改变，Linaro MAP 定位其机理为 MPI 通信暴露（46.7%→6.2%）与 OpenMP 空转等待（48.3%→76.5%）的交点。"),

# 算力含义：HR 要的「相同硬件省多少算力」。全部是头条数的算术换算，逐个带范围：
#   1/1.131 = 0.884 → 2D weak 165M / 32 节点少用 11.6% 节点时；1/1.332 = 0.751 → 24.9%（仓库 README 原有）；
#   1/3.81 = 0.262 → 3D fixed-20M 32 节点上节点时降到 26%。不许写成「平均节省」。
"a_value": ("对算力成本的含义：",
    "只改提交脚本的两个默认值、不改代码不加节点：同一作业的节点时在 2D weak 最大点少用 11.6%、"
    "3D 最佳点少用 24.9%，3D fixed-20M 32 节点上降到 flat MPI 的 26%；交付的是「先量再定默认值」的方法而非固定配置。"),

# 结论合并版：给 platform 变体用，省出篇幅给管线
"results_merged": ("性能结论（摘要）：",
    "weak scaling 上 2D 最佳布局 64×2（165M / 32 节点 794.8M equations/s，比 flat MPI 高 13.1%）、3D 最佳 32×4（最大增益 33.2%）；"
    "fixed-20M strong scaling 上 2D 达 29.83× 加速 / 93.2% 累积效率，3D 的 16×8 比 flat MPI 快 3.81×。"
    "最佳布局随维度、规模与每核工作量改变，Linaro MAP 定位其机理为 MPI 通信暴露（46.7%→6.2%）与 OpenMP 空转等待（48.3%→76.5%）的交点。"),
}

# ---------------- 项目二：hpc-benchmark-agent ----------------
P2_TITLE = "面向该 benchmark 数据的 Agent 式性能分析系统"
# 本项目排在 ARCHER2 前面时，「该 benchmark」没有指代对象，标题须自带出处
P2_TITLE_STANDALONE = "面向 ARCHER2 超算上 PETSc benchmark 数据的 Agent 式性能分析系统"
P2_DESC = ("项目描述：",
    "把上一项目的 PETSc benchmark 数据结构化为 SQLite，将性能分析任务封装为确定性工具，"
    "以中文规则 router 作为可验证 baseline，再接入 LLM function calling router，"
    "用自建 30 问五类中文评测集给两者打同一份分——规则 83.3%、LLM 100%。"
    "命题是：让 LLM 只负责「选哪个工具、参数是什么」，数值一律由确定性代码算，从而让 Agent 的正确性变成可评测量。")
# ⚠️ P2_DESC / P2_DESC_1P 开头写的是「上一项目的 PETSc benchmark 数据」——这句只在
#    ARCHER2 排在前面时成立。agent / backend 变体把本项目提到第一个，必须改用下面这份
#    独立描述，否则第一屏就出现一个指向不存在的「上一项目」的引用。
P2_DESC_STANDALONE = ("项目描述：",
    "把英国国家超算 ARCHER2 上真实的 PETSc benchmark 结果结构化为 SQLite，把性能分析任务封装为确定性工具："
    "让 LLM 只负责「选哪个工具、参数是什么」，数值一律由确定性代码算，从而让 Agent 的正确性变成可评测量。"
    "中文规则 router 作为可验证 baseline，与 LLM function calling router 共用同一套自建 30 问中文评测集打分——规则 83.3%、LLM 100%。")
# agent 变体（2026-09-16）：与 P2_DESC_1P 同一原则——描述不带数字，83.3% / 100% 留给 a_eval 的效果句。
P2_DESC_AGENT = ("项目描述：",
    "把英国国家超算 ARCHER2 上真实的 PETSc benchmark 结果结构化为 SQLite，把性能分析任务封装为确定性工具："
    "让 LLM 只负责「选哪个工具、参数是什么」，数值一律由确定性代码算，从而让 Agent 的正确性变成可评测量。")
# ③ 预览件专用：假设审计后的 408 个 run 已导入。**未实现，不许进 国内投递/**
P2_DESC_AGENT_V3 = ("项目描述：",
    "把下一项目审计后的 408 个 ARCHER2 run（264 weak + 144 strong scaling）经内容校验导入 SQLite，"
    "把性能分析任务封装为确定性工具：让 LLM 只负责「选哪个工具、参数是什么」，数值一律由确定性代码算，"
    "从而让 Agent 的正确性变成可评测量。")
P2_STACK = ("技术栈：", "Python、SQLite、pytest、FastAPI、OpenAI SDK（function calling）、Pydantic、Git、Linux")

P2 = {
"arch": ("分层架构与同构契约：",
    "数据导入 / 指标 / 工具 / 检索 / 路由 / 可观测六层，加 CLI 与 FastAPI 两个平级且互不依赖的进程边界；"
    "规则 router 与 LLM tool call 输出严格同构（intent + 参数），因此可共用同一套评测集、切换只需改一行 dispatch。"
    "各层合同由 229 项自动化测试钉死，全量离线可跑、不需要 API key（LLM 部分走 FakeLLM 依赖注入）。"),

"fc": ("LLM function calling 与防御式解析：",
    "tool schema 的 description 写明工具边界，unknowns 刻意设为可选——省略参数即「追问」、不调用工具即「拒答」；"
    "未调用工具、幻觉工具名、arguments 非合法 JSON 三类异常统一收敛为显式 unknown，绝不猜参数，以避免「静默算错」；"
    "API 失败向上抛出而非回退规则 router，以免污染评测。"),

"eval": ("评测机制与消融结论：",
    "自建 30 问五类中文评测集（正常 / 追问 / 拒答 / 数字陷阱 / 规则已知会错的对抗题），期望值是 tool call 而非答案文本，"
    "harness 对 router 实现无知；消融显示同一模型去掉 system prompt 只有 63.3%——准确率主要由工具说明书与策略 prompt 决定，而非模型本身。"
    "报告如实标注局限：题量 30、单模型、单次运行、出题人即作者。"),

"ops": ("工程化外围：",
    "trace_id 贯穿的 JSON Lines 事件流可完整回放一次执行，脱敏收敛在单一出口点并由扫描测试强制；"
    "FastAPI 暴露 POST /ask，非法 router 由 Pydantic 拦为 422、缺 key 映射 503 而非 500，与 CLI 的退出码 2 各自独立；"
    "最小 RAG 用 IDF 加权词法检索（纯标准库、刻意不用向量库），检索不到即返回空、不注入，"
    "未开启时 messages 与评测时逐字节一致并由测试锁死，以保结论可比。"),

# ---- agent 变体三段式（2026-09-16）。事实与 arch / fc / eval / ops 相同，按 HR 建议拆出
#      「可观测性」「自动化测试」「为什么词法检索」三条各自可见的 bullet。
#      5 个事件名与 229 / 422 / 503 均对 HPC_Agent README 与 tests/ 核过（test_llm_router、test_api、test_tracing）。
"a_contract": ("分层架构与同构契约：",
    "为了让规则 router 与 LLM tool call 能同尺比较，两者输出严格同构（intent + 参数）；"
    "导入 / 指标 / 工具 / 检索 / 路由 / 可观测六层，CLI 与 FastAPI 为互不依赖的进程边界；"
    "共用同一套评测集打分，切换只改一行 dispatch。"),

"a_defense": ("LLM function calling 与防御式解析：",
    "tool schema 的 description 写明工具边界，unknowns 刻意设为可选——省略参数即「追问」、不调用工具即「拒答」；"
    "未调用工具、幻觉工具名、arguments 非合法 JSON 三类异常统一收敛为显式 unknown，绝不猜参数，以避免「静默算错」；"
    "API 失败向上抛出而非回退规则 router，以免污染评测。"),

"a_eval": ("评测机制与消融结论：",
    "自建 30 问五类中文评测集（正常 / 追问 / 拒答 / 数字陷阱 / 对抗题），期望值是 tool call 而非答案文本，"
    "harness 对 router 实现无知；规则 83.3%、LLM 100%，消融显示同一模型去掉 system prompt 只有 63.3%——"
    "准确率主要由工具说明书与策略 prompt 决定。局限如实标注：题量 30、单模型、单次运行、出题人即作者。"),

"a_trace": ("可观测性：",
    "为了让路由出错时能定位到具体哪一步，trace_id 贯穿的 JSON Lines 事件流把每次 ask 落成 "
    "ask_start / route_result / tool_call / tool_result / answer 5 个事件，可完整回放一次执行；"
    "脱敏收敛在单一出口点并由扫描测试强制。"),

"a_tests": ("自动化测试覆盖异常边界：",
    "LLM 客户端经依赖注入换成 FakeLLM，229 项测试全量离线、不需要 API key，CI 每次 push 复跑；"
    "各层合同钉死——三类 LLM 异常各有用例，FastAPI 的 POST /ask 把非法 router 拦为 422、缺 key 映射 503。"),

# 为什么词法不用向量：理由全部来自仓库 rag.py 的文档串（离线 / 确定性 / 每条命中可解释 / 零新依赖，代价是同义改写检索不到）。
# 没做过词法 vs 向量的 A/B，所以不写准确率对比——HR 建议里的「提升百分之多少」在这个项目里不存在。
"a_rag": ("词法检索而非向量检索（最小 RAG）：",
    "为了不引入 embedding 模型与向量库、也不动评测口径，用 IDF 加权词法检索（纯标准库）：离线、确定性、每条命中可按 idf 分数解释；"
    "无命中即不注入，未开启时 messages 与评测时逐字节一致（测试锁死）；代价是同义改写检索不到。"),

# ③ 预览件专用（**未实现**）：假设审计后数据已导入且有跨仓库回归测试
"a_pipeline_v3": ("数据管线与跨仓库一致性：",
    "Agent 与 benchmark 是两个仓库，回答与论文里的数字可能各说各话；因此 benchmark 仓库导出审计后 CSV → 按内容校验的导入器 → SQLite，"
    "CI 用 pytest 断言 Agent 对「32 节点 2D 最快布局」等题的回答与 benchmark README 头条数（64×2、794.8M equations/s、+13.1%）逐字一致，"
    "两个仓库的口径由测试锁死，演示时可直接查真实结果。"),

# 压缩版：把 fc + eval 合成一条
"fc_eval_merged": ("LLM function calling、防御式解析与评测：",
    "tool schema 的 description 写明工具边界，unknowns 刻意可选——省略参数即「追问」、不调用工具即「拒答」；"
    "未调用工具、幻觉工具名、坏 JSON 三类异常统一收敛为显式 unknown，绝不猜参数以避免「静默算错」。"
    "自建 30 问五类中文评测集（期望值是 tool call 而非答案文本）给两个 router 打同一份分，"
    "消融显示同一模型去掉 system prompt 只有 63.3%——准确率主要由工具说明书与策略 prompt 决定。"),

# ---- 一页版：两条 ----
"o_eval": ("可评测的路由：",
    "中文规则 router 作为可验证 baseline，与 LLM function calling router 输出严格同构（intent + 参数），"
    "共用同一套自建 30 问五类中文评测集打分——规则 83.3%、LLM 100%；"
    "消融显示同一模型去掉 system prompt 只有 63.3%，即准确率主要由工具说明书与策略 prompt 决定，而非模型本身。"),

"o_def": ("防御式解析与工程化：",
    "未调用工具、幻觉工具名、arguments 非合法 JSON 三类异常统一收敛为显式 unknown，绝不猜参数以避免「静默算错」；"
    "trace_id 贯穿的 JSON Lines 事件流可完整回放一次执行，FastAPI 的 POST /ask 把非法 router 拦为 422、缺 key 映射 503；"
    "229 项自动化测试全量离线可跑、不需要 API key。"),

# ai_infra 压缩版：把服务化 + 可观测 + RAG 收成一条
"c_serve": ("服务化与可观测性：",
    "trace_id 贯穿的 JSON Lines 事件流可完整回放一次执行，脱敏收敛在单一出口点并由扫描测试强制；"
    "FastAPI 暴露 POST /ask，非法 router 由 Pydantic 拦为 422、缺 key 映射 503 而非 500；"
    "最小 RAG 用 IDF 加权词法检索（纯标准库、刻意不用向量库），未开启时 messages 与评测时逐字节一致并由测试锁死，以保结论可比。"),
}

# ---------------- 项目三：MARL ----------------
P3_TITLE = "多智能体 Actor-Critic 方法中的价值函数分解研究"
# 2026-09-16 手改版把「（本科毕业设计）」从标题挪到技术栈行末尾，并给 ARCHER2 也加了同类标注；
# 只在 inline 变体生效（非 inline 变体的技术栈是单独一行「技术栈：」）。
STACK_TAG = {"p1": "（硕士毕业论文）", "p3": "（本科毕业设计）"}
P3_DESC = ("项目描述：",
    "在 MAPPO 的 critic 上分别接入 VDN 加性分解与 QMIX 单调 mixing 做单变量对照：三个变体共用同一套 runner / buffer / shared RNN actor 与全部 PPO 超参，"
    "差异只在 critic 分支。结论与直觉相反——表达能力更强的 critic 没有赢：稀疏奖励的 Predator-Prey（300k steps）上，"
    "最简单的加性分解唯一学到正回报（≈150），单体 critic 始终为负（−300 → −30），单调 mixing 的 critic loss 起手即 5.4×10⁴、200k 步后二次发散。"
    "技术栈：Python、PyTorch、PyMARL、MAPPO、VDN、QMIX、CTDE、PPO、PettingZoo / MPE2。")
# 技术栈内联进标题行的变体用这份描述（去掉末尾重复的技术栈句）
P3_DESC_SHORT = (P3_DESC[0], P3_DESC[1].rsplit("技术栈：", 1)[0].rstrip())
P3 = [
("训练不收敛的根因诊断：",
    "MAPPO-QMIX 的 TD 目标沿用 value-based QMIX 的 max_a Qᵢ（贪婪动作），而 actor 是 on-policy，"
    "相减得到的 td_error 并非合法 advantage 而是系统性偏乐观的量，可解释「回报冲过理论最优值后崩塌」；"
    "另定位 hypernet 经 softplus 生成的 mixing 权重（softplus(0) ≈ 0.69）对局部 Q 的梯度做乘性放大，是 critic loss 起手即 5×10⁴ 的直接原因。"),
("负结果与工程化：",
    "去掉单调约束的 non-monotonic mixer 持续梯度爆炸、未在预算内收敛，如实写进论文；"
    "并指出三个 learner 实际都只产出一个共享标量 advantage，收益来自表示与梯度路径而非真正的 per-agent credit assignment。"
    "2026 年整理为可复现仓库：修正 Predator-Prey 合作边界、用 uv.lock 锁 CPU 版 PyTorch 使实验无需 GPU、补 pytest 并接入 GitHub Actions CI。"),
# [2] 一页版：结论 + 根因 + 负结果压成一条
("反直觉结论与根因诊断：",
    "表达能力更强的 critic 没有赢——稀疏奖励的 Predator-Prey（300k steps）上最简单的加性分解唯一学到正回报（≈150），"
    "单体 critic 始终为负，QMIX 的 critic loss 起手即 5.4×10⁴、200k 步后二次发散。"
    "根因是 MAPPO-QMIX 的 TD 目标沿用 value-based 的 max_a Qᵢ（贪婪动作）而 actor 是 on-policy，"
    "相减得到的 td_error 并非合法 advantage 而是系统性偏乐观的量；非单调 mixer 的持续梯度爆炸作为负结果如实写进论文。"),
# [3] agent 变体三段式（2026-09-16）：内容与 [2] 相同，按 HR 的「转化成通用的解决问题的表达」改形状
# [3] agent 变体（2026-09-16）：与 [2] 相同，只把结尾从「如实写进论文」扩成论文对负结果的归结
#     ——仓库 README 原话：a structural inductive bias is a precondition for stable training。
("反直觉结论与根因诊断：",
    "表达能力更强的 critic 没有赢——稀疏奖励的 Predator-Prey（300k steps）上加性分解唯一学到正回报（≈150），"
    "单体 critic 始终为负，QMIX 的 critic loss 起手即 5.4×10⁴、200k 步后二次发散。"
    "根因是 MAPPO-QMIX 的 TD 目标沿用 value-based 的 max_a Qᵢ 而 actor 是 on-policy，"
    "td_error 并非合法 advantage 而是系统性偏乐观；非单调 mixer 的持续梯度爆炸作为负结果写进论文，"
    "归结为结构性归纳偏置是 actor-critic 稳定训练的前提。"),
]

# ============================================================ 项目登记表
# 项目在简历里的出场顺序由变体的 projects 决定（默认 p1 → p2 → p3）。
# AI Infra 赛道先讲 ARCHER2，Agent / 后端赛道先讲 HPC_Agent——第一屏必须是对方要招的那件事。
# 每项登记：标题（p1 按变体取，其余是定值）、内联技术栈、链接、三档描述、bullet 表与项目符号列表号。
PROJECTS = {
"p1": dict(title=P1_TITLE, inline=P1_STACK_INLINE, stack=P1_STACK,
           desc=P1_DESC, desc_inline=P1_DESC_SHORT, desc_1p=P1_DESC_1P,
           bullets=P1, numid=NUM_A),
"p2": dict(title=P2_TITLE, inline=P2_STACK_INLINE, stack=P2_STACK,
           desc=P2_DESC, desc_inline=None, desc_1p=P2_DESC_1P,
           bullets=P2, numid=NUM_A),
# P3 的技术栈写在描述句尾，所以没有独立的 stack 行；default 对应「不写 p3 就取前两条」，
# P3[2] 是一页版专用的合并条，与 P3[0] 内容重叠，不能混进通用变体。
"p3": dict(title=P3_TITLE, inline=P3_STACK_INLINE, stack=None,
           desc=P3_DESC, desc_inline=P3_DESC_SHORT, desc_1p=P3_DESC_1P,
           bullets=P3, numid=NUM_B, default=[0, 1]),
}


# ============================================================ 变体配置
VARIANTS = {
"perf": dict(
    file=f"CV_perf_{DATE}.docx",
    tagline=None,   # 求职方向行：需要时填一句话，会加粗显示在联系方式下方
    skills=["parallel", "profiling", "dl", "eng", "data"],
    p1=["design", "weak", "strong", "map", "retract", "pipeline", "ops"],
    p2=["arch", "fc_eval_merged", "ops"],
),
"platform": dict(
    file=f"CV_aiplatform_{DATE}.docx",
    tagline=None,
    skills=["eng", "sched", "service", "parallel", "profiling", "data"],
    p1=["design", "retract", "pipeline", "ops", "results_merged", "map"],
    p2=["arch", "ops", "fc", "eval"],
),
"hpc": dict(
    file=f"CV_hpc_{DATE}.docx",
    tagline=None,
    skills=["parallel", "profiling", "numeric", "eng", "data"],
    p1=["design", "retract", "pipeline", "weak", "strong", "map", "ops", "limits"],
    p2=["arch", "fc_eval_merged", "ops"],
),
# 对标 ref/ai_infra 那份进面简历的排布。四处结构性差异：
#   1. 教育背景下加「关联课业」一行         2. 技能段改关键词式（SKILL_KW），行数减半
#   3. 技术栈内联进项目标题，每项目省一行   4. bullet 数字前置、压到两行内
# ✅ 投递用的一页版。每个项目只留最核心的 2–3 条，技能压到四行。
"ai_infra": dict(
    file=f"CV_ai_infra_{DATE}.docx",
    tagline=None,
    courses=True,
    skills_1p=["lang", "hpc", "ml", "eng"],
    stack_inline=True,
    onepage=True,
    p1=["o_layout", "o_map", "o_exposure", "o_audit_short"],
    p2=["o_eval", "o_def"],
    p3=[2],
),
# ---------------- 方向二：Agent 开发 / 后端开发 ----------------
# 与 AI Infra 赛道的唯一结构差异是 projects=["p2","p1","p3"]：HPC_Agent 提到第一个。
# 事实底稿完全共用，所以两个方向的口径不会漂——这正是把手工 agentCV 收进生成器的原因。
"agent": dict(
    file=f"CV_agent_{DATE}.docx",
    tagline=None,
    stack_inline=True,
    onepage=True,
    skills_kw=["lang", "dl", "service", "eng_lite", "parallel"],
    projects=["p2", "p1", "p3"],
    # 2026-09-16 改三段式：可观测性 / 自动化测试 / 词法检索各自成条（HR 建议），事实与 arch/fc/eval/ops 相同
    desc_agent=True,
    p2=["a_contract", "a_defense", "a_eval", "a_trace", "a_tests", "a_rag"],
    # ARCHER2 在这里不是主角：指标怎么来 → 结论 → 算力含义
    p1=["a_metric", "a_results", "a_value"],
    p3=[3],
),
# ③ 预览件：假设「审计后 408 run 导入 Agent + 跨仓库回归测试」已完成后的样子。
# **未实现、不投递**，输出到 preview/ 而非 国内投递/。做不做 ③ 由本人对照后决定。
"agent_v3": dict(
    file=f"CV_agent_v3预览_{DATE}.docx",
    out_dir=os.path.join(HERE, "preview"),
    tagline="【预览件：假设「审计后 408 个 run 已导入 Agent 的 SQLite」完成后的版本——未实现，不投递】",
    stack_inline=True,
    onepage=True,
    skills_kw=["lang", "dl", "service", "eng_lite", "parallel"],
    projects=["p2", "p1", "p3"],
    desc_agent=True,
    title_key="agent",      # 标题再长一点链接就折行；「408 个 run」已在上一项目的描述里
    p2=["a_contract", "a_pipeline_v3", "a_defense", "a_eval", "a_trace", "a_tests"],
    p1=["a_metric", "a_results", "a_value"],
    p3=[3],
),
"backend": dict(
    file=f"CV_backend_{DATE}.docx",
    tagline=None,
    stack_inline=True,
    onepage=True,
    skills_kw=["lang", "service", "eng_lite", "dl", "parallel"],
    projects=["p2", "p1", "p3"],
    # 后端岗先看分层与进程边界、再看可观测与接口，模型那层压成一条
    p2=["arch", "ops", "fc_eval_merged"],
    # 同 agent：背景与自建指标打头，性能结论收尾
    p1=["c_context", "results_merged"],
    p3=[2],
),

# 两页详细版：面试前自己回读，或对方明确要长版时用。一页版是它的子集，无独有表述。
"ai_infra_full": dict(
    file=f"CV_ai_infra_详细版_{DATE}.docx",
    tagline=None,
    courses=True,
    title_key="ai_infra",
    skills_kw=["lang", "parallel", "profiling", "dl", "gpu", "eng"],
    stack_inline=True,
    # 结论打头（对齐参考简历的数字前置），机理与推论紧随，方法与审计垫底
    p1=["c_layout", "c_map", "o_exposure", "c_saturate", "design", "c_retract", "c_pipeline"],
    p2=["arch", "fc", "eval", "c_serve"],
    p3=[0, 1],
),
}


# ============================================================ 组装
def build(key, cfg):
    P = []
    # 姓名本身也是指向个人主页的超链接（不加蓝色下划线，视觉上仍是普通标题）
    P.append(f'<w:p><w:pPr><w:ind w:left="4200" w:firstLine="420"/>{rpr(28, True)}</w:pPr>'
             f'{link(REL_SITE, NAME, 28, True)}</w:p>')
    # 联系方式：三处均为可点击外链
    P.append('<w:p><w:pPr>' + rpr(19) + '</w:pPr>'
             + link(REL_MAIL, EMAIL) + run(" | ", 19, False) + link(REL_MAIL_QQ, EMAIL_QQ)
             + run(" | ", 19, False) + run(PHONE, 19, False)
             + run(" | ", 19, False) + link(REL_GH, GITHUB)
             + run(" | ", 19, False) + link(REL_SITE, HOMEPAGE)
             + '</w:p>')
    if cfg["tagline"]:
        P.append(para([(cfg["tagline"], True)], sz=19))
    P.append(para(EDU_MSC, sz=19))
    P.append(para(EDU_BSC, sz=19, border=not cfg.get("courses")))
    if cfg.get("courses"):
        P.append(para([(COURSES[0], True), (COURSES[1], False)], sz=19, border=True))

    inline = cfg.get("stack_inline")

    def title(text, stack, pk):
        """项目标题。inline 变体（2026-09-16 起）：标题靠左、仓库链接右对齐在同一行，
        技术栈退成第二行。此前（09-03 手改版）链接挂在技术栈行末尾，技术栈稍长就把链接
        挤到第三行单独占一行。非 inline 变体仍是一行标题 + 行尾链接，技术栈另有「技术栈：」整行。"""
        rid, repo = REL_REPO[pk], f"lionleepower/{REPOS[pk]}"
        if inline:
            return [title_link(text, rid, repo, sz=20),
                    para([("｜" + stack + STACK_TAG.get(pk, ""), False)], sz=20)]
        return [para_link([(text, True)], rid, "  " + repo, sz=20)]

    onepage = cfg.get("onepage")
    skills, table = ((cfg["skills_1p"], SKILL_1P) if cfg.get("skills_1p")
                     else (cfg["skills_kw"], SKILL_KW) if cfg.get("skills_kw")
                     else (cfg["skills"], SKILL))
    P.append(f'<w:p><w:pPr>{rpr(24, True)}</w:pPr>{run("技术能力", 24, True)}</w:p>')
    for k in skills:
        h, b = table[k]
        P.append(para([(h, True), (b, False)], sz=19))

    # 项目段：出场顺序由 cfg["projects"] 决定（默认 p1 → p2 → p3）
    if inline:   # 标题里不再带「项目经历：」前缀，改用与「技术能力」同级的段头
        P.append(f'<w:p><w:pPr>{rpr(24, True)}</w:pPr>{run("项目经历", 24, True)}</w:p>')
    order = cfg.get("projects", ["p1", "p2", "p3"])
    for n, pk in enumerate(order):
        spec = PROJECTS[pk]
        head = spec["title"]
        if isinstance(head, dict):        # p1 的标题按变体取
            head = head[cfg.get("title_key", key)]
        desc = (spec["desc_1p"] if onepage else spec["desc_inline"] if inline else None) or spec["desc"]
        # 「该 benchmark」「上一项目」这两处前向引用只在 ARCHER2 排在前面时成立
        if pk == "p2" and ("p1" not in order or order.index("p1") > n):
            head, desc = P2_TITLE_STANDALONE, P2_DESC_STANDALONE
        if cfg.get("desc_agent"):        # 三段式变体：描述不带结论，数字留给 bullet 的效果句
            if pk == "p1":
                desc = P1_DESC_AGENT
            elif pk == "p2":
                desc = P2_DESC_AGENT_V3 if key == "agent_v3" else P2_DESC_AGENT
        P.extend(title(head, spec["inline"], pk))
        P.append(para([(desc[0], True), (desc[1], False)], sz=19))
        if not inline and spec["stack"]:
            P.append(para([(spec["stack"][0], True), (spec["stack"][1], False)], sz=19))
        for k in cfg.get(pk, spec.get("default", [])):
            P.append(bullet(*spec["bullets"][k], numid=spec["numid"]))
        if n < len(order) - 1:
            P.append(spacer(12))

    P.append(para([(PAPER[0], True), (PAPER[1], False)], sz=19))

    src = zipfile.ZipFile(SRC)
    doc = src.read('word/document.xml').decode('utf8')
    head = doc.split('<w:body>')[0] + '<w:body>'
    sectpr = re.search(r'<w:sectPr.*?</w:sectPr>', doc, re.S).group(0)
    new_doc = head + ''.join(P) + sectpr + '</w:body></w:document>'

    out_dir = cfg.get("out_dir", CN)
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, cfg["file"])
    if os.path.exists(out_path):
        os.remove(out_path)
    with zipfile.ZipFile(out_path, 'w', zipfile.ZIP_DEFLATED) as out:
        for item in src.infolist():
            data = src.read(item.filename)
            if item.filename == 'word/document.xml':
                data = new_doc.encode('utf8')
            elif item.filename == 'word/_rels/document.xml.rels':
                rels = data.decode('utf8')
                if REL_SITE not in rels:
                    rels = rels.replace('</Relationships>', EXTRA_RELS + '</Relationships>')
                data = rels.encode('utf8')
            out.writestr(item, data)
    src.close()
    print(f"{key:9s} -> {cfg['file']}  ({len(P)} paragraphs)")


if __name__ == "__main__":
    for key, cfg in VARIANTS.items():
        build(key, cfg)
