"""图形主界面启动器：提供一个窗口选择要启动的工具。"""

import argparse
import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox
import webbrowser

from . import batch_converter_v6 as bc
from . import language_tool as lt


def register_subparser(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser(
        "ui-gui",
        help="打开图形主界面 (选择运行 batch_converter 或 blank_tool)",
        description="以窗口的方式选择并启动各工具。",
    )
    parser.set_defaults(func=lambda _args: run_gui_menu())


def run_gui_menu() -> int:
    root = tk.Tk()
    root.title("工具启动主界面")
    root.geometry("560x340")
    root.minsize(520, 300)

    # 菜单栏
    menubar = tk.Menu(root)
    file_menu = tk.Menu(menubar, tearoff=0)
    file_menu.add_command(label="退出", command=root.destroy)
    menubar.add_cascade(label="文件", menu=file_menu)

    help_menu = tk.Menu(menubar, tearoff=0)
    help_menu.add_command(label="打开 README", command=_open_readme)
    menubar.add_cascade(label="帮助", menu=help_menu)
    root.config(menu=menubar)

    main = ttk.Frame(root, padding=16)
    main.pack(fill=tk.BOTH, expand=True)
    main.grid_columnconfigure(0, weight=1)

    # 头部
    title = ttk.Label(main, text="Python 工具启动器", font=("Segoe UI", 16, "bold"))
    title.grid(row=0, column=0, pady=(0, 4), sticky="n")
    subtitle = ttk.Label(main, text="请选择要启动的工具，或从菜单查看帮助", foreground="#555")
    subtitle.grid(row=1, column=0, pady=(0, 12), sticky="n")

    # 工具卡片区域
    cards = ttk.Frame(main)
    cards.grid(row=2, column=0, sticky="nsew")
    for c in (0, 1):
        cards.grid_columnconfigure(c, weight=1)

    # Batch Converter 卡片
    bc_frame = ttk.Labelframe(cards, text="Batch Converter", padding=12)
    bc_frame.grid(row=0, column=0, padx=(0, 8), sticky="nsew")
    ttk.Label(bc_frame, text="批量 Excel→CSV 转换，保持目录结构", wraplength=220).pack(anchor="w")
    ttk.Button(bc_frame, text="启动 (2)", command=lambda: _launch_tool(root, bc.run_gui)).pack(pady=10, fill="x")

    # Language Tool 卡片
    lt_frame = ttk.Labelframe(cards, text="Language Tool", padding=12)
    lt_frame.grid(row=0, column=1, padx=(8, 0), sticky="nsew")
    ttk.Label(lt_frame, text="多语言导出原型：按配置聚合并导出 CSV", wraplength=220).pack(anchor="w")
    ttk.Button(lt_frame, text="启动 (1)", command=lambda: _launch_tool(root, lt.run_gui)).pack(pady=10, fill="x")

    # 底部操作
    footer = ttk.Frame(main)
    footer.grid(row=3, column=0, sticky="ew", pady=(12, 0))
    footer.grid_columnconfigure(0, weight=1)
    ttk.Button(footer, text="退出", command=root.destroy).grid(row=0, column=1, sticky="e")

    # 快捷键
    root.bind("1", lambda _e: _launch_tool(root, lt.run_gui))
    root.bind("<Escape>", lambda _e: root.destroy())

    root.mainloop()
    return 0


def _launch_tool(root: tk.Tk, run_callable) -> None:
    """隐藏主界面，启动工具；工具关闭后返回主界面。"""
    try:
        root.withdraw()
        run_callable()
    except Exception as exc:  # 兜底错误弹窗
        messagebox.showerror("启动失败", f"启动工具时发生错误:\n{exc}")
    finally:
        root.deiconify()


def _open_readme() -> None:
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
    readme_path = os.path.join(repo_root, "README.md")
    if not os.path.exists(readme_path):
        messagebox.showinfo("提示", "未找到 README.md")
        return
    try:
        if sys.platform.startswith("win"):
            os.startfile(readme_path)  # type: ignore[attr-defined]
        elif sys.platform == "darwin":
            os.spawnlp(os.P_NOWAIT, "open", "open", readme_path)
        else:
            webbrowser.open_new_tab(f"file://{readme_path}")
    except Exception as exc:
        messagebox.showerror("打开失败", f"无法打开 README:\n{exc}")


