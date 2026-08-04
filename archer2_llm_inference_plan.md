# ARCHER2 上的 LLM 推理 benchmark —— 实验计划

> 目的：给 AI infra 赛道补上「推理性能」这块，且不虚构 GPU 经历。
> 方法论直接复用 `hpc_benchmark_archer2`：参数化提交 → 基于内容的审计 → 中位数 + 观测区间 → 排除干扰解释。

---

## 0. 必须先说清楚的一件事

**ARCHER2 主系统没有 GPU。** 它是 5,860 个 CPU 节点的 HPE Cray EX，双路 AMD EPYC 7742 Rome。
所以这个项目产出的是 **CPU 推理性能工程**，不是 GPU 经历。

这不是缺陷，是定位问题。它能给你的东西是 GPU 项目给不了的：

- **128 核 / 8 个 NUMD region / 256 GB DDR4 的节点** —— decode 阶段是纯访存受限，这是把 roofline 做实的最好平台
- **一个和 PETSc 项目同构的研究问题**：总核数固定时，怎么在「线程数」和「实例数」之间切分？这与 `ranks × threads` 是同一类问题，你已经有一整套方法论
- **Slingshot 多节点** —— 可以做「分布式推理在小模型上是负收益」这种有说服力的负结果

面试时的说法是：*「我没有 GPU 集群，所以我在能拿到的平台上，把推理性能里那个平台无关的部分做透了：访存墙、batch 的拐点、NUMA 亲和、并发实例与单实例的取舍、以及怎么让一份 benchmark 可审计。」* 这比一个跑通了 vLLM demo 的人有价值。

**开工前先查一件事**：ARCHER2 有一个独立的 GPU development platform（AMD Instinct，节点数很少）。
登录后 `sinfo` 看有没有 GPU 分区、或直接问 service desk 你的 account 有没有权限。
如果有 —— 哪怕只有几个节点 —— 就把第 5 阶段的 ROCm 对比做上，整个项目的分量会完全不同。

---

## 1. 环境与前置（半天）

| 项 | 说明 |
|---|---|
| 引擎 | **llama.cpp**（静态编译、CPU 后端成熟、GGUF 量化齐全、`llama-bench` 自带结构化输出）。**不要在 CPU 上跑 vLLM**，它的 CPU 后端不是一等公民，你会把时间花在环境上而不是实验上 |
| 编译 | `module load PrgEnv-gnu`；`cmake -DGGML_NATIVE=ON -DGGML_OPENMP=ON`。EPYC Rome **只有 AVX2，没有 AVX-512、没有 AMX** —— 这一点必须写进报告，它决定了 prefill 的算力上限 |
| 模型 | 在**登录节点**下载 GGUF（计算节点无外网）。放 `/work`，**不要放 `/home`** —— 计算节点看不见 `/home` |
| 内存 | 节点 256 GB，8B-F16（~16 GB）、70B-Q4（~40 GB）都放得下。**70B Q4 单节点跑起来**本身就是个好标题 |

准备三个模型档位，覆盖不同的算术强度：

- `Qwen3-1.7B` Q4_K_M —— 小模型，看开销占比
- `Qwen3-8B`（或 Llama-3.1-8B）**Q4_K_M / Q8_0 / F16** —— 主力，量化 = 直接改变每 token 的访存量
- `Qwen3-70B` 或 Llama-3.3-70B Q4_K_M —— 压满内存带宽的那个点

---

## 2. 阶段一：先测机器，再测模型（1 天）

**在跑任何推理之前，先把这个节点的访存上限钉死。** 没有这一步，后面所有 tokens/s 都只是数字。

- 每 NUMA region 跑 STREAM triad，再跑满节点 → 得到 **单 region / 单 socket / 整节点的实测带宽**
- 用 `lscpu` / `numactl -H` / `hwloc-ls` 核对 4 核一个 CCX、16 核一个 NUMA region、64 核一个 socket（和你 PETSc 项目里做过的完全一样）

**产出**：decode 阶段的理论上限
`tokens/s_max = 实测带宽 / 每 token 需要读过的权重字节数`
（decode 每生成 1 token 基本要把整个模型权重过一遍，所以这个上限非常紧）

后面每张 throughput 图都在旁边标这条线。**「我们达到了带宽上限的 71%」比「我们跑到了 23 tokens/s」强一个量级。**

---

## 3. 阶段二：布局扫描（核心，2–3 天）

这是和 PETSc 项目同构的那个实验，也是整个项目的主结论。

**固定 128 核不变**，改变怎么切：

| 布局 | 含义 |
|---|---|
| `1 × 128t` | 单实例吃满节点 —— 跨 8 个 NUMA region，远端访存 |
| `2 × 64t` | 每 socket 一个实例 |
| `4 × 32t` | |
| **`8 × 16t`** | **每 NUMA region 一个实例，全部本地访存** |
| `16 × 8t` | 超过 NUMA 粒度，实例太小 |

每个实例用 `numactl --cpunodebind=N --membind=N` 绑死。

两类指标分开报，**绝不合并**：

- **单请求延迟**：TTFT、inter-token latency 的 p50 / p95 —— `1×128t` 通常最好
- **聚合吞吐**：所有实例 tokens/s 之和 —— **`8×16t` 通常大幅领先**

**预期结论（也是卖点）**：延迟最优和吞吐最优是两个不同的布局，中间的取舍由 SLA 决定。
这正是真实推理服务每天在做的决策，而你有实测曲线。

同时扫 prefill 和 decode —— 它们的最优布局大概率不同（prefill 是 GEMM 算力受限，decode 是 GEMV 带宽受限），**这个反差本身就是一个结论**。

---

## 4. 阶段三：batch 拐点与量化（1–2 天）

- **batch size 1 → 2 → 4 → 8 → 16 → 32 → 64**，画 tokens/s 与 per-request latency 两条曲线
  找那个**膝点**：batch 增大时权重只读一次却服务多个请求，decode 从带宽受限逐渐转为算力受限
- **量化档位** Q4_K_M / Q8_0 / F16：每 token 访存量差 4 倍，如果吞吐不是差 4 倍，差额就是开销 —— 直接验证「decode 到底是不是纯带宽受限」
- **上下文长度** 512 / 2k / 8k / 32k：看 KV cache 增长怎么侵蚀带宽

---

## 5. 阶段四：多节点（1 天，很可能是负结果）

用 llama.cpp 的 RPC backend 把模型切到 2 / 4 个节点。

**预期是变慢**：Slingshot 每节点 2×100 Gb/s ≈ 25 GB/s，而本地 DDR4 是它的十几倍。
把张量切开就是把带宽换成网络。

**这个负结果要认真写**：它回答的是「什么时候值得跨节点」—— 答案是模型放不下单节点内存时，而不是想要更快时。
这和你 PETSc 项目里 `16×8` 只在饱和后才赢是同一种叙事：**收益取决于每个计算单元还剩多少工作量**。

---

## 6. 阶段五（可选，若拿得到 GPU 分区）

同一套 harness、同一批模型、同一个量化档位，在 AMD Instinct 上用 ROCm 版 llama.cpp（或 vLLM-ROCm）跑一遍。
产出一张 **CPU vs GPU 的每 token 成本 / 带宽利用率对照表**。
有这一张表，简历上「了解 GPU 推理」就变成「测过」。

---

## 7. 审计规则（照抄 PETSc 项目，这是你的招牌）

一次运行只有全部通过才进聚合：

1. 从运行输出解析 **实际线程数与 CPU 亲和**，不信提交脚本的参数
2. **模型文件 SHA-256** 与登记一致（防止跑串量化档位）
3. **生成 token 数完全一致**（固定 seed、固定 prompt、`--n-predict` 精确值）——
   长度不同的两次运行不能比 tokens/s
4. 排除首次运行（**页缓存冷启动**会污染第一次；等价于你 PETSc 里的 warm-up solve）
5. 每配置 **3–5 次重复**，取中位数，误差线为观测 min–max

未通过的**保留并标 superseded**，写进 audit summary CSV。

---

## 8. sbatch 骨架

```bash
#!/bin/bash
#SBATCH --job-name=llm_layout
#SBATCH --nodes=1
#SBATCH --exclusive
#SBATCH --time=01:00:00
#SBATCH --partition=standard
#SBATCH --qos=standard
#SBATCH --account=${ARCHER2_ACCOUNT}

module load PrgEnv-gnu

MODEL=/work/${PROJ}/${USER}/models/qwen3-8b-q4_k_m.gguf
OUT=/work/${PROJ}/${USER}/logs/llm

# 布局：实例数 × 每实例线程数 = 128
for LAYOUT in "1 128" "2 64" "4 32" "8 16" "16 8"; do
  set -- $LAYOUT; NINST=$1; NTHREAD=$2
  for REP in 1 2 3; do
    for (( i=0; i<NINST; i++ )); do
      NUMA=$(( i * 8 / NINST ))          # 8 个 NUMA region
      numactl --cpunodebind=$NUMA --membind=$NUMA \
        ./llama-bench -m "$MODEL" -t "$NTHREAD" -p 512 -n 128 -r 3 -o json \
        > "$OUT/inst${i}_n${NINST}_t${NTHREAD}_rep${REP}.json" 2>&1 &
    done
    wait
  done
done
```

**先用 1 个节点、1 小时把整条链路跑通再放量。** 你在 PETSc 项目上被 launcher 咬过一次，
这次第一件事就是写那个「从输出里读实际线程数」的校验脚本，而不是最后补。

---

## 9. 时间与预算

| 阶段 | 时间 | 节点小时（粗估） |
|---|---|---|
| 环境 + 编译 + 模型下载 | 0.5 天 | ~2 |
| 阶段一 带宽基线 | 1 天 | ~5 |
| 阶段二 布局扫描 | 2–3 天 | ~40 |
| 阶段三 batch / 量化 / 上下文 | 1–2 天 | ~30 |
| 阶段四 多节点 | 1 天 | ~20 |
| 分析 + README + 图表 | 2 天 | 0 |

**约 100 节点小时、1.5–2 周**（推理 run 都很短，主要成本是排队）。

---

## 10. 简历上会长成什么样

> **ARCHER2 上的 CPU LLM 推理性能研究**
> 在 128 核 / 8 NUMA region 的 EPYC 节点上，把总核数固定、扫描「实例数 × 每实例线程数」布局：
> 延迟最优与吞吐最优落在两个不同布局上（`1×128t` vs `8×16t`，聚合吞吐相差 N×），
> 取舍由 SLA 而非硬件决定。以实测 STREAM 带宽为上限，量化 decode 阶段达到访存墙的 X%，
> 并用量化档位（Q4/Q8/F16）三点验证 decode 确为带宽受限。多节点张量切分在 8B 模型上是负收益 ——
> 跨节点只在模型放不下单节点内存时才成立。全部结论基于 N 个通过内容审计的 run
> （线程亲和、模型 SHA-256、生成 token 数一致性、冷启动排除、3 次重复取中位数）。

一条 GPU 都没提，但每一句都是 AI infra 面试里会被追问的东西。
