"""CLI 子命令：提供一个带子菜单的主界面，用于启动各 GUI 工具。"""

import argparse

from . import batch_converter_v6 as bc
from . import language_tool as lt


def _register_menu_subparser(subparsers: argparse._SubParsersAction) -> None:
    menu = subparsers.add_parser(
        "ui",
        help="打开工具启动面板 (含 language_tool 与 batch_converter)",
        description="图形化启动面板：选择并启动内置 GUI 工具。",
    )
    menu.set_defaults(func=run_menu)


def register_subparser(subparsers: argparse._SubParsersAction) -> None:
    # 主菜单入口
    _register_menu_subparser(subparsers)

    bc_parser = subparsers.add_parser(
        "batch-gui",
        help="启动 batch_converter 的 GUI",
        description="启动 batch_converter 的 GUI 界面。",
    )
    bc_parser.set_defaults(func=lambda _args: bc.run_gui())

    # 注意：`blank-gui` 已由 `tools.blank_tool` 自行注册，这里不重复注册以避免冲突


def run_menu(_args: argparse.Namespace | None = None) -> int:
    """控制台菜单；工具关闭后返回菜单，直到用户退出。"""
    while True:
        print("================ 工具启动面板 ================")
        print("1) 启动 Language Tool 图形界面")
        print("2) 启动 Batch Converter 图形界面")
        print("q) 退出")
        print("=============================================")

        try:
            choice = input("请选择 (1/2/q): ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            return 1

        if choice == "1":
            lt.run_gui()
            continue
        if choice == "2":
            bc.run_gui()
            continue
        if choice == "q":
            return 0
        print("无效选择。")


