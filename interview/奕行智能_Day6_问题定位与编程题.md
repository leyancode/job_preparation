# Day 6 · 问题定位方法论 + 编程 / 笔试题

> 目标：「慢 / 错 / 不稳」三分归因流程 2 分钟讲完；6 个案例各 2 分钟；8 道手写题闭卷；笔试通用题过一遍。
> 今天 2.5 h 方法论与案例，2 h 编程，1 h 笔试通用。

---

## 1. 问题定位总流程（背）

```
0 复现与固定：版本（模型 / SDK / 驱动）、seed、shape、dtype、batch、输入样本；能否稳定复现？
1 分类：功能错（结果不对 / 崩溃）｜性能差（比预期慢）｜不稳定（偶发）
2 分层二分：端到端 → 层 → 算子 → kernel/指令；每一层都拿同样输入和参考实现对拍
3 三分归因（JD 原话：模型 / 软件栈 / 硬件架构）
   模型：结构（动态 shape、控制流、非常规算子）、精度敏感层、离群值、MoE 路由分布
   软件栈：算子实现（近似、累加精度、融合改变顺序）、编译器 tiling / 内存规划、layout、驱动、版本
   硬件：带宽、SRAM 容量、阵列形状、NoC 拥塞、累加位宽、格式不支持、功耗降频
4 用计数器 / profile 证明，而不是猜（阵列忙、DMA 忙、重叠比、每核活跃方差、带宽利用率）
5 修复 → 回归测试固化 → 反馈到对应团队（闭环）
```
要说的态度句：「我先确认这个算子在 roofline 上的位置，再决定往哪个方向查——如果它已经贴着带宽上限，再优化 kernel 也没用，得从字节数下手。」

---

## 2. 六个案例（每个：现象 → 假设 → 验证 → 结论）

**① decode tokens/s 只有理论上限的 30%**
假设：a) 权重没走最优 dtype / 有反量化开销；b) 小算子 launch 开销（norm、rope、采样）；c) KV 读取比预期大；d) DMA 与计算没重叠。
验证：profile 看 GEMV 实际 GB/s ÷ 峰值；kernel 数与总 launch 时间；KV 长度；DMA/阵列忙时间重叠比。
典型结论：非 GEMM 算子占了 50% 时间 → 融合 + 静态图；或反量化没融进 GEMM。

**② prefill 利用率低（MFU 20%）**
假设：seq 短 / batch 小让 GEMM 的 M 太小；K/N 不对齐阵列；attention 没用 flash 类实现；tiling 太小。
验证：按算子看 MFU；GEMM 形状表；attention 的片外流量。
结论：形状 padding 到阵列倍数、换 flash-attention kernel、增大 tile。

**③ INT8 量化后某任务精度崩**
Day 3 流程：全崩 → NaN / scale / layout；轻微 → 逐层 cosine 找跳变层 → 该层有离群通道 → per-channel / SmoothQuant / 保留 FP16。

**④ MoE 模型吞吐随 batch 不涨**
假设：专家负载不均、all-to-all 通信、小 GEMM 利用率、容量因子丢 token。
验证：每专家 token 数直方图；通信时间占比；grouped GEMM 利用率。
结论：路由不均 → 调容量 / 专家复制；通信 → 重叠或减少 EP 度。

**⑤ 客户模型某算子输出与 PyTorch 不一致**
先确认功能还是精度：最大绝对误差与相对误差量级；是否 layout / 转置 / 广播规则不同；近似实现（GeLU erf vs tanh、softmax 精度）；FP16 溢出；累加顺序不同导致的 1e-3 级差异（可接受，写 tolerance）。

**⑥ 多卡 TP 加速比只有 1.3×（4 卡）**
假设：AllReduce 延迟主导（decode 小消息）、跨 PCIe、没有通信-计算重叠、各卡负载不均。
验证：通信时间占比、消息大小、拓扑。
结论：TP 度降到 NVLink 域内、换 PP、增大 batch 让通信摊薄。
（用你论文的话：这就是通信暴露与并行度的权衡，我在 4,096 核上量过。）

---

## 3. 手写题（闭卷能写；numpy / PyTorch 都行）

### 3.1 数值稳定 softmax
```python
def softmax(x, axis=-1):
    m = x.max(axis=axis, keepdims=True)
    e = np.exp(x - m)
    return e / e.sum(axis=axis, keepdims=True)
```
追问：为什么减 max（防 exp 溢出，且结果不变）；FP16 下在哪一步最危险（exp 前的 x 和 sum）。

### 3.2 单头 causal attention（numpy）
```python
def attention(Q, K, V):               # [s, d]
    d = Q.shape[-1]
    S = Q @ K.T / np.sqrt(d)
    S = np.where(np.triu(np.ones_like(S, dtype=bool), 1), -np.inf, S)
    return softmax(S) @ V
```

### 3.3 带 KV cache 的 decode 循环
```python
K_cache, V_cache = [], []
for t in range(steps):
    x = embed(token)                  # [1, d]
    q, k, v = x @ Wq, x @ Wk, x @ Wv
    K_cache.append(k); V_cache.append(v)
    Kc, Vc = np.vstack(K_cache), np.vstack(V_cache)     # [t+1, d]
    s = q @ Kc.T / np.sqrt(d)         # [1, t+1]，无需 mask：只看历史
    out = softmax(s) @ Vc
    token = argmax(out @ Wo @ W_vocab)
```
追问：每步复杂度（O(t·d)）；cache 大小；为什么 prefill 后第一次 decode 要把 prompt 的 KV 一起用。

### 3.4 分块 GEMM
```python
def gemm_blocked(A, B, T=64):
    M, K = A.shape; _, N = B.shape
    C = np.zeros((M, N), dtype=A.dtype)
    for i in range(0, M, T):
        for j in range(0, N, T):
            for k in range(0, K, T):
                C[i:i+T, j:j+T] += A[i:i+T, k:k+T] @ B[k:k+T, j:j+T]
    return C
```
追问：为什么分块（片上复用、AI = T/2 量级）；T 怎么选；边角怎么处理；循环顺序对局部性的影响（i-k-j 让内层连续）。

### 3.5 per-channel 对称 INT8 量化 / 反量化（Day 3 已写）+ per-group 版本。

### 3.6 Roofline 估算题
给：峰值 P（TFLOPS）、带宽 BW（GB/s）、模型参数 N、权重 b 字节。求：单流 decode 上限 `BW/(N·b)`；拐点 batch `B* = (P/BW)·b/2`；prefill 1000 token 的理想时间 `2·N·1000/P`。

### 3.7 `torch.profiler` + hook 逐层对拍脚本
```python
ref_acts, dev_acts = {}, {}
# 两个模型分别注册 hook（Day 1 5.4），跑同一输入
for name in ref_acts:
    a, b = ref_acts[name].float().flatten(), dev_acts[name].float().flatten()
    cos = (a @ b) / (a.norm() * b.norm() + 1e-12)
    rel = (a - b).norm() / (a.norm() + 1e-12)
    print(f"{name:40s} cos={cos:.6f} rel={rel:.3e}")
```

### 3.8 RMSNorm + SiLU + 简单融合
```python
def rmsnorm(x, g, eps=1e-6): return x / np.sqrt((x**2).mean(-1, keepdims=True) + eps) * g
def silu(x): return x / (1 + np.exp(-x))
def swiglu_ffn(x, Wg, Wu, Wd): return (silu(x @ Wg) * (x @ Wu)) @ Wd
```

---

## 4. 笔试通用题（1 h 过一遍，按你已有基础只列易忘点）

**Python**
- 可变默认参数陷阱；`is` vs `==`；浅拷贝 / 深拷贝；GIL 与多线程（CPU 密集用多进程）；生成器 / 迭代器；装饰器写法；`__slots__`；列表推导 vs 生成器内存。
- numpy：广播规则；`axis` 语义；view vs copy（切片是 view，fancy index 是 copy）；`einsum`。
- 复杂度：排序 O(n log n)；哈希 O(1) 平均；堆 O(log n)。

**C / C++**（HPC 岗笔试常有）
- 指针与数组、`const` 位置、栈 vs 堆、内存对齐与 `struct` 大小、`static`、`volatile`、`inline`；`memcpy` 与 `memmove`；未定义行为（越界、signed overflow）。
- `sizeof(struct{char; int; char;})` = 12（对齐）；cache line 64 B、false sharing。
- 实现一个简单的矩阵乘并说明如何向量化 / 分块 / OpenMP 并行。

**体系结构 / OS**
- 进程 vs 线程；上下文切换；虚拟内存与页表、TLB；cache 映射与替换；流水线冒险；分支预测；内存一致性与 barrier；DMA 是什么。

**算法（easy–medium）**
- 两数之和（哈希）、二分查找、反转链表、LRU（OrderedDict / 哈希 + 双向链表）、BFS/DFS、topK（堆）、合并区间、矩阵转置原地、前缀和。
- 手写一个线程安全的计数器 / 生产者消费者（Python `queue`）。

**数值 / ML 基础**
- softmax 与交叉熵；反向传播链式法则；梯度消失 / 爆炸；Adam；dropout；BatchNorm vs LayerNorm；过拟合与正则。

---

## 5. PyTorch 第 6 小时

把 3.2 / 3.3 / 3.8 用 `torch` 重写并与 `F.scaled_dot_product_attention`、`nn.RMSNorm`（或手写）对拍；用 `torch.testing.assert_close(atol, rtol)` 设 tolerance，体会为什么 FP16 要放宽到 1e-2 量级。
