# Day 3 · 数据类型与量化 · 精度问题定位

> 目标：说清 FP16 / BF16 / FP8 / INT8 / INT4 的取舍；手写对称量化；背下 PTQ 流程与「精度掉了先查什么」。
> 你的锚点：论文里「结论绑定 solver / build / placement」= 量化结论绑定校准集 / 粒度 / 格式；HPC_Agent 的「显式 unknown 不静默算错」= 精度对拍时对 NaN / 溢出零容忍。

---

## 1. 浮点格式（符号 / 指数 / 尾数）

| 格式 | 位数 | 指数 | 尾数 | 最大值 | 相对精度 | 用途 |
|---|---|---|---|---|---|---|
| FP32 | 32 | 8 | 23 | 3.4e38 | 6e-8 | 主权重、累加、norm |
| TF32 | 19（存 32） | 8 | 10 | 同 FP32 | 5e-4 | NVIDIA tensor core 训练 |
| **FP16** | 16 | 5 | 10 | **65,504** | 5e-4 | 推理主流；**易溢出** |
| **BF16** | 16 | 8 | 7 | 3.4e38 | 4e-3 | 训练主流；范围同 FP32、精度低 |
| FP8 E4M3 | 8 | 4 | 3 | 448 | 6e-2 | 权重 / 激活（前向） |
| FP8 E5M2 | 8 | 5 | 2 | 57,344 | 1.2e-1 | 梯度（要范围） |
| INT8 | 8 | – | – | 127 | 需 scale | 权重 / 激活量化 |
| INT4 | 4 | – | – | 7 | 需 scale + group | weight-only |

- **FP16 vs BF16 怎么选**：BF16 范围大、不怕溢出（softmax 前的 logits、梯度、loss 累积），精度低但神经网络对尾数不敏感；FP16 精度高但 max 65,504，attention 分数 / 残差累积容易 inf → NaN。训练选 BF16；推理看芯片支持，很多 NPU 只有 FP16 阵列 → 要注意溢出保护（缩放、在 FP32 做 softmax/norm）。
- **累加精度**：INT8×INT8 → INT32 累加；FP16×FP16 → FP32 累加；FP8 → FP16/FP32 累加。累加位宽不够 = 长 K 维 GEMM 误差随 K 增长——追问「K 很大时精度变差」的标准答案。
- **舍入**：round-to-nearest-even 是默认；量化时 round 与 truncate 差别很大；随机舍入用于训练。

---

## 2. 量化基础

### 2.1 映射公式

- **对称**（常用于权重）：`s = max|x| / q_max`（INT8 q_max=127），`q = clamp(round(x/s), −127, 127)`，`x̂ = q·s`。
- **非对称**（常用于激活，分布不对称如 ReLU 后）：`s = (x_max − x_min)/255`，`z = round(−x_min/s)`，`q = clamp(round(x/s) + z, 0, 255)`，`x̂ = (q − z)·s`。
- 量化误差 ≈ 均匀噪声，方差 `s²/12`；**s 由最大值决定 → 离群值（outlier）会把 s 撑大、让大多数小值全被舍成 0** —— 这是 LLM 量化的核心难点。

### 2.2 粒度

| 粒度 | 一个 scale 覆盖 | 精度 | 代价 |
|---|---|---|---|
| per-tensor | 整个矩阵 | 最差 | 最省，硬件最简单 |
| per-channel（per-row） | 输出通道一行 | 好 | scale 向量，几乎免费 |
| per-group（g=128 / 64） | 一行里每 128 个元素 | 更好（INT4 必需） | 反量化时要按组乘，算子里多一步 |
| per-token（激活） | 每个 token 一行 | 动态、好 | 运行时算 max，需硬件支持动态 scale |

### 2.3 静态 vs 动态、PTQ vs QAT

- **静态量化**：激活 scale 用校准集提前算好（推理无额外开销，硬件友好）；**动态**：运行时按 token 算（精度好、有开销）。
- **PTQ**（训练后）：拿几百条校准样本 → 统计每层激活范围（max / 百分位 / MSE 最优 / KL） → 量化 → 评估。几小时内完成，LLM 主流。
- **QAT**：训练时插入伪量化（fake quant，前向量化-反量化、反向 STE 直通）→ 精度最好，但要训练成本。
- 校准范围选择：max（保范围、被离群值害）/ 百分位 99.99（截掉尾巴）/ MSE 最小化 / KL 散度最小化（TensorRT 的经典做法）。

---

## 3. LLM 量化的三类主流方案（各一句话原理 + 解决什么）

| 方案 | 量化对象 | 原理 | 解决什么 | 对性能的影响 |
|---|---|---|---|---|
| **Weight-only INT4/INT8**（RTN、**GPTQ**、**AWQ**） | 只有权重；激活保持 FP16 | GPTQ：逐列量化并用 Hessian 信息把误差补偿到未量化列（OBS 思想）；AWQ：按激活幅度找「重要权重通道」，用等价缩放保护它们再量化 | **decode 带宽**：每 token 读的权重字节 ÷ 4 | decode 提速接近字节比例；prefill 无收益甚至因反量化变慢 |
| **W8A8**（**SmoothQuant**、LLM.int8()） | 权重与激活都 INT8 | SmoothQuant：`Y = (X·diag(s)^{-1})·(diag(s)·W)`，把激活的离群通道难度按 α（常 0.5）迁移到权重；LLM.int8()：离群通道单独用 FP16 | 利用 INT8 阵列 **2× 算力**，prefill 与 decode 都受益 | 需要芯片有 INT8 GEMM；激活离群值是主要精度风险 |
| **FP8**（E4M3 权重/激活） | 权重 + 激活 | 浮点格式天然处理动态范围，只需 per-tensor scale | Hopper / 新 NPU 的 2× 算力，精度接近 BF16 | 硬件必须原生支持 |
| **KV cache 量化**（INT8 / FP8，per-token / per-head） | KV cache | 长上下文时 KV 读取是主要字节 | 显存减半、decode 长上下文提速 | attention kernel 需支持反量化 |

补充概念：**mixed precision**（敏感层保留高精度：首层、末层 lm_head、norm、softmax）；**权重离群值 / 激活离群值**（LLM 里某些通道幅度大 100×，来自 norm 与 attention sink）。

---

## 4. 精度评估

- **指标**：perplexity（WikiText 等，量化后上升 < 0.1–0.5 算好）；下游任务准确率（MMLU 等）；**逐层比对**：量化模型 vs FP32 golden 的 cosine similarity（> 0.99）、相对误差 `‖ŷ − y‖/‖y‖`、最大绝对误差；**首 token 一致率 / logits KL**。
- **敏感层规律**：第一层、最后几层、lm_head、attention 的 `W_o`、含离群通道的 `down_proj` 常最敏感；norm、softmax 一般不量化。
- **报告方式**（和你论文一样）：写清校准集、粒度、格式、评估集、随机种子；单次运行只能说「观测」，不能说「显著」。

---

## 5. 「精度错了 / 掉了」的定位流程（背）

```
0. 固定变量：seed、shape、dtype、batch=1、greedy 解码、关闭随机采样
1. 端到端确认：是全错（NaN / 乱码）还是轻微下降（ppl +2）？
   ├─ 全错 → 找数值异常：溢出 inf、NaN、scale=0、zero-point 越界、layout 错（NCHW/NHWC、转置）、量化前后 shape 不一致
   └─ 轻微 → 逐层对拍
2. 逐层对拍：hook 抓每层输出，与 FP32 golden 算 cosine / 相对误差，找第一个误差跳变的层
3. 二分到算子：把那层各算子单独在芯片 / 参考实现上跑，同输入比输出
4. 三分归因：
   模型：这层有离群通道 / 这层天然敏感 → 换粒度、保留 FP16、SmoothQuant
   软件栈：算子实现差异（GeLU tanh 近似 vs erf、softmax 在 FP16 做、累加精度、舍入模式、融合改变了计算顺序）
   硬件：阵列累加位宽、不支持的格式被软件模拟、denormal 处理、FMA 与分开乘加的差异
5. 修复后回归：把这条 case 写进自动化测试（tolerance 明确写出来）
```

**常见根因清单**（面试报 3–5 个）：softmax 在 FP16 溢出；per-tensor 被离群值撑大；校准集分布与实际不符；量化了不该量化的 norm / 首末层；累加精度不足；算子 tolerance 用绝对误差比大数；layout/转置错误看起来像「精度差」实际是功能错；随机性没固定就比对。

---

## 6. 对芯片性能的影响（把量化和 Day 2 连起来）

- 低比特 **降字节**（decode 提速）+ **升峰值**（INT8/FP8 阵列 2×，prefill 提速）。
- 但：weight-only 在 prefill 要反量化 → 需要融合进 GEMM kernel，否则反而慢；per-group 反量化在阵列里不好做 → 芯片支持决定能用什么粒度；动态激活量化要在线算 max → 多一次读。
- 「验证不同数据类型对精度与性能的影响」这项工作的标准产出：一张表，行 = 配置（FP16 / W8A8 / W4A16 / FP8 / KV-INT8），列 = ppl、任务精度、TTFT、TPOT、吞吐、显存。

---

## 7. 十个追问

1. FP16 和 BF16 各差在哪、训练为什么选 BF16？
2. INT8 乘法为什么要 INT32 累加？
3. 对称和非对称量化分别用在哪？
4. per-group 为什么 INT4 必需？（4 bit 只有 16 档，小组才能让 scale 贴近局部分布）
5. weight-only 为什么对 prefill 没帮助？
6. SmoothQuant 的 α 是什么、取 0.5 的含义？（难度在激活和权重之间平均分）
7. 量化后 ppl 从 6.1 到 6.3 算好吗？（通常可接受，看任务）
8. 精度全崩（输出乱码）先查什么？（NaN/inf、scale、layout）
9. 怎么找出敏感层？（逐层单独量化看 ppl 变化，或逐层 cosine）
10. KV cache 量化对什么场景最有用？（长上下文、大 batch）

## 8. 动手（1.5 h）

```python
import numpy as np
def quant_sym_per_channel(W, bits=8):
    qmax = 2**(bits-1) - 1
    s = np.abs(W).max(axis=1, keepdims=True) / qmax     # 每行一个 scale
    q = np.clip(np.round(W / s), -qmax, qmax)
    return q.astype(np.int8), s
W = np.random.randn(256, 256).astype(np.float32); W[3, :] *= 50   # 人为加一行离群
q, s = quant_sym_per_channel(W); What = q * s
print(np.linalg.norm(What - W) / np.linalg.norm(W))
# 对比 per-tensor（s 用全局 max）：误差明显变大 → 亲眼看到离群值的危害
```
再做：per-group（g=64）版本；INT4（qmax=7）下 per-channel vs per-group 误差；用 `torch.ao.quantization.quantize_dynamic` 把 Day 1 的 toy 模型 linear 层动态 INT8，比对输出 cosine。

PyTorch 第 3 小时：`model.half()` / `.to(torch.bfloat16)` 后跑 toy 模型，故意把输入放大 300 倍观察 FP16 出 inf 而 BF16 不出。
