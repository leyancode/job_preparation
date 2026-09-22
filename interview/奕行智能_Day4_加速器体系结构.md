# Day 4 · AI 加速器体系结构：GPU vs NPU/TPU · RISC-V/RVV · 多卡通信

> 目标：画出「一个 GEMM 在 NPU 上的生命周期」；说清 scratchpad 与 cache 的差别对软件的含义；讲 CUDA 编程模型与 NCCL（简历上写了）；RVV 三个概念。
> 你的锚点：EPYC 的 CCX / L3 / NUMA / 带宽 你已经很熟——NPU 只是把「谁管缓存」从硬件改成了编译器。

---

## 1. 三种架构对照（先建总图）

| 维度 | CPU（你的 EPYC） | GPU（CUDA） | NPU / TPU 类（奕行「类 TPU」） |
|---|---|---|---|
| 并行粒度 | 少量强核 + SIMD（AVX2 256b） | 数千 SIMT 线程，warp=32 | 大 MAC 阵列（脉动）+ 向量单元 + 标量核 |
| 谁管调度 | 硬件乱序 + OS | 硬件 warp 调度器（动态隐藏延迟） | **编译器静态调度**（VLIW 式，指令顺序、时序在编译期定） |
| 片上存储 | cache（硬件透明） | 寄存器 + shared memory（软件管理）+ L1/L2 cache | **scratchpad SRAM（软件/编译器显式管理，DMA 搬运）** |
| 适合 | 分支多、不规则、延迟敏感 | 规则大并行、动态 shape 尚可 | 静态 shape 的稠密张量算子（GEMM、conv） |
| 弱点 | 算力密度低 | 功耗、成本 | 不规则算子、动态 shape、控制流；软件栈决定一切 |
| 性能上限的决定者 | 带宽 + 向量化 | 占用率 + 访存合并 + tensor core 利用率 | tiling 是否填满阵列与 SRAM、DMA 与计算能否重叠 |

---

## 2. GPU（课程层级，但要能讲）

- **CUDA 编程模型**：grid → block → thread；同 block 内线程共享 shared memory、可 `__syncthreads()`；**warp = 32 线程锁步执行**（分支发散会串行化）；kernel 由 host 发起（launch 开销 ~几 µs）。
- **存储层次**：寄存器（每线程）→ shared memory / L1（每 SM，~228 KB on H100）→ L2（50 MB）→ HBM（80 GB，3.35 TB/s）。
- **访存合并（coalescing）**：一个 warp 访问连续 128 B 才是一次事务；stride 访问带宽暴跌——和 CPU 的 cache line 同理。
- **占用率（occupancy）**：每 SM 常驻 warp 数；靠切换 warp 隐藏访存延迟；寄存器 / shared memory 用太多则占用率下降。
- **Tensor core**：矩阵乘专用单元（`mma` 指令），FP16/BF16/TF32/FP8/INT8；GEMM 高性能的来源；形状要对齐（16 的倍数）。
- **CUDA graph**：把一串 kernel launch 录下来一次提交，消 launch 开销——decode 小算子多时非常有效。
- **Streams**：并发 kernel 与拷贝重叠。
- **H100 数字**：132 SM、FP16 dense ≈ 990 TFLOPS、FP8 ≈ 1979、HBM3 3.35 TB/s、NVLink 900 GB/s。

---

## 3. NPU / TPU 类架构（这是重点，公司是「类 TPU」）

### 3.1 脉动阵列（systolic array）
- N×N 个 MAC 单元排成网格；权重预先装入（**weight-stationary**），输入从左向右流、部分和从上向下流，每个周期每个 MAC 做一次乘加，**数据在单元之间直接传递、不回存储器** → 极高的算力密度和能效。
- TPU v1：256×256 INT8 阵列 = 65,536 MAC，700 MHz → 92 TOPS；24 MiB 统一缓冲区（unified buffer，scratchpad），4 MiB 累加器。
- **形状匹配**：GEMM 的 K、N 要能填满 256 宽；M 是流过的行数（越多越好，摊掉装载权重的时间）。**decode 的 M=1（或 batch）** → 装一次权重只用一行 → 阵列利用率 ≈ B/256 —— 这是 NPU 上 decode 更依赖 batch 的原因。
- **数据流**：weight-stationary（权重驻留，适合权重复用多的 conv/GEMM）、output-stationary（部分和驻留，减少累加器带宽）、row-stationary（Eyeriss，平衡各类复用）。选择决定哪类数据反复过片外。

### 3.2 片上存储：scratchpad vs cache
- cache：硬件决定放什么、何时换出；软件不可见但不可控；miss 不可预测。
- **scratchpad**：地址空间显式，**编译器/运行时决定每个 tile 何时 DMA 进来、何时写回**；可预测、无 tag 开销、面积效率高；代价是**所有 tiling / 双缓冲 / 生命周期都是软件的责任**——性能问题往往是「编译器的 tiling 决策不好」而不是硬件。
- **DMA 双缓冲（ping-pong）**：计算 tile i 时搬 tile i+1；需要 SRAM 容量 ≥ 2 个 tile；带宽 × 计算时间 ≥ tile 字节数才能完全掩盖。**「搬运与计算不重叠」是 NPU 利用率低的头号原因。**

### 3.3 向量单元与标量核
- GEMM 以外的算子（softmax、norm、激活、RoPE、采样、MoE 路由）跑在向量单元（SIMD/向量处理器）上；奕行用 **RISC-V + RVV** 做这部分是合理的架构选择。
- 非 GEMM 算子如果没有融合、或向量单元太弱，会成为 Amdahl 的串行部分——阵列再强也被拖住。**面试可问：Epoch 上非 GEMM 算子由 RVV 核执行还是专用向量单元？**

### 3.4 多核 + NoC
- 多个核（每核一套阵列 + SRAM）通过片上网络（mesh / ring）互联；切分方式：按 batch / 按 head / 按输出通道（TP 的片内版）/ 按层（流水）。
- NoC 问题的表现：核间同步等待、带宽争用（多核同时从 HBM 取同一权重）、all-reduce 在片内的延迟。**权重广播 vs 各核独立读取**是常见的优化点。
- 多核负载不均 = 你的 OpenMP 空转；tail effect = 最后一个 tile 只有部分核有活。

### 3.5 指令调度
- VLIW / 静态调度：编译器把 DMA、阵列、向量、标量指令打包到时槽，硬件不重排 → **编译器质量 = 性能**；动态 shape 会打断静态计划（padding 或重编译）。
- 「虚拟指令集（VISA）」的作用：模型 → 图 → 虚拟指令（与硬件代际解耦）→ 后端映射到具体硬件指令；类似 PTX 之于 SASS。

### 3.6 「一个 GEMM 在 NPU 上的生命周期」（会画）

```
HBM/DDR 权重 ──DMA──► SRAM 权重 tile ──► 装入阵列（weight-stationary）
HBM 激活    ──DMA──► SRAM 激活 tile ──► 流过阵列 ──► 累加器(INT32/FP32)
                                     ──► 向量单元：反量化 / bias / 激活函数 / norm（融合）
                                     ──► SRAM 输出 tile ──DMA──► HBM
瓶颈候选：① DMA 带宽（tile 太小、没双缓冲）② 阵列装权重次数（M 小）③ 阵列形状不匹配（padding）
        ④ 向量单元太慢（非 GEMM 算子串行化）⑤ 累加器容量 ⑥ 多核同步 / NoC
profiling 看：阵列忙周期占比、DMA 忙周期占比、两者重叠比例、SRAM 命中/换入次数、每核活跃时间方差
```

---

## 4. RISC-V 与 RVV（基础即可，但要会三个概念）

- RISC-V：开放模块化 ISA，基础整数集 + 扩展（M 乘除、F/D 浮点、**V 向量**、C 压缩…）；自研芯片选它是为了免授权与可定制扩展（自定义指令给 AI 算子）。
- **RVV（向量扩展）三个概念**：
  1. **VLEN**：硬件向量寄存器位宽，**软件不写死**（vector-length agnostic）——同一段代码在 VLEN=128 和 512 的芯片上都能跑；对比 AVX2 固定 256 位、换宽度要重编译。
  2. **`vsetvli`**：每次循环前告诉硬件「我要处理多少个元素、元素多宽」，硬件返回本次实际能处理的 `vl`，尾部循环自动处理（无需 mask 尾巴）。
  3. **LMUL**：把 2/4/8 个向量寄存器拼成一个更长的逻辑寄存器，换取更大吞吐、减少循环次数（代价是可用寄存器数变少）。
- 对 AI 的意义：向量单元处理 norm / softmax / 激活 / 数据重排；自定义扩展加矩阵指令（社区有 matrix extension 提案）；RVV 的 strided / indexed load 适合 gather/scatter（MoE 路由、embedding）。

---

## 5. 多卡通信与 NCCL（简历写了「NCCL 集合通信」）

- NCCL = GPU 上的集合通信库（MPI 集合的 GPU 版）：`AllReduce / ReduceScatter / AllGather / Broadcast / AlltoAll`，走 NVLink / PCIe / IB。
- **Ring AllReduce**：reduce-scatter + all-gather，每卡发送 `2(N−1)/N × size` ≈ 2×size，带宽最优、延迟 O(N)；**Tree**：延迟 O(log N)，小消息好。和你 MPI 里讲的 Rabenseifner / recursive doubling 一一对应。
- 张量并行每层 2 次 AllReduce（attention 后、FFN 后），消息 = 激活大小 `B×s×d×b`；decode 时消息小 → 延迟主导 → TP 跨节点很差；这就是「互联带宽是芯片宣传点」的原因。
- 通信-计算重叠：把 AllReduce 与下一层 GEMM 流水；NCCL 用独立 stream。
- 通用估算：`T = α + size/β`；NVLink 900 GB/s vs PCIe 64 GB/s vs IB 400 Gb/s ≈ 50 GB/s。

---

## 6. 十个追问

1. 脉动阵列为什么能效高？（数据在 MAC 之间流动，不回存储器；控制简单）
2. decode 在 NPU 上为什么比 GPU 更依赖 batch？（阵列装一次权重要流过足够多行）
3. scratchpad 对软件意味着什么？（tiling、双缓冲、生命周期全是编译器/程序员的责任）
4. 「DMA 与计算没重叠」怎么从 profile 看出？（DMA 忙与阵列忙时间不重叠、总时间 ≈ 两者之和）
5. 静态调度架构最怕什么？（动态 shape、控制流、不规则算子）
6. 数据流（weight/output-stationary）怎么选？（看哪类张量复用最多、片上容量）
7. CUDA 里 warp 分支发散是什么？（同 warp 走不同分支串行执行）
8. 访存合并为什么重要？（一次事务 128 B；stride 访问浪费带宽）
9. Ring AllReduce 每卡发送多少数据？（≈ 2 × size × (N−1)/N）
10. RVV 和 AVX 的根本区别？（向量长度无关、`vsetvli` 处理尾部、LMUL 分组）

## 7. 动手（1 h）+ PyTorch 第 4 小时

- 手算：某 NPU 峰值 200 TOPS INT8、带宽 400 GB/s；8B 模型 INT8 权重 8 GB → 单流 decode 上限 50 tokens/s；拐点 batch = 200e12/400e9 ÷ (2/1) = 250。画出 roofline。
- 画 tiling + 双缓冲时序图：tile 计算 10 µs、搬运 8 µs → 重叠后每 tile 10 µs；搬运 12 µs → 12 µs（memory-bound）。
- PyTorch：`torch.compile(model)` 跑 toy 模型，对比编译前后 profiler 里的 kernel 数量（融合的直观感受）；用 `torch.fx.symbolic_trace` 打印图，数一数节点。
