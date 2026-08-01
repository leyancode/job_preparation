# Bash 问题记录

这份笔记用来记录学习 benchmark 脚本时遇到的 Bash 语法问题。
说明以中文为主，同时保留关键英文术语，方便以后查资料时能对应上。

## 问题 1: `"${...}"` 是什么？

在 Bash 里，`${...}` 叫做 parameter expansion，也就是“参数展开”或“变量展开”。
它的作用是让 Bash 取出变量或特殊参数的值。

最基本的例子：

```bash
name="Leyan"
echo "${name}"
```

输出：

```text
Leyan
```

为什么要加花括号 `{}`？

- 明确告诉 Bash：变量名到哪里结束
- 方便变量后面直接拼接字符串

例如：

```bash
PETSC_ARCH="arch-omp-opt"
echo "build_${PETSC_ARCH}_log"
```

这里如果写成 `"$PETSC_ARCH_log"`，Bash 会把它当成另一个变量
`PETSC_ARCH_log`，而不是 `PETSC_ARCH` 加上 `_log`。

为什么外面还要加双引号 `""`？

- 防止变量里的空格被拆成多个参数
- 防止变量内容被当成通配符再展开

更安全的习惯：

```bash
cd "${PROJECT_ROOT}"
```

不太安全的写法：

```bash
cd $PROJECT_ROOT
```

## 问题 2: `${RANKS:-1 2 4 8}` 里的 `:-` 是什么？

这是 parameter expansion 里很常见的一种 default value 语法。

```bash
RANKS="${RANKS:-1 2 4 8 16 32 64 128}"
```

意思是：

- 如果 `RANKS` 已经有值，而且不是空字符串，就用它自己的值
- 如果 `RANKS` 没设置，或者值为空，就改用后面的默认值

例子 1：`RANKS` 没设置

```bash
unset RANKS
echo "${RANKS:-1 2 4}"
```

输出：

```text
1 2 4
```

例子 2：`RANKS` 已经有值

```bash
RANKS="2 8 32"
echo "${RANKS:-1 2 4}"
```

输出：

```text
2 8 32
```

这也是为什么 Slurm 脚本喜欢用它：脚本可以提供一个安全默认值，
但提交作业时也允许用户 override，也就是“覆盖默认值”。

ARCHER2 例子：

```bash
RANKS="8 16 32" sbatch scripts/run_ex2_size_grid.sbatch
```

## 问题 3: 这里的 `-` 是不是“设值”？

不是。`:-` 本身不是“设值命令”，它只是一个“如果为空就用默认值”的展开规则。

看这行：

```bash
RANKS="${RANKS:-1 2 4 8 16 32 64 128}"
```

真正发生的事情分两层：

1. `${RANKS:-...}` 先决定“本次应该展开成什么文本”
2. 外层的 `RANKS="..."` 再把这个结果赋值给 `RANKS`

所以：

- `:-` 负责“选择值”
- `=` 负责“写回变量”

## 问题 4: 这两种写法有什么区别？

保留默认值、允许覆盖：

```bash
RANKS="${RANKS:-1 2 4 8 16 32 64 128}"
```

直接写死赋值：

```bash
RANKS="1 2 4 8 16 32 64 128"
```

区别是：

- 第一种会保留用户提前提供的值
- 第二种无条件覆盖原来的值

例子：

```bash
RANKS="8 16"
RANKS="${RANKS:-1 2 4}"
echo "${RANKS}"
```

输出：

```text
8 16
```

但是如果写成：

```bash
RANKS="8 16"
RANKS="1 2 4"
echo "${RANKS}"
```

输出：

```text
1 2 4
```

## 问题 5: 为什么 `RANKS="${1 2 4 8}"` 是错的？

因为这不是合法的 Bash parameter expansion 语法。

```bash
RANKS="${1 2 4 8}"
```

`${...}` 里面必须放一个合法的参数表达式，比如：

- `${RANKS}`：普通变量
- `${1}`：第一个 positional parameter，也就是第一个位置参数
- `${RANKS:-default}`：带默认值的展开

但 `${1 2 4 8}` 里面不是一个合法表达式，所以 Bash 会报
`bad substitution`。

如果你只是想写一串普通字符串，应该这样写：

```bash
RANKS="1 2 4 8"
```

## 问题 6: `${x:-v}` 和 `${x-v}` 有什么区别？

这两个很像，但它们对 empty string，也就是空字符串，处理不同。

```bash
${x:-v}
```

意思：

- 如果 `x` 没设置，用 `v`
- 如果 `x` 已设置但为空，也用 `v`

```bash
${x-v}
```

意思：

- 只有当 `x` 没设置时，才用 `v`
- 如果 `x=""`，那就保留空字符串

例子：

```bash
x=""
printf '<%s>\n' "${x:-fallback}"
printf '<%s>\n' "${x-fallback}"
```

输出：

```text
<fallback>
<>
```

对于学习脚本来说，`:-` 往往更安全，因为“空值”通常也表示“没有提供有效输入”。

## 问题 7: `${x:=v}` 是什么？

这个写法比 `:-` 更进一步：它不只是临时使用默认值，还会把默认值真的写回变量。

```bash
unset x
echo "${x:=fallback}"
echo "${x}"
```

输出：

```text
fallback
fallback
```

意思是：

- 如果 `x` 没设置或为空，就把 `fallback` 赋值给 `x`
- 然后展开成这个值

它和 `${x:-v}` 的区别是：

- `${x:-v}`：只是在这一次展开时用默认值，不一定改变量本身
- `${x:=v}`：会真的修改变量

## 问题 8: `read` 是怎么用的？

`read` 是 Bash 的 built-in command，也就是 Bash 内建命令。
它的作用是：从输入里读一行内容，然后放进变量里。

最简单的例子：

```bash
read name
echo "${name}"
```

如果你输入：

```text
Leyan
```

那么 `name` 就会保存 `Leyan`。

### 8.1 `read` 的基本形式

```bash
read var1 var2 var3
```

意思是：从一行输入中读取内容，按分隔符拆开后分别放进多个变量。

例如：

```bash
echo "red blue green" | read a b c
```

概念上它想做的是：

- `a="red"`
- `b="blue"`
- `c="green"`

不过在 Bash 里，通过 pipe 给 `read` 传值时有 subshell 细节，
初学时先更推荐看脚本里的写法。

如果想在 `read` 之后查看变量值，应该分别展开：

```bash
echo "${a}"
echo "${b}"
echo "${c}"
```

或者一次打印：

```bash
echo "${a} ${b} ${c}"
```

下面这种写法是错的：

```bash
echo "${a b c}"
```

因为 `${...}` 里面一次只能写一个合法的 parameter expansion。
例如 `${a}`、`${b}`、`${x:-default}` 都对，但 `${a b c}` 不对。

### 8.1.1 为什么 `echo "red blue green" | read a b c` 不推荐初学时使用？

因为管道 `|` 右边的 `read` 往往运行在 subshell 里。
`read` 在那个子 shell 里确实能读到值，但命令结束后，外层 shell
不一定还能看到 `a`、`b`、`c`。

学习时更推荐这样写：

```bash
read a b c <<< "red blue green"
echo "${a}"
echo "${b}"
echo "${c}"
```

这里 `<<<` 是 here-string，会把右边的文本直接喂给 `read`。
这样变量就留在当前 shell 里，更容易观察结果。

### 8.2 脚本里的 `read -r`

你脚本里常见的是：

```bash
read -r SCALE M N UNKNOWNS
```

其中 `-r` 的意思是：

- 不要把反斜杠 `\` 当成转义符处理

这通常是更安全的默认习惯，所以教程和正式脚本里常写 `read -r`。

### 8.3 `IFS=, read -r ...` 是什么？

在这个脚本里：

```bash
while IFS=, read -r SCALE M N UNKNOWNS; do
```

这里有三层含义：

1. `IFS=,`
   把 field separator，也就是字段分隔符，临时设成逗号
2. `read -r SCALE M N UNKNOWNS`
   从当前这一行中读取 4 个字段
3. `while ...; do`
   对文件中的每一行都重复这件事

如果一行 CSV 是：

```text
small,1000,1000,1000000
```

那么这一行读进来后：

- `SCALE="small"`
- `M="1000"`
- `N="1000"`
- `UNKNOWNS="1000000"`

### 8.4 `read -r -a RANKS_LIST <<< "${RANKS}"` 是什么？

这是你当前脚本里另一句很关键的话：

```bash
read -r -a RANKS_LIST <<< "${RANKS}"
```

可以拆成 3 部分理解。

第一部分，`-a RANKS_LIST`

- `-a` 表示读入 array，也就是数组
- `RANKS_LIST` 是数组名

第二部分，`<<< "${RANKS}"`

- `<<<` 叫 here-string
- 它会把右边这段文本当成一小段输入，喂给 `read`

第三部分，整体效果

如果：

```bash
RANKS="1 2 4 8"
```

那么执行后：

```bash
read -r -a RANKS_LIST <<< "${RANKS}"
```

就相当于把字符串 `"1 2 4 8"` 按默认空白分隔，读成数组：

```bash
RANKS_LIST[0]="1"
RANKS_LIST[1]="2"
RANKS_LIST[2]="4"
RANKS_LIST[3]="8"
```

这也是为什么后面脚本可以这样循环：

```bash
for R in "${RANKS_LIST[@]}"; do
```

因为 `RANKS_LIST` 已经不是一个普通字符串，而是一个数组了。

### 8.5 为什么不直接 `for R in ${RANKS}`？

两种写法都能跑，但转成数组更清晰，也更方便后面统一处理：

```bash
read -r -a RANKS_LIST <<< "${RANKS}"
read -r -a THREADS_LIST <<< "${THREADS}"
```

这样脚本结构会更对称：

- 一个字符串变量保存用户输入
- 一个数组变量保存拆分后的结果

这对学习也更好，因为你能清楚区分：

- `RANKS` 是原始文本
- `RANKS_LIST` 是可迭代的数组

## 问题 9: 为什么 `echo "${a}"`、`echo ${a}`、`echo $a` 看起来一样？

如果变量值很简单，比如：

```bash
a="red"
```

那么下面三句通常都会显示同样的结果：

```bash
echo "${a}"
echo ${a}
echo $a
```

这是因为：

- 变量里没有空格
- 没有通配符
- 不是空字符串
- `echo` 又会把参数重新用空格打印出来

所以表面上看不出区别。

但它们并不总是等价。差别通常出现在 Bash 把变量展开成“几个参数”时。

例如：

```bash
a="red blue"
printf '[%s]\n' ${a}
printf '[%s]\n' "${a}"
```

输出：

```text
[red]
[blue]
[red blue]
```

这里可以看出：

- `${a}` 会发生 word splitting，也就是按空白拆成多个参数
- `"${a}"` 会把整个值保留成一个参数

所以更安全的默认习惯仍然是：

```bash
echo "${a}"
```

而不是：

```bash
echo $a
```

### 9.1 为什么在 `echo` 里很难看出区别？

例如：

```bash
a="red blue"
echo ${a}
echo "${a}"
```

显示结果都可能是：

```text
red blue
```

但内部其实不同：

- `echo ${a}` 可能拿到了两个参数：`red` 和 `blue`
- `echo "${a}"` 拿到的是一个参数：`red blue`

只是 `echo` 恰好把它们又打印成了一行，所以差别被遮住了。

### 9.2 用 `for` 看差别更明显

```bash
a="red blue"
for x in ${a}; do
  printf '<%s>\n' "${x}"
done
```

输出：

```text
<red>
<blue>
```

而：

```bash
a="red blue"
for x in "${a}"; do
  printf '<%s>\n' "${x}"
done
```

输出：

```text
<red blue>
```

这说明不加引号时，Bash 会把字符串拆词；加了引号后，会把它当成一个整体。

## 问题 10: `ts() { date -Iseconds; }` 是什么？

这里的 `ts` 是脚本作者自己定义的函数名，不是 Bash 关键字。

```bash
ts() { date -Iseconds; }
```

意思是：

- 定义一个叫 `ts` 的函数
- 每次调用 `ts` 时，就执行 `date -Iseconds`

可以把 `ts` 理解成 `timestamp` 的缩写。

例如：

```bash
ts
```

可能输出：

```text
2026-06-15T14:23:10+01:00
```

### 10.1 为什么这里不用 `${}`？

因为这里没有在“展开变量”，而是在“执行命令”。

例如这句里：

```bash
date -Iseconds
```

- `date` 是命令名
- `-Iseconds` 是命令选项

`${...}` 只在变量展开或 parameter expansion 时使用，例如：

```bash
echo "${SCALE}"
echo "${RANKS:-1 2 4}"
```

### 10.2 `$(ts)` 又是什么？

如果脚本里有：

```bash
echo "[RUN] $(ts) scale=${SCALE}"
```

其中 `$(ts)` 叫 command substitution，也就是“命令替换”。

意思是：

- 先执行函数 `ts`
- 把它的输出结果插入当前位置

所以这句并不是在取变量 `ts`，而是在调用函数并取它的输出。

## 问题 11: 为什么 `for scale in ${SCALES}; do` 可以直接用字符串？

因为 Bash 的 `for ... in ...` 本来就可以遍历一串由空白分隔的单词。

如果：

```bash
SCALES="small medium large"
```

那么：

```bash
for scale in ${SCALES}; do
  echo "${scale}"
done
```

展开后可以近似理解成：

```bash
for scale in small medium large; do
```

所以循环会依次得到：

- `scale="small"`
- `scale="medium"`
- `scale="large"`

### 11.1 为什么这里反而不能随便加双引号？

如果你写成：

```bash
for scale in "${SCALES}"; do
```

那么整个字符串会被当成一个整体，只循环一次：

- `scale="small medium large"`

这和脚本原意不同。

所以这里是“故意利用 word splitting”把一个字符串拆成多个项目。

### 11.2 那为什么 `RANKS` 和 `THREADS` 还要转成数组？

脚本里有：

```bash
read -r -a RANKS_LIST <<< "${RANKS}"
read -r -a THREADS_LIST <<< "${THREADS}"
```

这样做的好处是更清晰：

- `RANKS`、`THREADS` 是原始字符串
- `RANKS_LIST`、`THREADS_LIST` 是拆分后的数组

后面再写：

```bash
for R in "${RANKS_LIST[@]}"; do
```

语义就更明确。

## 问题 12: `if [[ ! -f "${SIZE_TABLE}" ]]; then` 是什么意思？

这句的意思是：

```bash
if [[ ! -f "${SIZE_TABLE}" ]]; then
```

中文可读成：

如果 `SIZE_TABLE` 这个路径不是一个存在的普通文件，就执行 `then`
后面的代码。

拆开看：

- `if`：开始条件判断
- `[[ ... ]]`：条件测试
- `-f`：判断“这个路径是否是普通文件”
- `!`：取反，表示“不是”

所以：

```bash
-f "${SIZE_TABLE}"
```

表示：

- 文件存在
- 并且它是普通文件，不是目录

再加上 `!`：

```bash
! -f "${SIZE_TABLE}"
```

就变成：

- 文件不存在，或者不是普通文件

### 12.1 为什么要用两个 `[` 号？

Bash 里常见两种测试写法：

```bash
[ ... ]
[[ ... ]]
```

其中：

- `[ ... ]` 是较老的 `test` 风格
- `[[ ... ]]` 是 Bash 提供的更现代的条件判断语法

在 Bash 脚本里，`[[ ... ]]` 通常更稳妥，因为：

- 语法更清晰
- 处理字符串和变量时更安全
- 写复杂条件时更不容易出错

对当前脚本来说，你可以先把它简单记成：

```bash
[[ 条件 ]]
```

就是 Bash 的“判断框”。

### 12.2 这个判断在脚本里的作用是什么？

`SIZE_TABLE` 指向问题规模 CSV 文件。
脚本在真正运行 benchmark 之前，先检查这个文件是否存在。

如果不存在，后面这类操作就都会失败：

- 读取 CSV
- 解析 `scale,m,n,unknowns`
- 生成不同规模的实验配置

所以这里先报错退出，是一种很正常的防御式检查。

## 快速总结

```bash
${x}      # 展开变量 x
${x:-v}   # 如果 x 未设置或为空，就用 v
${x-v}    # 如果 x 未设置，就用 v
${x:=v}   # 如果 x 未设置或为空，就把 v 赋给 x 再使用
read x    # 读一行到变量 x
read -r   # 读取时不解释反斜杠
read -a   # 读成数组
IFS=,     # 临时把字段分隔符设成逗号
<<< text  # 把一小段文本作为输入喂给命令
```

## WSL 练习命令

从仓库根目录运行：

```bash
cd ~/leyan/jobSkill/petsc-benchmark-suite/s2795693
```

查看这份笔记：

```bash
sed -n '1,260p' tutorial/BASH_QUESTION_LOG.md
```

练习默认值展开：

```bash
bash -c 'unset x; echo "${x:-fallback}"; x=""; echo "${x:-fallback}"; echo "${x-fallback}"'
```

练习 `read` 和数组：

```bash
bash -c 'RANKS="1 2 4 8"; read -r -a arr <<< "${RANKS}"; printf "%s\n" "${arr[@]}"'
```

## 和当前 Slurm 脚本的关系

在 `scripts/run_ex2_size_grid.sbatch` 里，这些语法的作用分别是：

- 用 `${...}` 安全展开变量
- 用 `:-` 给 `SCALES`、`RANKS`、`THREADS` 等变量提供默认值
- 用 `read -r -a` 把 `"1 2 4 8"` 这种字符串转成数组
- 用 `IFS=, read -r ...` 一行一行读取 CSV 文件

这样脚本既能保持默认配置，也能在提交作业时灵活覆盖参数。
