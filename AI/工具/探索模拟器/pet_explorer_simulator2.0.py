import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
import random
from datetime import datetime
import re # 导入正则表达式模块用于解析数量区间

# --- 数据结构与常量定义 (无变化) ---
RATING_MAP = {'S': 5, 'A': 4, 'B': 3, 'C': 2, 'D': 1}
ATTR_ID_MAP = {1: "力量", 2: "体质", 3: "敏捷", 4: "感知"}
REVERSE_ATTR_MAP = {v: k for k, v in ATTR_ID_MAP.items()}

class PetExplorerSimulator(tk.Tk):
    """
    宠物探索模拟器 v2.0 - “丰饶之获”掉落系统版
    内核: 在 v1.9 基础上，集成复杂的 DropJar 掉落系统。
    功能: 支持导入掉落表，根据事件结果（成功/大成功）触发对应掉落，并生成详细掉落报告。
    界面: 保持“护眼绿洲”设计。
    """
    def __init__(self):
        super().__init__()
        self.title("宠物探索模拟器 (v2.0 内核 | AI聊天机器人 '丰饶之获' 版)")
        self.geometry("980x1050")
        self.minsize(900, 800)

        # --- 色彩定义 (无变化) ---
        self.COLORS = {
            "bg_main": "#E9F5E9", "bg_frame": "#F1F8F1", "text_main": "#3E4A3E",
            "text_light": "#607D8B", "accent": "#4CAF50", "accent_fg": "#FFFFFF",
            "success": "#4CAF50", "failure": "#D9534F", "entry_bg": "#FFFFFF",
            "entry_fg": "#3E4A3E", "tree_heading": "#DDEEE0",
        }

        self.event_data = None
        self.drop_data = None # 【新增】用于存储掉落表数据
        self.all_simulation_data = []

        self.configure(bg=self.COLORS["bg_main"])
        self._configure_styles()
        self._create_widgets()
        self._bind_events()
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
        self.style.configure('TEntry', fieldbackground=self.COLORS["entry_bg"], foreground=self.COLORS["entry_fg"], insertcolor=self.COLORS["text_main"], bordercolor="#B0C4B0", relief="solid")
        self.style.map('TCombobox', fieldbackground=[('readonly', self.COLORS["entry_bg"])], selectbackground=[('readonly', self.COLORS["bg_frame"])], selectforeground=[('readonly', self.COLORS["text_main"])], bordercolor=[('readonly', "#B0C4B0")])
        self.option_add('*TCombobox*Listbox.background', self.COLORS["entry_bg"]); self.option_add('*TCombobox*Listbox.foreground', self.COLORS["text_main"])
        self.option_add('*TCombobox*Listbox.selectBackground', self.COLORS["accent"]); self.option_add('*TCombobox*Listbox.selectForeground', self.COLORS["accent_fg"])
        self.style.configure('TCheckbutton', background=self.COLORS["bg_frame"], foreground=self.COLORS["text_main"])
        self.style.map('TCheckbutton', indicatorcolor=[('selected', self.COLORS["accent"]), ('!selected', "#B0C4B0")])
        self.style.configure("Treeview.Heading", background=self.COLORS["tree_heading"], foreground=self.COLORS["accent"], font=font_bold, relief="flat")
        self.style.map("Treeview.Heading", background=[('active', self.COLORS["bg_frame"])])
        self.style.configure("Treeview", background=self.COLORS["entry_bg"], fieldbackground=self.COLORS["entry_bg"], foreground=self.COLORS["text_main"], rowheight=25)
        self.style.map('Treeview', background=[('selected', self.COLORS["accent"])], foreground=[('selected', self.COLORS["accent_fg"])])

    def _create_widgets(self):
        main_frame = ttk.Frame(self, padding="10", style='Main.TFrame')
        main_frame.pack(fill="both", expand=True, padx=5, pady=5)
        main_frame.columnconfigure(0, weight=1)
        
        # --- 区域1, 2, 3, 4 (无变化) ---
        # (代码与之前版本相同，为简洁此处省略)
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
            var = tk.StringVar(value=str(default_val))
            entry = ttk.Entry(params_frame, width=10, textvariable=var)
            entry.grid(row=row, column=col*2+1, padx=(0,20), pady=5)
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
        prob_settings_frame = ttk.Frame(prob_frame); prob_settings_frame.pack(fill="x", pady=(0, 10))
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
        button_frame.grid(row=0, column=0, rowspan=3, padx=(0, 20)) # rowspan 改为 3
        self.import_event_button = ttk.Button(button_frame, text="📂 导入事件表", command=self.import_event_data)
        self.import_event_button.pack(fill='x')
        # 【新增】导入掉落表按钮
        self.import_drop_button = ttk.Button(button_frame, text="🎁 导入掉落表", command=self.import_drop_data)
        self.import_drop_button.pack(fill='x', pady=5)
        self.start_button = ttk.Button(button_frame, text="▶️ 开始完整模拟", command=self.start_simulation)
        self.start_button.pack(fill='x')
        
        status_filter_frame = ttk.Frame(control_frame)
        status_filter_frame.grid(row=0, column=1, rowspan=3, sticky='nsew') # rowspan 改为 3
        status_filter_frame.columnconfigure(1, weight=1)
        self.event_status_label = ttk.Label(status_filter_frame, text="事件表状态: 未导入", style="Failure.TLabel")
        self.event_status_label.grid(row=0, column=0, columnspan=2, sticky="w", pady=(0,5))
        # 【新增】掉落表状态标签
        self.drop_status_label = ttk.Label(status_filter_frame, text="掉落表状态: 未导入", style="Failure.TLabel")
        self.drop_status_label.grid(row=1, column=0, columnspan=2, sticky="w", pady=(0,10))
        ttk.Label(status_filter_frame, text="🔍 筛选报告:").grid(row=2, column=0, padx=(0, 5), sticky='w')
        self.filter_combo = ttk.Combobox(status_filter_frame, state="readonly")
        self.filter_combo.grid(row=2, column=1, sticky="ew")

        # --- 区域6, 7 (无变化) ---
        # (代码与之前版本相同，为简洁此处省略)
        self.selected_params_frame = ttk.LabelFrame(main_frame, text="🏷️ 区域6: 选中报告的参数", padding="15")
        self.selected_params_frame.grid(row=5, column=0, sticky="ew", pady=10)
        self.param_placeholder_label = ttk.Label(self.selected_params_frame, text="ℹ️ 请从上方筛选报告以查看其详细参数。", style="Placeholder.TLabel")
        self.param_placeholder_label.pack(pady=10)
        output_frame = ttk.LabelFrame(main_frame, text="📜 区域7: 完整模拟结果", padding=(15,10))
        output_frame.grid(row=6, column=0, sticky="nsew", pady=(10, 0))
        main_frame.rowconfigure(6, weight=1)
        output_frame.columnconfigure(0, weight=1); output_frame.rowconfigure(0, weight=1)
        self.output_text = tk.Text(output_frame, wrap="word", height=10, state="disabled", bg=self.COLORS["entry_bg"], fg=self.COLORS["text_main"], relief="solid", bd=1, highlightthickness=0, font=('Consolas', 10))
        self.output_text.configure(borderwidth=1, relief="solid")
        scrollbar = ttk.Scrollbar(output_frame, orient="vertical", command=self.output_text.yview)
        self.output_text.configure(yscrollcommand=scrollbar.set)
        self.output_text.grid(row=0, column=0, sticky="nsew"); scrollbar.grid(row=0, column=1, sticky="ns")

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
            result_text = f"大成功: {prob_perfect:.2%}  |  成功: {prob_success:.2%}  |  总成功率: {prob_perfect+prob_success:.2%}  |  失败: {prob_failure:.2%}"
            self.prob_result_label.config(text=result_text, style="Accent.TLabel")
        except (ValueError, KeyError): self.prob_result_label.config(text="等待输入有效的核心参数...", style="Placeholder.TLabel")
        except Exception as e: self.prob_result_label.config(text=f"计算错误: {e}", style="Failure.TLabel")

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

    def _import_data_generic(self, title, file_types):
        file_path = filedialog.askopenfilename(title=title, filetypes=file_types)
        if not file_path: return None
        try:
            return pd.read_csv(file_path) if file_path.endswith('.csv') else pd.read_excel(file_path)
        except Exception as e:
            messagebox.showerror("错误", f"导入文件失败: {e}")
            return None

    def import_event_data(self):
        df = self._import_data_generic("请选择事件表文件", [("Excel files", "*.xlsx *.xls"), ("CSV files", "*.csv")])
        if df is not None:
            self.event_data = df
            self.event_data[['Attr1', 'Attr2']] = self.event_data[['Attr1', 'Attr2']].fillna(0)
            self.event_status_label.config(text=f"✔ 事件表状态: 已导入 {len(self.event_data)} 条", style="Success.TLabel")

    def import_drop_data(self):
        df = self._import_data_generic("请选择掉落表文件 (DropJar)", [("Excel files", "*.xlsx *.xls"), ("CSV files", "*.csv")])
        if df is not None:
            self.drop_data = df
            self.drop_status_label.config(text=f"✔ 掉落表状态: 已导入 {len(self.drop_data)} 条", style="Success.TLabel")

    # --- 【全新】掉落核心逻辑 ---
    def _parse_num(self, num_str):
        """解析数量字符串，支持 '3' 或 '1-5' 或 '2,5' 格式"""
        num_str = str(num_str).strip()
        match = re.match(r'(\d+)[-,]?(\d+)?', num_str)
        if match:
            start = int(match.group(1))
            end = int(match.group(2)) if match.group(2) else start
            return random.randint(min(start, end), max(start, end))
        return 0 # 格式错误则返回0

    def _process_drops(self, jar_id):
        """根据JarId处理掉落，返回掉落物字典和描述字符串列表"""
        if self.drop_data is None or pd.isna(jar_id) or int(jar_id) == 0:
            return {}, []

        drops = {}
        drop_descriptions = []
        
        try:
            # 筛选出对应JarId的所有掉落规则
            jar_rules = self.drop_data[self.drop_data['JarId'] == int(jar_id)]
            if jar_rules.empty:
                return {}, []

            # 按权重分组进行处理
            for group_id, group_df in jar_rules.groupby('WeightGroup'):
                drop_times = int(group_df['DropTimes'].iloc[0])
                
                # 执行多次掉落（放回式）
                for _ in range(drop_times):
                    # 在组内根据权重随机选择一个物品
                    chosen_item = group_df.sample(n=1, weights='Weight').iloc[0]
                    item_id = int(chosen_item['ItemId'])
                    num = self._parse_num(chosen_item['Num'])
                    
                    if num > 0:
                        # 累加到总掉落字典
                        drops[item_id] = drops.get(item_id, 0) + num
                        # 记录本次掉落描述
                        drop_descriptions.append(f"    -> 获得物品 {item_id} x {num}")

        except Exception as e:
            print(f"处理掉落时发生错误 (JarId: {jar_id}): {e}")
            # 可以选择在报告中显示错误信息
            drop_descriptions.append(f"    -> !掉落处理异常: {e}")

        return drops, drop_descriptions

    def _run_single_simulation(self, pet_attrs_val, p, s, normal_events_list, reward_events_list):
        current_satiety, current_mood, total_explore_progress = s["宠物初始饱食度"], s["宠物初始心情"], 0
        run_results = {"total": 0, "perfect": 0, "success": 0, "failure": 0}
        run_total_drops = {} # 【新增】单次模拟的总掉落
        run_event_details = [] # 【新增】单次模拟的事件详情

        while current_satiety > 0:
            satiety_cost = p["饱食度消耗X"]
            if current_mood < p["低心情阈值"]: satiety_cost *= p["心情系数Z"]
            current_satiety -= satiety_cost
            if current_satiety <= 0: break
            
            event_num = run_results["total"] + 1
            run_results["total"] += 1
            
            current_event = None
            if total_explore_progress >= p["奖励事件触发阈值"] and reward_events_list:
                current_event = random.choice(reward_events_list); total_explore_progress = 0
            elif normal_events_list:
                current_event = random.choices(normal_events_list, weights=[e['SpawnWeight'] for e in normal_events_list], k=1)[0]
            else: break

            event_id = current_event.get('Id', 'N/A')
            event_desc = f"  事件 {event_num} (ID: {event_id}): "
            
            # --- 检定与掉落逻辑 ---
            jar_id_to_use = None
            if pd.isna(current_event['Attr1']) or current_event['Attr1'] == 0:
                chosen_outcome = "success"
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
            
            if chosen_outcome == "perfect":
                event_desc += "大成功"
                jar_id_to_use = current_event.get('PerfectJarId')
            elif chosen_outcome == "success":
                event_desc += "成功"
                jar_id_to_use = current_event.get('SuccessJarId')
            else: # failure
                event_desc += "失败"
                current_mood = max(0, current_mood - p["检定失败扣除心情Y"])

            run_event_details.append(event_desc)
            
            # 处理掉落
            event_drops, drop_descs = self._process_drops(jar_id_to_use)
            if event_drops:
                run_event_details.extend(drop_descs) # 将掉落详情加入事件日志
                for item_id, num in event_drops.items():
                    run_total_drops[item_id] = run_total_drops.get(item_id, 0) + num

            if pd.notna(current_event.get('ExploreProgress')):
                try: min_p, max_p = map(int, str(current_event['ExploreProgress']).split(',')); total_explore_progress += random.randint(min_p, max_p)
                except (ValueError, TypeError): total_explore_progress += int(current_event.get('ExploreProgress', 0))
        
        return run_results, run_total_drops, run_event_details

    def start_simulation(self):
        if self.event_data is None: messagebox.showwarning("警告", "请先导入事件表！"); return
        if self.drop_data is None: messagebox.showwarning("警告", "请先导入掉落表！"); return
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
            cumulative_total_drops = {}
            individual_run_outputs = []
            
            normal_events = self.event_data[self.event_data['Type'] == 1].copy()
            reward_events = self.event_data[self.event_data['Type'] == 2].copy()
            if 'SpawnWeight' not in normal_events.columns or normal_events['SpawnWeight'].isnull().any(): raise ValueError("普通事件中存在无效的'SpawnWeight'值")
            normal_events_list = normal_events.to_dict('records'); reward_events_list = reward_events.to_dict('records')
            
            for i in range(simulation_count):
                run_results, run_total_drops, run_event_details = self._run_single_simulation(pet_attrs_val, p, s, normal_events_list, reward_events_list)
                
                for key in cumulative_results: cumulative_results[key] += run_results[key]
                for item_id, num in run_total_drops.items():
                    cumulative_total_drops[item_id] = cumulative_total_drops.get(item_id, 0) + num
                
                success_rate = (run_results["perfect"] + run_results["success"]) / run_results["total"] if run_results["total"] > 0 else 0
                
                # 构建单次模拟的详细报告
                run_report = [f"--- 第 {i+1:02d} 次模拟 (成功率: {success_rate:.2%}) ---"]
                run_report.extend(run_event_details)
                if run_total_drops:
                    sorted_drops = sorted(run_total_drops.items())
                    drop_summary = ", ".join([f"物品{k}: {v}个" for k, v in sorted_drops])
                    run_report.append(f"  本轮总掉落: {drop_summary}")
                else:
                    run_report.append("  本轮无掉落。")
                individual_run_outputs.append("\n".join(run_report))

            total_events = cumulative_results["total"]
            avg_success_rate = (cumulative_results["perfect"] + cumulative_results["success"]) / total_events if total_events > 0 else 0
            display_label = f"{timestamp_key} [{pet_attrs_brief}] [成功率: {avg_success_rate:.2%}]"
            full_report_str = self.format_report(timestamp_key, pet_attrs_full, cumulative_results, cumulative_total_drops, individual_run_outputs, simulation_count, avg_success_rate)
            self.all_simulation_data.insert(0, {"id": timestamp_key, "label": display_label, "report": full_report_str, "parameters": p, "avg_success_rate": avg_success_rate})
            self.update_filter_options()
            self.filter_combo.set(display_label)
            self.on_filter_selected()
        except Exception as e: messagebox.showerror("模拟出错", f"执行模拟时发生错误: {e}")

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
            
            # 【新增】总掉落物汇总
            if cumulative_drops:
                report_lines.append("\n--- 平均掉落物汇总 (每轮) ---")
                sorted_drops = sorted(cumulative_drops.items())
                drop_summary = []
                for item_id, total_num in sorted_drops:
                    avg_num = total_num / sim_count
                    drop_summary.append(f"物品 {item_id}: {avg_num:.2f} 个")
                report_lines.append(", ".join(drop_summary))
            
            report_lines.append("\n--- 各次模拟详情 ---"); report_lines.extend(individuals)
        report_lines.append("=" * 60 + "\n"); return "\n".join(report_lines)

    def update_filter_options(self):
        options = ["显示全部"] + [item["label"] for item in self.all_simulation_data]
        self.filter_combo['values'] = options

    def on_filter_selected(self, event=None):
        selection = self.filter_combo.get()
        self.output_text.config(state="normal")
        self.output_text.delete("1.0", tk.END)
        if selection == "显示全部" or not selection:
            self.display_all_reports(); self._update_selected_params_display(None)
        else:
            found = False
            for item in self.all_simulation_data:
                if item["label"] == selection:
                    self.output_text.insert(tk.END, item["report"])
                    self._update_selected_params_display(item["parameters"])
                    found = True; break
            if not found: self.display_all_reports(); self._update_selected_params_display(None)
        self.output_text.config(state="disabled")

    def display_all_reports(self):
        self.output_text.config(state="normal")
        self.output_text.delete("1.0", tk.END)
        for item in self.all_simulation_data: self.output_text.insert(tk.END, item["report"] + "\n")
        self.output_text.config(state="disabled"); self.output_text.see("1.0")

if __name__ == "__main__":
    app = PetExplorerSimulator()
    app.mainloop()
