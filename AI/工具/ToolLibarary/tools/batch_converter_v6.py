# -----------------------------------------------------------------------------
# Batch Excel to CSV Converter (v6.0 - Final Optimized)
# Author: AI聊天机器人
# Current Time: Wed Jul 23 12:42:20 CST 2025
# -----------------------------------------------------------------------------

import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import pandas as pd
import os
import threading
import json
from typing import List, Tuple

def excel_to_csv(input_file_path: str, output_file_path: str, size: int | None = None) -> str:
    """
    读取 Excel 文件（首个工作表）并导出为 CSV。

    参数:
    - input_file_path: 输入 Excel 文件路径 (.xlsx/.xls)
    - output_file_path: 输出 CSV 文件路径
    - size: 可选，限制导出的最大行数（不含表头）；为 None 时不限制

    返回:
    - 写出的 CSV 文件路径（与 output_file_path 相同）
    """
    if not os.path.isfile(input_file_path):
        raise FileNotFoundError(f"Excel 文件不存在: {input_file_path}")

    # 读取 Excel（默认第一个工作表）
    df = pd.read_excel(input_file_path)

    # 可选行数限制
    if size is not None:
        if not isinstance(size, int) or size < 0:
            raise ValueError("size 必须是非负整数或 None")
        if size > 0:
            df = df.head(size)

    # 确保输出目录存在
    output_dir = os.path.dirname(output_file_path) or "."
    os.makedirs(output_dir, exist_ok=True)

    # 写出 CSV，使用 UTF-8-SIG 以便在 Excel 中显示中文
    df.to_csv(output_file_path, index=False, encoding='utf-8-sig')

    return output_file_path

class ExcelBatchConverterApp:
    """
    一个功能完备的批量Excel转CSV工具，具备以下特性：
    - 扫描指定目录及子目录下的所有Excel文件。
    - 批量转换并保持原始目录结构。
    - 记忆上次使用的源/目标目录。
    - 提供快捷按钮直接打开源/目标目录。
    - 文件列表默认不选中，且每行提供独立的“打开”按钮。
    """
    def __init__(self, root):
        self.root = root
        self.root.title("批量 Excel 转 CSV 转换器 v6.0")
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

        ttk.Label(main_frame, text="源目录:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        ttk.Entry(main_frame, textvariable=self.source_dir, width=60).grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        ttk.Button(main_frame, text="选择...", command=self.select_source_dir).grid(row=0, column=2, padx=5, pady=5)
        ttk.Button(main_frame, text="打开", command=lambda: self.open_path_in_explorer(self.source_dir.get())).grid(row=0, column=3, padx=5, pady=5)

        ttk.Label(main_frame, text="目标目录:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        ttk.Entry(main_frame, textvariable=self.target_dir, width=60).grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        ttk.Button(main_frame, text="选择...", command=self.select_target_dir).grid(row=1, column=2, padx=5, pady=5)
        ttk.Button(main_frame, text="打开", command=lambda: self.open_path_in_explorer(self.target_dir.get())).grid(row=1, column=3, padx=5, pady=5)

        list_frame = ttk.LabelFrame(main_frame, text="检测到的 Excel 文件 (请勾选需要转换的文件)", padding="10")
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

        action_frame = ttk.Frame(main_frame)
        action_frame.grid(row=3, column=0, columnspan=4, pady=5, sticky="ew")
        
        ttk.Button(action_frame, text="扫描文件", command=self.scan_files).pack(side="left", padx=5)
        ttk.Button(action_frame, text="全选", command=self.select_all).pack(side="left", padx=5)
        ttk.Button(action_frame, text="取消全选", command=self.deselect_all).pack(side="left", padx=5)
        
        self.convert_button = ttk.Button(action_frame, text="开始转换", command=self.start_conversion_thread, style="Accent.TButton")
        self.convert_button.pack(side="right", padx=10)
        style = ttk.Style()
        style.configure("Accent.TButton", foreground="white", background="blue")

        status_frame = ttk.Frame(main_frame)
        status_frame.grid(row=4, column=0, columnspan=4, sticky="ew", padx=5, pady=5)
        status_frame.grid_columnconfigure(0, weight=1)
        self.status_label = ttk.Label(status_frame, text="正在加载配置...")
        self.status_label.grid(row=0, column=0, sticky="w")
        self.progress = ttk.Progressbar(status_frame, orient="horizontal", mode="determinate")
        self.progress.grid(row=1, column=0, columnspan=2, sticky="ew")

        self.load_settings()
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def open_path_in_explorer(self, path):
        if not path or not os.path.isdir(path):
            messagebox.showwarning("路径无效", f"目录不存在或无效:\n{path}")
            return
        try:
            os.startfile(path)
        except Exception as e:
            messagebox.showerror("错误", f"无法打开目录: {e}")

    # --- 修改：函数名和功能简化，直接打开传入的文件路径 ---
    def open_file(self, file_path):
        """用默认程序打开指定的文件。"""
        if not os.path.isfile(file_path):
            messagebox.showerror("文件不存在", f"文件已不存在或被移动:\n{file_path}")
            return
        try:
            os.startfile(file_path)
        except Exception as e:
            messagebox.showerror("打开失败", f"无法打开文件: {e}")

    # --- 修改：扫描文件的核心逻辑 ---
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
                    relative_path = os.path.relpath(full_path, src_dir)
                    found_files.append((relative_path, full_path))
        found_files.sort()
        
        if not found_files:
            self.status_label.config(text="在源目录中未找到任何 Excel 文件。")
            return
            
        # --- 核心修改点在这里 ---
        for relative_path, full_path in found_files:
            # 为每一行创建一个容器 Frame
            row_frame = ttk.Frame(self.checkbox_frame)
            row_frame.pack(fill='x', expand=True, pady=1)

            # 1. 默认不选中
            var = tk.BooleanVar(value=False)
            
            # 创建复选框，并放入行容器中，靠左显示
            cb = ttk.Checkbutton(row_frame, text=relative_path, variable=var)
            cb.pack(side="left", padx=(10, 5), fill='x', expand=True)
            
            # 2. 创建“打开”按钮，并放入行容器中，靠右显示
            # 使用 lambda p=full_path 来正确捕获每次循环中的文件路径
            open_btn = ttk.Button(row_frame, text="打开", width=8, command=lambda p=full_path: self.open_file(p))
            open_btn.pack(side="right", padx=(5, 10))

            self.file_checkboxes.append((var, full_path))
        
        self.status_label.config(text=f"扫描完成！发现 {len(self.file_checkboxes)} 个文件。请勾选需要转换的项。")

    # --- 以下是之前版本已有的函数，无需修改 ---
    def load_settings(self):
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    if os.path.isdir(settings.get("source_dir", "")):
                        self.source_dir.set(settings.get("source_dir", ""))
                    if os.path.isdir(settings.get("target_dir", "")):
                        self.target_dir.set(settings.get("target_dir", ""))
                self.status_label.config(text="配置已加载。请选择目录并扫描文件。")
            else:
                self.status_label.config(text="未找到配置文件。请选择目录并扫描文件。")
        except (json.JSONDecodeError, IOError) as e:
            self.status_label.config(text=f"加载配置失败: {e}")

    def save_settings(self):
        try:
            os.makedirs(self.config_dir, exist_ok=True)
            settings = {
                "source_dir": self.source_dir.get(),
                "target_dir": self.target_dir.get()
            }
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=4)
        except IOError as e:
            print(f"保存配置失败: {e}")

    def on_closing(self):
        self.save_settings()
        self.root.destroy()

    def on_frame_configure(self, event=None):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def on_canvas_configure(self, event):
        self.canvas.itemconfig(self.canvas_window, width=event.width)

    def select_dir(self, var_to_set):
        initial_dir = var_to_set.get() if var_to_set.get() else os.path.expanduser('~')
        dir_path = filedialog.askdirectory(title="请选择一个目录", initialdir=initial_dir)
        if dir_path:
            var_to_set.set(dir_path)

    def select_source_dir(self):
        self.select_dir(self.source_dir)

    def select_target_dir(self):
        self.select_dir(self.target_dir)

    def select_all(self):
        for var, _ in self.file_checkboxes:
            var.set(True)

    def deselect_all(self):
        for var, _ in self.file_checkboxes:
            var.set(False)

    def start_conversion_thread(self):
        src_dir = self.source_dir.get()
        tgt_dir = self.target_dir.get()
        if not src_dir or not tgt_dir:
            messagebox.showerror("错误", "源目录和目标目录都必须选择！")
            return
        files_to_convert = [path for var, path in self.file_checkboxes if var.get()]
        if not files_to_convert:
            messagebox.showwarning("提示", "没有选择任何文件进行转换。")
            return
        self.convert_button.config(state="disabled")
        self.progress['value'] = 0
        thread = threading.Thread(target=self.batch_convert, args=(files_to_convert, src_dir, tgt_dir))
        thread.daemon = True
        thread.start()

    def batch_convert(self, files_to_convert, src_dir, tgt_dir):
        total_files = len(files_to_convert)
        self.progress['maximum'] = total_files
        for i, src_path in enumerate(files_to_convert):
            try:
                relative_path = os.path.relpath(os.path.dirname(src_path), src_dir)
                target_sub_dir = os.path.join(tgt_dir, relative_path)
                base_name = os.path.basename(src_path)
                file_name_without_ext = os.path.splitext(base_name)[0]
                target_csv_path = os.path.join(target_sub_dir, f"{file_name_without_ext}.csv")
                os.makedirs(target_sub_dir, exist_ok=True)
                self.status_label.config(text=f"正在转换 ({i+1}/{total_files}): {os.path.basename(src_path)}")
                df = pd.read_excel(src_path)
                df.to_csv(target_csv_path, index=False, encoding='utf-8-sig')
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("转换错误", f"转换文件失败: {src_path}\n错误: {e}"))
            self.progress['value'] = i + 1
        self.status_label.config(text=f"转换完成！共处理 {total_files} 个文件。")
        self.convert_button.config(state="normal")
        self.root.after(0, lambda: messagebox.showinfo("成功", f"所有选中的文件已成功转换！"))

def run_gui() -> None:
    """启动 Batch Converter GUI。"""
    root = tk.Tk()
    app = ExcelBatchConverterApp(root)
    root.mainloop()