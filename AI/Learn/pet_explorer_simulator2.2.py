# -----------------------------------------------------------------------------
# Batch Excel to CSV Converter with Shortcuts (v5.0 - Final)
# Author: AI聊天机器人
# Current Time: Wed Jul 23 12:34:07 CST 2025
# -----------------------------------------------------------------------------

import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import pandas as pd
import os
import threading
import json
from typing import List, Tuple

class ExcelBatchConverterApp:
    """
    一个功能完备的批量Excel转CSV工具，具备以下特性：
    - 扫描指定目录及子目录下的所有Excel文件。
    - 批量转换并保持原始目录结构。
    - 记忆上次使用的源/目标目录。
    - 提供快捷按钮直接打开源/目标目录和选中的Excel文件。
    """
    def __init__(self, root):
        self.root = root
        self.root.title("批量 Excel 转 CSV 转换器 v5.0")
        # 稍微加宽窗口以容纳新按钮
        self.root.geometry("750x600")
        self.root.minsize(650, 500)

        self.config_dir = os.path.join(os.path.expanduser('~'), '.batch_converter')
        self.config_file = os.path.join(self.config_dir, 'config.json')

        self.source_dir = tk.StringVar()
        self.target_dir = tk.StringVar()
        self.file_checkboxes: List[Tuple[tk.BooleanVar, str]] = []

        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        main_frame.grid_rowconfigure(2, weight=1)
        main_frame.grid_columnconfigure(1, weight=1)

        # --- 目录选择 (UI调整以容纳新按钮) ---
        ttk.Label(main_frame, text="源目录:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        ttk.Entry(main_frame, textvariable=self.source_dir, width=60).grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        ttk.Button(main_frame, text="选择...", command=self.select_source_dir).grid(row=0, column=2, padx=5, pady=5)
        # 新增：打开源目录按钮
        ttk.Button(main_frame, text="打开", command=lambda: self.open_path_in_explorer(self.source_dir.get())).grid(row=0, column=3, padx=5, pady=5)

        ttk.Label(main_frame, text="目标目录:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        ttk.Entry(main_frame, textvariable=self.target_dir, width=60).grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        ttk.Button(main_frame, text="选择...", command=self.select_target_dir).grid(row=1, column=2, padx=5, pady=5)
        # 新增：打开目标目录按钮
        ttk.Button(main_frame, text="打开", command=lambda: self.open_path_in_explorer(self.target_dir.get())).grid(row=1, column=3, padx=5, pady=5)

        # --- 文件列表 (与之前相同) ---
        list_frame = ttk.LabelFrame(main_frame, text="检测到的 Excel 文件", padding="10")
        list_frame.grid(row=2, column=0, columnspan=4, padx=5, pady=10, sticky="nsew")
        list_frame.grid_rowconfigure(0, weight=1)
        list_frame.grid_columnconfigure(0, weight=1)

        self.canvas = tk.Canvas(list_frame, borderwidth=0)
        self.checkbox_frame = ttk.Frame(self.canvas)
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.canvas_window = self.canvas.create_window((0, 0), window=self.checkbox_frame, anchor="nw")
        self.checkbox_frame.bind("<Configure>", self.on_frame_configure)
        self.canvas.bind("<Configure>", self.on_canvas_configure)

        # --- 操作按钮 (UI调整) ---
        action_frame = ttk.Frame(main_frame)
        action_frame.grid(row=3, column=0, columnspan=4, pady=5, sticky="ew")
        
        ttk.Button(action_frame, text="扫描文件", command=self.scan_files).pack(side="left", padx=5)
        ttk.Button(action_frame, text="全选", command=self.select_all).pack(side="left", padx=5)
        ttk.Button(action_frame, text="取消全选", command=self.deselect_all).pack(side="left", padx=5)
        # 新增：打开选中Excel文件按钮
        self.open_excel_button = ttk.Button(action_frame, text="打开选中Excel", command=self.open_selected_excel, state="disabled")
        self.open_excel_button.pack(side="left", padx=15)
        
        self.convert_button = ttk.Button(action_frame, text="开始转换", command=self.start_conversion_thread, style="Accent.TButton")
        self.convert_button.pack(side="right", padx=10)
        style = ttk.Style()
        style.configure("Accent.TButton", foreground="white", background="blue")

        # --- 状态和进度条 (与之前相同) ---
        status_frame = ttk.Frame(main_frame)
        status_frame.grid(row=4, column=0, columnspan=4, sticky="ew", padx=5, pady=5)
        status_frame.grid_columnconfigure(0, weight=1)
        self.status_label = ttk.Label(status_frame, text="正在加载配置...")
        self.status_label.grid(row=0, column=0, sticky="w")
        self.progress = ttk.Progressbar(status_frame, orient="horizontal", mode="determinate")
        self.progress.grid(row=1, column=0, columnspan=2, sticky="ew")

        self.load_settings()
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    # --- 新增：打开路径的函数 ---
    def open_path_in_explorer(self, path):
        """在系统的文件浏览器中打开指定的路径。"""
        if not path or not os.path.isdir(path):
            messagebox.showwarning("路径无效", f"目录不存在或无效:\n{path}")
            return
        try:
            # os.startfile 在 Windows 上表现最好，也能在某些Linux/macOS环境下工作
            os.startfile(path)
        except AttributeError:
            # 为 macOS 和 Linux 提供备用方案
            import subprocess
            try:
                subprocess.run(['open', path], check=True) # macOS
            except (FileNotFoundError, subprocess.CalledProcessError):
                try:
                    subprocess.run(['xdg-open', path], check=True) # Linux
                except (FileNotFoundError, subprocess.CalledProcessError):
                    messagebox.showerror("无法打开", "无法在您的操作系统上找到打开文件夹的命令。")
        except Exception as e:
            messagebox.showerror("错误", f"无法打开目录: {e}")

    # --- 新增：打开选中Excel文件的函数 ---
    def open_selected_excel(self):
        """用默认程序打开列表中第一个被选中的Excel文件。"""
        selected_file = None
        for var, path in self.file_checkboxes:
            if var.get():
                selected_file = path
                break # 找到第一个就停止

        if not selected_file:
            # 理论上按钮是禁用的，不会触发，但作为安全措施
            messagebox.showinfo("提示", "请先在列表中勾选一个文件。")
            return
        
        if not os.path.isfile(selected_file):
            messagebox.showerror("文件不存在", f"文件已不存在或被移动:\n{selected_file}")
            return

        try:
            os.startfile(selected_file)
        except Exception as e:
            messagebox.showerror("打开失败", f"无法打开文件: {e}")

    # --- 修改：扫描文件后更新按钮状态 ---
    def scan_files(self):
        src_dir = self.source_dir.get()
        if not src_dir or not os.path.isdir(src_dir):
            messagebox.showerror("错误", "源目录无效或未选择！")
            return
        for widget in self.checkbox_frame.winfo_children():
            widget.destroy()
        self.file_checkboxes.clear()
        found_files = []
        for root, _, files in os.walk(src_dir):
            for file in files:
                if file.lower().endswith(('.xlsx', '.xls')):
                    full_path = os.path.join(root, file)
                    relative