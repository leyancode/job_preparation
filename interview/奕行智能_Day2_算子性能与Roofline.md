# Day 2 · 核心算子性能：GEMM · Attention · Norm · MoE · 融合 · Roofline

> 目标：能判断任一算子是 compute-bound 还是 memory-bound；讲清 FlashAttention 为什么快；说清 MoE 为什么利用率难；用 MFU / 带宽利用率描述「没跑满」。
> 你的锚点：论文里「同时看迭代数、每迭代成本、总吞吐」= 这里「同时看 FLOPs、bytes、实际时间」；exposure share = 利用率损失的可加归因。

---

## 1. Roofline 的完整说法（简历上写了「roofline / 访存墙估算」）

- 算术强度 `AI = FLOPs / bytes_moved`（bytes 指片外内存流量，不是片上）。
- `可达性能 = min(P_peak, AI × BW)`；拐点 `AI* = P_peak / BW`。
- **AI < AI*：memory-bound**，优化方向是减少字节（量化、融合、复用、tiling）；**AI > AI*：compute-bound**，优化方向是提高阵列利用率（形状对齐、流水、去 bubble）。
- 三种常用「墙」：算力墙、带宽墙、（多卡）通信墙；再往下还有 launch 开销 / 延迟墙（小算子太多）。
- **利用率指标**：`MFU = 实测 FLOP/s ÷ 峰值`；带宽利用率 = 实测 GB/s ÷ 峰值；训练里还有 HFU（含重计算）。**性能问题定位第一步永远是：这个算子在 roofline 上的哪个位置、离它自己的上限差多少。**

对照表（数量级要有感觉）：

| 平台 | 峰值算力（FP16/BF16 dense） | 带宽 | AI* |
|---|---|---|---|
| H100 SXM | ≈ 990 TFLOPS | 3.35 TB/s HBM3 | ≈ 295 |
| A100 | ≈ 312 TFLOPS | 2.0 TB/s | ≈ 156 |
| 你的 EPYC 7742 节点（AVX2 FP64） | ≈ 4.6 TFLOPS | ≈ 0.2 TB/s（理论 0.41） | ≈ 23 |
| 典型 NPU（示意） | INT8 数百 TOPS | LPDDR / HBM 数百 GB/s | 几百 |

INT8 阵列峰值通常是 FP16 的 2×，FP8 同理——所以低比特既降字节又升峰值。

---

## 2. GEMM

`C[M×N] = A[M×K] · B[K×N]`：FLOPs = 2MNK；最少字节 = (MK + KN + MN) × b。

- 整体 AI（b=2 字节）`= 2MNK / (2(MK+KN+MN)) = MNK/(MK+KN+MN)`。M=N=K=4096 → AI ≈ 1365 ≫ 295 → compute-bound。
- **GEMV（decode, M=1）**：AI = NK/(K+KN+N) ≈ 1 → 注定 memory-bound，MFU 个位数是正常的，不是 bug。
- **Tiling**：把 C 切成 T_M×T_N 块，K 方向分段累加；每块把 A、B 的条带搬进片上（shared memory / SRAM），复用 T 次。片上 AI ≈ `T_M·T_N / (T_M + T_N)`（每从片外读 1 个元素做多少次乘加）——**块越大越接近 compute-bound，但受片上容量限制**；这和「工作集放进 L3 后 superlinear」是同一个物理。
- **形状不好的表现**：M/N/K 不是阵列宽度（如 128 / 256）的整数倍 → 边角 tile padding 浪费；K 很小 → 累加流水填不满；N 小（小 batch decode）→ 变 GEMV。
- **利用率损失来源清单**：tile 边角 / 阵列形状不匹配 / 搬运与计算不重叠（没双缓冲）/ 累加精度转换 / bank conflict / launch 开销。

---

## 3. Attention 的性能

### 3.1 朴素实现的问题
`S = QKᵀ` 是 s×s，FP16 下 s=8K 一个头就是 128 MB；写回内存再读回来做 softmax、再读回来乘 V——**三次往返片外内存，attention 变成 memory-bound**，尽管 FLOPs 本身不大。

### 3.2 FlashAttention 的思路（不减少 FLOPs，减少字节）
按 K/V 分块流式处理，用 **online softmax** 维护每行的运行最大值 m 和归一化和 l，S 与 P 永不物化：

```
m_new = max(m_old, rowmax(S_blk))
l_new = e^(m_old − m_new)·l_old + Σ e^(S_blk − m_new)
O_new = e^(m_old − m_new)·O_old + e^(S_blk − m_new)·V_blk
最后 O = O_new / l_new
```
片外流量从 O(s²) 降到 O(s)，速度提升 2–4×，内存 O(s)。反向用重计算换内存。**面试标准答法：「它快是因为 IO-aware，把中间矩阵留在片上，不是因为算得少」。**

### 3.3 decode 阶段的 attention
每步 Q 只有 1 行，主要工作是**读整段 KV cache**（memory-bound）；多个 Q 头共享一个 KV 头（GQA）提高复用；长上下文时它取代权重读成为主要字节来源。PagedAttention 解决的是 KV 的**内存碎片和共享**（分块表），不是算力。

---

## 4. 元素级算子与算子融合

- Softmax、RMSNorm、SiLU、残差加、RoPE：FLOPs 极少，**全是访存受限**（AI < 1）。
- 单独跑每个算子 = 每个都从片外读一遍、写一遍；**融合**（norm+linear 的输入、gate·up·silu 三合一、attention 内部、残差+norm）= 把它们放进同一个 kernel/同一次片上驻留 → 字节数与 launch 次数同时下降。
- NPU 上融合更重要：kernel 之间的调度是静态的，每次回片外 DRAM 的代价相对更高；编译器的 fusion pass 是性能的主要来源之一。
- **判断融合收益**：`节省字节 = (被融合中间张量的大小) × 2（写+读）`；对照带宽算时间。

---

## 5. MoE 的性能

- 计算：每 token 只算 k 个专家的 FFN → FLOPs 便宜；但每个专家收到的 token 数不同 → **一堆形状各异的小 GEMM**，阵列利用率差、需要 padding 或 grouped GEMM。
- 负载不均：热门专家排队，其它核空转（**你论文里 OpenMP 空转的翻版**）；训练加辅助均衡损失，推理用容量因子（capacity factor）限制并丢弃 / 重路由。
- 专家并行（EP）：专家分布在不同卡，token 路由 = **all-to-all** 两次（去、回）；小 batch 时通信占比高。这和 MPI 集合通信的 α–β 模型一样：消息小 → 延迟主导。
- 内存：所有专家权重都要驻留 → 总参数决定显存，激活参数决定算力。
- 面试常问：「MoE 吞吐为什么随 batch 不涨」→ 专家不均 + all-to-all + 小 GEMM 利用率。

---

## 6. 「没跑满」怎么说（词汇表）

| 现象 | 术语 | 第一反应 |
|---|---|---|
| 阵列大部分时间空闲 | 低 MFU / 阵列利用率 | 形状？tiling？搬运没重叠？ |
| 带宽用了但算力没用 | memory-bound | 融合、量化、增大 batch |
| 算力和带宽都没用满 | 延迟/launch-bound、pipeline bubble、同步等待 | 算子太碎、依赖链、host 开销 |
| 多核部分忙部分闲 | 负载不均 / tail effect | 切分粒度、MoE 路由 |
| 多卡等通信 | 通信暴露（communication exposure） | 重叠、减少同步、换并行策略 |

这张表就是你论文「通信暴露 vs 线程空转」的通用版，面试时可以直接说「我在 CPU 集群上做过同样的归因，方法是把时间拆成可加的类别再看谁随配置变化」。

---

## 7. 十个追问

1. 给 M=N=K=1024 FP16 GEMM，是 compute 还是 memory bound？（AI ≈ 341 > 295，H100 上勉强 compute-bound；A100 上 compute-bound）
2. decode 的 GEMV MFU 只有 3%，是 bug 吗？（不是，AI≈1，上限就是带宽）
3. FlashAttention 减少了 FLOPs 吗？（没有，减少片外 IO）
4. 什么情况下 attention 比 FFN 更贵？（长上下文：KV 读取与 s² 计算超过权重）
5. 算子融合为什么在 NPU 上比 GPU 更关键？（静态调度、片外访问成本高、launch 无法动态掩盖）
6. RMSNorm 单独一个 kernel 的 AI 是多少量级？（< 1）
7. MoE 8 专家 top-2，激活参数怎么算？（共享部分 + 2/8 的专家参数）
8. tiling 的块大小怎么定？（片上容量 / 阵列尺寸 / 双缓冲要两份）
9. 怎么用 profiler 数据判断 memory 还是 compute bound？（实测 FLOP/s 与 GB/s 各除以峰值，看哪个接近 1）
10. 小 batch 下怎么提高 decode 吞吐？（量化减字节、GQA/KV 量化、投机解码用一次读权重出多个 token）

## 8. 动手（1.5 h）

- numpy：朴素三重循环 vs `np.dot` vs 分块 GEMM（块 64），计时；理解分块为什么在 numpy 里不一定更快（BLAS 已经分块）。
- 写 online softmax，与 `np.exp(x - x.max()) / sum` 逐元素比对。
- PyTorch 第 2 小时：用 `torch.profiler` 对比 `F.scaled_dot_product_attention` 与你手写的 attention 在 s = 512 / 2048 的时间。
