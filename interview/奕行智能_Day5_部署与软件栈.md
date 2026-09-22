# Day 5 · 部署与软件栈：PyTorch 工具链 · 推理引擎 · 并行策略 · 客户模型适配

> 目标：画出模型从 PyTorch 到芯片的流程；说清 TTFT / TPOT / 吞吐；算子不支持的三条路；DP / TP / PP / EP 各切什么（简历写了「数据 / 张量并行、batching 与吞吐-时延取舍」）。
> 半天正文 + 1 h PyTorch + （可选）本机 llama.cpp 实测。

---

## 1. 模型 → 芯片：典型软件栈

```
PyTorch 模型（eager）
  │  torch.export / FX / ONNX 导出            ← 前端：把 Python 变成图
  ▼
计算图（算子 + 张量 + shape/dtype）
  │  图优化：常量折叠、算子融合、layout 转换（NCHW↔NHWC）、死代码消除、量化插入
  ▼
算子级 IR（如 MLIR 方言 / TVM Relay-TIR / 厂商 IR / 虚拟指令集）
  │  算子映射：查算子库（手写 kernel）或代码生成（自动 tiling / 调度）
  │  内存规划：SRAM 分配、生命周期、DMA 调度
  ▼
硬件指令 / kernel 二进制  →  运行时（driver、内存管理、多核调度、host-device 队列）
```

- **静态 shape vs 动态 shape**：NPU 编译器偏好静态（tiling 在编译期定）；LLM 的 seq 长度可变 → 分桶（bucketing）/ padding / 按 max 编译 / 动态 shape 支持。
- **算子覆盖率**是适配的第一道门；**图优化的 pass 顺序**决定融合能否发生；**layout** 错误是「精度错」最常见的功能性原因之一。
- 厂商 SDK 的通用结构：模型转换工具 + 算子库 + 编译器 + 运行时 + profiler + 精度对拍工具。你面的岗位就是拿这些工具把客户模型跑通、跑对、跑快。

---

## 2. PyTorch 工具链（今天的 1 小时动手）

| 工具 | 干什么 | 一句话 |
|---|---|---|
| eager | 逐算子立即执行 | 灵活，launch 开销大 |
| `torch.compile` | Dynamo 抓图 → Inductor 生成融合 kernel | 一行提速；graph break 是常见问题 |
| `torch.fx` / `torch.export` | 图表示，可遍历 / 改写 / 导出 | 写图优化 pass、插量化节点 |
| ONNX | 跨框架交换格式；opset 版本 | 导出时算子不支持 / 动态维度报错 |
| `torch.profiler` | 算子级时间、Chrome trace | 定位热点、看 kernel 数 |
| forward hook | 逐层抓输入输出 | 精度对拍 |
| 自定义算子（`torch.library` / C++ 扩展） | 注册新算子、给不支持的算子提供实现 | 适配时的第三条路 |
| `torch.ao.quantization` | 动态 / 静态 / QAT 量化 API | PTQ 原型 |

动手：把 Day 1 的 toy 模型 `torch.export`（或 `fx.symbolic_trace`）导出，打印 graph，写一个 pass 把 `RMSNorm → Linear` 标记为可融合；再 `torch.onnx.export` 看 opset 和节点。

---

## 3. 推理引擎与服务指标

### 3.1 指标（要能定义 + 说由什么决定）

| 指标 | 定义 | 由什么决定 |
|---|---|---|
| **TTFT** | 首 token 延迟 | prefill：prompt 长度 × 算力；排队时间 |
| **TPOT / ITL** | 每输出 token 间隔 | decode：每 token 字节 ÷ 带宽；batch 大小；KV 长度 |
| 端到端延迟 | TTFT + n × TPOT | |
| 吞吐 | 系统每秒 tokens（或每秒请求） | batch、并发、显存能放多少 KV |
| **吞吐-时延取舍** | batch↑ → 吞吐↑、TPOT↑（过拐点后） | roofline 拐点；SLO 决定 batch 上限 |
| goodput | 满足 SLO 的吞吐 | 服务真正关心的 |

### 3.2 引擎与它们各自解决的问题

| 引擎 | 关键技术 | 解决什么 |
|---|---|---|
| **vLLM** | **PagedAttention**（KV 按 block 分页，块表间接寻址）、**continuous batching**（请求随到随加入、完成即退出，不等整批）、prefix caching | KV 内存碎片与浪费（利用率从 ~30% 到 ~90%）；batch 内长短不一的等待；共享前缀复用 |
| TensorRT-LLM | 编译优化 kernel、in-flight batching、FP8/INT4 | NVIDIA 上极致性能 |
| llama.cpp | GGUF 量化格式、CPU/多后端、`llama-bench` | 端侧 / CPU；你 ARCHER2 计划用的 |
| SGLang | RadixAttention 前缀树、结构化输出 | 多轮 / agent 场景前缀复用 |

### 3.3 推理优化清单（会说每条解决什么）
- **KV cache 量化 / GQA**：减 decode 字节。
- **投机解码（speculative decoding）**：小模型起草 k 个 token，大模型一次前向验证 → 一次读权重出多个 token，decode 从 memory-bound 中榨吞吐；接受率决定收益。
- **Prefix caching**：系统 prompt / 多轮历史的 KV 复用 → 降 TTFT。
- **Chunked prefill**：长 prompt 切块与 decode 混批，避免 decode 被长 prefill 卡住（TPOT 抖动）。
- **算子融合 / CUDA graph / 静态图**：消 launch 开销，小 batch decode 尤其重要。
- **量化**（Day 3）。
- **调度**：按 SLO 限制 batch；优先级；抢占。

---

## 4. 并行策略（简历写了「数据 / 张量并行」）

| 并行 | 切什么 | 通信 | 何时用 |
|---|---|---|---|
| **DP（数据并行）** | 复制整模型，切 batch | 训练：梯度 AllReduce；推理：无（多副本负载均衡） | 模型放得下一卡 |
| **TP（张量并行，Megatron）** | 切单层矩阵：`W_q/k/v`、`W_up/gate` 按列切，`W_o`、`W_down` 按行切 | **每层 2 次 AllReduce**（激活大小），需高带宽（NVLink / 片内 NoC） | 单卡放不下、延迟敏感；一般不跨节点 |
| **PP（流水并行）** | 按层切成 stage | 相邻 stage 点对点传激活（小） | 跨节点；有 bubble，用 micro-batch 填 |
| **EP（专家并行）** | MoE 专家分卡 | **all-to-all** 两次 / 层 | MoE 模型 |
| SP / CP（序列 / 上下文并行） | 切序列长度 | attention 内 AllGather KV 或 ring | 超长上下文 |

- TP 为什么需要高互联：decode 每层两次 AllReduce、消息小、延迟主导 → 跨 PCIe / 跨机就把 TPOT 拖垮。
- 组合：8 卡内 TP、跨机 PP、MoE 加 EP。
- **和你 MPI 经验的对应**：TP 的 AllReduce = CG 里的 VecTDot 归约（每步同步、随 N 暴露）；PP 的 bubble = 负载不均；EP 的 all-to-all = MPI_Alltoall。

---

## 5. 客户模型适配流程（岗位日常，背成一条线）

```
1. 拿模型 + 客户的精度/性能目标（SLO）
2. 算子覆盖检查：导出图 → 列出算子 → 对照算子库 → 标出不支持 / 部分支持（某 dtype、某 shape）
3. 不支持算子的三条路：
   ① 分解为已支持算子（如 GeLU → tanh 近似的基本算子；LayerNorm → mean/var/…）
   ② 写自定义算子（向量单元 / RVV 核）并注册到编译器
   ③ 回退到 host CPU（fallback）——能跑但要看数据往返代价
4. 精度对拍：FP32 golden → 芯片输出，逐层 cosine / 相对误差 / 端到端指标（Day 3 流程）
5. 性能基线：profiler → 算子时间分布 → 每个热点在 roofline 的位置（Day 2）
6. 优化：融合 / tiling / 量化 / 并行策略 / batch；验证精度不回退
7. 回归自动化：pytest 参数化（shape × dtype × batch），golden 比对带明确 tolerance，性能阈值断言
8. 问题闭环：把根因归到模型 / 软件栈 / 硬件，反馈给对应团队（算子 / 编译器 / 架构）
```
第 7 步就是你 `HPC_Agent` CI 里「声明即测试」和 benchmark 仓库里「头条数锁进 pytest」的做法——面试时直接引用。

---

## 6. 十个追问

1. TTFT 和 TPOT 分别由什么决定？怎么分别优化？
2. continuous batching 和 static batching 差别？（不等整批；请求级别的加入退出）
3. PagedAttention 解决的是算力还是内存？（内存碎片 / 共享）
4. 投机解码为什么能提速？收益取决于什么？（一次读权重验证多 token；接受率、小模型开销）
5. TP 为什么不跨节点？（每层两次小消息 AllReduce，延迟主导）
6. PP 的 bubble 怎么减？（更多 micro-batch、交错调度）
7. 一个客户模型有芯片不支持的算子，你怎么办？（三条路 + 评估代价）
8. 怎么设计推理性能回归测试？（固定 shape/dtype/batch 矩阵、golden + tolerance、阈值、CI）
9. 动态 shape 在 NPU 上为什么麻烦？（静态 tiling / 编译期内存规划；分桶或 padding）
10. batch 加大后 TPOT 什么时候开始明显上升？（过 roofline 拐点，或 KV 读取超过权重）

## 7. 可选：本机 llama.cpp 实测（2 h，有余力再做）

```bash
git clone https://github.com/ggml-org/llama.cpp && cd llama.cpp
cmake -B build -DGGML_NATIVE=ON && cmake --build build -j
# 下载一个 ~1B 的 GGUF Q4_K_M 模型到 models/
./build/bin/llama-bench -m models/<model>.gguf -p 512 -n 128 -t 4,8
```
记录 `pp512`（prefill tokens/s）与 `tg128`（decode tokens/s）；查本机内存带宽（或 STREAM），算 `decode 上限 = 带宽 / 模型字节`，得到「达到上限的 X%」。**这一个数字就能把「推理性能测试经验」从零变成一次真实测量**，且方法论与你的 ARCHER2 计划完全一致。
