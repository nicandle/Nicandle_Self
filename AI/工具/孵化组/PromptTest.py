# -*- coding: utf-8 -*-
# AI聊天机器人 @ 2025-11-10
# 功能: Excel数据格式化导出工具 (v1.5 - 物种优先不重复逻辑)

import tkinter as tk
from tkinter import ttk, messagebox, font
import pandas as pd
import random
import os
import re

class DataGeneratorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("数据生成工具 v1.5 - by AI聊天机器人")
        self.root.geometry("900x600")

        # --- 数据存储 ---
        self.species_df_original = None
        self.feature_type1_list = []
        self.feature_type2_list = []
        
        # 仅保留 'Name' 列
        self.display_columns = ['Name'] 
        
        # 使用一个set来存储被选中的物种名称，以保持状态
        self.selected_species = set()

        # --- UI 样式 ---
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.default_font = font.nametofont("TkDefaultFont")
        self.default_font.configure(family="Microsoft YaHei", size=10)
        self.root.option_add("*Font", self.default_font)
        # 定义选中行的样式tag
        self.style.configure('selected_row.TTreeview', background='lightgreen', foreground='black')
        self.style.map('selected_row.TTreeview',
                       background=[('selected', '#0078D7')],
                       foreground=[('selected', 'white')])

        # --- 创建主框架 ---
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # --- 左侧控制面板 ---
        left_panel = ttk.Frame(main_frame, padding="10", relief="groove", borderwidth=2)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))

        # --- 1. 筛选区域 ---
        filter_frame = ttk.LabelFrame(left_panel, text="筛选与选择", padding="10")
        filter_frame.pack(fill=tk.X, pady=10)

        self.filters = {}
        filter_fields = [] 
        
        for i, field in enumerate(filter_fields):
            ttk.Label(filter_frame, text=f"{field}:").grid(row=i, column=0, padx=5, pady=5, sticky="w")
            entry = ttk.Entry(filter_frame, width=15)
            entry.grid(row=i, column=1, padx=5, pady=5)
            self.filters[field] = entry
        
        if not filter_fields:
            ttk.Label(filter_frame, text="无可用筛选字段 (仅按名称显示)").pack(pady=5)
        else:
            ttk.Label(filter_frame, text="提示: 可输入=, >, <").grid(row=len(filter_fields), columnspan=2, pady=(5,0), sticky='w')

        filter_button_frame = ttk.Frame(filter_frame)
        if not filter_fields:
            filter_button_frame.pack(pady=10)
        else:
            filter_button_frame.grid(row=len(filter_fields) + 1, columnspan=2, pady=10)

        ttk.Button(filter_button_frame, text="刷新/重置", command=self.reset_filter).pack(side=tk.LEFT, padx=2)
        ttk.Button(filter_button_frame, text="全部取消选中", command=self.clear_all_selections).pack(side=tk.LEFT, padx=2)

        # --- 2. 导出设置区域 ---
        export_frame = ttk.LabelFrame(left_panel, text="导出设置", padding="10")
        export_frame.pack(fill=tk.X, pady=10)

        ttk.Label(export_frame, text="导出总行数:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.rows_entry = ttk.Entry(export_frame, width=15)
        self.rows_entry.grid(row=0, column=1, padx=5, pady=5)
        self.rows_entry.insert(0, "100")

        ttk.Label(export_frame, text="每行特征组数:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.features_entry = ttk.Entry(export_frame, width=15)
        self.features_entry.grid(row=1, column=1, padx=5, pady=5)
        self.features_entry.insert(0, "2")

        # --- 3. 执行按钮 ---
        action_frame = ttk.Frame(left_panel, padding="10")
        action_frame.pack(fill=tk.X, pady=20)
        
        self.generate_button = ttk.Button(action_frame, text="按视图/选中生成", command=self.generate_and_export, style='Accent.TButton')
        self.generate_button.pack(fill=tk.X, ipady=8, pady=(0, 5))
        self.style.configure('Accent.TButton', font=('Microsoft YaHei', 11, 'bold'), foreground='white', background='#0078D7')

        self.random_generate_button = ttk.Button(action_frame, text="全量随机导出", command=self.generate_fully_random_and_export)
        self.random_generate_button.pack(fill=tk.X, ipady=8, pady=(5, 0))

        # --- 右侧数据显示区域 ---
        right_panel = ttk.Frame(main_frame)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        species_table_frame = ttk.LabelFrame(right_panel, text="物种数据预览 (单击行可选中/取消)", padding="10")
        species_table_frame.pack(fill=tk.BOTH, expand=True)

        self.tree = ttk.Treeview(species_table_frame, show='headings', columns=self.display_columns)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.tree.bind('<Button-1>', self.on_row_click)

        vsb = ttk.Scrollbar(species_table_frame, orient="vertical", command=self.tree.yview)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.configure(yscrollcommand=vsb.set)
        
        # --- 状态栏 ---
        self.status_label = ttk.Label(self.root, text="正在初始化...", anchor='w', relief=tk.SUNKEN)
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X)

        self.load_data()

    def on_row_click(self, event):
        item_id = self.tree.identify_row(event.y)
        if not item_id: return
        current_values = self.tree.item(item_id, 'values')
        if not current_values: return 
        species_name = str(current_values[0]).lstrip('✔ ')
        current_tags = self.tree.item(item_id, 'tags')
        if 'selected_row' in current_tags:
            if species_name in self.selected_species:
                self.selected_species.remove(species_name)
            self.tree.item(item_id, values=[species_name] + list(current_values[1:]), tags=())
        else:
            self.selected_species.add(species_name)
            new_values = [f"✔ {species_name}"] + list(current_values[1:]),
            self.tree.item(item_id, values=new_values, tags=('selected_row',))
        return "break"

    def update_species_table(self, df):
        self.tree.delete(*self.tree.get_children())
        self.tree["columns"] = self.display_columns
        for col in self.display_columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=300, anchor='w') 
        for index, row in df.iterrows():
            values = list(row[self.display_columns])
            species_name = values[0]
            tags_to_apply = ()
            if species_name in self.selected_species:
                values[0] = f"✔ {species_name}"
                tags_to_apply = ('selected_row',)
            self.tree.insert("", "end", values=values, tags=tags_to_apply)

    def clear_all_selections(self):
        self.selected_species.clear()
        self.status_label.config(text="已取消所有选中。")
        self.apply_filter() 

    def generate_and_export(self):
        species_list = []
        source_name = ""
        if self.selected_species:
            species_list = list(self.selected_species)
            source_name = f"{len(species_list)}个选中项"
        else:
            current_species_ids = self.tree.get_children()
            if not current_species_ids:
                messagebox.showwarning("无数据", "没有可用于生成的物种数据。")
                return
            species_list = [str(self.tree.item(item)['values'][0]).lstrip('✔ ') for item in current_species_ids]
            source_name = "当前视图"
        self._perform_generation(species_list, source_name)

    def load_data(self):
        try:
            self.status_label.config(text="正在加载 Excel 文件...")
            species_file, feature_file = "GeneSpecies.xlsx", "GeneFeature.xlsx"
            if not os.path.exists(species_file) or not os.path.exists(feature_file):
                raise FileNotFoundError(f"请确保 {species_file} 和 {feature_file} 文件在同一目录下。")
            self.species_df_original = pd.read_excel(species_file)
            if 'Name' not in self.species_df_original.columns:
                raise KeyError(f"GeneSpecies.xlsx 文件必须包含 'Name' 列")
            features_df = pd.read_excel(feature_file)
            self.feature_type1_list = features_df[features_df['FeatureType'] == 1]['Name'].tolist()
            self.feature_type2_list = features_df[features_df['FeatureType'] == 2]['Name'].tolist()
            if self.species_df_original.empty or not self.feature_type1_list or not self.feature_type2_list:
                messagebox.showwarning("数据警告", "一个或多个Excel文件为空或缺少所需数据。")
                self.status_label.config(text="数据加载不完整。")
                return
            self.update_species_table(self.species_df_original)
            self.status_label.config(text="数据加载成功！")
        except (FileNotFoundError, KeyError) as e:
            messagebox.showerror("文件错误", str(e))
            self.status_label.config(text=f"错误：{e}")
        except Exception as e:
            messagebox.showerror("加载错误", f"加载文件时发生错误: {e}")
            self.status_label.config(text=f"错误: {e}")

    def apply_filter(self):
        if self.species_df_original is None: return
        filtered_df = self.species_df_original.copy()
        self.update_species_table(filtered_df)
        self.status_label.config(text=f"列表已刷新，共 {len(filtered_df)} 条结果。")

    def reset_filter(self):
        for entry in self.filters.values(): entry.delete(0, tk.END)
        if self.species_df_original is not None:
            self.update_species_table(self.species_df_original)
            self.status_label.config(text="视图已重置，选中项已保留。")

    def generate_fully_random_and_export(self):
        if self.species_df_original is None or self.species_df_original.empty:
            messagebox.showwarning("无数据", "原始物种数据为空。"); return
        species_list = self.species_df_original['Name'].tolist()
        self._perform_generation(species_list, "全量数据")

    def _perform_generation(self, species_list, source_name):
        try:
            num_rows, num_feature_pairs = int(self.rows_entry.get()), int(self.features_entry.get())
            if num_rows <= 0 or num_feature_pairs <= 0: raise ValueError
        except ValueError: messagebox.showerror("输入错误", "行数和特征组数必须是正整数。"); return
        
        if not self.feature_type1_list or not self.feature_type2_list:
            messagebox.showwarning("无数据", "特征列表为空，请检查 GeneFeature.xlsx 文件。"); return
            
        self.status_label.config(text=f"正在基于 {source_name} 生成数据..."); self.root.update_idletasks()
        
        # --- [修改核心逻辑] 构建优先不重复的物种队列 ---
        # 逻辑：如果需要100行，有30个物种。我们生成 [30乱序] + [30乱序] + [30乱序] + [10乱序]
        target_species_queue = []
        while len(target_species_queue) < num_rows:
            # 复制一份当前列表并打乱
            current_batch = species_list[:]
            random.shuffle(current_batch)
            target_species_queue.extend(current_batch)
        
        # 裁剪到精确的行数
        target_species_queue = target_species_queue[:num_rows]
        
        generated_lines = set()
        output_lines = []
        
        # 遍历预设好的物种队列生成特征
        for species in target_species_queue:
            # 为当前指定的物种尝试生成不重复的特征组合
            # 尝试次数限制，防止因特征组合耗尽导致的死循环
            max_feature_attempts = 50 
            unique_found = False
            
            for _ in range(max_feature_attempts):
                features = []
                for _ in range(num_feature_pairs):
                    features.extend([random.choice(self.feature_type1_list), random.choice(self.feature_type2_list)])
                
                line = f"{species} {' '.join(features)}"
                
                if line not in generated_lines:
                    generated_lines.add(line)
                    output_lines.append(line)
                    unique_found = True
                    break # 找到唯一组合，跳出尝试循环，处理下一个物种
            
            if not unique_found:
                # 如果这个物种尝试了50次都没生成唯一的行（说明特征组合可能饱和了），
                # 策略：跳过该行。这可能导致最终行数少于 num_rows，但保证了数据不重复。
                print(f"警告: 物种 {species} 无法生成新的唯一特征组合，已跳过。")

        if len(output_lines) < num_rows:
            messagebox.showwarning("生成不完整", f"计划生成 {num_rows} 行，实际生成 {len(output_lines)} 行。\n原因：部分物种的特征组合已耗尽或重复。")
            
        try:
            output_filename = "output.txt"
            with open(output_filename, "w", encoding="utf-8") as f: f.write("\n".join(output_lines))
            self.status_label.config(text=f"成功导出 {len(output_lines)} 行到 {output_filename}")
            messagebox.showinfo("成功", f"数据已成功导出到 {os.path.abspath(output_filename)}")
        except Exception as e: messagebox.showerror("导出失败", f"写入文件时发生错误: {e}"); self.status_label.config(text=f"错误：写入文件失败。")

if __name__ == "__main__":
    root = tk.Tk()
    app = DataGeneratorApp(root)
    root.mainloop()