# -----------------------------------------------------------------------------
# Batch Excel to CSV Converter (v7.3 - Final with Auto-Path)
# Author: AI聊天机器人
# Current Time: Tue Sep 09 14:42:57 CST 2025
# -----------------------------------------------------------------------------

import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import pandas as pd
import os
import threading
import json
import sys
from typing import Dict
from datetime import datetime

class ExcelBatchConverterApp:
    """
    一个功能完备的批量Excel转CSV工具，具备以下特性：
    - (新) 首次运行可根据工具位置自动设置默认路径。
    - (新) 使用树状视图展示文件，并在文件名前显示复选框 ☐/☑。
    - (新) 显示文件最后修改时间，并支持点击列头排序。
    - 扫描指定目录及子目录下的所有Excel文件。
    - 批量转换并保持原始目录结构。
    - 记忆上次使用的源/目标目录。
    - 提供快捷按钮直接打开源/目标目录。
    - (新) 双击文件条目可直接打开文件。
    """
    def __init__(self, root):
        self.root = root
        self.root.title("批量 Excel 转 CSV 转换器 v7.3")
        self.root.geometry("850x650")
        self.root.minsize(700, 550)

        self.config_dir = os.path.join(os.path.expanduser('~'), '.batch_converter')
        self.config_file = os.path.join(self.config_dir, 'config.json')

        self.source_dir = tk.StringVar()
        self.target_dir = tk.StringVar()
        self.file_items: Dict[str, str] = {} 

        # --- 样式优化 ---
        style = ttk.Style()
        # 1. 使用 configure 强制设置默认前景色(文字)和背景色
        style.configure("Accent.TButton",
                        foreground="black",  # 按钮文字颜色设为黑色
                        background="dodgerblue",
                        font=('Helvetica', 10, 'bold'),
                        padding=(10, 5))
        # 2. 使用 map 来定义当按钮状态改变时的样式 (例如鼠标悬停)
        style.map("Accent.TButton",
                  background=[('active', 'mediumblue'), ('disabled', 'grey')])

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

        list_frame = ttk.LabelFrame(main_frame, text="检测到的 Excel 文件 (单击选择，双击打开)", padding="10")
        list_frame.grid(row=2, column=0, columnspan=4, padx=5, pady=10, sticky="nsew")
        list_frame.grid_rowconfigure(0, weight=1)
        list_frame.grid_columnconfigure(0, weight=1)

        self.tree = ttk.Treeview(list_frame, columns=("mtime",), show="tree headings")
        self.tree.heading("#0", text="文件路径")
        self.tree.heading("mtime", text="最后修改时间", command=lambda: self.sort_treeview_column("mtime", False))
        
        self.tree.column("#0", width=400, stretch=tk.YES)
        self.tree.column("mtime", width=150, anchor="center")

        scrollbar_y = ttk.Scrollbar(list_frame, orient="vertical", command=self.tree.yview)
        scrollbar_x = ttk.Scrollbar(list_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)
        
        scrollbar_y.grid(row=0, column=1, sticky="ns")
        scrollbar_x.grid(row=1, column=0, columnspan=2, sticky="ew")
        self.tree.grid(row=0, column=0, sticky="nsew")

        self.tree.bind("<Double-1>", self.on_tree_double_click)
        self.tree.bind("<Button-1>", self.on_tree_click)

        action_frame = ttk.Frame(main_frame)
        action_frame.grid(row=3, column=0, columnspan=4, pady=5, sticky="ew")
        
        ttk.Button(action_frame, text="扫描文件", command=self.scan_files).pack(side="left", padx=5)
        ttk.Button(action_frame, text="全选", command=self.select_all).pack(side="left", padx=5)
        ttk.Button(action_frame, text="取消全选", command=self.deselect_all).pack(side="left", padx=5)
        
        self.convert_button = ttk.Button(action_frame, text="开始转换", command=self.start_conversion_thread, style="Accent.TButton")
        self.convert_button.pack(side="right", padx=10)

        status_frame = ttk.Frame(main_frame)
        status_frame.grid(row=4, column=0, columnspan=4, sticky="ew", padx=5, pady=5)
        status_frame.grid_columnconfigure(0, weight=1)
        self.status_label = ttk.Label(status_frame, text="正在加载配置...")
        self.status_label.grid(row=0, column=0, sticky="w")
        self.progress = ttk.Progressbar(status_frame, orient="horizontal", mode="determinate")
        self.progress.grid(row=1, column=0, columnspan=2, sticky="ew")

        self.load_settings()
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def sort_treeview_column(self, col, reverse):
        # 仅对文件项进行排序，文件夹保持在原位
        file_items_data = []
        folder_items = []
        
        for item_id in self.tree.get_children(''):
            if item_id in self.file_items:
                file_items_data.append((self.tree.set(item_id, col), item_id))
            else: # 假设不是文件就是文件夹
                folder_items.append(item_id)

        file_items_data.sort(reverse=reverse)
        
        # 重新排列，文件夹总是在文件前面
        for index, item_id in enumerate(folder_items):
            self.tree.move(item_id, '', index)
        
        for index, (val, item_id) in enumerate(file_items_data):
            self.tree.move(item_id, '', len(folder_items) + index)

        self.tree.heading(col, command=lambda: self.sort_treeview_column(col, not reverse))

    def on_tree_double_click(self, event):
        item_id = self.tree.identify_row(event.y)
        if item_id in self.file_items:
            file_path = self.file_items[item_id]
            self.open_file(file_path)

    def on_tree_click(self, event):
        region = self.tree.identify_region(event.x, event.y)
        if region == "tree":
            item_id = self.tree.identify_row(event.y)
            if item_id in self.file_items:
                self.toggle_selection(item_id)

    def toggle_selection(self, item_id):
        """切换单个项目的选中状态"""
        current_tags = self.tree.item(item_id, "tags")
        current_text = self.tree.item(item_id, "text")
        
        if "checked" in current_tags:
            self.tree.item(item_id, tags=(), text=f"☐ {current_text.lstrip('☑ ')}")
        else:
            self.tree.item(item_id, tags=("checked",), text=f"☑ {current_text.lstrip('☐ ')}")

    def open_path_in_explorer(self, path):
        if not path or not os.path.isdir(path):
            messagebox.showwarning("路径无效", f"目录不存在或无效:\n{path}")
            return
        try:
            os.startfile(path)
        except Exception as e:
            messagebox.showerror("错误", f"无法打开目录: {e}")

    def open_file(self, file_path):
        if not os.path.isfile(file_path):
            messagebox.showerror("文件不存在", f"文件已不存在或被移动:\n{file_path}")
            return
        try:
            os.startfile(file_path)
        except Exception as e:
            messagebox.showerror("打开失败", f"无法打开文件: {e}")

    def scan_files(self):
        src_dir = self.source_dir.get()
        if not src_dir or not os.path.isdir(src_dir):
            messagebox.showerror("错误", "源目录无效或未选择！")
            return
        
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.file_items.clear()

        parent_map = {"": ""}
        
        found_files_count = 0
        for root, _, files in os.walk(src_dir):
            for file in files:
                if file.lower().endswith(('.xlsx', '.xls')):
                    found_files_count += 1
                    full_path = os.path.join(root, file)
                    relative_path = os.path.relpath(full_path, src_dir)
                    
                    parent_id = ""
                    path_parts = os.path.dirname(relative_path).split(os.sep)
                    
                    current_path = ""
                    for part in path_parts:
                        if part == "." or not part: continue
                        child_path = os.path.join(current_path, part)
                        if child_path not in parent_map:
                            parent_id = self.tree.insert(parent_map[current_path], "end", text=part, open=False)
                            parent_map[child_path] = parent_id
                        current_path = child_path
                    
                    parent_id = parent_map.get(os.path.dirname(relative_path), "")

                    mtime_stamp = os.path.getmtime(full_path)
                    mtime_str = datetime.fromtimestamp(mtime_stamp).strftime('%Y-%m-%d %H:%M:%S')

                    item_id = self.tree.insert(parent_id, "end", text=f"☐ {os.path.basename(relative_path)}", 
                                               values=(mtime_str,))
                    self.file_items[item_id] = full_path

        self.tree.tag_configure("checked", background="lightgreen")

        if found_files_count == 0:
            self.status_label.config(text="在源目录中未找到任何 Excel 文件。")
        else:
            self.status_label.config(text=f"扫描完成！发现 {found_files_count} 个文件。单击文件进行选择。")

    def load_settings(self):
        # 检查配置文件是否存在
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    # 如果配置文件中存在有效路径，则加载它们
                    if os.path.isdir(settings.get("source_dir", "")):
                        self.source_dir.set(settings.get("source_dir", ""))
                    if os.path.isdir(settings.get("target_dir", "")):
                        self.target_dir.set(settings.get("target_dir", ""))
                self.status_label.config(text="配置已加载。请选择目录并扫描文件。")
            except (json.JSONDecodeError, IOError) as e:
                self.status_label.config(text=f"加载配置失败: {e}")
        else:
            # --- 首次运行：配置文件不存在，自动设置默认路径 ---
            self.status_label.config(text="首次运行，正在设置默认路径...")
            try:
                # 1. 获取工具当前所在的目录
                #    sys.executable 在打包成exe后也能正确获取路径
                if getattr(sys, 'frozen', False):
                    tool_dir = os.path.dirname(sys.executable)
                else:
                    tool_dir = os.path.dirname(os.path.abspath(__file__))
                
                # 假设工具在 ".../Design/策划工具"
                # 2. 计算 Design 目录
                #    它是 "策划工具" 目录的上一级
                design_dir = os.path.dirname(tool_dir)
                
                # 3. 计算 SBT 目录
                #    它是 Design 目录的上一级
                sbt_dir = os.path.dirname(design_dir)
                
                # 4. 构建默认的源目录和目标目录
                default_source = design_dir
                default_target = os.path.join(sbt_dir, "Config")
                
                # 5. 检查路径是否存在，如果存在则设置
                if os.path.isdir(default_source):
                    self.source_dir.set(default_source)
                
                if os.path.isdir(default_target):
                    self.target_dir.set(default_target)
                
                self.status_label.config(text="已根据工具位置设置默认路径。请确认后扫描。")

            except Exception as e:
                self.status_label.config(text=f"自动设置默认路径失败: {e}")

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
        for item_id in self.file_items:
            current_tags = self.tree.item(item_id, "tags")
            if "checked" not in current_tags:
                self.toggle_selection(item_id)

    def deselect_all(self):
        for item_id in self.file_items:
            current_tags = self.tree.item(item_id, "tags")
            if "checked" in current_tags:
                self.toggle_selection(item_id)

    def start_conversion_thread(self):
        src_dir = self.source_dir.get()
        tgt_dir = self.target_dir.get()
        if not src_dir or not tgt_dir:
            messagebox.showerror("错误", "源目录和目标目录都必须选择！")
            return
        
        files_to_convert = []
        for item_id in self.file_items:
            if "checked" in self.tree.item(item_id, "tags"):
                files_to_convert.append(self.file_items[item_id])

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
                target_sub_dir = os.path.join(tgt_dir, relative_path) if relative_path != '.' else tgt_dir
                base_name = os.path.basename(src_path)
                file_name_without_ext = os.path.splitext(base_name)[0]
                target_csv_path = os.path.join(target_sub_dir, f"{file_name_without_ext}.csv")
                os.makedirs(target_sub_dir, exist_ok=True)
                self.status_label.config(text=f"正在转换 ({i+1}/{total_files}): {os.path.basename(src_path)}")
                df = pd.read_excel(src_path)
                df.to_csv(target_csv_path, index=False, encoding='utf-8-sig')
            except Exception as e:
                self.root.after(0, lambda p=src_path, err=e: messagebox.showerror("转换错误", f"转换文件失败: {p}\n错误: {err}"))
            self.progress['value'] = i + 1
        self.status_label.config(text=f"转换完成！共处理 {total_files} 个文件。")
        self.convert_button.config(state="normal")
        self.root.after(0, lambda: messagebox.showinfo("成功", f"所有选中的文件已成功转换！"))

if __name__ == "__main__":
    root = tk.Tk()
    app = ExcelBatchConverterApp(root)
    root.mainloop()