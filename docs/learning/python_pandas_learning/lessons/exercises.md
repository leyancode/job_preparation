# Exercises

这些练习建议在读完 `06_runtime_scaling_tables.md` 之后做。先自己用 pandas 写，再运行 `scripts/05_generate_tables.py` 查看 helper answers。

## Exercise 1: 找出每个 problem size 最快的配置

问题：

```text
For each scale, which row has the lowest runtime_mean_s?
```

提示：

```python
idx = df.groupby("scale")["runtime_mean_s"].idxmin()
fastest = df.loc[idx]
```

你需要记录：

- scale
- total_cores
- threads
- runtime_mean_s
- speedup
- CUs

## Exercise 2: 找出每个 problem size 最便宜的配置

问题：

```text
For each scale, which row has the lowest CUs?
```

提示：

```python
idx = df.groupby("scale")["cu"].idxmin()
cheapest = df.loc[idx]
```

思考：

- fastest 和 cheapest 是同一行吗？
- 如果不是，报告里应该优先讨论哪个？

## Exercise 3: 找出 efficiency > 100% 的行

问题：

```text
Which configurations have efficiency > 1.0?
```

提示：

```python
df[df["efficiency"] > 1.0]
```

思考：

- 是不是所有 problem size 都有这种情况？
- 这些行通常出现在低 core count 还是高 core count？
- 可能原因是什么？

## Exercise 4: 比较 MPI-only 和 hybrid

在同一个 `total_cores` 下比较：

```text
T = 1
T = 2
T = 4
T = 8
```

问题：

- 哪个 runtime 更低？
- 哪个 CUs 更低？
- T=8 是否经常比 T=1/T=2/T=4 差？

## Exercise 5: 写一句报告解释

用自己的话写 3 句：

1. 增加 total cores 对 runtime 的整体影响。
2. CUs 为什么和 total cores 不同。
3. 为什么 efficiency 可能超过 100%。

## Quick Check

1. `idxmin()` 返回的是最小值本身，还是最小值所在行的 index？
2. 为什么找最快配置时看 `runtime_mean_s`，找最便宜配置时看 `cu`？
3. `df[df["efficiency"] > 1.0]` 这种写法属于什么类型的 pandas 操作？
4. 比较 MPI-only 和 hybrid 时，为什么要控制相同的 `total_cores`？
5. 写报告时，为什么不能只说“最快配置”，还要讨论 CUs 或 efficiency？
