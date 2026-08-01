# 06 Runtime Scaling Tables: 如何生成报告用表格？

本节目标：把 raw runs 聚合成 report-ready tables，而不是直接把原始 CSV 放进报告。

## 为什么 table 是主线？

`runtime_results.csv` 是 raw data：一行代表一次 run。

报告里需要的是聚合后的配置结果：同一个配置如果跑了多次，应该合并成一行，例如：

```text
runtime_mean_s = 多次 runtime 的平均值
n_runs = 这个配置跑了几次
```

主表不一定要展示 `n_runs` 或 `runtime_std_s`，但 CSV 输出中保留这些字段，方便追溯。

## 分组字段

这次按完整运行配置分组：

```text
scale
m
n
unknowns
nodes
ppn
threads
mpi_ranks
total_cores
unknowns_per_core
matrix_type
```

这些字段相同，说明是同一种运行配置。

## 计算字段

聚合后计算：

```text
runtime_mean_s
runtime_std_s
runtime_min_s
runtime_max_s
n_runs
speedup
efficiency
cu
```

主 Markdown 表展示更精简的字段：

```text
total cores
nodes
ppn
MPI ranks
threads
unknowns/core
runtime mean/s
speedup
efficiency
CUs
```

## speedup 和 efficiency

baseline 使用同一个 problem size 下：

```text
nodes = 1
ppn = 1
threads = 1
total_cores = 1
```

公式：

```text
speedup = baseline runtime / runtime_mean
efficiency = speedup / total_cores
```

如果 efficiency 超过 100%，不要自动认为公式错了。实测数据可能出现 superlinear speedup，也可能受 baseline、缓存、内存访问、测量波动影响。报告里应该说明，而不是简单把它截断到 100%。

## CUs

这里使用 ARCHER2 风格的资源成本估计：

```text
CUs = nodes x runtime_mean / 3600
```

因为 1 CU 是 1 node for 1 hour，不管你用了 1 core 还是 128 cores。

## 运行

```bash
python scripts/05_generate_tables.py
```

## 输出

```text
outputs/runtime_scaling_tables_pandas.csv
outputs/runtime_scaling_tables_pandas.md
outputs/runtime_scaling_table_exercise_answers.md
```

## 学习重点

这一课最重要的不是 Markdown 格式，而是理解：

- raw runs 和 report table 的区别
- 为什么要 `groupby`
- 为什么 fastest configuration 不一定是 cheapest configuration
- 为什么 CUs 对 HPC 报告很重要

## Quick Check

1. raw runs 和 report-ready table 的区别是什么？
2. 为什么分组字段里要包含 `nodes`、`ppn`、`threads`、`mpi_ranks`？
3. `runtime_mean_s` 和 `runtime_std_s` 分别说明什么？
4. `speedup` 和 `efficiency` 的公式分别是什么？
5. 为什么最快配置不一定是最省 CUs 的配置？
