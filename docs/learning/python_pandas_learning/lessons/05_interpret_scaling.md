# 05 Interpret Scaling: 如何从 table 写结论？

本节目标：从 report-ready runtime tables 中写出性能分析结论。图可以作为辅助检查，但主证据来自 `runtime_scaling_tables_pandas.md`。

## 问题 1：增加 total cores 后 runtime 是否下降？

看同一个 `scale` 内，`total cores` 增大时 `runtime mean/s` 是否下降。

如果下降明显，可以写：

```text
For this problem size, increasing total cores generally reduces runtime.
```

如果下降不平滑，可以继续解释：

```text
The scaling is not monotonic for all hybrid configurations, suggesting communication, threading, or measurement overhead.
```

## 问题 2：同一个 total cores 下 MPI-only 和 hybrid 哪个更好？

在同一个 `total cores` 下比较不同 `threads`：

- `threads = 1` 更接近 MPI-only
- `threads > 1` 是 hybrid MPI+OpenMP

比较标准：

- `runtime mean/s` 越低，运行越快
- `CUs` 越低，资源成本越低

在当前单节点数据中，因为所有配置 `nodes = 1`，所以 `CUs` 和 runtime 成正比；未来如果有多节点数据，CUs 会更重要。

## 问题 3：speedup 和 efficiency 怎么解释？

公式：

```text
speedup = baseline runtime / runtime mean
efficiency = speedup / total cores
```

baseline 是同一个 problem size 的 1 node、1 ppn、1 thread、1 total core。

如果 `efficiency > 100%`，不要直接删掉或改成 100%。这可能说明：

- superlinear speedup
- cache/memory behavior 改善
- 1-core baseline 特别慢
- 重复实验数量有限导致测量波动

报告里可以写：

```text
Some low-core-count configurations show efficiency above 100%, which is possible in measured strong-scaling data and may reflect superlinear effects or baseline sensitivity.
```

## 问题 4：CUs 说明了什么？

这里：

```text
CUs = nodes x runtime mean / 3600
```

因为 1 CU 是 1 node for 1 hour，不管用了多少 cores。

所以对于当前 `nodes = 1` 的数据：

```text
lower runtime = lower CUs
```

但是如果以后有 `nodes = 2, 4, ...`，最快配置不一定是最省 CU 的配置。

## 问题 5：如何组织报告段落？

可以按这个顺序写：

1. 先说 overall trend：runtime 是否随 total cores 增加而下降。
2. 再说 best configuration：哪个配置 runtime 最低。
3. 再说 MPI-only vs hybrid：同 core count 下哪个更好。
4. 再说 efficiency：是否接近理想 scaling，是否出现 >100%。
5. 最后说 CUs：最快和最省资源是否一致。

## 一个短模板

```text
For the [scale] problem size, runtime generally decreases as total cores increase.
The fastest configuration is [configuration], with a mean runtime of [runtime] seconds.
At the same total core count, [MPI-only/hybrid] is generally better in this dataset.
Efficiency remains below ideal scaling for most configurations, although some low-core-count cases exceed 100%, likely due to measured superlinear or baseline effects.
Because all runs use one node, CU cost is proportional to runtime in this dataset.
```

## Quick Check

1. 判断 scaling 是否有效时，应该在同一个 `scale` 内比较什么？
2. 同一个 `total cores` 下，如何比较 MPI-only 和 hybrid？
3. `speedup = baseline runtime / runtime mean` 中 baseline 指什么？
4. 为什么 efficiency 可能超过 100%，但不应该直接改成 100%？
5. 在当前单节点数据中，为什么 CUs 和 runtime 成正比？
