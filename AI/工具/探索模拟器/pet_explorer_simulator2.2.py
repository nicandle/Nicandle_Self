import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
import random
from datetime import datetime
import re
import json
import os
import subprocess
import sys

# --- 数据结构与常量定义 ---
RATING_MAP = {'S': 5, 'A': 4, 'B': 3, 'C': 2, 'D': 1}
ATTR_ID_MAP = {1: "力量", 2: "体质", 3: "敏捷", 4: "感知"}
REVERSE_ATTR_MAP = {v: k for k, v in ATTR_ID_MAP.items()}
ITEM_RARITY_MAP = {1: 'D', 2: 'C', 3: 'B', 4: 'A', 5: 'S'}
CONFIG_FILE = "simulator_config.json"

class PetExplorerSimulator(tk.Tk):
    """
    宠物探索模拟器 v2.4 - “工作流优化”版
    内核: 在 v2.3 基础上，优化核心工作流程。
    功能: 
    1. 报告筛选移至输出区，并新增“仅显示当前”默认选项。
    2. 自动保存和加载上次的表格路径，状态栏显示导入时间。
    3. 为每个表格添加“快捷打开”按钮。
    """
    def __init__(self):
        super().__init__()
        self.title("宠物探索模拟器 (v2.4 内核 | AI聊天机器人 '工作流优化' 版)")
        self.geometry("1366x800")
        self.minsize(1100, 650)
        
        self.COLORS = {
            "bg_main": "#E9F5E9", "bg_frame": "#F1F8F1", "text_main": "#3E4A3E",
            "text_light": "#607D8B", "accent": "#4CAF50", "accent_fg": "#FFFFFF",
            "success": "#4CAF50", "failure": "#D9534F", "entry_bg": "#FFFFFF",
            "entry_fg": "#3E4A3E", "tree_heading": "#DDEEE0", "button_light": "#F0F0F0"
        }
        
        self.event_data, self.drop_data, self.item_info_data = None, None, None
        self.item_info_map = {}
        self.all_simulation_data = []
        self.file_paths = {"event": "", "drop": "", "item": ""}
        
        self.configure(bg=self.COLORS["bg_main"])
        self._configure_styles()
        self._create_widgets()
        self._bind_events()
        self.load_config() # 启动时加载配置
        self.after(100, self.calculate_probabilities)

    def _configure_styles(self):
        self.style = ttk.Style(self)
        self.style.theme_use('clam')
        font_normal = ('Microsoft YaHei UI', 10); font_bold = ('Microsoft YaHei UI', 10, 'bold')
        self.style.configure('.', background=self.COLORS["bg_main"], foreground=self.COLORS["text_main"], font=font_normal, fieldbackground=self.COLORS["entry_bg"], troughcolor=self.COLORS["bg_frame"])
        self.style.configure('Main.TFrame', background=self.COLORS["bg_main"])
        self.style.configure('TFrame', background=self.COLORS["bg_frame"])
        self.style.configure('TLabelframe', background=self.COLORS["bg_frame"], borderwidth=1, relief="solid", bordercolor="#D0E0D0")
        self.style.configure('TLabelframe.Label', background=self.COLORS["bg_frame"], foreground=self.COLORS["accent"], font=font_bold)
        self.style.configure('TLabel', background=self.COLORS["bg_frame"], foreground=self.COLORS["text_main"])
        self.style.configure('Success.TLabel', foreground=self.COLORS["success"]); self.style.configure('Failure.TLabel', foreground=self.COLORS["failure"])
        self.style.configure('Placeholder.TLabel', foreground=self.COLORS["text_light"]); self.style.configure('Accent.TLabel', foreground=self.COLORS["accent"], font=font_bold)
        self.style.configure('TButton', background=self.COLORS["accent"], foreground=self.COLORS["accent_fg"], font=font_bold, borderwidth=0, padding=(10, 5))
        self.style.map('TButton', background=[('active', '#5CB85C'), ('pressed', '#449D44')])
        # 【v2.4 新增】快捷打开按钮样式
        self.style.configure('Light.TButton', background=self.COLORS["button_light"], foreground=self.COLORS["text_main"], font=font_normal, borderwidth=1, relief="solid", bordercolor="#CCCCCC")
        self.style.map('Light.TButton', background=[('active', '#E0E0E0')])
        self.style.configure('TEntry', fieldbackground=self.COLORS["entry_bg"], foreground=self.COLORS["entry_fg"], insertcolor=self.COLORS["text_main"], bordercolor="#B0C4B0", relief="solid")
        self.style.map('TCombobox', fieldbackground=[('readonly', self.COLORS["entry_bg"])], selectbackground=[('readonly', self.COLORS["bg_frame"])], selectforeground=[('readonly', self.COLORS["text_main"])], bordercolor=[('readonly', "#B0C4B0")])
        self.option_add('*TCombobox*Listbox.background', self.COLORS["entry_bg"]); self.option_add('*TCombobox*Listbox.foreground', self.COLORS["text_main"])
        self.option_add('*TCombobox*Listbox.selectBackground', self.COLORS["accent"]); self.option_add('*TCombobox*Listbox.selectForeground', self.COLORS["accent_fg"])
        self.option_add('*TCombobox*Listbox.font', font_normal)
        self.style.configure('TCheckbutton', background=self.COLORS["bg_frame"], foreground=self.COLORS["text_main"])
        self.style.map('TCheckbutton', indicatorcolor=[('selected', self.COLORS["accent"]), ('!selected', "#B0C4B0")])
        self.style.configure("Treeview.Heading", background=self.COLORS["tree_heading"], foreground=self.COLORS["accent"], font=font_bold, relief="flat")
        self.style.map("Treeview.Heading", background=[('active', self.COLORS["bg_frame"])])
        self.style.configure("Treeview", background=self.COLORS["entry_bg"], fieldbackground=self.COLORS["entry_bg"], foreground=self.COLORS["text_main"], rowheight=25)
        self.style.map('Treeview', background=[('selected', self.COLORS["accent"])], foreground=[('selected', self.COLORS["accent_fg"])])

    def _create_widgets(self):
        paned_window = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        paned_window.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        left_frame = ttk.Frame(paned_window, style='Main.TFrame', padding=10)
        left_frame.columnconfigure(0, weight=1)
        paned_window.add(left_frame, weight=1)
        right_frame = ttk.Frame(paned_window, style='Main.TFrame', padding=10)
        right_frame.columnconfigure(0, weight=1)
        right_frame.rowconfigure(1, weight=1)
        paned_window.add(right_frame, weight=2)

        # --- 区域1-4: 左侧框架 (与v2.3基本相同) ---
        pet_attr_frame = ttk.LabelFrame(left_frame, text="🐾 区域1: 宠物属性", padding="15")
        pet_attr_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        self.pet_attrs = {}
        for i, (attr_id, attr_name) in enumerate(ATTR_ID_MAP.items()):
            ttk.Label(pet_attr_frame, text=f"{attr_name}:").grid(row=0, column=i*2, padx=(0,5), pady=5, sticky="w")
            combo = ttk.Combobox(pet_attr_frame, values=list(RATING_MAP.keys()), width=5, state="readonly")
            combo.set("D"); combo.grid(row=0, column=i*2+1, padx=(0,20), pady=5)
            self.pet_attrs[attr_id] = combo

        params_frame = ttk.LabelFrame(left_frame, text="⚙️ 区域2: 核心参数", padding="15")
        params_frame.grid(row=1, column=0, sticky="ew", pady=10)
        self.params = {}
        self.param_definitions = {
            "模拟次数": 10, "饱食度消耗X": 5, "检定失败扣除心情Y": 10, "心情系数Z": 3, 
            "大成功初始权重a": 15, "成功初始权重b": 65, "失败初始权重c": 35, "大成功系数α": 20, 
            "成功系数β": 10, "双属性联结系数γ": 0.7, "低心情阈值": 30, "奖励事件触发阈值": 100
        }
        for i, (name, default_val) in enumerate(self.param_definitions.items()):
            row, col = divmod(i, 2)
            ttk.Label(params_frame, text=f"{name}:").grid(row=row, column=col*2, padx=(0,5), pady=5, sticky="w")
            var = tk.StringVar(value=str(default_val))
            entry = ttk.Entry(params_frame, width=10, textvariable=var)
            entry.grid(row=row, column=col*2+1, padx=(0,20), pady=5)
            self.params[name] = var

        initial_state_frame = ttk.LabelFrame(left_frame, text="🏁 区域3: 宠物初始状态", padding="15")
        initial_state_frame.grid(row=2, column=0, sticky="ew", pady=10)
        self.initial_states = {}
        state_definitions = {"宠物初始心情": 100, "宠物初始饱食度": 100}
        for i, (name, default_val) in enumerate(state_definitions.items()):
            ttk.Label(initial_state_frame, text=f"{name}:").grid(row=0, column=i*2, padx=(0,5), pady=5, sticky="w")
            entry = ttk.Entry(initial_state_frame, width=12); entry.insert(0, str(default_val))
            entry.grid(row=0, column=i*2+1, padx=(0,20), pady=5)
            self.initial_states[name] = entry

        prob_frame = ttk.LabelFrame(left_frame, text="🔬 区域4: 检定概率速查", padding="15")
        prob_frame.grid(row=3, column=0, sticky="ew", pady=10)
        # ... (区域4内部布局与v2.3完全相同，此处省略以保持简洁)
        prob_frame.columnconfigure(0, weight=1)
        prob_settings_frame = ttk.Frame(prob_frame); prob_settings_frame.pack(fill="x", pady=(0, 10))
        self.is_dual_attr = tk.BooleanVar(value=False)
        dual_check = ttk.Checkbutton(prob_settings_frame, text="双属性检定", variable=self.is_dual_attr)
        dual_check.pack(anchor='w')
        attr1_frame = ttk.Frame(prob_settings_frame); attr1_frame.pack(fill='x', pady=2)
        ttk.Label(attr1_frame, text="属性1:").pack(side='left')
        self.prob_attr1_combo = ttk.Combobox(attr1_frame, values=list(ATTR_ID_MAP.values()), width=6, state="readonly")
        self.prob_attr1_combo.set("力量"); self.prob_attr1_combo.pack(side='left', padx=(2,5))
        ttk.Label(attr1_frame, text="要求:").pack(side='left')
        self.prob_rating1_combo = ttk.Combobox(attr1_frame, values=list(RATING_MAP.keys()), width=4, state="readonly")
        self.prob_rating1_combo.set("B"); self.prob_rating1_combo.pack(side='left', padx=(2,5))
        self.attr2_frame = ttk.Frame(prob_settings_frame)
        self.attr2_frame.pack(fill='x', pady=2)
        self.prob_attr2_label = ttk.Label(self.attr2_frame, text="属性2:")
        self.prob_attr2_combo = ttk.Combobox(self.attr2_frame, values=list(ATTR_ID_MAP.values()), width=6, state="readonly")
        self.prob_attr2_combo.set("体质")
        self.prob_rating2_label = ttk.Label(self.attr2_frame, text="要求:")
        self.prob_rating2_combo = ttk.Combobox(self.attr2_frame, values=list(RATING_MAP.keys()), width=4, state="readonly")
        self.prob_rating2_combo.set("B")
        self.prob_attr2_label.pack(side='left'); self.prob_attr2_combo.pack(side='left', padx=(2,5))
        self.prob_rating2_label.pack(side='left'); self.prob_rating2_combo.pack(side='left', padx=(2,5))
        self.prob_result_label = ttk.Label(prob_frame, text="请在上方设置检定场景...", style="Placeholder.TLabel", font=('Microsoft YaHei UI', 11, 'bold'), wraplength=400)
        self.prob_result_label.pack(pady=10)
        self._toggle_dual_attr_view()

        # --- 区域5: 左侧框架 (【v2.4 变更】新增快捷打开按钮) ---
        control_frame = ttk.LabelFrame(left_frame, text="🎛️ 区域5: 数据导入与模拟控制", padding="15")
        control_frame.grid(row=4, column=0, sticky="ew", pady=10)
        control_frame.columnconfigure(1, weight=1) # 让导入按钮占据空间
        
        # 事件表
        self.import_event_button = ttk.Button(control_frame, text="📂 导入事件表", command=self.import_event_data)
        self.import_event_button.grid(row=0, column=1, sticky='ew', padx=(0,5))
        self.open_event_button = ttk.Button(control_frame, text="打开", style="Light.TButton", width=5, command=lambda: self.open_file("event"))
        self.open_event_button.grid(row=0, column=2, sticky='w')
        self.event_status_label = ttk.Label(control_frame, text="事件表状态: 未导入", style="Failure.TLabel")
        self.event_status_label.grid(row=1, column=1, columnspan=2, sticky="w", pady=(2,5))

        # 掉落表
        self.import_drop_button = ttk.Button(control_frame, text="🎁 导入掉落表", command=self.import_drop_data)
        self.import_drop_button.grid(row=2, column=1, sticky='ew', padx=(0,5))
        self.open_drop_button = ttk.Button(control_frame, text="打开", style="Light.TButton", width=5, command=lambda: self.open_file("drop"))
        self.open_drop_button.grid(row=2, column=2, sticky='w')
        self.drop_status_label = ttk.Label(control_frame, text="掉落表状态: 未导入", style="Failure.TLabel")
        self.drop_status_label.grid(row=3, column=1, columnspan=2, sticky="w", pady=(2,5))

        # 物品图鉴
        self.import_item_button = ttk.Button(control_frame, text="📚 导入物品图鉴", command=self.import_item_data)
        self.import_item_button.grid(row=4, column=1, sticky='ew', padx=(0,5))
        self.open_item_button = ttk.Button(control_frame, text="打开", style="Light.TButton", width=5, command=lambda: self.open_file("item"))
        self.open_item_button.grid(row=4, column=2, sticky='w')
        self.item_status_label = ttk.Label(control_frame, text="物品图鉴: 未导入", style="Failure.TLabel")
        self.item_status_label.grid(row=5, column=1, columnspan=2, sticky="w", pady=(2,10))

        # 开始按钮
        self.start_button = ttk.Button(control_frame, text="▶️ 开始完整模拟", command=self.start_simulation)
        self.start_button.grid(row=6, column=1, columnspan=2, sticky='ew', pady=(10,0))

        # --- 区域6-7: 右侧框架 (【v2.4 变更】筛选功能移入区域7) ---
        self.selected_params_frame = ttk.LabelFrame(right_frame, text="🏷️ 区域6: 选中报告的参数", padding="15")
        self.selected_params_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        self.param_placeholder_label = ttk.Label(self.selected_params_frame, text="ℹ️ 请从下方筛选报告以查看其详细参数。", style="Placeholder.TLabel")
        self.param_placeholder_label.pack(pady=10)

        output_frame = ttk.LabelFrame(right_frame, text="📜 区域7: 完整模拟结果", padding=(15,10))
        output_frame.grid(row=1, column=0, sticky="nsew")
        output_frame.columnconfigure(0, weight=1); output_frame.rowconfigure(1, weight=1) # 文本框在第1行
        
        # 【v2.4 新增】筛选控制条
        filter_bar = ttk.Frame(output_frame)
        filter_bar.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        ttk.Label(filter_bar, text="🔍 筛选报告:").pack(side="left", padx=(0, 5))
        self.filter_combo = ttk.Combobox(filter_bar, state="readonly", width=40)
        self.filter_combo.pack(side="left", fill="x", expand=True)

        self.output_text = tk.Text(output_frame, wrap="word", state="disabled", bg=self.COLORS["entry_bg"], fg=self.COLORS["text_main"], relief="solid", bd=1, highlightthickness=0, font=('Consolas', 10))
        scrollbar = ttk.Scrollbar(output_frame, orient="vertical", command=self.output_text.yview)
        self.output_text.configure(yscrollcommand=scrollbar.set)
        self.output_text.grid(row=1, column=0, sticky="nsew"); scrollbar.grid(row=1, column=1, sticky="ns")

    # --- 新增与修改的核心逻辑 ---

    def load_config(self):
        """【v2.4 新增】从JSON文件加载配置"""
        try:
            if os.path.exists(CONFIG_FILE):
                with open(CONFIG_FILE, 'r') as f:
                    self.file_paths = json.load(f)
                # 尝试自动加载文件
                if self.file_paths.get("event"): self.import_event_data(self.file_paths["event"])
                if self.file_paths.get("drop"): self.import_drop_data(self.file_paths["drop"])
                if self.file_paths.get("item"): self.import_item_data(self.file_paths["item"])
        except Exception as e:
            messagebox.showerror("配置加载错误", f"无法加载配置文件 '{CONFIG_FILE}':\n{e}")
            self.file_paths = {"event": "", "drop": "", "item": ""}

    def save_config(self):
        """【v2.4 新增】保存配置到JSON文件"""
        try:
            with open(CONFIG_FILE, 'w') as f:
                json.dump(self.file_paths, f, indent=4)
        except Exception as e:
            print(f"Warning: Could not save config file: {e}")

    def open_file(self, file_key):
        """【v2.4 新增】用系统默认程序打开文件"""
        path = self.file_paths.get(file_key)
        if path and os.path.exists(path):
            try:
                if sys.platform == "win32":
                    os.startfile(path)
                elif sys.platform == "darwin": # macOS
                    subprocess.Popen(["open", path])
                else: # linux
                    subprocess.Popen(["xdg-open", path])
            except Exception as e:
                messagebox.showerror("打开失败", f"无法打开文件 '{path}':\n{e}")
        else:
            messagebox.showwarning("文件未找到", f"没有已加载的{file_key}文件或路径无效。")

    def _import_data_generic(self, title, file_types, existing_path=None):
        file_path = existing_path or filedialog.askopenfilename(title=title, filetypes=file_types)
        if not file_path: return None, None
        try:
            df = pd.read_csv(file_path) if file_path.endswith('.csv') else pd.read_excel(file_path)
            return df, file_path
        except Exception as e:
            messagebox.showerror("错误", f"导入文件失败: {e}")
            return None, None

    def import_event_data(self, path=None):
        df, file_path = self._import_data_generic("请选择事件表文件", [("Excel/CSV", "*.xlsx *.xls *.csv")], path)
        if df is not None:
            self.event_data = df
            self.event_data[['Attr1', 'Attr2']] = self.event_data[['Attr1', 'Attr2']].fillna(0)
            self.file_paths["event"] = file_path
            self.save_config()
            timestamp = datetime.now().strftime("%H:%M:%S")
            self.event_status_label.config(text=f"✔ 事件表: 已导入 {len(self.event_data)} 条 (于 {timestamp})", style="Success.TLabel")

    def import_drop_data(self, path=None):
        df, file_path = self._import_data_generic("请选择掉落表文件 (DropJar)", [("Excel/CSV", "*.xlsx *.xls *.csv")], path)
        if df is not None:
            self.drop_data = df
            self.file_paths["drop"] = file_path
            self.save_config()
            timestamp = datetime.now().strftime("%H:%M:%S")
            self.drop_status_label.config(text=f"✔ 掉落表: 已导入 {len(self.drop_data)} 条 (于 {timestamp})", style="Success.TLabel")

    def import_item_data(self, path=None):
        df, file_path = self._import_data_generic("请选择物品图鉴文件", [("Excel/CSV", "*.xlsx *.xls *.csv")], path)
        if df is not None:
            try:
                # ... (验证逻辑不变)
                self.item_info_data = df
                self.item_info_map = df.set_index('Id')[['Name', 'Rarity', 'Type']].to_dict('index')
                self.file_paths["item"] = file_path
                self.save_config()
                timestamp = datetime.now().strftime("%H:%M:%S")
                self.item_status_label.config(text=f"✔ 物品图鉴: 已载入 {len(self.item_info_map)} 个 (于 {timestamp})", style="Success.TLabel")
            except Exception as e:
                # ... (错误处理不变)
                messagebox.showerror("处理错误", f"处理物品图鉴时出错: {e}")

    def start_simulation(self):
        # ... (前置检查不变)
        if self.event_data is None: messagebox.showwarning("警告", "请先导入事件表！"); return
        if self.drop_data is None: messagebox.showwarning("警告", "请先导入掉落表！"); return
        if not self.item_info_map: messagebox.showwarning("警告", "请先导入物品图鉴！"); return
        try:
            # ... (参数获取不变)
            pet_attrs_val = {attr_id: RATING_MAP[combo.get()] for attr_id, combo in self.pet_attrs.items()}
            p = {name: float(var.get()) for name, var in self.params.items()}
            s = {name: int(entry.get()) for name, entry in self.initial_states.items()}
            simulation_count = int(p["模拟次数"])
            if simulation_count <= 0: messagebox.showerror("输入错误", "模拟次数必须 > 0"); return
        except (ValueError, KeyError): messagebox.showerror("输入错误", "参数或初始状态必须为有效数字！"); return
        
        try:
            # ... (模拟核心逻辑不变)
            timestamp_key = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            pet_attrs_brief = " ".join([f"{ATTR_ID_MAP[k][0]}:{v.get()}" for k, v in self.pet_attrs.items()])
            pet_attrs_full = " ".join([f"{ATTR_ID_MAP[k]}:{v.get()}" for k, v in self.pet_attrs.items()])
            cumulative_results = {"total": 0, "perfect": 0, "success": 0, "failure": 0}
            cumulative_total_drops = {}
            individual_run_outputs = []
            normal_events_list = self.event_data[self.event_data['Type'] == 1].to_dict('records')
            reward_events_list = self.event_data[self.event_data['Type'] == 2].to_dict('records')
            
            for i in range(simulation_count):
                run_results, run_total_drops, run_event_details = self._run_single_simulation(pet_attrs_val, p, s, normal_events_list, reward_events_list)
                for key in cumulative_results: cumulative_results[key] += run_results[key]
                for item_id, num in run_total_drops.items():
                    cumulative_total_drops[item_id] = cumulative_total_drops.get(item_id, 0) + num
                success_rate = (run_results["perfect"] + run_results["success"]) / run_results["total"] if run_results["total"] > 0 else 0
                run_report = [f"--- 第 {i+1:02d} 次模拟 (成功率: {success_rate:.2%}) ---"]
                run_report.extend(run_event_details)
                if run_total_drops:
                    run_report.append("\n  本轮总掉落:")
                    run_report.append(self._format_drop_table(run_total_drops, is_avg=False))
                else:
                    run_report.append("  本轮无掉落。")
                individual_run_outputs.append("\n".join(run_report))

            total_events = cumulative_results["total"]
            avg_success_rate = (cumulative_results["perfect"] + cumulative_results["success"]) / total_events if total_events > 0 else 0
            display_label = f"{timestamp_key} [{pet_attrs_brief}] [成功率: {avg_success_rate:.2%}]"
            full_report_str = self.format_report(timestamp_key, pet_attrs_full, cumulative_results, cumulative_total_drops, individual_run_outputs, simulation_count, avg_success_rate)
            
            # 【v2.4 变更】将新报告插入列表顶部
            new_report_data = {"id": timestamp_key, "label": display_label, "report": full_report_str, "parameters": p, "avg_success_rate": avg_success_rate}
            self.all_simulation_data.insert(0, new_report_data)
            
            self.update_filter_options()
            # 【v2.4 变更】默认选中“仅显示当前报告”
            self.filter_combo.set("⭐ 仅显示当前报告")
            self.on_filter_selected()
        except Exception as e:
            messagebox.showerror("模拟出错", f"执行模拟时发生错误: {e}")

    def update_filter_options(self):
        """【v2.4 变更】更新筛选列表选项"""
        options = []
        if self.all_simulation_data:
            options.append("⭐ 仅显示当前报告")
        options.append("显示全部")
        options.extend([item["label"] for item in self.all_simulation_data])
        self.filter_combo['values'] = options

    def on_filter_selected(self, event=None):
        """【v2.4 变更】处理筛选逻辑"""
        selection = self.filter_combo.get()
        self.output_text.config(state="normal")
        self.output_text.delete("1.0", tk.END)
        
        report_to_show = None
        params_to_show = None

        if selection == "⭐ 仅显示当前报告":
            if self.all_simulation_data:
                report_to_show = self.all_simulation_data[0]["report"]
                params_to_show = self.all_simulation_data[0]["parameters"]
        elif selection == "显示全部" or not selection:
            self.display_all_reports()
            self._update_selected_params_display(None)
            return # 特殊处理，直接返回
        else:
            for item in self.all_simulation_data:
                if item["label"] == selection:
                    report_to_show = item["report"]
                    params_to_show = item["parameters"]
                    break
        
        if report_to_show:
            self.output_text.insert(tk.END, report_to_show)
        
        self._update_selected_params_display(params_to_show)
        self.output_text.config(state="disabled")
        self.output_text.see("1.0")

    # --- 以下为未发生重大变更的函数 (为完整性保留) ---
    def _bind_events(self):
        for combo in self.pet_attrs.values(): combo.bind("<<ComboboxSelected>>", self.calculate_probabilities)
        for var in self.params.values(): var.trace_add("write", self.calculate_probabilities)
        self.prob_attr1_combo.bind("<<ComboboxSelected>>", self.calculate_probabilities)
        self.prob_rating1_combo.bind("<<ComboboxSelected>>", self.calculate_probabilities)
        self.prob_attr2_combo.bind("<<ComboboxSelected>>", self.calculate_probabilities)
        self.prob_rating2_combo.bind("<<ComboboxSelected>>", self.calculate_probabilities)
        self.is_dual_attr.trace_add("write", self._toggle_dual_attr_view)
        self.filter_combo.bind("<<ComboboxSelected>>", self.on_filter_selected)
        self.protocol("WM_DELETE_WINDOW", self.on_closing) # 捕获关闭事件

    def on_closing(self):
        """【v2.4 新增】关闭前保存配置"""
        self.save_config()
        self.destroy()

    def calculate_probabilities(self, *args):
        try:
            p = {name: float(var.get()) for name, var in self.params.items()}
            pet_attrs_val = {attr_id: RATING_MAP[combo.get()] for attr_id, combo in self.pet_attrs.items()}
            attr1_name = self.prob_attr1_combo.get(); attr1_req_str = self.prob_rating1_combo.get()
            attr1_id = REVERSE_ATTR_MAP[attr1_name]; attr1_req_val = RATING_MAP[attr1_req_str]
            w_perfect, w_success = p["大成功初始权重a"], p["成功初始权重b"]
            if self.is_dual_attr.get():
                attr2_name = self.prob_attr2_combo.get(); attr2_req_str = self.prob_rating2_combo.get()
                if attr1_name == attr2_name: self.prob_result_label.config(text="错误: 双属性检定不能选择相同的属性。", style="Failure.TLabel"); return
                attr2_id = REVERSE_ATTR_MAP[attr2_name]; attr2_req_val = RATING_MAP[attr2_req_str]
                avg_diff = ((pet_attrs_val[attr1_id] - attr1_req_val) + (pet_attrs_val[attr2_id] - attr2_req_val)) / 2.0
                w_perfect += avg_diff * p["大成功系数α"] * p["双属性联结系数γ"]; w_success += avg_diff * p["成功系数β"] * p["双属性联结系数γ"]
            else:
                rating_diff = pet_attrs_val[attr1_id] - attr1_req_val
                w_perfect += rating_diff * p["大成功系数α"]; w_success += rating_diff * p["成功系数β"]
            weights = [max(0, w_perfect), max(0, w_success), p["失败初始权重c"]]
            total_weight = sum(weights)
            if total_weight > 0: prob_perfect, prob_success, prob_failure = weights[0] / total_weight, weights[1] / total_weight, weights[2] / total_weight
            else: prob_perfect, prob_success, prob_failure = 0, 0, 1
            result_text = (f"总成功率: {prob_perfect+prob_success:.2%}\n"
               f"大成功: {prob_perfect:.2%} | 成功: {prob_success:.2%} | 失败: {prob_failure:.2%}")
            self.prob_result_label.config(text=result_text, style="Accent.TLabel")
        except (ValueError, KeyError): self.prob_result_label.config(text="等待输入有效的核心参数...", style="Placeholder.TLabel")
        except Exception as e: self.prob_result_label.config(text=f"计算错误: {e}", style="Failure.TLabel")

    def _toggle_dual_attr_view(self, *args):
        if self.is_dual_attr.get(): self.attr2_frame.pack(fill='x', pady=2)
        else: self.attr2_frame.pack_forget()
        self.calculate_probabilities()

    def _update_selected_params_display(self, params_dict=None):
        for widget in self.selected_params_frame.winfo_children(): widget.destroy()
        if params_dict is None:
            self.param_placeholder_label = ttk.Label(self.selected_params_frame, text="ℹ️ 请从下方筛选报告以查看其详细参数。", style="Placeholder.TLabel")
            self.param_placeholder_label.pack(pady=10)
        else:
            for i, (name, value) in enumerate(params_dict.items()):
                row, col = divmod(i, 2)
                ttk.Label(self.selected_params_frame, text=f"{name}:").grid(row=row, column=col*2, padx=(0,5), pady=5, sticky="w")
                ttk.Label(self.selected_params_frame, text=f"{value}", font=('Microsoft YaHei UI', 9, 'bold')).grid(row=row, column=col*2+1, padx=(0,20), pady=5, sticky="w")

    def _get_item_name(self, item_id): return self.item_info_map.get(item_id, {}).get('Name', f"未知物品({item_id})")
    def _get_item_rarity(self, item_id): return self.item_info_map.get(item_id, {}).get('Rarity')
    def _parse_num(self, num_str):
        num_str = str(num_str).strip()
        match = re.match(r'(\d+)[-,]?(\d+)?', num_str)
        if match:
            start = int(match.group(1))
            end = int(match.group(2)) if match.group(2) else start
            return random.randint(min(start, end), max(start, end))
        return 0
    def _process_drops(self, jar_id):
        if self.drop_data is None or pd.isna(jar_id) or int(jar_id) == 0: return {}, []
        drops, drop_descriptions = {}, []
        try:
            jar_rules = self.drop_data[self.drop_data['JarId'] == int(jar_id)]
            if jar_rules.empty: return {}, []
            for _, group_df in jar_rules.groupby('WeightGroup'):
                drop_times = int(group_df['DropTimes'].iloc[0])
                for _ in range(drop_times):
                    chosen_item = group_df.sample(n=1, weights='Weight').iloc[0]
                    item_id, num = int(chosen_item['ItemId']), self._parse_num(chosen_item['Num'])
                    if num > 0:
                        drops[item_id] = drops.get(item_id, 0) + num
                        drop_descriptions.append(f"    -> 获得 [{self._get_item_name(item_id)}] x {num}")
        except Exception as e: drop_descriptions.append(f"    -> !掉落处理异常: {e}")
        return drops, drop_descriptions
    def _run_single_simulation(self, pet_attrs_val, p, s, normal_events_list, reward_events_list):
        current_satiety, current_mood, total_explore_progress = s["宠物初始饱食度"], s["宠物初始心情"], 0
        run_results = {"total": 0, "perfect": 0, "success": 0, "failure": 0}
        run_total_drops, run_event_details = {}, []
        while current_satiety > 0:
            satiety_cost = p["饱食度消耗X"]
            if current_mood < p["低心情阈值"]: satiety_cost *= p["心情系数Z"]
            current_satiety -= satiety_cost
            if current_satiety <= 0: break
            run_results["total"] += 1
            current_event = None
            if total_explore_progress >= p["奖励事件触发阈值"] and reward_events_list:
                current_event = random.choice(reward_events_list); total_explore_progress = 0
            elif normal_events_list:
                current_event = random.choices(normal_events_list, weights=[e['SpawnWeight'] for e in normal_events_list], k=1)[0]
            else: break
            event_desc = f"  事件 {run_results['total']} (ID: {current_event.get('Id', 'N/A')}): "
            jar_id_to_use = None
            if pd.isna(current_event['Attr1']) or current_event['Attr1'] == 0: chosen_outcome = "success"
            else:
                w_perfect, w_success = p["大成功初始权重a"], p["成功初始权重b"]
                attr1_id, attr1_val = int(current_event['Attr1']), int(current_event['Attr1_value'])
                if pd.isna(current_event['Attr2']) or current_event['Attr2'] == 0:
                    rating_diff = pet_attrs_val[attr1_id] - attr1_val
                    w_perfect += rating_diff * p["大成功系数α"]; w_success += rating_diff * p["成功系数β"]
                else:
                    attr2_id, attr2_val = int(current_event['Attr2']), int(current_event['Attr2_value'])
                    avg_diff = ((pet_attrs_val[attr1_id] - attr1_val) + (pet_attrs_val[attr2_id] - attr2_val)) / 2.0
                    w_perfect += avg_diff * p["大成功系数α"] * p["双属性联结系数γ"]; w_success += avg_diff * p["成功系数β"] * p["双属性联结系数γ"]
                weights = [max(0, w_perfect), max(0, w_success), p["失败初始权重c"]]
                chosen_outcome = random.choices(["perfect", "success", "failure"], weights=weights, k=1)[0]
            run_results[chosen_outcome] += 1
            if chosen_outcome == "perfect": event_desc += "大成功"; jar_id_to_use = current_event.get('PerfectJarId')
            elif chosen_outcome == "success": event_desc += "成功"; jar_id_to_use = current_event.get('SuccessJarId')
            else: event_desc += "失败"; current_mood = max(0, current_mood - p["检定失败扣除心情Y"])
            run_event_details.append(event_desc)
            event_drops, drop_descs = self._process_drops(jar_id_to_use)
            if event_drops:
                run_event_details.extend(drop_descs)
                run_event_details.append(f"    -> (本次事件共掉落 {sum(event_drops.values())} 件物品)")
                for item_id, num in event_drops.items(): run_total_drops[item_id] = run_total_drops.get(item_id, 0) + num
            if pd.notna(current_event.get('ExploreProgress')):
                try: min_p, max_p = map(int, str(current_event['ExploreProgress']).split(',')); total_explore_progress += random.randint(min_p, max_p)
                except (ValueError, TypeError): total_explore_progress += int(current_event.get('ExploreProgress', 0))
        return run_results, run_total_drops, run_event_details
    def _format_drop_table(self, drop_dict, is_avg=False, sim_count=1):
        if not drop_dict: return ""
        table_data = []
        for item_id, total_num in sorted(drop_dict.items()):
            name = self._get_item_name(item_id)
            rarity_num = self._get_item_rarity(item_id)
            rarity_str = ITEM_RARITY_MAP.get(rarity_num, 'N/A') if rarity_num is not None else 'N/A'
            name_width = sum(2 if '\u4e00' <= char <= '\u9fff' else 1 for char in name)
            table_data.append({'name': name, 'rarity': rarity_str, 'id': str(item_id), 'num': f"{total_num / sim_count:.2f}" if is_avg else str(total_num), 'name_width': name_width})
        max_name_width = max(d['name_width'] for d in table_data) if table_data else 10
        max_id_width = max(len(d['id']) for d in table_data) if table_data else 7
        max_num_width = max(len(d['num']) for d in table_data) if table_data else 5
        header = (f"  {'物品名称':<{max_name_width-2}} | {'稀有度':^5} | {'物品ID':^{max_id_width}} | {( '平均数量' if is_avg else '数量'):>{max_num_width}}")
        separator = "  " + "-" * (len(header)-2)
        rows = [header, separator]
        for d in table_data: rows.append(f"  {d['name']}{' ' * (max_name_width - d['name_width'])} | {d['rarity']:^5} | {d['id']:^{max_id_width}} | {d['num']:>{max_num_width}}")
        return "\n".join(rows)
    def format_report(self, timestamp, pet_attrs, cumulative, cumulative_drops, individuals, sim_count, avg_success_rate):
        total_events = cumulative["total"]
        report_lines = [f"==================== 模拟报告 ({timestamp}) ===================="]
        report_lines.append(f"宠物属性: {pet_attrs}")
        if total_events == 0: report_lines.append("\n在所有模拟中，由于初始饱食度不足，未发生任何事件。")
        else:
            avg_total, avg_perfect, avg_success, avg_failure = total_events / sim_count, cumulative["perfect"] / sim_count, cumulative["success"] / sim_count, cumulative["failure"] / sim_count
            report_lines.append(f"\n--- 总体平均结果 ({sim_count}次模拟) ---")
            report_lines.append(f"平均每轮发生 {avg_total:.2f} 次事件，其中：")
            report_lines.append(f"【{avg_perfect:.2f}】次大成功, 【{avg_success:.2f}】次成功, 【{avg_failure:.2f}】次失败")
            report_lines.append(f"整体平均成功率: {avg_success_rate:.2%}")

            if cumulative_drops:
                report_lines.append("\n--- 平均掉落物汇总 (每轮) ---")
                # 初始化统计字典
                summary = {'S': 0, 'A': 0, 'B': 0, 'C': 0, 'D': 0, '食物': 0, '训练卡': 0}

                for item_id, total_num in cumulative_drops.items():
                    avg_num = total_num / sim_count
                    item_info = self.item_info_map.get(item_id)
                    if item_info:
                        # 按稀有度统计
                        rarity_str = ITEM_RARITY_MAP.get(item_info.get('Rarity'))
                        if rarity_str:
                            summary[rarity_str] += avg_num

                        # 按类型统计
                        item_type = item_info.get('Type')
                        if item_type == 2:
                            summary['食物'] += avg_num
                        elif item_type == 3:
                            summary['训练卡'] += avg_num

            # 格式化输出
            report_lines.append(f"  稀有度: S[{summary['S']:.2f}] A[{summary['A']:.2f}] B[{summary['B']:.2f}] C[{summary['C']:.2f}] D[{summary['D']:.2f}]")
            report_lines.append(f"  特  殊: 食物[{summary['食物']:.2f}] 训练卡[{summary['训练卡']:.2f}]")
            
            report_lines.append("\n--- 各次模拟详情 ---"); report_lines.extend(individuals)
        report_lines.append("=" * 60 + "\n"); return "\n".join(report_lines)
    def display_all_reports(self):
        self.output_text.config(state="normal")
        self.output_text.delete("1.0", tk.END)
        for item in self.all_simulation_data: self.output_text.insert(tk.END, item["report"] + "\n")
        self.output_text.config(state="disabled"); self.output_text.see("1.0")

if __name__ == "__main__":
    app = PetExplorerSimulator()
    app.mainloop()
