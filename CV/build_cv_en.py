#!/usr/bin/env python3
"""
英文简历生成器（海外投递：英国 / 欧洲英语岗位）。

排版原语与母版 package 直接复用 build_cv.py，所以中英两边的字号、边距、项目符号
完全一致；内容是**重写而非翻译**——英文简历的惯例是动词开头、过去式、impact 打头。

四个变体，全部一页：

  agent      AI / Agent Engineer、LLM Application Engineer（HPC_Agent 第一个）
  backend    Backend / Software Engineer（HPC_Agent 第一个，bullet 换成分层与服务化打头）
  ai_infra   ML / AI Infrastructure、HPC Performance Engineer（ARCHER2 第一个）
  rse        Research Software Engineer（EPCC / STFC / 大学 RSE 组；ARCHER2 第一个，
             多一条「可发布性」bullet：脱敏日志、SHA-256 manifest、fake-Slurm CI）

与中文版的取舍差异（不是翻译问题）：
  · 页头一行 right-to-work —— 不写会被默认需要 sponsorship 而直接过滤
  · 页头一行 location + "open to relocation"
  · 两行 Profile —— 英国简历的惯例，也是唯一能写「我投的是什么岗」的地方
  · 不放照片 / 年龄 / 性别 / 婚姻状况
  · First-Class Honours 写全称
  · 不写 referees（需要时对方会要）

用法：
    python3 build_cv.py                       # 先生成中文版，一致性检查要用
    python3 build_cv_en.py
    soffice --headless --convert-to pdf 海外投递/CV_*_EN_*.docx --outdir 海外投递
"""
import os, re, zipfile

import build_cv as cn
from build_cv import rpr, run, para, para_link, spacer, link, bullet, NUM_A, NUM_B

HERE = cn.HERE
OUT_DIR = os.path.join(HERE, "海外投递")
DATE = "20260912"

# ============================================================ 投递前必须确认的几项
# 英国号码（2026-09-12 起有）。写成 +44 7xxx xxxxxx 的英国习惯分组。
UK_PHONE = "+44 7887 930137"
PHONE = UK_PHONE or cn.PHONE

# LinkedIn：英国简历几乎都放。None 则整段省略并在 build 时提醒。
LINKEDIN = None            # 例："linkedin.com/in/leyan-li"
LINKEDIN_URL = f"https://{LINKEDIN}" if LINKEDIN else None
REL_LINKEDIN = "rId96"     # build_cv 用到 rId95，这里往后接

LOCATION = "Edinburgh, UK · open to relocation (UK / EU)"

# ⚠️ 措辞取决于签证状态，改状态必须改这句。2026-09-12 的状态：Student visa 在手，
#    课程 2026-08 完成，Graduate Route **尚未申请**。
#    · Student visa 在课程完成后、签证到期前允许全职工作（学位课程）—— 这句话要向
#      爱丁堡 Student Immigration Service 确认课程完成的正式登记日期后再投。
#    · Graduate Route 批下来后改成：
#      "Right to work in the UK: Graduate Route visa held, valid until <date>; no sponsorship required."
WORK_AUTH = ("Right to work in the UK: Student visa (full-time work permitted post-course); applying for the "
             "2-year Graduate Route — no sponsorship required.")

NAME_EN = "LEYAN LI"

# ============================================================ 事实底稿（英文）
EDU = [
    [("University of Edinburgh", True),
     (" — MSc High Performance Computing with Data Science | Sep 2025 – Dec 2026 (expected). "
      "Taught courses and dissertation completed Aug 2026 — ", False),
     ("available immediately", True), ("; degree conferred Dec 2026", False)],
    # 与中文版同口径（2026-09-16）：日期写整个本科，2+2 解释两校
    [("University of Liverpool", True),
     (" / XJTLU — BSc Computer Science (2+2), ", False), ("First-Class Honours", True),
     (" | Sep 2021 – Jun 2025", False)],
]

# 逐项须能在成绩单上找到对应课；没修过的直接删（同中文版 COURSES 的规则）
COURSEWORK = ("Relevant coursework: ",
    "Message-Passing Programming (MPI), Threaded Programming (OpenMP), HPC Architectures, Performance "
    "Programming, GPU / Accelerator Programming, HPC Data Analytics, Machine Learning")

# Profile：两行，说清「投什么岗 + 凭什么」。每个变体一句，不写形容词。
PROFILE = {
"agent": ("MSc HPC & Data Science graduate targeting AI / agent engineering roles. Built and evaluated a tool-calling "
          "LLM agent over real supercomputer data — deterministic tools, rule baseline, 30-question eval set, prompt "
          "ablation, 229 offline tests — on top of 4,096-core performance work on ARCHER2."),
"backend": ("MSc HPC & Data Science graduate targeting backend / software engineering roles. Designed a layered Python "
            "service (SQLite → deterministic tools → routing → FastAPI) with trace-id observability, typed HTTP contracts "
            "and 229 offline tests; ran a 408-run audited benchmark pipeline on a national supercomputer."),
"ai_infra": ("MSc HPC & Data Science graduate targeting ML / AI infrastructure and performance engineering roles. Ran a "
             "408-run hybrid MPI+OpenMP study on ARCHER2 (32 nodes / 4,096 cores), attributed layout rankings with Linaro "
             "MAP and PETSc -log_view, and built an evaluable LLM tool-calling agent on the data."),
"rse": ("MSc HPC & Data Science graduate targeting Research Software Engineer roles. Designed and ran an audited PETSc "
        "scaling study on ARCHER2 (32 nodes / 4,096 cores, 408 runs), withdrew a flawed phase on evidence, and published "
        "the pipeline with sanitised logs, a SHA-256 manifest, pytest-pinned figures and fake-Slurm CI."),
}

# ---------------- 技能条目 ----------------
# 规则同中文版：技能段只写项目段证明不了的东西（语言、工具面、了解性知识）。
SK = {
"lang": ("Languages: ", "C / C++, Python, Bash, SQL"),

"parallel": ("Parallel & performance: ",
    "MPI, OpenMP, hybrid MPI+OpenMP, PETSc, Slurm, numactl / hwloc, Linaro MAP; strong / weak scaling, "
    "saturation; collective cost (halo, allreduce); roofline / memory bandwidth; NUMA, thread affinity"),

"parallel_short": ("Parallel & performance: ",
    "MPI, OpenMP, PETSc, Slurm, Linaro MAP; strong / weak scaling, NUMA and thread affinity"),

"dl": ("Deep learning & LLM: ",
    "PyTorch, NumPy, pandas; LLM function calling / tool-schema design, offline evaluation and ablations. GPU and "
    "inference serving at coursework / self-study level: CUDA model, NCCL, data / tensor parallelism, batching vs. "
    "latency, KV cache, quantisation"),

# agent 变体：LLM 那行讲工具面与概念，做过的事留给项目 bullet
"llm": ("LLM & agents: ",
    "OpenAI-compatible function calling / tool-schema design, system-prompt policy, offline evaluation sets and "
    "ablations, structured tracing; working knowledge of RAG, planning / memory / reflection patterns and "
    "LangGraph-style orchestration; PyTorch, NumPy, pandas"),

"service": ("Backend & services: ",
    "FastAPI + Pydantic, SQLite / MySQL (indexing, transactions, query tuning), REST / HTTP, JSON Lines structured "
    "logging, exception → HTTP status mapping; working knowledge of rate limiting, idempotency, Redis / TTL, Docker"),

"eng": ("Engineering: ",
    "Linux, Git, pytest, GitHub Actions CI, FastAPI + Pydantic, SQLite / MySQL, working knowledge of Docker"),

"eng_lite": ("Engineering: ",
    "Linux, Git, pytest, GitHub Actions CI; reproducible pipelines with regression tests that pin key figures"),

"rse_eng": ("Research software practice: ",
    "Linux, Git, pytest, GitHub Actions CI; reproducible pipelines from Slurm submission to audited logs and "
    "regression-tested figures; data sanitisation and provenance (SHA-256 manifests); Docker, Spack (working knowledge)"),

"numeric": ("Numerical methods: ",
    "PETSc KSP / PC (CG + GAMG, GMRES + block Jacobi / ICC); 2D / 3D stencils; iterations vs. per-iteration cost"),
}

# ---------------- 项目一：ARCHER2 ----------------
P1_TITLE = {
"ai_infra": "Parallel Layout Selection and Performance Attribution at 4,096 Cores on ARCHER2",
"rse":      "Audited PETSc Hybrid MPI+OpenMP Scaling Study on ARCHER2 (32 nodes / 4,096 cores, 408 runs)",
"agent":    "PETSc Layout Study at 4,096 Cores on ARCHER2 — the agent's data source and credibility baseline",
"backend":  "Auditable Benchmark Pipeline at 4,096 Cores on ARCHER2 (408 accepted runs)",
}
P1_STACK = "C · PETSc · MPI · OpenMP · Slurm · Linaro MAP · Python / pandas · CI"
P1_DESC = ("On ARCHER2, the UK national supercomputer (dual-socket AMD EPYC 7742, 128 cores/node, Slingshot): with total "
    "core count fixed, how should work split between MPI ranks and OpenMP threads per rank? Workload: 2D/3D "
    "stencil with CG+GAMG, 5M–165M unknowns, four full-node layouts from 128×1 (flat MPI) to 16×8.")
# agent / backend：ARCHER2 不是主角，描述只讲「问题值多少钱、做到多大」
P1_DESC_CONTEXT = ("A controlled experiment on ARCHER2 (dual-socket AMD EPYC 7742, 128 cores/node): with total cores fixed, "
    "how to split MPI ranks vs. OpenMP threads — values usually left to job-script defaults and rarely measured. "
    "2D/3D stencil + CG+GAMG, 5M–165M unknowns, four full-node layouts, up to 32 nodes.")

P1 = {
"layout": ("Layout selection: ",
    "In 2D weak scaling, 64×2 beat flat MPI by 13.1% (794.8M equations/s at 165M unknowns on 32 nodes); "
    "fixed-20M strong scaling reached 29.83× speedup at 93.2% cumulative efficiency. "
    "In 3D the optimum moved to 32×4 (up to +33.2%) and 16×8 (3.81× faster than flat MPI): "
    "the best degree of parallelism shifts with dimension, size and per-core work — there is no single "
    "“optimal thread count”."),

"map": ("Root-cause attribution: ",
    "Linaro MAP explained the ranking as the crossing of two curves — as threads per rank rose, the MPI share of the "
    "solve window fell 46.7% → 6.2% while OpenMP wait rose 48.3% → 76.5%: communication exposure traded against "
    "thread idling. Ruled out threaded BLAS (LibSci ≤ 2.1% of solve-window core-time); as instrumentation perturbs "
    "runtime, the profile only ranked layouts and was never mixed with uninstrumented timings."),

# exposure share：ai_infra / rse 用这版（不带「MAP 扰动」半句——map 已说过）
"exposure": ("Additive metric of my own: ",
    "Defined a “synchronisation exposure share” on PETSc -log_view: event nesting makes naive leaf-event sums reach "
    "116–372% of KSPSolve, but halo exchange and global reductions sit on disjoint call paths, so their sum is the one "
    "legitimate metric. Zero instrumentation overhead, covers all 264 weak-scaling runs; at 32 nodes it falls from "
    "48.2% for flat MPI to 26.4% for 16×8."),

"audit_short": ("Trustworthiness gate: ",
    "An audit found 302 of 303 logs whose actual MPI process count disagreed with the filename, so I discarded that "
    "entire phase of performance curves; formal conclusions rest on 408 audited runs alone. Made "
    "“parse process and thread counts from log content, not filenames” a hard check at the analysis entry point."),

"audit": ("Trustworthiness gate: ",
    "An audit found 302 of 303 logs whose actual MPI process count disagreed with the filename, so I discarded that "
    "entire phase of performance curves; formal conclusions rest on 408 audited runs alone. Made "
    "“parse process and thread counts from log content, not filenames” a hard check at the analysis entry point; "
    "job scripts are parameterised, pytest pins headline figures, and CI exercises the submission path against a "
    "fake Slurm."),

# rse 专用：可发布性与证据链
"publish": ("Trustworthiness gate and publishable evidence chain: ",
    "An audit found 302 of 303 launcher-era logs whose actual MPI process count disagreed with the filename; I "
    "discarded that phase and made “parse counts from log content, not filenames” a hard check at the analysis entry "
    "point. Every accepted log passes six content checks (architecture, actual ranks × threads, convergence, "
    "timed-stage event count, linked library, solver signature); failures stay “superseded”, never in a median. Five "
    "representative logs are published de-identified by script with a SHA-256 manifest; 16 analysis scripts are "
    "pytest-pinned and CI runs them plus the Slurm scripts against a fake Slurm."),

# agent / backend：背景 + 自建指标一条，结论一条
"context": ("Scope and a metric of my own: ",
    "Pushed to 32 nodes / 4,096 cores, where saturation becomes visible. Linaro MAP perturbs runtime, so it only ranks "
    "layouts by share; PETSc -log_view has zero overhead and covers all 264 weak-scaling runs, on which I defined an "
    "additive “synchronisation exposure share” — nested leaf events sum to 116–372% of KSPSolve, but halo exchange and "
    "global reductions sit on disjoint call paths, so their sum is legitimate. At 32 nodes it falls from 48.2% (flat "
    "MPI) to 26.4% (16×8), making “why is this layout faster” a per-point measurement."),

"results": ("Results (summary): ",
    "Weak scaling: best 2D layout 64×2 (794.8M equations/s at 165M / 32 nodes, +13.1% over flat MPI), best 3D 32×4 "
    "(up to +33.2%); fixed-20M strong scaling: 2D 29.83× at 93.2% cumulative efficiency, 3D 16×8 3.81× faster than "
    "flat MPI. The optimum shifts with dimension, size and per-core work; MAP locates the mechanism as the crossing of "
    "MPI exposure (46.7% → 6.2%) and OpenMP wait (48.3% → 76.5%)."),
}

# ---------------- 项目二：HPC_Agent ----------------
P2_TITLE = "Agent-Based Performance Analysis System over the Benchmark Data"
P2_TITLE_STANDALONE = "Evaluable Tool-Calling LLM Agent over Real Supercomputer Benchmark Data"
P2_STACK = "Python · SQLite · FastAPI · Pydantic · OpenAI SDK (function calling) · pytest"
P2_DESC = ("Structured the benchmark data above into SQLite and wrapped each analysis task as a deterministic tool: the LLM "
    "only decides which tool to call and with what arguments, while every number comes from deterministic code — "
    "turning agent correctness into something measurable.")
P2_DESC_STANDALONE = ("Structured real PETSc benchmark results from ARCHER2 into SQLite and wrapped each analysis task as a "
    "deterministic tool: the LLM only decides which tool to call and with what arguments; every number comes from "
    "deterministic code, so agent correctness becomes measurable.")

P2 = {
"routing": ("Measurable routing: ",
    "Built a rule-based router as a verifiable baseline, output-isomorphic with the LLM function-calling router "
    "(intent + arguments), so both score on one self-built 30-question, five-category set — 83.3% for rules, 100% "
    "for the LLM. Ablation: the same model scores 63.3% without the system prompt, so accuracy is driven by tool "
    "documentation and policy prompt, not the model."),

"defense_eng": ("Defensive parsing and engineering: ",
    "Collapsed three failure modes — no tool call, hallucinated tool name, malformed JSON arguments — into an explicit "
    "unknown rather than guessing, so the system never returns a silently wrong number. A trace_id-threaded JSON Lines "
    "event stream replays any execution; FastAPI POST /ask maps an invalid router to 422 and a missing key to 503. "
    "229 automated tests run fully offline."),

# ---- agent 变体四条 ----
"arch": ("Layered architecture with an isomorphic contract: ",
    "Six layers (ingestion / metrics / tools / retrieval / routing / observability) behind two peer process boundaries, "
    "CLI and FastAPI. Rule router and LLM tool call emit the same shape (intent + arguments), so one evaluation set "
    "scores both and switching is a one-line dispatch change. Contracts pinned by 229 automated tests that run fully "
    "offline with no API key."),

"fc": ("Function calling and defensive parsing: ",
    "Tool-schema descriptions state each tool's boundary; the size argument is deliberately optional — omitting it means "
    "“ask back”, calling no tool means “decline”. No tool call, hallucinated tool name and malformed JSON all collapse to "
    "an explicit unknown: the system never guesses an argument, so never returns a silently wrong number. API failures "
    "propagate rather than falling back to rules, keeping the evaluation clean."),

"eval": ("Evaluation and ablation: ",
    "Self-built 30-question set in five categories (normal / ask-back / decline / number trap / adversarial); the "
    "expected value is the tool call, not answer text, so the harness is router-agnostic. Rules 83.3%, LLM 100%; the "
    "same model without its system prompt drops to 63.3% — accuracy is driven by tool documentation and policy prompt, "
    "not the model. Limits stated (30 questions, one model, one run)."),

"ops": ("Observability, API and minimal RAG: ",
    "trace_id-threaded JSON Lines event stream replays any execution; redaction centralised in one function and "
    "enforced by a scanning test. FastAPI POST /ask: invalid router → 422 via Pydantic, missing key → 503 not 500. "
    "Minimal RAG with IDF-weighted lexical retrieval (standard library, deliberately no vector store); no hit → nothing "
    "injected, and with RAG off the messages are byte-identical to the evaluation, pinned by a test."),

# backend 变体：fc + eval 合成一条，给服务化让位置
"fc_eval": ("Function calling, defensive parsing and evaluation: ",
    "Tool-schema descriptions state each tool's boundary and the size argument is optional — omit it to “ask back”, call "
    "no tool to “decline”; no tool call, hallucinated tool name and malformed JSON all collapse to an explicit unknown. "
    "A self-built 30-question set scores both routers on the tool call, not the answer text: rules 83.3%, LLM 100%; the "
    "same model without its system prompt drops to 63.3%."),
}

# ---------------- 项目三：MARL ----------------
P3_TITLE = "Value Factorisation in Multi-Agent Actor-Critic Methods (BSc dissertation)"
P3_STACK = "Python · PyTorch · PyMARL · MAPPO / VDN / QMIX · PettingZoo"
P3 = {
"full": ("Counter-intuitive result and root cause: ",
    "Attached VDN additive factorisation and QMIX monotonic mixing to a MAPPO critic as a single-variable comparison "
    "(shared runner, buffer, actor and PPO hyperparameters; only the critic differs). The more expressive critic did "
    "not win — on sparse-reward Predator-Prey (300k steps) only the additive critic reached positive return (≈150); "
    "QMIX's critic loss opened at 5.4×10⁴ and diverged again after 200k steps. Cause: the inherited value-based target "
    "max_a Qᵢ against an on-policy actor makes td_error systematically optimistic, not a valid advantage. The "
    "non-monotonic mixer's gradient explosion is reported as a negative result."),

# agent / backend：压短，给第一个项目让行
"short": ("Counter-intuitive result and root cause: ",
    "Single-variable comparison of VDN additive and QMIX monotonic critics inside MAPPO (shared runner, buffer, actor, "
    "PPO hyperparameters). The more expressive critic did not win: on sparse-reward Predator-Prey (300k steps) only the "
    "additive critic reached positive return (≈150); QMIX's critic loss opened at 5.4×10⁴ and diverged again. Root cause: "
    "the inherited value-based target max_a Qᵢ against an on-policy actor makes td_error systematically optimistic."),
}

PROJECTS = {
"p1": dict(title=P1_TITLE, stack=P1_STACK, bullets=P1, numid=NUM_A),
"p2": dict(title=P2_TITLE, stack=P2_STACK, bullets=P2, numid=NUM_A),
"p3": dict(title=P3_TITLE, stack=P3_STACK, bullets=P3, numid=NUM_B),
}

PUBLICATION = ("Publication: ",
    "Li, Leyan. Convolutional Neural Networks Based Medical Image Analysis. EMITI 2024.")


# ============================================================ 变体配置
# cn: 中英事实一致性检查的中文对照文件（build_cv.py 的输出名）
VARIANTS = {
"agent": dict(
    file=f"CV_agent_EN_{DATE}.docx", cn=f"CV_agent_{cn.DATE}.docx",
    skills=["lang", "llm", "service", "eng_lite", "parallel_short"],
    projects=["p2", "p1", "p3"],
    p2=["arch", "fc", "eval", "ops"],
    p1=["context", "results"], p1_desc="context",
    p3=["short"],
),
"backend": dict(
    file=f"CV_backend_EN_{DATE}.docx", cn=f"CV_backend_{cn.DATE}.docx",
    skills=["lang", "service", "eng_lite", "llm", "parallel_short"],
    projects=["p2", "p1", "p3"],
    p2=["arch", "ops", "fc_eval"],
    p1=["context", "results"], p1_desc="context",
    p3=["short"],
),
"ai_infra": dict(
    file=f"CV_ai_infra_EN_{DATE}.docx", cn=f"CV_ai_infra_{cn.DATE}.docx",
    coursework=True,
    skills=["lang", "parallel", "dl", "eng"],
    projects=["p1", "p2", "p3"],
    p1=["layout", "map", "exposure", "audit_short"],
    p2=["routing", "defense_eng"],
    p3=["full"],
),
"rse": dict(
    file=f"CV_rse_EN_{DATE}.docx", cn=f"CV_ai_infra_{cn.DATE}.docx",
    coursework=True,
    skills=["lang", "parallel", "numeric", "rse_eng"],
    projects=["p1", "p2", "p3"],
    p1=["layout", "map", "exposure", "publish"],
    p2=["routing", "defense_eng"],
    p3=["short"],
),
}


# ============================================================ 组装
def heading(text):
    return f'<w:p><w:pPr>{rpr(24, True)}</w:pPr>{run(text, 24, True)}</w:p>'


EXTRA_RELS = cn.EXTRA_RELS
if LINKEDIN_URL:
    EXTRA_RELS += (f'<Relationship Id="{REL_LINKEDIN}" Type="{cn.HYPERLINK}" '
                   f'Target="{LINKEDIN_URL}" TargetMode="External"/>')


def build(key, cfg):
    P = []
    P.append(f'<w:p><w:pPr><w:ind w:left="4200" w:firstLine="420"/>{rpr(28, True)}</w:pPr>'
             f'{link(cn.REL_SITE, NAME_EN, 28, True)}</w:p>')
    contact = ('<w:p><w:pPr>' + rpr(19) + '</w:pPr>'
               + link(cn.REL_MAIL, cn.EMAIL) + run(" | ", 19, False) + run(PHONE, 19, False)
               + run(" | GitHub: ", 19, False) + link(cn.REL_GH, cn.GITHUB)
               + run(" | ", 19, False) + link(cn.REL_SITE, cn.HOMEPAGE))
    if LINKEDIN:
        contact += run(" | ", 19, False) + link(REL_LINKEDIN, LINKEDIN)
    P.append(contact + '</w:p>')
    P.append(para([(LOCATION + " · " + WORK_AUTH, True)], sz=19))

    P.append(heading("PROFILE"))
    P.append(para([(PROFILE[key], False)], sz=19))

    P.append(heading("EDUCATION"))
    for i, segs in enumerate(EDU):
        P.append(para(segs, sz=19, border=(i == len(EDU) - 1 and not cfg.get("coursework"))))
    if cfg.get("coursework"):
        P.append(para([(COURSEWORK[0], True), (COURSEWORK[1], False)], sz=19, border=True))

    P.append(heading("TECHNICAL SKILLS"))
    for k in cfg["skills"]:
        h, b = SK[k]
        P.append(para([(h, True), (b, False)], sz=19))
    P.append(spacer(12))

    P.append(heading("PROJECTS"))
    order = cfg["projects"]
    for n, pk in enumerate(order):
        spec = PROJECTS[pk]
        title = spec["title"]
        if isinstance(title, dict):
            title = title[key]
        desc = None
        if pk == "p1":
            desc = P1_DESC_CONTEXT if cfg.get("p1_desc") == "context" else P1_DESC
        elif pk == "p2":
            # 「the benchmark data above」只在 ARCHER2 排在前面时成立
            standalone = "p1" not in order or order.index("p1") > n
            title = P2_TITLE_STANDALONE if standalone else P2_TITLE
            desc = P2_DESC_STANDALONE if standalone else P2_DESC
        P.append(para([(title, True)], sz=20))
        P.append(para_link([("| " + spec["stack"] + "  ", False)],
                           cn.REL_REPO[pk], f"lionleepower/{cn.REPOS[pk]}", sz=20))
        if desc:
            P.append(para([(desc, False)], sz=19))
        for k in cfg[pk]:
            P.append(bullet(*spec["bullets"][k], numid=spec["numid"]))
        if n < len(order) - 1:
            P.append(spacer(6))

    P.append(para([(PUBLICATION[0], True), (PUBLICATION[1], False)], sz=19))

    src = zipfile.ZipFile(cn.SRC)
    doc = src.read('word/document.xml').decode('utf8')
    head = doc.split('<w:body>')[0] + '<w:body>'
    sectpr = re.search(r'<w:sectPr.*?</w:sectPr>', doc, re.S).group(0)
    new_doc = head + ''.join(P) + sectpr + '</w:body></w:document>'

    os.makedirs(OUT_DIR, exist_ok=True)
    out_path = os.path.join(OUT_DIR, cfg["file"])
    if os.path.exists(out_path):
        os.remove(out_path)
    with zipfile.ZipFile(out_path, 'w', zipfile.ZIP_DEFLATED) as out:
        for item in src.infolist():
            data = src.read(item.filename)
            if item.filename == 'word/document.xml':
                data = new_doc.encode('utf8')
            elif item.filename == 'word/_rels/document.xml.rels':
                rels = data.decode('utf8')
                if cn.REL_SITE not in rels:
                    rels = rels.replace('</Relationships>', EXTRA_RELS + '</Relationships>')
                data = rels.encode('utf8')
            out.writestr(item, data)
    src.close()
    print(f"{key:9s} -> 海外投递/{cfg['file']}  ({len(P)} paragraphs)")
    return out_path


# ============================================================ 中英事实一致性检查
# 中英是两份手写文本，最大的风险是改了一边忘了另一边。每个英文变体都有一个中文对照文件
# （VARIANTS[*]["cn"]）：下面这张头条数字表里，凡在中文对照里出现的数字，英文版必须也有，
# 反之亦然——两边的「头条数字集合」必须相等，否则 build 直接失败。
HEADLINE = ["4,096", "794.8", "13.1", "29.83", "93.2", "33.2", "3.81",
            "46.7", "6.2", "48.3", "76.5", "2.1",
            "302", "303", "408", "264", "116", "372", "48.2", "26.4",
            "83.3", "63.3", "229", "150", "5.4"]


def text_of(path):
    d = zipfile.ZipFile(path).read('word/document.xml').decode('utf8')
    return re.sub(r'<[^>]+>', '', d)


def check(key, en_path, cn_file):
    cn_path = os.path.join(cn.CN, cn_file)
    if not os.path.exists(cn_path):
        print(f"  ! 找不到中文对照 {cn_path}，跳过一致性检查（先跑 build_cv.py）")
        return
    cn_text, en_text = text_of(cn_path), text_of(en_path)
    only_cn = [n for n in HEADLINE if n in cn_text and n not in en_text]
    only_en = [n for n in HEADLINE if n in en_text and n not in cn_text]
    if only_cn or only_en:
        raise SystemExit(f"✗ {key}: 中英事实漂移（对照 {cn_file}）\n"
                         + "".join(f"    {n}  只在中文版\n" for n in only_cn)
                         + "".join(f"    {n}  只在英文版\n" for n in only_en))
    both = sum(1 for n in HEADLINE if n in en_text)
    print(f"  ✓ {key}: {both} 个头条数字与 {cn_file} 一致")


if __name__ == "__main__":
    if UK_PHONE is None:
        print("  ! UK_PHONE 未设置，正在使用 +86 号码——投英国岗前请换成英国号码")
    if LINKEDIN is None:
        print("  ! LINKEDIN 未设置，页头没有 LinkedIn——英国简历几乎都放，建议补上")
    for key, cfg in VARIANTS.items():
        path = build(key, cfg)
        check(key, path, cfg["cn"])
