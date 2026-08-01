#course/dissertation #stencil #sparse-matrix #2d #3d #type/concept #status/review

> [!info] 知识图谱
> 前置：[[00 PETSc-ARCHER2 性能研究知识图谱]]  
> 后续：[[05 CG 与 GAMG]] · [[04 矩阵分区 Halo 与通信]]

# 2D-3D Stencil 与稀疏矩阵

## 一、从Poisson方程到 `Ax=b`

Poisson方程是一类偏微分方程，用来描述温度、电势等空间场。连续方程定义在无限多个空间位置上，计算机不能直接存储这些位置。离散化（discretisation）先用有限网格点代表空间，再用相邻网格点的数值近似导数。

离散后得到线性方程组：

```text
A x = b
```

| 符号 | 含义 |
| --- | --- |
| `A` | 系数矩阵，记录网格点之间的耦合关系 |
| `x` | 未知向量，每个元素对应一个网格点的待求值 |
| `b` | 已知右端向量 |
| matrix row | 一个网格点对应的一条方程 |
| matrix column | 该方程引用的未知量编号 |
| diagonal entry | 行号与列号相同的矩阵元素 |
| nonzero | 数值不为零、需要实际存储和计算的矩阵元素 |

大多数网格点只与附近少数点耦合，因此矩阵绝大多数位置为零。这种矩阵称为稀疏矩阵（sparse matrix）。

## 二、Stencil 是什么

Stencil描述一个网格点与哪些邻居发生耦合。离散Poisson问题后，每个网格点对应线性系统中的一个未知量和一行矩阵。

### 2D五点Stencil

```text
        -1
         |
   -1 -- 4 -- -1
         |
        -1
```

内部点最多连接上下左右4个邻居，加上对角项，每行最多5个非零元。

### 3D七点Stencil

```text
中心点对角项 6
邻居：x±1、y±1、z±1
```

内部点最多连接6个邻居，加上对角项，每行最多7个非零元。

| 项目 | 2D | 3D |
| --- | ---: | ---: |
| 网格 | m×n | m×n×p |
| 邻居数 | 最多4 | 最多6 |
| 每行非零元 | 最多5 | 最多7 |
| 对角值 | 4 | 6 |

代码位置：[2D assembly](../../../src/ex2_repeat.c#L41) · [3D assembly](../../../src/3d_repeat.c#L37)

## 三、为什么稀疏矩阵通常受内存限制

Sparse matrix-vector multiplication（SpMV）需要读取：

- 矩阵数值；
- 列索引；
- 输入向量的非连续元素；
- 输出向量。

每个非零元只贡献少量浮点运算，却带来多次内存读取。它的arithmetic intensity通常较低，所以内存带宽、缓存复用和远程数据访问容易决定性能。

3D每行比2D多两个非零元。因此相同未知数下，3D每次MatMult通常处理更多矩阵数据和浮点操作。

PETSc日志把稀疏矩阵向量乘记为 `MatMult`。它计算 `y=A×x`，是CG每次迭代中的主要计算kernel之一。这里的kernel指反复执行、占据主要计算时间的核心操作。AIJ是PETSc对压缩稀疏行一类矩阵格式的名称：程序只保存非零数值及其列索引，而不是保存大量的零。一个flop表示一次浮点运算，flop/s表示每秒完成的浮点运算数量。

### Arithmetic intensity与Roofline

```text
arithmetic intensity = floating-point operations / bytes moved

attainable performance
  ≤ min(peak compute performance,
        memory bandwidth × arithmetic intensity)
```

Roofline是一种用峰值计算能力、内存带宽和arithmetic intensity估计性能上限的模型。如果一个kernel位于memory-bandwidth一侧，增加计算单元或线程不一定提高性能。此时数据布局、缓存命中和NUMA访问比理论峰值flop/s更重要。Roofline适合形成假设；要声称MatMult受带宽限制，仍需要内存带宽或硬件计数器证据。

> [!warning]- Eq/s 的跨维度限制
> “处理一个未知量”在2D和3D中不是相同工作量。Eq/s适合在同一维度中比较布局；跨维度比较时应同时报告seconds/iteration、MatMult时间、PCApply时间和PETSc flops。

## 四、当前driver的线性编号

2D driver把二维坐标映射成连续编号：

```text
Ii = i × n + j
邻居偏移 = ±1, ±n
```

3D driver使用：

```text
Ii = i + m × j + m × n × k
邻居偏移 = ±1, ±m, ±m×n
```

这些偏移决定哪些非零元可能落到其他MPI rank拥有的列中。

## 五、矩阵存储与非零元

正式运行通常使用PETSc并行AIJ矩阵。概念上可分为：

```text
本地对角块 diagonal block
  列属于当前rank拥有的向量范围

非对角块 off-diagonal block
  列属于其他rank，需要远程向量值
```

MatMult开始前或执行过程中，PETSc通过VecScatter取得off-diagonal block所需的远程向量元素。off-diagonal nonzeros的数量和通信邻居结构，比“2D还是3D”这个标签更直接地决定实际通信。

## 六、不要默认当前程序使用几何域分解

当前driver执行：

```c
MatSetSizes(A, PETSC_DECIDE, PETSC_DECIDE, global_n, global_n);
MatGetOwnershipRange(A, &Istart, &Iend);
```

PETSc随后给每个rank一段连续矩阵行。程序没有用DMDA把网格显式分成二维方块或三维立方体。

```mermaid
flowchart LR
    A["规则2D/3D网格"] --> B["线性编号"]
    B --> C["连续矩阵行区间"]
    C --> D["MPI ranks"]
```

因此，标准surface-to-volume模型只能作为背景知识，不能直接当作当前程序的通信量证明。应从 `VecScatter`、消息统计、off-diagonal nonzeros或实际scatter图测量。

DMDA是PETSc用于管理规则多维网格、ghost区域和处理器网格的组件。使用DMDA才会显式构造二维或三维笛卡尔式网格划分：[DMDACreate2d](https://petsc.org/release/manualpages/DMDA/DMDACreate2d/)

## 七、比较2D与3D时保持哪些条件

| 应保持一致 | 原因 |
| --- | --- |
| unknown数量尽量接近 | 控制问题规模 |
| nodes与cores/node | 控制硬件资源 |
| layout | 控制MPI/OpenMP映射 |
| CG+GAMG选项 | 控制算法 |
| warm-up与19次重复求解 | 控制测量阶段 |
| build与PETSc arch | 控制软件环境 |

即使以上条件匹配，五点与七点矩阵的每方程工作量仍不同。这是研究对象本身的差异，不应人为消除，但需要在解释中明确。

## 速查

| 看到的指标 | 它回答什么 |
| --- | --- |
| unknowns | 问题大小 |
| nonzeros | 稀疏矩阵工作量 |
| MatMult time | SpMV总成本 |
| VecScatter time | MatMult中的远程数据交换/等待 |
| flops | 实际浮点工作量 |
| Eq/s | 应用吞吐量，不是统一硬件效率 |

## 自测

> [!example]- 为什么五点stencil对应每行最多5个非零元？
> 一个内部网格点连接4个邻居，并有1个对角项，所以最多有5个非零元。

> [!example]- 为什么3D和2D的Eq/s不能直接解释成硬件效率差异？
> 3D七点矩阵每行通常处理更多非零元。两个维度中“一个equation”对应的内存和浮点工作量不同。

> [!example]- 当前driver为什么不能直接套用笛卡尔子域的surface-to-volume模型？
> driver把网格线性编号后按连续矩阵行分配给ranks，没有显式使用DMDA构造二维方块或三维立方体子域。
