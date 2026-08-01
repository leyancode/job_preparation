#course/dissertation #archer2 #numa #openmp #type/concept #status/review

> [!info] 知识图谱
> 前置：[[02 MPI-OpenMP 混合并行与布局]]  
> 后续：[[04 矩阵分区 Halo 与通信]] · [[08 性能机理验证方法]]

# ARCHER2 硬件拓扑与线程绑定

## 读前概念

| 术语 | 含义 |
| --- | --- |
| CPU / processor | 执行程序指令的处理器；ARCHER2每节点安装两个CPU |
| core | CPU内部可独立执行指令的物理核心 |
| socket | 主板上安装一个物理CPU的位置，也常用来指该CPU |
| main memory | 容量较大但比cache慢的主存，程序的大部分矩阵和向量存放在这里 |
| cache | 位于核心附近的小容量高速存储，用来暂存近期数据 |
| L1/L2/L3 | cache层级；L1最小且最快，L3更大并由多个核心共享 |
| latency | 完成一次访问需要等待的时间 |
| bandwidth | 单位时间能够传输的数据量 |
| affinity | 把进程或线程限制到指定CPU核心集合 |
| SMT | Simultaneous Multithreading，一个物理核心提供多个硬件线程 |

硬件拓扑描述核心、cache、内存控制器和socket之间的层次关系。程序访问越远的资源，通常需要更长时间；多个线程共享同一资源时，也可能竞争其容量或带宽。

## 一、节点层次

一个 ARCHER2 compute node 有 128 个物理核心：

```text
node
├── socket 0：64 cores
│   ├── 4 NUMA regions，每个 16 cores
│   └── 8 CCD，每个 CCD 含 2 个 CCX
└── socket 1：64 cores
    ├── 4 NUMA regions，每个 16 cores
    └── 8 CCD，每个 CCD 含 2 个 CCX

CCX：4 cores，共享 16 MB L3
CCD：2 CCX，共 8 cores
NUMA region：16 cores，即 4 CCX
```

每个核心有私有 L1/L2。不同 CCX 不共享 L3。节点还提供 SMT，但正式实验用 `--hint=nomultithread`，目标是每个物理核心只使用一个硬件线程。

来源：[ARCHER2 Hardware](https://docs.archer2.ac.uk/user-guide/hardware/)

## 二、为什么拓扑影响性能

| 层次 | 共享资源或边界 | 可能出现的成本 |
| --- | --- | --- |
| core | 执行流水线、L1/L2 | 单线程计算速度 |
| CCX | 4 cores 共享 L3 | L3容量、共享与跨CCX访问 |
| NUMA | 本地内存控制器 | 远程内存延迟和带宽 |
| socket | 64 cores | 跨socket数据访问 |
| node | 128 cores、网络接口 | MPI注入带宽与节点间通信 |

NUMA 的 first-touch 规则意味着，物理页通常由第一次写入它的线程所在 NUMA region 分配。初始化线程和计算线程放置不一致时，后续访问可能经过远程内存控制器。

NUMA是Non-Uniform Memory Access，中文常译为非一致内存访问。同一节点中的所有核心都能访问整台节点的主存，但访问本地NUMA region连接的内存通常更快。first-touch不是把数据永久锁在某个线程上，而是决定物理页最初由哪个NUMA region提供。

> [!warning]- 易错点：CCX 与 NUMA 不是一回事
> 4 个线程跨越 CCX 的临界点，但仍可完全位于一个 16-core NUMA region 内。8-thread rank 通常跨两个 CCX，不等于跨 NUMA。只有实际 affinity 和 CPU 编号映射才能确定边界是否被跨越。

## 三、当前布局的预期放置

在 `OMP_PLACES=cores`、`OMP_PROC_BIND=close` 且连续放置成立时：

| 布局，每节点 | 每个 rank 的预期范围 | 拓扑解释 |
| --- | --- | --- |
| 128×1 | 1 core | 没有OpenMP团队 |
| 64×2 | 2 adjacent cores | 一个CCX容纳两个rank |
| 32×4 | 4 adjacent cores | 一个rank正好位于一个CCX |
| 16×8 | 8 adjacent cores | 一个rank跨两个CCX，通常位于一个CCD |

这些是待验证的映射，不是从环境变量自动推出的事实。

## 四、用 xthi 验证实际放置

ARCHER2 官方提供 `xthi`，输出每个 MPI rank 和 OpenMP thread 的 CPU affinity。

```bash
module load xthi
export OMP_PLACES=cores
export OMP_PROC_BIND=close
export OMP_DYNAMIC=FALSE

export OMP_NUM_THREADS=4
export SRUN_CPUS_PER_TASK=4
srun --nodes=1 \
     --ntasks=32 \
     --ntasks-per-node=32 \
     --cpus-per-task=4 \
     --exact \
     --hint=nomultithread \
     --distribution=block:block \
     --cpu-bind=cores \
     xthi
```

把 `32/4` 分别替换为 `128/1`、`64/2`、`16/8`。检查：

1. 每个rank的线程数是否正确；
2. 同一rank内线程是否使用不同物理核心；
3. 不同rank的核心集合是否重叠；
4. 4-thread rank是否落入一个CCX；
5. 8-thread rank是否跨两个CCX；
6. 是否完全避开SMT的第二硬件线程。

来源：[ARCHER2 Running Jobs](https://docs.archer2.ac.uk/user-guide/scheduler/)

> [!tip]- CPU mask 的辅助证据
> `srun --cpu-bind=verbose` 会输出每个 task 的 CPU mask。任务内部读取 `/proc/self/status` 的 `Cpus_allowed_list` 也能得到允许使用的 CPU 列表。`xthi` 更强，因为它同时显示 OpenMP threads 的实际 affinity。

## 五、必须区分的两类结论

```text
xthi 输出正确
  ⇒ 可以说 placement 与设计一致

32×4 比 16×8 快
  ⇏ 已证明原因是 CCX/L3
```

拓扑验证只证明程序放在哪里。机理验证还要测量缓存、内存、MPI等待和OpenMP同步，并做只改变放置策略的控制实验。详见 [[08 性能机理验证方法]]。

## 速查

| 问题 | 回答 |
| --- | --- |
| 每节点多少物理核心 | 128 |
| 每节点多少socket | 2 |
| 每节点多少NUMA regions | 8 |
| 每个NUMA多少核心 | 16 |
| 每个CCX多少核心 | 4 |
| 每个CCX共享多少L3 | 16 MB |
| 验证线程落点 | `xthi` |
| 正式绑定策略 | cores + close + no SMT |

## 自测

> [!example]- 一个socket、NUMA region和CCX分别包含多少核心？
> ARCHER2每个socket有64个核心，每个NUMA region有16个核心，每个CCX有4个核心。

> [!example]- 为什么8-thread rank跨两个CCX不等于跨NUMA？
> 一个NUMA region包含4个CCX。8个相邻核心可以跨两个CCX，同时仍完全位于同一个NUMA region。

> [!example]- `OMP_PROC_BIND=close`为什么不能替代xthi证据？
> 它只表达放置策略。xthi输出才能确认runtime最终把每个rank和thread放到了哪些核心。
