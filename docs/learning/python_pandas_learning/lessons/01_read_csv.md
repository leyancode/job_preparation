# 01 Read CSV: CSV 里到底有什么？

本节目标：用 `pandas` 读取 `runtime_results.csv`，先观察数据，不急着画图。

## 核心问题

我们要先知道：

- 有多少行？
- 有哪些列？
- 每列是什么类型？
- 前几行长什么样？
- 数值列有没有被当成字符串？

## 运行

```bash
python scripts/01_read_csv.py
```

## 你会看到什么

脚本会打印：

- CSV 路径
- `df.shape`
- `df.columns`
- `df.head()`
- `df.info()`
- 关键列的唯一值

## 关键概念

`pd.read_csv(...)` 会返回一个 `DataFrame`。可以把 `DataFrame` 理解成带列名的表格。

常用观察方法：

```python
df.head()
df.columns
df.info()
df.describe()
```

这些方法的目的不是做最终分析，而是避免在不了解数据时直接画图。

## Quick Check

1. `pd.read_csv(...)` 返回的对象是什么？

返回的是 pandas `DataFrame`，可以理解成带列名的表格。

2. `df.shape[0]` 和 `df.shape[1]` 分别表示什么？

`df.shape[0]` 表示行数 rows，`df.shape[1]` 表示列数 columns。

3. `df.columns` 和 `df.shape[1]` 有什么区别？

`df.columns` 给出列名，`df.shape[1]` 给出列的数量。

4. `df.info()` 主要帮助你检查哪些信息？

它可以帮助检查行数、列数、列名、每列的 non-null 数量、数据类型 dtype，以及内存占用。

5. `dropna().unique()` 通常用来观察什么？

通常用来观察某一列里有哪些不同取值。`dropna()` 用来去掉空值或缺失值，`unique()` 用来找出不重复的值。
