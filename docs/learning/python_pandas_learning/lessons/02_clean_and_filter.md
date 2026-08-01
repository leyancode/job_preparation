# 02 Clean and Filter: 哪些数据可以用于画图？

本节目标：把原始 CSV 变成适合 Runtime Scaling 图的数据。

## 核心问题

画图前要明确：

- 只用成功完成的实验：`status == "completed"`
- 只比较指定线程数：`T = 1, 2, 4, 8`
- 确认数值列确实是 numeric
- 验证 `total_cores = nodes x ppn x threads`

## 运行

```bash
python scripts/02_clean_and_filter.py
```

## 关键概念

`pandas` 常见过滤写法：

```python
completed = df[df["status"] == "completed"]
selected = completed[completed["threads"].isin([1, 2, 4, 8])]
```

常见类型转换写法：

```python
df["runtime_seconds"] = pd.to_numeric(df["runtime_seconds"], errors="coerce")
```

`errors="coerce"` 的意思是：如果某个值无法转换成数字，就变成 `NaN`，方便之后检查和过滤。

## 检查点

脚本会打印：

- 清洗前后行数
- 保留下来的 `threads`
- 保留下来的 `scale`
- `total_cores` 验证是否通过

## Quick Check

1. 为什么画图或聚合前要先过滤 `status == "completed"`？
确保数据完整

批改：方向正确。更准确地说，是为了只保留真正成功完成的实验运行，避免 failed、timeout、cancelled 等不完整运行进入图表或均值计算。Runtime scaling 比较的是有效运行时间，如果失败任务也混进去，数学含义就变了。

2. `df["threads"].isin([1, 2, 4, 8])` 的作用是什么？
保证["threads]在[1,2,4,8]之内

批改：意思正确。可以写得更规范一点：筛选 `threads` 列，只保留线程数属于 `[1, 2, 4, 8]` 的行。这里的 `.isin(...)` 会返回一列 True/False，pandas 再用它过滤 DataFrame。

3. `pd.to_numeric(..., errors="coerce")` 遇到无法转换的值会怎么处理？
报错

批改：这里需要修正。`errors="coerce"` 的意思不是报错，而是把无法转换成数字的值变成 `NaN`。这样后面可以用 `dropna(...)` 把有问题的行过滤掉。如果想让无法转换的值直接报错，通常会用 `errors="raise"`。

4. 为什么要验证 `total_cores = nodes x ppn x threads`？
确保数值正确

批改：正确。可以再补一句：`total_cores` 是后面做 runtime scaling 的核心横轴之一，如果它和 `nodes * ppn * threads` 不一致，说明 CSV 里的资源配置或清洗过程有问题，后面的 scaling 图和表格都会不可靠。

1. 如果清洗后行数明显变少，你应该先检查哪些列？
"status"

批改：`status` 是应该先检查的列之一。更完整的答案还应包括：`threads` 是否只保留了 `[1, 2, 4, 8]`，以及 `scale`、`unknowns`、`total_cores`、`runtime_seconds` 是否因为无法转换或缺失变成了 `NaN` 并被 `dropna(...)` 删除。也可以检查原始数据里有多少 failed 或 timeout 记录。
