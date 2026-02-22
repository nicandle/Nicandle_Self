import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
import random
from datetime import datetime

# --- 数据结构与常量定义 (无变化) ---
RATING_MAP = {'S': 5, 'A': 4, 'B': 3, 'C': 2, 'D': 1}
ATTR_ID_MAP = {1: "力量", 2: "体质", 3: "敏捷", 4: "感知"}
REVERSE_ATTR_MAP = {v: k for k, v in ATTR_ID_MAP.items()}

class PetExplorerSimulator(tk.Tk):
    """
    宠物探索模拟器 v1.9 - “护眼绿洲”设计版
    内核: 继承 v1.7/v1.8 的全部功能。
    界面: 全新设计的护眼主题，采用柔和的豆沙绿色调，提供舒适、宁静的视觉体验。
    """
    def __init__(self):
        super().__init__()
        self.title("宠物探索模拟器 (v1.9 内核 | AI聊天机器人 '护眼绿洲' 版)")
        self.geometry("980x1050")
        self.minsize(900, 800)

        # --- 【新增】护眼色彩定义 ---
        self.COLORS = {
            "bg_main": "#E9F5E9",       # 主背景 (非常柔和的淡绿色)
            "bg_frame": "#F1F8F1",      # 框架背景 (比主背景稍亮的白色感绿)
            "text_main": "#3E4A3E",      # 主文本 (深灰绿色)
            "text_light": "#607D8B",     # 辅文本/占位符 (蓝灰色)
            "accent": "#4CAF50",        # 主题色/高亮 (温和的绿色)
            "accent_fg": "#FFFFFF",     # 主题色上的文字 (白色)
            "success": "#4CAF50",        # 成功 (与主题色一致)
            "failure": "#D9534F",        # 失败 (柔和的红色)
            "entry_bg": "#FFFFFF",      # 输入框背景 (白色)
            "entry_fg": "#3E4A3E",      # 输入框文字
            "tree_heading": "#DDEEE0",  # 表头背景 (稍深的淡绿)
        }

        self.event_data = None
        self.all_simulation_data = []

        self.configure(bg=self.COLORS["bg_main"])
        self._configure_styles()
        self._create_widgets()
        self._bind_events()
        self.after(100, self.calculate_probabilities)

# ... 省略前面的代码 ...

    def _configure_styles(self):
        """【全新】配置“护眼绿洲”主题样式"""
        self.style = ttk.Style(self)
        self.style.theme_use('clam')

        # --- 全局配置 ---
        font_normal = ('Microsoft YaHei UI', 10)
        font_bold = ('Microsoft YaHei UI', 10, 'bold')
        
        # --- 控件样式定义 ---
        self.style.configure('.', 
            background=self.COLORS["bg_main"], 
            foreground=self.COLORS["text_main"], 
            font=font_normal,
            fieldbackground=self.COLORS["entry_bg"],
            troughcolor=self.COLORS["bg_frame"])

        self.style.configure('TFrame', background=self.COLORS["bg_frame"])
        self.style.configure('Main.TFrame', background=self.COLORS["bg_main"]) # <--- 【新增】为 main_frame 定义专属样式

        self.style.configure('TLabelframe', 
            background=self.COLORS["bg_frame"], 
            borderwidth=1, 
            relief="solid",
            bordercolor="#D0E0D0")
        # ... 其他样式配置不变 ...

    def _create_widgets(self):
        """【界面重构】应用新样式和布局"""
        # --- 【修改】使用新的 'Main.TFrame' 样式并删除错误行 ---
        main_frame = ttk.Frame(self, padding="10", style='Main.TFrame')
        main_frame.pack(fill="both", expand=True, padx=5, pady=5)
        main_frame.columnconfigure(0, weight=1)

 
        # --- 区域1: 宠物属性面板 ---
        pet_attr_frame = ttk.LabelFrame(main_frame, text="🐾 区域1: 宠物属性 (用于模拟与速查)", padding="15")
        pet_attr_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        self.pet_attrs = {}
        ratings = list(RATING_MAP.keys())
        for i, (attr_id, attr_name) in enumerate(ATTR_ID_MAP.items()):
            ttk.Label(pet_attr_frame, text=f"{attr_name}:").grid(row=0, column=i*2, padx=(0,5), pady=5, sticky="w")
            combo = ttk.Combobox(pet_attr_frame, values=ratings, width=5, state="readonly")
            combo.set("D"); combo.grid(row=0, column=i*2+1, padx=(0,20), pady=5)
            self.pet_attrs[attr_id] = combo

        # --- 区域2: 核心参数 ---
        params_frame = ttk.LabelFrame(main_frame, text="⚙️ 区域2: 核心参数 (用于模拟与速查)", padding="15")
        params_frame.grid(row=1, column=0, sticky="ew", pady=10)
        self.params = {}
        self.param_definitions = {
            "模拟次数": 10, "饱食度消耗X": 5, "检定失败扣除心情Y": 10, "心情系数Z": 3, 
            "大成功初始权重a": 15, "成功初始权重b": 65, "失败初始权重c": 35, "大成功系数α": 20, 
            "成功系数β": 10, "双属性联结系数γ": 0.7, "低心情阈值": 30, "奖励事件触发阈值": 100
        }
        for i, (name, default_val) in enumerate(self.param_definitions.items()):
            row, col = divmod(i, 4)
            ttk.Label(params_frame, text=f"{name}:").grid(row=row, column=col*2, padx=(0,5), pady=5, sticky="w")
            entry = ttk.Entry(params_frame, width=10); entry.insert(0, str(default_val))
            entry.grid(row=row, column=col*2+1, padx=(0,20), pady=5)
            self.params[name] = entry
        # +++ 新代码 (修正后) +++
        for i, (name, default_val) in enumerate(self.param_definitions.items()):
            row, col = divmod(i, 4)
            ttk.Label(params_frame, text=f"{name}:").grid(row=row, column=col*2, padx=(0,5), pady=5, sticky="w")

            # 1. 创建一个 StringVar
            var = tk.StringVar(value=str(default_val))

            # 2. 将 Entry 与 StringVar 关联
            entry = ttk.Entry(params_frame, width=10, textvariable=var)
            entry.grid(row=row, column=col*2+1, padx=(0,20), pady=5)

            # 3. 在字典中存储 StringVar 而不是 Entry 控件本身
            self.params[name] = var

        # --- 区域3: 宠物初始状态 ---
        initial_state_frame = ttk.LabelFrame(main_frame, text="🏁 区域3: 宠物初始状态 (仅用于模拟)", padding="15")
        initial_state_frame.grid(row=2, column=0, sticky="ew", pady=10)
        self.initial_states = {}
        state_definitions = {"宠物初始心情": 100, "宠物初始饱食度": 100}
        for i, (name, default_val) in enumerate(state_definitions.items()):
            ttk.Label(initial_state_frame, text=f"{name}:").grid(row=0, column=i*2, padx=(0,5), pady=5, sticky="w")
            entry = ttk.Entry(initial_state_frame, width=12); entry.insert(0, str(default_val))
            entry.grid(row=0, column=i*2+1, padx=(0,20), pady=5)
            self.initial_states[name] = entry

        # --- 区域4: 检定概率速查 ---
        prob_frame = ttk.LabelFrame(main_frame, text="🔬 区域4: 检定概率速查 (实时分析)", padding="15")
        prob_frame.grid(row=3, column=0, sticky="ew", pady=10)
        prob_frame.columnconfigure(0, weight=1)
        
        prob_settings_frame = ttk.Frame(prob_frame)
        prob_settings_frame.pack(fill="x", pady=(0, 10))
        
        self.is_dual_attr = tk.BooleanVar(value=False)
        dual_check = ttk.Checkbutton(prob_settings_frame, text="双属性检定", variable=self.is_dual_attr)
        dual_check.grid(row=0, column=0, padx=(0, 20))
        ttk.Label(prob_settings_frame, text="属性1:").grid(row=0, column=1)
        self.prob_attr1_combo = ttk.Combobox(prob_settings_frame, values=list(ATTR_ID_MAP.values()), width=6, state="readonly")
        self.prob_attr1_combo.set("力量"); self.prob_attr1_combo.grid(row=0, column=2, padx=(2,5))
        ttk.Label(prob_settings_frame, text="要求:").grid(row=0, column=3)
        self.prob_rating1_combo = ttk.Combobox(prob_settings_frame, values=list(RATING_MAP.keys()), width=4, state="readonly")
        self.prob_rating1_combo.set("B"); self.prob_rating1_combo.grid(row=0, column=4, padx=(2,15))
        self.prob_attr2_label = ttk.Label(prob_settings_frame, text="属性2:")
        self.prob_attr2_combo = ttk.Combobox(prob_settings_frame, values=list(ATTR_ID_MAP.values()), width=6, state="readonly")
        self.prob_attr2_combo.set("体质")
        self.prob_rating2_label = ttk.Label(prob_settings_frame, text="要求:")
        self.prob_rating2_combo = ttk.Combobox(prob_settings_frame, values=list(RATING_MAP.keys()), width=4, state="readonly")
        self.prob_rating2_combo.set("B")

        self.prob_result_label = ttk.Label(prob_frame, text="请在上方设置检定场景...", style="Placeholder.TLabel", font=('Microsoft YaHei UI', 11, 'bold'))
        self.prob_result_label.pack(pady=10)
        self._toggle_dual_attr_view()

        # --- 区域5: 控制与筛选 ---
        control_frame = ttk.LabelFrame(main_frame, text="🎛️ 区域5: 模拟控制与报告筛选", padding="15")
        control_frame.grid(row=4, column=0, sticky="ew", pady=10)
        control_frame.columnconfigure(1, weight=1)
        
        button_frame = ttk.Frame(control_frame)
        button_frame.grid(row=0, column=0, rowspan=2, padx=(0, 20))
        self.import_button = ttk.Button(button_frame, text="📂 导入事件表", command=self.import_data)
        self.import_button.pack(fill='x')
        self.start_button = ttk.Button(button_frame, text="▶️ 开始完整模拟", command=self.start_simulation)
        self.start_button.pack(fill='x', pady=(5,0))
        
        status_filter_frame = ttk.Frame(control_frame)
        status_filter_frame.grid(row=0, column=1, rowspan=2, sticky='nsew')
        status_filter_frame.columnconfigure(1, weight=1)
        self.import_status_label = ttk.Label(status_filter_frame, text="状态: 未导入数据", style="Failure.TLabel")
        self.import_status_label.grid(row=0, column=0, columnspan=2, sticky="w", pady=(0,10))
        ttk.Label(status_filter_frame, text="🔍 筛选报告:").grid(row=1, column=0, padx=(0, 5), sticky='w')
        self.filter_combo = ttk.Combobox(status_filter_frame, state="readonly")
        self.filter_combo.grid(row=1, column=1, sticky="ew")

        # --- 区域6: 选中报告的参数 ---
        self.selected_params_frame = ttk.LabelFrame(main_frame, text="🏷️ 区域6: 选中报告的参数", padding="15")
        self.selected_params_frame.grid(row=5, column=0, sticky="ew", pady=10)
        self.param_placeholder_label = ttk.Label(self.selected_params_frame, text="ℹ️ 请从上方筛选报告以查看其详细参数。", style="Placeholder.TLabel")
        self.param_placeholder_label.pack(pady=10)

        # --- 区域7: 模拟结果 ---
        output_frame = ttk.LabelFrame(main_frame, text="📜 区域7: 完整模拟结果", padding=(15,10))
        output_frame.grid(row=6, column=0, sticky="nsew", pady=(10, 0))
        main_frame.rowconfigure(6, weight=1)
        output_frame.columnconfigure(0, weight=1); output_frame.rowconfigure(0, weight=1)
        self.output_text = tk.Text(output_frame, wrap="word", height=10, state="disabled", 
                                   bg=self.COLORS["entry_bg"], fg=self.COLORS["text_main"], 
                                   relief="solid", bd=1, highlightthickness=0,
                                   font=('Consolas', 10))
        self.output_text.configure(borderwidth=1, relief="solid")
        scrollbar = ttk.Scrollbar(output_frame, orient="vertical", command=self.output_text.yview)
        self.output_text.configure(yscrollcommand=scrollbar.set)
        self.output_text.grid(row=0, column=0, sticky="nsew"); scrollbar.grid(row=0, column=1, sticky="ns")

    # --- 以下所有逻辑函数均与 v1.7/v1.8 版本完全相同，无需修改 ---
    def _bind_events(self):
        for combo in self.pet_attrs.values(): combo.bind("<<ComboboxSelected>>", self.calculate_probabilities)
        for var in self.params.values(): var.trace_add("write", self.calculate_probabilities)
        self.prob_attr1_combo.bind("<<ComboboxSelected>>", self.calculate_probabilities)
        self.prob_rating1_combo.bind("<<ComboboxSelected>>", self.calculate_probabilities)
        self.prob_attr2_combo.bind("<<ComboboxSelected>>", self.calculate_probabilities)
        self.prob_rating2_combo.bind("<<ComboboxSelected>>", self.calculate_probabilities)
        self.is_dual_attr.trace_add("write", self.calculate_probabilities)
        self.filter_combo.bind("<<ComboboxSelected>>", self.on_filter_selected)

    def _toggle_dual_attr_view(self):
        if self.is_dual_attr.get():
            self.prob_attr2_label.grid(row=0, column=5); self.prob_attr2_combo.grid(row=0, column=6, padx=(2,5))
            self.prob_rating2_label.grid(row=0, column=7); self.prob_rating2_combo.grid(row=0, column=8, padx=(2,5))
        else:
            self.prob_attr2_label.grid_remove(); self.prob_attr2_combo.grid_remove()
            self.prob_rating2_label.grid_remove(); self.prob_rating2_combo.grid_remove()
        self.calculate_probabilities()

    def calculate_probabilities(self, *args):
        try:
            p = {name: float(var.get()) for name, var in self.params.items()}
            pet_attrs_val = {attr_id: RATING_MAP[combo.get()] for attr_id, combo in self.pet_attrs.items()}
            attr1_name = self.prob_attr1_combo.get(); attr1_req_str = self.prob_rating1_combo.get()
            attr1_id = REVERSE_ATTR_MAP[attr1_name]; attr1_req_val = RATING_MAP[attr1_req_str]
            w_perfect, w_success = p["大成功初始权重a"], p["成功初始权重b"]
            if self.is_dual_attr.get():
                attr2_name = self.prob_attr2_combo.get(); attr2_req_str = self.prob_rating2_combo.get()
                if attr1_name == attr2_name:
                    self.prob_result_label.config(text="错误: 双属性检定不能选择相同的属性。", style="Failure.TLabel"); return
                attr2_id = REVERSE_ATTR_MAP[attr2_name]; attr2_req_val = RATING_MAP[attr2_req_str]
                avg_diff = ((pet_attrs_val[attr1_id] - attr1_req_val) + (pet_attrs_val[attr2_id] - attr2_req_val)) / 2.0
                w_perfect += avg_diff * p["大成功系数α"] * p["双属性联结系数γ"]
                w_success += avg_diff * p["成功系数β"] * p["双属性联结系数γ"]
            else:
                rating_diff = pet_attrs_val[attr1_id] - attr1_req_val
                w_perfect += rating_diff * p["大成功系数α"]; w_success += rating_diff * p["成功系数β"]
            weights = [max(0, w_perfect), max(0, w_success), p["失败初始权重c"]]
            total_weight = sum(weights)
            if total_weight > 0:
                prob_perfect = weights[0] / total_weight; prob_success = weights[1] / total_weight; prob_failure = weights[2] / total_weight
            else:
                prob_perfect, prob_success, prob_failure = 0, 0, 1
            result_text = f"总成功率: {prob_perfect+prob_success:.2%}  |  大成功: {prob_perfect:.2%}  |  成功: {prob_success:.2%}  |  失败: {prob_failure:.2%}"
            self.prob_result_label.config(text=result_text, style="Accent.TLabel")
        except (ValueError, KeyError):
            self.prob_result_label.config(text="等待输入有效的核心参数...", style="Placeholder.TLabel")
        except Exception as e:
            self.prob_result_label.config(text=f"计算错误: {e}", style="Failure.TLabel")

    def _update_selected_params_display(self, params_dict=None):
        for widget in self.selected_params_frame.winfo_children(): widget.destroy()
        if params_dict is None:
            self.param_placeholder_label = ttk.Label(self.selected_params_frame, text="ℹ️ 请从上方筛选报告以查看其详细参数。", style="Placeholder.TLabel")
            self.param_placeholder_label.pack(pady=10)
        else:
            for i, (name, value) in enumerate(params_dict.items()):
                row, col = divmod(i, 4)
                ttk.Label(self.selected_params_frame, text=f"{name}:").grid(row=row, column=col*2, padx=(0,5), pady=5, sticky="w")
                ttk.Label(self.selected_params_frame, text=f"{value}", font=('Microsoft YaHei UI', 9, 'bold')).grid(row=row, column=col*2+1, padx=(0,20), pady=5, sticky="w")

    def import_data(self):
        file_path = filedialog.askopenfilename(title="请选择事件表文件", filetypes=[("Excel files", "*.xlsx *.xls"), ("CSV files", "*.csv"), ("All files", "*.*")])
        if not file_path: return
        try:
            self.event_data = pd.read_csv(file_path) if file_path.endswith('.csv') else pd.read_excel(file_path)
            self.event_data[['Attr1', 'Attr2']] = self.event_data[['Attr1', 'Attr2']].fillna(0)
            self.import_status_label.config(text=f"✔ 状态: 已成功导入 {len(self.event_data)} 条事件", style="Success.TLabel")
        except Exception as e:
            messagebox.showerror("错误", f"导入文件失败: {e}"); self.event_data = None
            self.import_status_label.config(text=f"✖ 状态: 导入失败", style="Failure.TLabel")

    def _run_single_simulation(self, pet_attrs_val, p, s, normal_events_list, reward_events_list):
        current_satiety, current_mood, total_explore_progress = s["宠物初始饱食度"], s["宠物初始心情"], 0
        run_results = {"total": 0, "perfect": 0, "success": 0, "failure": 0}
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
            if pd.isna(current_event['Attr1']) or current_event['Attr1'] == 0: run_results["success"] += 1
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
                if chosen_outcome == "failure": current_mood = max(0, current_mood - p["检定失败扣除心情Y"])
            if pd.notna(current_event.get('ExploreProgress')):
                try: min_p, max_p = map(int, str(current_event['ExploreProgress']).split(',')); total_explore_progress += random.randint(min_p, max_p)
                except (ValueError, TypeError): total_explore_progress += int(current_event.get('ExploreProgress', 0))
        return run_results

    def start_simulation(self):
        if self.event_data is None: messagebox.showwarning("警告", "请先导入事件表！"); return
        try:
            pet_attrs_val = {attr_id: RATING_MAP[combo.get()] for attr_id, combo in self.pet_attrs.items()}
            p = {name: float(var.get()) for name, var in self.params.items()}
            s = {name: int(entry.get()) for name, entry in self.initial_states.items()}
            simulation_count = int(p["模拟次数"])
            if simulation_count <= 0: messagebox.showerror("输入错误", "模拟次数必须 > 0"); return
        except (ValueError, KeyError): messagebox.showerror("输入错误", "参数或初始状态必须为有效数字！"); return
        try:
            timestamp_key = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            pet_attrs_brief = " ".join([f"{ATTR_ID_MAP[k][0]}:{v.get()}" for k, v in self.pet_attrs.items()])
            pet_attrs_full = " ".join([f"{ATTR_ID_MAP[k]}:{v.get()}" for k, v in self.pet_attrs.items()])
            cumulative_results = {"total": 0, "perfect": 0, "success": 0, "failure": 0}
            individual_run_outputs = []
            normal_events = self.event_data[self.event_data['Type'] == 1].copy()
            reward_events = self.event_data[self.event_data['Type'] == 2].copy()
            if 'SpawnWeight' not in normal_events.columns or normal_events['SpawnWeight'].isnull().any(): raise ValueError("普通事件中存在无效的'SpawnWeight'值")
            normal_events_list = normal_events.to_dict('records'); reward_events_list = reward_events.to_dict('records')
            for i in range(simulation_count):
                run_results = self._run_single_simulation(pet_attrs_val, p, s, normal_events_list, reward_events_list)
                for key in cumulative_results: cumulative_results[key] += run_results[key]
                success_rate = (run_results["perfect"] + run_results["success"]) / run_results["total"] if run_results["total"] > 0 else 0
                individual_run_outputs.append(f"第 {i+1:02d} 次: 总事件 {run_results['total']}, 大成功 {run_results['perfect']}, 成功 {run_results['success']}, 失败 {run_results['failure']} (成功率: {success_rate:.2%})")
            total_events = cumulative_results["total"]
            avg_success_rate = (cumulative_results["perfect"] + cumulative_results["success"]) / total_events if total_events > 0 else 0
            display_label = f"{timestamp_key} [{pet_attrs_brief}] [成功率: {avg_success_rate:.2%}]"
            full_report_str = self.format_report(timestamp_key, pet_attrs_full, cumulative_results, individual_run_outputs, simulation_count, avg_success_rate)
            self.all_simulation_data.insert(0, {"id": timestamp_key, "label": display_label, "report": full_report_str, "parameters": p, "avg_success_rate": avg_success_rate})
            self.update_filter_options()
            self.filter_combo.set(display_label)
            self.on_filter_selected()
        except Exception as e: messagebox.showerror("模拟出错", f"执行模拟时发生错误: {e}")

    def format_report(self, timestamp, pet_attrs, cumulative, individuals, sim_count, avg_success_rate):
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
            report_lines.append("\n--- 各次模拟简报 ---"); report_lines.extend(individuals)
        report_lines.append("=" * 60 + "\n"); return "\n".join(report_lines)

    def update_filter_options(self):
        options = ["显示全部"] + [item["label"] for item in self.all_simulation_data]
        self.filter_combo['values'] = options

    def on_filter_selected(self, event=None):
        selection = self.filter_combo.get()
        self.output_text.config(state="normal")
        self.output_text.delete("1.0", tk.END)
        if selection == "显示全部" or not selection:
            self.display_all_reports()
            self._update_selected_params_display(None)
        else:
            found = False
            for item in self.all_simulation_data:
                if item["label"] == selection:
                    self.output_text.insert(tk.END, item["report"])
                    self._update_selected_params_display(item["parameters"])
                    found = True
                    break
            if not found:
                 self.display_all_reports()
                 self._update_selected_params_display(None)
        self.output_text.config(state="disabled")

    def display_all_reports(self):
        self.output_text.config(state="normal")
        self.output_text.delete("1.0", tk.END)
        for item in self.all_simulation_data:
            self.output_text.insert(tk.END, item["report"] + "\n")
        self.output_text.config(state="disabled")
        self.output_text.see("1.0")

if __name__ == "__main__":
    app = PetExplorerSimulator()
    app.mainloop()
