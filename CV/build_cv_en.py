#!/usr/bin/env python3
"""
英文一页版简历生成器（海外投递）。

排版原语与母版 package 直接复用 build_cv.py，所以中英两边的字号、边距、项目符号
完全一致；内容是**重写而非翻译**——英文简历的惯例是动词开头、过去式、impact 打头。

与中文版的取舍差异（不是翻译问题）：
  · 加 work authorisation 一行 —— 不写会被默认需要 sponsorship 而直接过滤
  · 不放照片 / 年龄 / 性别 / 婚姻状况
  · First-Class Honours 写全称
  · 不写 referees（现在列人反而占地方，需要时对方会要）

用法：
    python3 build_cv_en.py
    soffice --headless --convert-to pdf 海外投递/CV_ai_infra_EN_*.docx --outdir 海外投递
"""
import os, re, zipfile

import build_cv as cn
from build_cv import rpr, run, para, spacer, link, bullet, NUM_A, NUM_B

HERE = cn.HERE
OUT_DIR = os.path.join(HERE, "海外投递")
DATE = "20260805"
OUT_FILE = f"CV_ai_infra_EN_{DATE}.docx"

# ============================================================ 投递前必须确认的两项
# ⚠️ 英国号码。没有就先留 +86，但要知道只有 +86 会显著降低回复率。
UK_PHONE = None
PHONE = UK_PHONE or cn.PHONE

# ⚠️ 措辞取决于你届时的签证状态，**拿到批复前不要写死到期日**。
# 现在这句只声明「毕业后有工作权利、入职时不需要 sponsorship」，是能站得住的最弱声明。
# 如果 Graduate Route 已批，改成 "Graduate Route visa held, valid until <日期>"。
WORK_AUTH = ("Work authorisation: eligible for the UK Graduate Route on completion of my MSc "
             "— no sponsorship needed to start.")

NAME_EN = "LEYAN LI"

# ============================================================ 内容
EDU = [
    [("University of Edinburgh", True),
     (" — MSc High Performance Computing with Data Science | Sep 2025 – Dec 2026", False)],
    [("  Coursework and dissertation completed Aug 2026 · ", False),
     ("available from 1 Sep 2026", True),
     (" · degree conferred Dec 2026", False)],
    [("University of Liverpool", True),
     (" — BSc (Hons) Computer Science, ", False), ("First-Class Honours", True),
     (" · 2+2 with Xi'an Jiaotong-Liverpool University | Sep 2023 – Jun 2025", False)],
]

COURSEWORK = ("Relevant coursework: ",
    "Message-Passing Programming (MPI), Threaded Programming (OpenMP), HPC Architectures, "
    "Performance Programming, GPU / Accelerator Programming, Parallel Design Patterns, "
    "High-Performance Data Analytics, Machine Learning")

SKILLS = [
("Languages: ", "C / C++, Python, Bash, SQL"),

("Parallel & performance: ",
    "MPI, OpenMP, hybrid MPI+OpenMP, PETSc, Slurm, numactl / hwloc, Linaro MAP; strong / weak scaling, parallel "
    "efficiency, saturation points; collective-communication cost (halo exchange, allreduce); roofline and "
    "memory-bandwidth analysis; NUMA and thread affinity"),

("Deep learning & LLM: ",
    "PyTorch, NumPy, pandas; LLM function calling and tool-schema design, offline evaluation sets and ablations. "
    "GPU and inference serving at coursework / self-study level: CUDA programming model, NCCL, data and tensor "
    "parallelism, batching vs. latency trade-offs, KV cache and quantisation"),

# 「reproducible experiment pipelines …」那句删掉了：P1 的 bullet 已经逐项证明过，
# 重复不增加可信度，只挤占一页纸的行数（同 ../README.md 的技能段规则）
("Engineering: ",
    "Linux, Git, pytest, GitHub Actions CI, FastAPI + Pydantic, SQLite / MySQL, working knowledge of Docker"),
]

PROJECTS = [
dict(
title="Parallel Layout Selection and Performance Attribution at 4,096 Cores on ARCHER2",
stack="C · PETSc · MPI · OpenMP · Slurm · Linaro MAP · Python / pandas · GitHub Actions",
url="  github.com/leyancode/hpc_benchmark_archer2",
desc=("On ARCHER2, the UK national supercomputer (dual-socket AMD EPYC 7742, 128 cores/node, Slingshot): with total "
    "core count fixed, how should work split between MPI ranks and OpenMP threads per rank? Workload was a 2D/3D "
    "stencil with CG+GAMG, 5M–165M unknowns, over four full-node layouts (128×1 / 64×2 / 32×4 / 16×8)."),
bullets=[
("Layout selection: ",
    "In 2D weak scaling, 64×2 beat flat MPI by 13.1% (794.8M equations/s at 165M unknowns on 32 nodes); "
    "fixed-20M strong scaling reached 29.83× speedup at 93.2% cumulative efficiency. "
    "In 3D the optimum moved to 32×4 (up to +33.2%) and 16×8 (3.81× faster than flat MPI) — "
    "the best degree of parallelism shifts with dimension, problem size and per-core work; there is no single "
    "“optimal thread count”, and the same diminishing-returns curve governs scaling a fixed batch onto more machines."),
("Root-cause attribution: ",
    "Linaro MAP explained the ranking as the crossing point of two curves — as threads per rank rose, "
    "MPI share of the solve window fell 46.7% → 6.2% while OpenMP wait time rose 48.3% → 76.5%, "
    "trading communication exposure against thread idling. Ruled out threaded BLAS as an explanation "
    "(LibSci ≤ 2.1% of solve-window core-time); instrumentation perturbs runtime, so the profile ranked layouts only "
    "and was never mixed with uninstrumented timings."),
("Trustworthiness gate: ",
    "An audit found 302 of 303 logs whose actual MPI process count disagreed with the filename, so I discarded that "
    "entire phase of performance curves; formal conclusions rest on 408 audited runs alone. Made "
    "“parse process and thread counts from log content, not filenames” a hard check at the analysis entry point; "
    "job scripts are parameterised, pytest pins headline figures, and CI exercises the submission path against a "
    "fake Slurm."),
]),

dict(
title="Agent-Based Performance Analysis System over the Benchmark Data",
stack="Python · SQLite · FastAPI · Pydantic · OpenAI SDK (function calling) · pytest",
url="  github.com/leyancode/hpc-benchmark-agent",
desc=("Structured the benchmark data above into SQLite and wrapped each analysis task as a deterministic tool: the LLM "
    "only decides which tool to call and with what arguments, while every number comes from deterministic code — "
    "turning agent correctness into something measurable."),
bullets=[
("Measurable routing: ",
    "Built a rule-based router as a verifiable baseline, output-isomorphic with the LLM function-calling router "
    "(intent + arguments), so both score against the same self-built 30-question, five-category evaluation set — "
    "83.3% for rules, 100% for the LLM. An ablation showed the same model scores 63.3% without the system prompt: "
    "accuracy is driven mainly by tool documentation and policy prompt, not by the model itself."),
("Defensive parsing and engineering: ",
    "Collapsed three failure modes — no tool call, hallucinated tool name, malformed JSON arguments — into an explicit "
    "unknown rather than guessing arguments, so the system never returns a silently wrong number. "
    "A trace_id-threaded JSON Lines event stream replays any execution; FastAPI's POST /ask rejects an invalid router "
    "as 422 and maps a missing key to 503. 229 automated tests run fully offline."),
]),

dict(
title="Value Factorisation in Multi-Agent Actor-Critic Methods (BSc dissertation)",
stack="Python · PyTorch · PyMARL · MAPPO · VDN · QMIX · CTDE · PPO · PettingZoo / MPE2",
url="  github.com/leyancode/marl-value-factorisation",
# 描述并进 bullet：一页版在这里省两行，且这个项目本来就只有一条结论要讲
desc=None,
bullets=[
("Counter-intuitive result and root cause: ",
    "Attached VDN additive factorisation and QMIX monotonic mixing to a MAPPO critic as a single-variable comparison "
    "(variants share runner, buffer, shared-RNN actor and all PPO hyperparameters; only the critic branch differs). "
    "The more expressive critic did not win — on sparse-reward Predator-Prey (300k steps) the simplest additive "
    "factorisation reached positive return (≈150), the monolithic critic stayed negative, and "
    "QMIX's critic loss started at 5.4×10⁴ and diverged again after 200k steps. The cause: MAPPO-QMIX inherits the "
    "value-based TD target max_a Qᵢ (greedy action) while the actor is on-policy, so the resulting td_error is not a "
    "valid advantage but a systematically optimistic quantity. The non-monotonic mixer's persistent gradient "
    "explosion is reported as a negative result."),
]),
]

PUBLICATION = ("Publication: ",
    "Li, Leyan. Convolutional Neural Networks Based Medical Image Analysis. "
    "EMITI 2024.")


# ============================================================ 组装
def heading(text):
    return f'<w:p><w:pPr>{rpr(24, True)}</w:pPr>{run(text, 24, True)}</w:p>'


def build():
    P = []
    P.append(f'<w:p><w:pPr><w:ind w:left="4200" w:firstLine="420"/>{rpr(28, True)}</w:pPr>'
             f'{link(cn.REL_SITE, NAME_EN, 28, True)}</w:p>')
    P.append('<w:p><w:pPr>' + rpr(19) + '</w:pPr>'
             + link(cn.REL_MAIL, cn.EMAIL) + run(" | ", 19, False) + run(PHONE, 19, False)
             + run(" | GitHub: ", 19, False) + link(cn.REL_GH, cn.GITHUB)
             + run(" | ", 19, False) + link(cn.REL_SITE, cn.HOMEPAGE)
             + '</w:p>')
    P.append(para([(WORK_AUTH, True)], sz=19))

    P.append(heading("EDUCATION"))
    for i, segs in enumerate(EDU):
        P.append(para(segs, sz=19, border=(i == len(EDU) - 1)))
    P.append(para([(COURSEWORK[0], True), (COURSEWORK[1], False)], sz=19))

    P.append(heading("TECHNICAL SKILLS"))
    for h, b in SKILLS:
        P.append(para([(h, True), (b, False)], sz=19))
    P.append(spacer(12))

    P.append(heading("PROJECTS"))
    for i, pj in enumerate(PROJECTS):
        P.append(para([(pj["title"], True), ("  | " + pj["stack"], False), (pj["url"], False)], sz=20))
        if pj["desc"]:
            P.append(para([(pj["desc"], False)], sz=19))
        for h, b in pj["bullets"]:
            P.append(bullet(h, b, numid=NUM_A if i < 2 else NUM_B))
        if i < len(PROJECTS) - 1:
            P.append(spacer(6))

    P.append(para([(PUBLICATION[0], True), (PUBLICATION[1], False)], sz=19))

    src = zipfile.ZipFile(cn.SRC)
    doc = src.read('word/document.xml').decode('utf8')
    head = doc.split('<w:body>')[0] + '<w:body>'
    sectpr = re.search(r'<w:sectPr.*?</w:sectPr>', doc, re.S).group(0)
    new_doc = head + ''.join(P) + sectpr + '</w:body></w:document>'

    os.makedirs(OUT_DIR, exist_ok=True)
    out_path = os.path.join(OUT_DIR, OUT_FILE)
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
                    rels = rels.replace('</Relationships>', cn.EXTRA_RELS + '</Relationships>')
                data = rels.encode('utf8')
            out.writestr(item, data)
    src.close()
    print(f"en        -> 海外投递/{OUT_FILE}  ({len(P)} paragraphs)")
    return out_path


# ============================================================ 中英事实一致性检查
# 中英是两份手写文本，最大的风险是改了一边忘了另一边。这里把头条数字钉死：
# 每一个都必须同时出现在中文一页版和英文版里，否则 build 直接失败。
HEADLINE = ["4,096", "794.8", "13.1", "29.83", "93.2", "33.2", "3.81",
            "46.7", "6.2", "48.3", "76.5", "2.1",
            "302", "303", "408", "83.3", "63.3", "229", "150", "5.4"]


def text_of(path):
    d = zipfile.ZipFile(path).read('word/document.xml').decode('utf8')
    return re.sub(r'<[^>]+>', '', d)


def check(en_path):
    cn_path = os.path.join(cn.CN, f"CV_ai_infra_{cn.DATE}.docx")
    if not os.path.exists(cn_path):
        print(f"  ! 找不到中文一页版 {cn_path}，跳过一致性检查（先跑 build_cv.py）")
        return
    cn_text, en_text = text_of(cn_path), text_of(en_path)
    missing = [(n, "中文版" if n not in cn_text else "英文版")
               for n in HEADLINE if n not in cn_text or n not in en_text]
    if missing:
        raise SystemExit("✗ 中英事实漂移，以下数字只在一边出现：\n" +
                         "\n".join(f"    {n}  缺在 {side}" for n, side in missing))
    print(f"  ✓ {len(HEADLINE)} 个头条数字中英两版一致")


if __name__ == "__main__":
    if UK_PHONE is None:
        print("  ! UK_PHONE 未设置，正在使用 +86 号码——投英国岗前请换成英国号码")
    path = build()
    check(path)
