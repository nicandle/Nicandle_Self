## 工具集 (Python CLI + GUI)

一个可扩展的 Python 工具集，包含命令行入口与两个图形工具：`language_tool` 与 `batch_converter_v6`。主入口 `main.py` 会自动发现 `tools/` 目录中的工具并注册为子命令。

### 目录结构

```
.
├─ main.py              # 主入口，自动发现 tools 下的工具作为子命令
├─ tools/
│  ├─ __init__.py
│  ├─ language_tool.py  # 多语言导出/比对工具 + Excel→CSV 标准化
│  ├─ batch_converter_v6.py  # 批量 Excel→CSV 转换 GUI + 单文件转换 API
│  └─ launcher.py       # CLI 启动面板与快捷 GUI 子命令
├─ requirements.txt     # 依赖管理
└─ README.md            # 项目说明
```

### 安装

可选：创建虚拟环境

```powershell
python -m venv .venv
.\.venv\Scripts\activate
```

安装依赖

```powershell
pip install -r requirements.txt
```

依赖说明：
- `pandas` 负责读写 CSV/Excel
- `openpyxl` 负责 `.xlsx`
- `xlrd` 负责 `.xls`

### 用法总览（CLI）

```powershell
py main.py --help
```
常用子命令：
- `py main.py ui`：打开控制台启动面板（在菜单中选择要启动的 GUI）
- `py main.py language-gui`：直接启动 Language Tool GUI
- `py main.py batch-gui`：直接启动 Batch Converter GUI

如在非 Windows 环境，可将 `py` 改为 `python`。

### 工具一：language_tool

- GUI 启动：
  - `py main.py language-gui`
  - 或 `py main.py ui` 后在菜单中选择 1

- GUI 功能：
  - 流程 1：全量导出多语言（根据 `LanguageExport.csv` 配置汇总）
  - 流程 2：增量比对与导出（新旧版本差异）
  - 流程 3：Excel 转为标准 CSV（重命名前两列为 `key` 与 `Chinese Simplified`）

- Python API（用于脚本调用）：

```python
from tools.language_tool import lockey_tool

# 将 Excel 的第一个工作表转换为 CSV，并重命名前两列
lockey_tool(
    input_file_path=r"C:\path\in.xlsx",
    output_file_path=r"C:\path\out.csv",
    size=None,  # 可选：限制导出行数；None 表示不限制
)
```

参数说明：
- `input_file_path`：输入 Excel 路径（.xlsx/.xls）
- `output_file_path`：输出 CSV 路径
- `size`：可选，非负整数；限制导出行数（不含表头），`None` 为不限制

### 工具二：batch_converter_v6

- GUI 启动：
  - `py main.py batch-gui`
  - 或 `py main.py ui` 后在菜单中选择 2

- GUI 功能：
  - 扫描所选源目录与子目录中的 Excel 文件
  - 手动勾选需要转换的文件
  - 保持原目录结构输出至目标目录（转换为 CSV，UTF-8-SIG 编码）

- Python API（用于脚本调用单文件转换）：

```python
from tools.batch_converter_v6 import excel_to_csv

excel_to_csv(
    input_file_path=r"C:\path\in.xlsx",
    output_file_path=r"C:\path\out.csv",
    size=100,  # 可选：导出前 100 行
)
```

参数说明：
- `input_file_path`：输入 Excel 路径（.xlsx/.xls）
- `output_file_path`：输出 CSV 路径
- `size`：可选，非负整数；限制导出行数（不含表头），`None` 为不限制

### 扩展与自定义

在 `tools/` 下新增模块，可通过以下两种方式接入 CLI：
- 定义 `register_subparser(subparsers)`：完全自定义子命令和参数
- 或同时定义 `add_arguments(parser)` 与 `run(args)`：按约定接入，子命名为模块名

### 版本

当前版本：`0.1.0`


