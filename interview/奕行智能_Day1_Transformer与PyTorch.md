# Day 1 · Transformer 推理原理 + PyTorch 起步

> 目标：闭卷写出 decoder layer 的算子表与 KV cache 公式，并对 Llama-3-8B 算出实数；PyTorch 能跑一个 toy 模型并看 profiler。
> 你的锚点：这一天所有「访存」「带宽」的讨论都和你论文里 SpMV / CG 是访存受限的推理是同一套逻辑。

---

## 1. 一个 decoder-only LLM 长什么样

```
tokens ──► Embedding (vocab × d)
   │
   ├─ × L 层 ─────────────────────────────────────────────────────┐
   │   x ── RMSNorm ── Q,K,V = x·W_q, x·W_k, x·W_v ── RoPE(Q,K)   │
   │                 ── Attention(Q,K,V) ── ·W_o ── + x (残差)     │
   │   x ── RMSNorm ── FFN: down( silu(gate(x)) ⊙ up(x) ) ── + x   │
   └──────────────────────────────────────────────────────────────┘
   │
final RMSNorm ──► lm_head (d × vocab) ──► logits ──► 采样下一个 token
```

**符号**：`d` = hidden size（d_model）；`h` = 头数；`d_h = d/h` = 每头维度；`h_kv` = KV 头数（GQA）；`d_ff` = FFN 中间维；`L` = 层数；`V` = 词表；`s` = 序列长度；`B` = batch。

### Llama-3-8B 的实数（背下来，面试算题用）

| 项 | 值 |
|---|---|
| L | 32 |
| d | 4096 |
| h / h_kv / d_h | 32 / 8 / 128（GQA，4 个 Q 头共享 1 个 KV 头） |
| d_ff | 14336（SwiGLU，三个矩阵 gate / up / down） |
| V | 128,256 |
| 参数量 | ≈ 8.03B；FP16 权重 ≈ 16 GB，INT8 ≈ 8 GB，INT4 ≈ 4–4.5 GB |

每层参数：attention `W_q` 4096×4096 + `W_k`,`W_v` 各 4096×1024 + `W_o` 4096×4096 ≈ 41.9M；FFN 3 × 4096×14336 ≈ 176M → 每层 ≈ 218M，× 32 ≈ 6.98B，加 embedding + lm_head 2 × 128256×4096 ≈ 1.05B → ≈ 8.03B ✓。
（Qwen2.5-7B 对照：L 28、d 3584、h 28、h_kv 4、d_ff 18944。）

---

## 2. 每个算子做什么、代价多少

### 2.1 Attention（单头）

`S = Q Kᵀ / √d_h`（s×s）→ causal mask（上三角置 −∞）→ `P = softmax(S)`（按行）→ `O = P V`。
多头 = 把 d 切成 h 份各做一次，再拼接乘 `W_o`。

- **为什么除以 √d_h**：点积方差随 d_h 线性增长，不缩放 softmax 会饱和、梯度消失。
- **Causal mask**：位置 i 只能看 ≤ i，这是 decode 能用 KV cache 的前提（历史的 K、V 不会因新 token 而变）。
- **MHA / GQA / MQA**：Q 头 h 个，KV 头分别为 h / h_kv（h_kv < h）/ 1。KV 头少 → KV cache 线性变小、decode 读 KV 的带宽变小；精度损失很小（Llama-3、Qwen2 都用 GQA）。

### 2.2 RoPE（旋转位置编码）

把 Q、K 的每对维度 (2i, 2i+1) 按位置 m 旋转角 `m·θ_i`，`θ_i = base^(−2i/d_h)`（base 10000 或更大）。点积 `q_m · k_n` 只依赖相对位置 m−n。**为什么外推差**：训练没见过的角度；YaRN / NTK 缩放 base 来延长。面试只需说到这里。

### 2.3 RMSNorm

`y = x / sqrt(mean(x²) + ε) · γ`。比 LayerNorm 少了减均值和 β；元素级、访存受限；通常与后面的 linear 融合。

### 2.4 FFN（SwiGLU）

`down( silu(x W_gate) ⊙ (x W_up) )`。三个 GEMM，参数量占每层约 80%。`silu(z) = z·σ(z)`。

### 2.5 lm_head + 采样

`logits = x W_vocab`（d×V 的 GEMM/GEMV，8B 模型这一个矩阵 0.5B 参数）；greedy / top-k / top-p / temperature 采样。

### 2.6 MoE（Mixture of Experts）

FFN 换成 E 个专家，router `softmax(x W_r)` 取 top-k（常 k=2）个专家，输出加权和。**激活参数**（每 token 真正算的）≪ 总参数（如 DeepSeek-V3 671B 总 / 37B 激活；Mixtral 8×7B 47B 总 / 13B 激活）。
代价：专家负载不均（热门专家排队、冷门空转 —— 和你 OpenMP 空转是同一类利用率损失）、专家并行时的 all-to-all 通信、容量因子 / token 丢弃 / padding。训练加负载均衡辅助损失。

---

## 3. Prefill 与 decode：为什么瓶颈完全不同

| | Prefill（处理 prompt） | Decode（逐 token 生成） |
|---|---|---|
| 一次处理 | s 个 token 一起 | 1 个 token（× batch B） |
| 主要算子 | GEMM：`[s×d]·[d×d]` | GEMV：`[1×d]·[d×d]`（batch 后 `[B×d]`） |
| FLOPs | ≈ 2 × 参数量 × s | ≈ 2 × 参数量（每 token） |
| 读权重 | 一次，摊到 s 个 token | **每 token 读一遍全部权重** |
| 算术强度 | 高 → **compute-bound** | 低 → **memory-bound** |
| 决定指标 | TTFT（首 token 延迟） | TPOT（每 token 时间）/ 吞吐 |

### 3.1 关键公式（会推导）

- **每 token FLOPs ≈ 2 × N_params**（每个权重一次乘一次加）+ attention 部分 `4 × L × s × d`（读 KV 做 QKᵀ 和 PV），短上下文时可忽略。
- **每 token 读取字节 ≈ 权重字节 + KV cache 字节**。
- **decode 算术强度**（batch B，权重每元素 b 字节）：`AI ≈ 2B / b` FLOP/byte。FP16 时 `AI ≈ B`；INT4 时 `AI ≈ 4B`。
- **Roofline**：`可达性能 = min(峰值算力, AI × 带宽)`；**拐点（ridge point）** `AI* = 峰值算力 / 带宽`。
  例：H100 SXM ≈ 990 TFLOPS(FP16 dense) / 3.35 TB/s → `AI* ≈ 295`。FP16 权重要 **B ≈ 300** 才到 compute-bound；INT4 要 B ≈ 74。这就是「batching 把 decode 从访存墙推向算力墙」的定量说法。
- **单流 decode 上限**：`tokens/s ≤ 带宽 / 每 token 字节`。8B FP16 在 H100：3.35e12 / 16e9 ≈ **209 tokens/s**（理论上限，实际 60–80%）；INT4 → ≈ 700+。你的 ARCHER2 节点 DDR4 8 通道 ≈ 200 GB/s 实测 ~150 → 8B FP16 ≈ 9 tokens/s，Q4 ≈ 33。**这是「量化对每 token 访存量的影响」的全部内容**，简历上那句话就是这道题。

### 3.2 KV cache

- 为什么：causal 下历史 token 的 K、V 不变，缓存起来避免每步重算 → 每步 attention 复杂度 O(s) 而不是 O(s²)。
- **大小公式**：`bytes = 2 (K 和 V) × L × h_kv × d_h × s × B × bytes_per_elem`。
- Llama-3-8B FP16：每 token `2 × 32 × 8 × 128 × 2 B = 131,072 B = 128 KB`；8K 上下文一条序列 = **1 GB**；batch 64 × 8K = 64 GB —— 这就是显存被 KV cache 吃掉的量级。若无 GQA（h_kv = 32）则 ×4 = 512 KB/token。
- Qwen2.5-7B：`2 × 28 × 4 × 128 × 2 = 56 KB/token`。
- decode 每步要**读一遍整段 KV**：长上下文时 KV 读取字节可超过权重字节 → 上下文越长 TPOT 越慢；KV 量化（INT8 / FP8）直接减半。
- 内存管理：预分配按最大长度 → 浪费；vLLM 的 PagedAttention 按块（block）分配，像 OS 分页。

---

## 4. 十个追问（自测，答不出就回上面）

1. decoder 一层里哪几个 GEMM、形状各是什么？（QKV 投影、O 投影、gate/up/down）
2. 为什么 decode 是 memory-bound？用公式说。（每 token 读全部权重，AI ≈ 2B/b）
3. batch 从 1 涨到 64，decode 每 token 延迟怎么变、吞吐怎么变？（延迟几乎不变直到拐点，吞吐近似线性涨）
4. GQA 为什么能省 KV 又不太掉精度？（K/V 的冗余高；Q 保持全头数）
5. KV cache 8B 模型 8K 上下文多大？（1 GB FP16）
6. 量化权重到 INT4 对 prefill 有多大帮助？（几乎没有，prefill 是算力受限；还多了反量化开销）
7. 为什么 lm_head 在小模型里占比很大？（V 大：128256×4096 = 0.5B）
8. RoPE 为什么是在 Q、K 上而不是 V？（位置信息只需影响相似度打分）
9. MoE 为什么「算力便宜、系统贵」？（激活参数少；但全部专家权重都要在内存里、负载不均、all-to-all）
10. 长上下文时 decode 变慢的原因是什么？（每步读 KV 线性增长 + attention 计算增长）

---

## 5. PyTorch 起步（今天 1 小时；后面每天 1 小时递进）

### 5.1 必会的十行

```python
import torch, torch.nn as nn, torch.nn.functional as F
x = torch.randn(2, 8, 64)              # [batch, seq, d]，默认 float32、CPU
x.shape, x.dtype, x.device             # 三个最常看的属性
x16 = x.to(torch.bfloat16)             # dtype 转换；.half() = float16
y = x @ x.transpose(-1, -2)            # 矩阵乘（批量广播）
lin = nn.Linear(64, 128, bias=False)   # 权重 [128, 64]；y = x @ W.T
out = lin(x)                           # [2, 8, 128]
with torch.no_grad(): ...              # 推理时关闭 autograd
sd = model.state_dict()                # {name: tensor}，权重导出/加载
p = sum(t.numel() for t in model.parameters())   # 参数量
```

### 5.2 手写单头 causal attention（今天要写出来）

```python
def attention(q, k, v):                # q,k,v: [B, s, d_h]
    d = q.shape[-1]
    s = q @ k.transpose(-1, -2) / d**0.5          # [B, s, s]
    mask = torch.triu(torch.ones(s.shape[-2:], dtype=torch.bool), 1)
    s = s.masked_fill(mask, float('-inf'))
    p = torch.softmax(s, dim=-1)
    return p @ v
```

### 5.3 看算子时间分布

```python
from torch.profiler import profile, ProfilerActivity
with profile(activities=[ProfilerActivity.CPU]) as prof:
    model(x)
print(prof.key_averages().table(sort_by="cpu_time_total", row_limit=15))
```
看到 `aten::linear` / `aten::mm` 占大头即验证「decode 阶段 linear 主导」。

### 5.4 Hook：逐层抓输出（Day 3 精度对拍要用）

```python
acts = {}
def hook(name):
    def fn(m, inp, out): acts[name] = out.detach()
    return fn
for name, m in model.named_modules():
    if isinstance(m, nn.Linear): m.register_forward_hook(hook(name))
```

### 5.5 今天的动手任务

1. 用 `nn.Module` 拼一个 2 层 toy decoder（RMSNorm + 你写的 attention + SwiGLU FFN），d=64。
2. 跑 profiler，把前 5 个算子记下来。
3. 手算它的参数量，和 `sum(numel)` 对上。
