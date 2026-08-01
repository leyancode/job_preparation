# Python Runtime Scaling Learning Path

这个目录是一套问题导向的 Python 数据分析练习，用 `pandas` 复现 `size_grid_summary/runtime_results.csv` 的 Runtime Scaling 表格，并用 `matplotlib` 做可选的趋势检查图。

核心链路是：

```text
runtime_results.csv
-> read CSV
-> clean/filter data
-> groupby aggregate repeated runs
-> build report-ready runtime scaling tables
-> compute speedup, efficiency, and CUs
-> optionally plot Runtime vs Total Cores
-> interpret scaling behaviour for the report
```

## 0. Prepare Environment

```bash
cd ~/leyan/jobSkill/petsc-benchmark-suite/s2795693/analysis/python_runtime_scaling_learning
bash setup_env.sh
source .venv/bin/activate
```

如果以后重新打开终端，只需要再运行：

```bash
cd ~/leyan/jobSkill/petsc-benchmark-suite/s2795693/analysis/python_runtime_scaling_learning
source .venv/bin/activate
```

这个 `.venv` 也是当前 `analysis/scripts/ksp_2d_scaling/` 使用的 Python 环境。

## 1. Run the Lessons

每个脚本对应一节讲义：

```bash
python scripts/01_read_csv.py
python scripts/02_clean_and_filter.py
python scripts/03_groupby_aggregate.py
python scripts/05_generate_tables.py

# Optional visual check
python scripts/04_plot_runtime_scaling.py
```

建议阅读顺序：

1. `lessons/00_environment.md`
2. `lessons/01_read_csv.md`
3. `lessons/02_clean_and_filter.md`
4. `lessons/03_groupby_aggregate.md`
5. `lessons/06_runtime_scaling_tables.md`
6. `lessons/05_interpret_scaling.md`
7. `lessons/exercises.md`
8. `lessons/04_plot_runtime_scaling.md` optional visual check

## Question Bank

学习过程中问过的问题会记录在 `QUESTIONS.md`。之后继续向 Codex 询问和本学习项目有关的问题时，也请把新的问题、核心解释和可复查命令追加到这个问题库中，方便后面复习。

## Review Notes

批改 lesson 里的 Quick Check 或练习答案时，保留原来的答案，不要直接覆盖。请在原答案下面另起一行写批改意见、修正答案或补充解释，方便对照看到自己的原始理解和修改后的理解。

## 2. Expected Outputs

运行到最后会生成：

- `outputs/runtime_scaling_aggregated_pandas.csv`
- `outputs/runtime_scaling_tables_pandas.csv`
- `outputs/runtime_scaling_tables_pandas.md`
- `outputs/runtime_scaling_table_exercise_answers.md`
- `outputs/runtime_scaling_pandas_linear.png`
- `outputs/runtime_scaling_pandas_logy.png`
- `outputs/runtime_scaling_interpretation.md`

## 3. What You Should Be Able To Explain

完成后，你应该能回答：

- `DataFrame` 是什么？
- 为什么 CSV 读入后要检查类型？
- 为什么要过滤 `status == "completed"`？
- `groupby(...).agg(...)` 在这里解决了什么问题？
- 为什么 raw runs 不应该直接放进报告？
- `speedup` 和 `efficiency` 怎么算？
- 为什么 `efficiency` 可能超过 100%？
- `CUs = nodes x runtime_mean / 3600` 表示什么？
- 为什么 Runtime Scaling 图常常需要 log scale？
- 在同一个 total cores 下，MPI-only 和 hybrid 配置如何比较？
