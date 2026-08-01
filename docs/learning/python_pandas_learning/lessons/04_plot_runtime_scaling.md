# 04 Plot Runtime Scaling: 如何做 optional visual check？

本节目标：用 `matplotlib` 画出 Runtime vs Total Cores，帮助你理解趋势。

注意：现在报告主线是 `Table 1a-1e`，图不再是最终核心输出。它的作用是 visual check：帮助你快速看出 scaling 是否合理、哪些配置明显异常。

## 图的设计

横轴：

```text
total cores = nodes x ppn x threads
```

纵轴：

```text
runtime / solve time seconds
```

每个 problem size 一个 subplot：

```text
[1M]       [5M]       [10M]
[20M]      [40.96M]
```

每张小图四条线：

```text
T = 1, 2, 4, 8
```

## 运行

```bash
python scripts/04_plot_runtime_scaling.py
```

## 输出

```text
outputs/runtime_scaling_pandas_linear.png
outputs/runtime_scaling_pandas_logy.png
outputs/runtime_scaling_interpretation.md
```

## 为什么同时画 linear 和 log-y？

linear y-axis 更直观，适合看绝对 runtime 差距。

log-y 更适合 scaling 图，因为 1 core 到 128 cores 的 runtime 跨度很大。log-y 能让高 core count 区域的差异更清楚。

## Quick Check

1. Runtime Scaling 图的横轴和纵轴分别是什么？
2. 为什么每个 problem size 要分成不同 subplot？
3. 每条线里的 `T = 1, 2, 4, 8` 表示什么？
4. linear y-axis 和 log-y axis 分别适合观察什么？
5. 为什么这张图现在是 optional visual check，而不是报告主证据？
