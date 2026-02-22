import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
import os
import sys
import subprocess
from datetime import datetime
import glob
import re
import webbrowser

# --- 全局变量与配置 ---
APP_NAME = "多语言工具 by AI聊天机器人 (V6.3)"
CONFIG_FILE = "tool_config.txt"
TRANSLATION_URL = "https://transify.garena.com/resources/4290/lang/5"
TRANSIFY_URL = "https://transify.garena.com/resources/4290/lang/5"
base_dir = ""
export_dir = ""
last_exported_file_path = ""

# --- UI绑定的变量 ---
# 【关键修正 1】在这里只声明变量名，不赋值为None，或者赋值为None都可以，
# 关键是理解它们只是占位符，必须在Tk()之后重新赋值。
app = None
new_file_path_var = None
old_file_path_var = None
export_dir_var = None
work_dir_var = None
time_var = None
status_label1 = None
status_label2 = None
open_work_dir_button = None
open_export_dir_button = None


# --- 辅助功能函数 (无修改) ---
def update_time_display():
    if time_var:
        current_time_str = datetime.now().strftime("%H:%M")
        time_var.set(f"当前时间: {current_time_str}")

def save_paths(work_path, exp_path):
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            f.write(f"{work_path}\n")
            f.write(f"{exp_path}\n")
    except Exception as e:
        print(f"无法保存路径配置: {e}")

def load_paths():
    work_path, exp_path = "", ""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                if len(lines) >= 1:
                    path = lines[0].strip()
                    if os.path.isdir(path): work_path = path
                if len(lines) >= 2:
                    path = lines[1].strip()
                    if os.path.isdir(path): exp_path = path
        except Exception as e:
            print(f"无法加载路径配置: {e}")
    return work_path, exp_path

def open_folder(path):
    if not path or not os.path.isdir(path):
        messagebox.showwarning("提示", "路径无效或未选择。")
        return
    try:
        if sys.platform == "win32": os.startfile(path)
        elif sys.platform == "darwin": subprocess.Popen(["open", path])
        else: subprocess.Popen(["xdg-open", path])
    except Exception as e:
        messagebox.showerror("错误", f"无法打开目录: {e}")

def open_translation_website():
    try:
        webbrowser.open_new_tab(TRANSLATION_URL)
    except Exception as e:
        messagebox.showerror("打开失败", f"无法打开浏览器链接: {e}")

def open_transify_website():
    try:
        webbrowser.open_new_tab(TRANSIFY_URL)
    except Exception as e:
        messagebox.showerror("打开失败", f"无法打开浏览器链接: {e}")

# --- 核心功能函数 (无修改) ---
def _find_latest_files(directory):
    import re
    import glob
    pattern = os.path.join(directory, "nvwa_lan_*.csv")
    upload_version_pattern = re.compile(r"_uploadversion\.csv$")
    files = [f for f in glob.glob(pattern) if not upload_version_pattern.search(f)]
    if not files:
        return None, None
    def get_timestamp(filepath):
        match = re.search(r'nvwa_lan_(\d{12})\.csv', os.path.basename(filepath))
        return match.group(1) if match else '0'
    files.sort(key=get_timestamp, reverse=True)
    latest_file = files[0]
    second_latest_file = files[1] if len(files) > 1 else None
    return latest_file, second_latest_file

def process_full_export():
    update_time_display()
    global base_dir, export_dir, last_exported_file_path
    if not base_dir:
        messagebox.showwarning("提示", "请先选择一个工作目录")
        return
    if not export_dir:
        messagebox.showwarning("提示", "请先在顶部设置一个默认的导出路径")
        return
    config_path = os.path.join(base_dir, "LanguageExport.csv")
    if not os.path.exists(config_path):
        messagebox.showerror("错误", f"在工作目录下未找到配置文件: {config_path}")
        return
    try:
        status_label1.config(text="状态: 正在读取配置...", fg="blue")
        app.update_idletasks()
        config_df = pd.read_csv(config_path, skiprows=[1])
        all_language_data = []
        for index, row in config_df.iterrows():
            table_name, sheet_name, column_name = row['TableName'], row['SheetName'], row['ColumnName']
            target_filename = f"{table_name}.csv"
            search_pattern = os.path.join(base_dir, '**', target_filename)
            found_files = glob.glob(search_pattern, recursive=True)
            if not found_files: continue
            source_csv_path = found_files[0]
            source_df = pd.read_csv(source_csv_path, skiprows=[1], dtype=str).fillna('')
            if column_name not in source_df.columns: continue
            id_column_name = source_df.columns[0]
            for _, source_row in source_df.iterrows():
                if pd.notna(source_row[id_column_name]) and source_row[id_column_name] != '':
                    unique_id, text_content = source_row[id_column_name], source_row[column_name]
                    tag = f"{table_name}_{sheet_name}_{column_name}_{unique_id}"
                    all_language_data.append({'Key': tag, 'Chinese Simplified': text_content})
        if not all_language_data:
            messagebox.showinfo("完成", "未提取到任何数据。")
            status_label1.config(text="状态: 未提取到数据", fg="orange")
            return
        result_df = pd.DataFrame(all_language_data)
        timestamp = datetime.now().strftime("%Y%m%d%H%M")
        output_filename = f"nvwa_lan_{timestamp}.csv"
        output_path = os.path.join(export_dir, output_filename)
        result_df.to_csv(output_path, index=False, encoding='utf-8-sig')
        messagebox.showinfo("成功", f"全量导出完成！\n文件已保存至: {output_path}")
        status_label1.config(text=f"状态: 导出成功", fg="green")
        last_exported_file_path = output_path
        new_file_path_var.set(last_exported_file_path)
        auto_suggest_old_file()
    except Exception as e:
        messagebox.showerror("导出失败", f"发生错误: {e}")
        status_label1.config(text="状态: 导出失败", fg="red")

def process_incremental_export():
    update_time_display()
    global export_dir
    new_file_path = new_file_path_var.get()
    old_file_path = old_file_path_var.get()
    if not new_file_path or not old_file_path:
        messagebox.showwarning("文件未选择", "请先选择【新文件】和【旧文件】。")
        return
    if new_file_path == old_file_path:
        messagebox.showwarning("文件选择错误", "新旧文件不能是同一个文件。")
        return
    if not export_dir:
        messagebox.showwarning("提示", "请先在顶部设置一个默认的导出路径")
        return
    try:
        status_label2.config(text="状态: 正在比对文件...", fg="blue")
        app.update_idletasks()
        df_new = pd.read_csv(new_file_path).set_index('Key')
        df_old = pd.read_csv(old_file_path).set_index('Key')
        new_tags = df_new.index.difference(df_old.index)
        df_added = df_new.loc[new_tags].reset_index()
        merged_df = df_new.join(df_old, lsuffix='_new', rsuffix='_old', how='inner')
        modified_rows = merged_df[merged_df['Chinese Simplified_new'] != merged_df['Chinese Simplified_old']]
        df_modified = modified_rows[['Chinese Simplified_new']].reset_index().rename(columns={'Chinese Simplified_new': 'Chinese Simplified'})
        upload_df = pd.concat([df_added, df_modified], ignore_index=True)
        if upload_df.empty:
            messagebox.showinfo("无变化", "比对完成，没有新增或修改的内容。")
            status_label2.config(text="状态: 无内容变化", fg="green")
            return
        base_new_filename = os.path.splitext(os.path.basename(new_file_path))[0]
        output_filename = f"{base_new_filename}_uploadversion.csv"
        output_path = os.path.join(export_dir, output_filename)
        upload_df = upload_df[['Key', 'Chinese Simplified']]
        upload_df.to_csv(output_path, index=False, encoding='utf-8-sig')
        messagebox.showinfo("成功", f"增量导出完成！\n共 {len(upload_df)} 条差异。\n文件已保存至: {output_path}")
        status_label2.config(text=f"状态: 增量导出成功", fg="green")
    except KeyError as e:
        messagebox.showerror("比对失败", f"发生列名错误: {e}\n请确保CSV文件包含 'Key' 和 'Chinese Simplified' 列。")
        status_label2.config(text="状态: 比对失败 (列名错误)", fg="red")
    except Exception as e:
        messagebox.showerror("比对失败", f"发生错误: {e}")
        status_label2.config(text="状态: 比对失败", fg="red")

# --- UI交互函数 (现在可以正确更新UI了) ---
def select_directory():
    global base_dir
    path = filedialog.askdirectory(title="请选择根工作目录", initialdir=base_dir if base_dir else os.path.expanduser("~"))
    if path:
        set_base_dir(path)
        save_paths(base_dir, export_dir)
        auto_select_comparison_files()

def select_export_directory():
    global export_dir
    path = filedialog.askdirectory(title="请选择默认导出路径", initialdir=export_dir if export_dir else (base_dir if base_dir else os.path.expanduser("~")))
    if path:
        set_export_dir(path)
        save_paths(base_dir, export_dir)

def set_base_dir(path):
    global base_dir
    base_dir = path
    work_dir_var.set(base_dir) # 现在修改的是正确的全局StringVar
    open_work_dir_button.config(state=tk.NORMAL)
    status_label1.config(text="状态: 待命", fg="gray")
    status_label2.config(text="状态: 待命", fg="gray")
    new_file_path_var.set("")
    old_file_path_var.set("")

def set_export_dir(path):
    global export_dir
    export_dir = path
    export_dir_var.set(export_dir) # 现在修改的是正确的全局StringVar
    open_export_dir_button.config(state=tk.NORMAL)

def auto_select_comparison_files():
    search_dir = export_dir if export_dir and os.path.isdir(export_dir) else base_dir
    if not search_dir or not os.path.isdir(search_dir):
        return
    latest_file, second_latest_file = _find_latest_files(search_dir)
    if latest_file:
        new_file_path_var.set(latest_file)
    else:
        new_file_path_var.set("")
    if second_latest_file:
        old_file_path_var.set(second_latest_file)
    else:
        old_file_path_var.set("")

def select_new_file():
    initial_dir = export_dir if export_dir else (base_dir if base_dir else os.path.expanduser("~"))
    filepath = filedialog.askopenfilename(
        title="选择新文件 (New)",
        initialdir=initial_dir,
        filetypes=[("CSV files", "nvwa_lan_*.csv"), ("All files", "*.*")]
    )
    if filepath:
        new_file_path_var.set(filepath)
        auto_suggest_old_file()

def select_old_file():
    initial_dir = export_dir if export_dir else (base_dir if base_dir else os.path.expanduser("~"))
    filepath = filedialog.askopenfilename(
        title="选择旧文件 (Old)",
        initialdir=initial_dir,
        filetypes=[("CSV files", "nvwa_lan_*.csv"), ("All files", "*.*")]
    )
    if filepath:
        old_file_path_var.set(filepath)

def auto_suggest_old_file():
    new_file = new_file_path_var.get()
    if not new_file or not os.path.exists(new_file):
        old_file_path_var.set("")
        return
    search_dir = os.path.dirname(new_file)
    file_pattern = os.path.join(search_dir, "nvwa_lan_*.csv")
    upload_version_pattern = re.compile(r"_uploadversion\.csv$")
    all_files = [f for f in glob.glob(file_pattern) if not upload_version_pattern.search(f)]
    if len(all_files) < 2:
        old_file_path_var.set("")
        return
    file_list = []
    for f in all_files:
        match = re.search(r'nvwa_lan_(\d{12})\.csv', os.path.basename(f))
        if match:
            file_list.append({'path': f, 'time': match.group(1)})
    file_list.sort(key=lambda x: x['time'], reverse=True)
    current_new_file_index = -1
    for i, file_info in enumerate(file_list):
        if os.path.samefile(file_info['path'], new_file):
            current_new_file_index = i
            break
    if current_new_file_index != -1 and current_new_file_index + 1 < len(file_list):
        suggested_old_file = file_list[current_new_file_index + 1]['path']
        old_file_path_var.set(suggested_old_file)
    else:
        old_file_path_var.set("")

def run_gui() -> None:
    # 【关键修正 2】将所有UI组件和变量的赋值操作都指向全局变量
    global app, new_file_path_var, old_file_path_var, export_dir_var, work_dir_var, time_var
    global open_work_dir_button, open_export_dir_button
    global status_label1, status_label2

    # 【关键修正 3】正确的初始化顺序
    # 1. 创建主窗口实例
    app = tk.Tk()
    
    # 2. 立即实例化所有全局的Tkinter变量
    new_file_path_var = tk.StringVar(app)
    old_file_path_var = tk.StringVar(app)
    export_dir_var = tk.StringVar(app)
    work_dir_var = tk.StringVar(app)
    time_var = tk.StringVar(app)

    # 3. 现在可以安全地构建UI的其余部分了
    app.title(APP_NAME)
    app.geometry("800x650")
    app.resizable(True, True)

    top_frame = tk.Frame(app, padx=10, pady=10)
    top_frame.pack(fill=tk.X)
    title_label = tk.Label(top_frame, text=APP_NAME, font=("Helvetica", 16, "bold"))
    title_label.pack()
    time_label = tk.Label(top_frame, textvariable=time_var, font=("Helvetica", 9))
    time_label.pack(pady=(0, 10))

    path_frame = tk.Frame(top_frame)
    path_frame.pack(fill=tk.X)
    
    work_dir_frame = tk.Frame(path_frame)
    work_dir_frame.pack(fill=tk.X, pady=2)
    dir_button = tk.Button(work_dir_frame, text="选择工作目录", command=select_directory, width=12)
    dir_button.pack(side=tk.LEFT, padx=(0, 5))
    open_work_dir_button = tk.Button(work_dir_frame, text="打开", command=lambda: open_folder(base_dir), width=5, state=tk.DISABLED)
    open_work_dir_button.pack(side=tk.LEFT, padx=(0, 5))
    work_dir_entry = tk.Entry(work_dir_frame, textvariable=work_dir_var, state='readonly')
    work_dir_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

    export_dir_frame = tk.Frame(path_frame)
    export_dir_frame.pack(fill=tk.X, pady=2)
    export_dir_button = tk.Button(export_dir_frame, text="选择导出路径", command=select_export_directory, width=12)
    export_dir_button.pack(side=tk.LEFT, padx=(0, 5))
    open_export_dir_button = tk.Button(export_dir_frame, text="打开", command=lambda: open_folder(export_dir), width=5, state=tk.DISABLED)
    open_export_dir_button.pack(side=tk.LEFT, padx=(0, 5))
    export_dir_entry = tk.Entry(export_dir_frame, textvariable=export_dir_var, state='readonly', fg="darkgreen")
    export_dir_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

    separator = tk.Frame(app, height=2, bd=1, relief=tk.SUNKEN)
    separator.pack(fill=tk.X, padx=10, pady=10)

    content_frame = tk.Frame(app, padx=10, pady=5)
    content_frame.pack(fill=tk.BOTH, expand=True)
    content_frame.grid_columnconfigure(0, weight=1, minsize=380)
    content_frame.grid_columnconfigure(1, weight=1, minsize=380)

    left_column = tk.Frame(content_frame)
    left_column.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
    frame1 = tk.LabelFrame(left_column, text="流程 1: 全量导出多语言", padx=10, pady=10)
    frame1.pack(fill=tk.BOTH, expand=True)
    desc1 = tk.Label(frame1, text="从配置表出发，在工作目录及其子目录中\n搜索所有CSV，提取文本并生成汇总文件。", justify=tk.LEFT)
    desc1.pack(anchor="w", pady=(0, 10))
    button1 = tk.Button(frame1, text="执行全量导出", command=process_full_export, bg="#c8e6c9", height=2)
    button1.pack(pady=10, fill=tk.X)
    status_label1 = tk.Label(frame1, text="状态: 待命", fg="gray")
    status_label1.pack(pady=5)

    right_column = tk.Frame(content_frame)
    right_column.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
    frame2 = tk.LabelFrame(right_column, text="流程 2: 增量比对与导出", padx=10, pady=10)
    frame2.pack(fill=tk.BOTH, expand=True)
    desc2 = tk.Label(frame2, text="对比两个版本的CSV文件，导出差异（新增/修改）。\n将自动在导出目录中查找，亦可手动指定。", justify=tk.LEFT)
    desc2.pack(anchor="w", pady=(0, 10))

    new_file_frame = tk.Frame(frame2)
    new_file_frame.pack(fill=tk.X, pady=2)
    select_new_button = tk.Button(new_file_frame, text="选择新文件 (New)", command=select_new_file, width=15)
    select_new_button.pack(side=tk.LEFT, padx=(0, 5))
    new_file_entry = tk.Entry(new_file_frame, textvariable=new_file_path_var, state='readonly')
    new_file_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

    old_file_frame = tk.Frame(frame2)
    old_file_frame.pack(fill=tk.X, pady=2)
    select_old_button = tk.Button(old_file_frame, text="选择旧文件 (Old)", command=select_old_file, width=15)
    select_old_button.pack(side=tk.LEFT, padx=(0, 5))
    old_file_entry = tk.Entry(old_file_frame, textvariable=old_file_path_var, state='readonly')
    old_file_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

    run_button2 = tk.Button(frame2, text="开始增量导出", command=process_incremental_export, bg="#bbdefb", height=2)
    run_button2.pack(pady=10, fill=tk.X)
    
    link_frame2 = tk.Frame(frame2)
    link_frame2.pack(pady=(5,0), anchor='w')
    link_desc_label2 = tk.Label(link_frame2, text="将导出的UploadVersion上传至")
    link_desc_label2.pack(side=tk.LEFT)
    link_button2 = tk.Button(link_frame2, text="Transify网站", command=open_translation_website, fg="blue", relief=tk.FLAT, cursor="hand2", bd=0, highlightthickness=0)
    link_button2.pack(side=tk.LEFT, padx=(0,5))
    status_label2 = tk.Label(frame2, text="状态: 待命", fg="gray")
    status_label2.pack(pady=5)

    # 4. 最后，加载路径并启动主循环
    initial_work_path, initial_export_path = load_paths()
    if initial_work_path: 
        set_base_dir(initial_work_path)
    else:
        work_dir_var.set("工作目录: 未设置")
    if initial_export_path: 
        set_export_dir(initial_export_path)
    else:
        export_dir_var.set("导出路径: 未设置")

    auto_select_comparison_files()
    update_time_display()
    app.mainloop()

def register_subparser(subparsers):
    parser = subparsers.add_parser(
        "language-gui",
        help="启动 language_tool 的 GUI",
        description="启动多语言工具图形界面",
    )
    parser.set_defaults(func=lambda _args: run_gui())

if __name__ == "__main__":
    run_gui()