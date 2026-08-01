# 00 Environment: 环境能不能跑？

本节目标：建立一个只属于这个学习目录的 Python 环境，安装 `pandas` 和 `matplotlib`。

## 为什么要用 `.venv`

`.venv` 是 virtual environment。它把这个练习需要的 Python 包和系统 Python 分开，避免把学习依赖装到全局环境里。

## 命令

```bash
cd ~/leyan/petsc-benchmark-suite/s2795693/analysis/python_runtime_scaling_learning
bash setup_env.sh
source .venv/bin/activate
```

看到类似下面的输出就说明环境可用：

```text
pandas: ...
matplotlib: ...
Environment is ready.
```

## 检查点

```bash
python - <<'PY'
import pandas as pd
import matplotlib
print(pd.__version__)
print(matplotlib.__version__)
PY
```

如果这个命令没有报错，就可以进入下一课。

## 如果 `python3 -m venv` 失败

在一些 Debian/Ubuntu 环境里，系统 Python 可能缺少 `ensurepip`，这时会看到类似：

```text
The virtual environment was not created successfully because ensurepip is not available.
```

解决方法之一是安装系统包：

```bash
sudo apt install python3.10-venv
```

本目录的 `setup_env.sh` 也会优先尝试使用 `uv venv`。如果你的机器上有 `uv`，通常不需要额外安装 `python3-venv`。

## Quick Check

1. 为什么不建议把 `pandas` 和 `matplotlib` 直接装进系统 Python？
2. 激活 `.venv` 之后，`python` 指向的是系统 Python 还是虚拟环境里的 Python？
3. 如何检查当前环境里 `pandas` 和 `matplotlib` 是否安装成功？
4. 如果重新打开一个终端，为什么需要再次运行 `source .venv/bin/activate`？
