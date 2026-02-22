"""工具模块包。

在此目录下添加独立的工具模块文件，例如 `example.py`、`csv_cleaner.py` 等。
每个模块可以选择以下两种方式之一来接入主 CLI：

1) 定义 `register_subparser(subparsers)`，完全自定义子命令。
2) 同时定义 `add_arguments(parser)` 与 `run(args)`，按约定接入，子命令名为模块名。
"""



