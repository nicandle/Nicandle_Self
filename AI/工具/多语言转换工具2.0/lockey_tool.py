import os
import glob
import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from datetime import datetime
import shutil
import json
import subprocess

# --- 原有代码 ---
base_dir = ""
export_dir = ""
blacklist_folders = []
CONFIG_FILE = "config.json"

def load_config():
    """加载上次保存的路径配置"""
    global base_dir, export_dir, blacklist_folders
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                config = json.load(f)
                base_dir = config.get('base_dir', '')
                export_dir = config.get('export_dir', '')
                blacklist_folders = config.get('blacklist_folders', [])
                if base_dir:
                    base_dir_var.set(base_dir)
                if export_dir:
                    export_dir_var.set(export_dir)
                update_blacklist_display()
        except:
            pass

def save_config():
    """保存当前路径配置"""
    config = {
        'base_dir': base_dir,
        'export_dir': export_dir,
        'blacklist_folders': blacklist_folders
    }
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
    except:
        pass

def select_base_directory():
    global base_dir
    base_dir = filedialog.askdirectory(title="选择工作目录", initialdir=base_dir if base_dir else None)
    if base_dir:
        base_dir = os.path.normpath(base_dir)
        base_dir_var.set(base_dir)
        save_config()
        messagebox.showinfo("成功", f"工作目录已设置为:\n{base_dir}")

def select_export_directory():
    global export_dir
    export_dir = filedialog.askdirectory(title="选择默认导出路径", initialdir=export_dir if export_dir else None)
    if export_dir:
        export_dir = os.path.normpath(export_dir)
        export_dir_var.set(export_dir)
        save_config()
        messagebox.showinfo("成功", f"默认导出路径已设置为:\n{export_dir}")

def update_blacklist_display():
    """更新黑名单显示"""
    blacklist_listbox.delete(0, tk.END)
    for folder_path in blacklist_folders:
        if base_dir and folder_path.startswith(base_dir):
            display_path = os.path.relpath(folder_path, base_dir)
        else:
            display_path = folder_path
        blacklist_listbox.insert(tk.END, display_path)
    blacklist_count_label.config(text=f"黑名单文件夹数量: {len(blacklist_folders)}")

def add_to_blacklist():
    """添加文件夹到黑名单"""
    global blacklist_folders
    if not base_dir:
        messagebox.showwarning("提示", "请先选择工作目录")
        return
    selected_folder = filedialog.askdirectory(title="选择要加入黑名单的文件夹", initialdir=base_dir)
    if not selected_folder:
        return
    selected_folder = os.path.normpath(selected_folder)
    normalized_base_dir = os.path.normpath(base_dir)
    try:
        common_path = os.path.commonpath([normalized_base_dir, selected_folder])
        if os.path.normpath(common_path) != normalized_base_dir:
            messagebox.showwarning("提示", "只能选择工作目录下的文件夹")
            return
    except ValueError:
        messagebox.showwarning("提示", "只能选择工作目录下的文件夹")
        return
    if selected_folder in blacklist_folders:
        messagebox.showinfo("提示", "该文件夹已在黑名单中")
        return
    if selected_folder == normalized_base_dir:
        messagebox.showwarning("提示", "不能将工作目录本身加入黑名单")
        return
    blacklist_folders.append(selected_folder)
    save_config()
    update_blacklist_display()
    relative_path = os.path.relpath(selected_folder, normalized_base_dir)
    log_message(f"已添加到黑名单: {relative_path}", "INFO")
    messagebox.showinfo("成功", f"已将文件夹加入黑名单:\n{relative_path}")

def remove_from_blacklist():
    """从黑名单移除选中的文件夹"""
    global blacklist_folders
    selection = blacklist_listbox.curselection()
    if not selection:
        messagebox.showwarning("提示", "请先选择要移除的项")
        return
    selected_indices = sorted(selection, reverse=True)
    removed_items = []
    for index in selected_indices:
        folder_path = blacklist_folders[index]
        if base_dir and folder_path.startswith(base_dir):
            display_path = os.path.relpath(folder_path, base_dir)
        else:
            display_path = folder_path
        removed_items.append(display_path)
    confirm = messagebox.askyesno("确认", f"确定要从黑名单移除以下文件夹吗?\n\n" + "\n".join(removed_items))
    if confirm:
        for index in selected_indices:
            folder_path = blacklist_folders.pop(index)
            if base_dir and folder_path.startswith(base_dir):
                display_path = os.path.relpath(folder_path, base_dir)
            else:
                display_path = folder_path
            log_message(f"已从黑名单移除: {display_path}", "INFO")
        save_config()
        update_blacklist_display()
        messagebox.showinfo("成功", f"已移除 {len(removed_items)} 项")

def clear_blacklist():
    """清空黑名单"""
    global blacklist_folders
    if not blacklist_folders:
        messagebox.showinfo("提示", "黑名单已经是空的")
        return
    confirm = messagebox.askyesno("确认", f"确定要清空黑名单吗?\n当前有 {len(blacklist_folders)} 个文件夹")
    if confirm:
        blacklist_folders = []
        save_config()
        update_blacklist_display()
        log_message("已清空黑名单", "INFO")
        messagebox.showinfo("成功", "黑名单已清空")

def is_in_blacklist_folder(file_path):
    """检查文件是否在黑名单文件夹中"""
    file_path = os.path.normpath(file_path)
    for blacklist_folder in blacklist_folders:
        blacklist_folder = os.path.normpath(blacklist_folder)
        if file_path.startswith(blacklist_folder + os.sep) or file_path == blacklist_folder:
            return True, blacklist_folder
    return False, None

def update_time_display():
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    time_label.config(text=f"当前时间: {current_time}")

def get_latest_export_folder(exclude_folder=None):
    """获取导出路径下最新的时间戳文件夹（可排除指定文件夹）"""
    if not export_dir or not os.path.exists(export_dir):
        return None
    folders = [f for f in os.listdir(export_dir) if os.path.isdir(os.path.join(export_dir, f)) and f.isdigit()]
    if not folders:
        return None
    folders_sorted = sorted(folders, reverse=True)
    for folder in folders_sorted:
        folder_path = os.path.join(export_dir, folder)
        if exclude_folder and os.path.normpath(folder_path) == os.path.normpath(exclude_folder):
            continue
        return folder_path
    return None

def log_message(message, level="INFO"):
    """添加日志到文本框"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    level_colors = {"INFO": "black", "SUCCESS": "green", "WARNING": "orange", "ERROR": "red", "P4": "purple"}
    tag_name = f"level_{level}"
    log_text.tag_configure(tag_name, foreground=level_colors.get(level, "black"))
    log_text.insert(tk.END, f"[{timestamp}] [{level}] {message}\n", tag_name)
    log_text.see(tk.END)
    app.update_idletasks()

def clear_log():
    """清空日志"""
    log_text.delete(1.0, tk.END)

def preview_config():
    """预览配置文件内容"""
    if not base_dir:
        messagebox.showwarning("提示", "请先选择一个工作目录")
        return
    config_path = os.path.join(base_dir, "LanguageExport.xlsx")
    if not os.path.exists(config_path):
        messagebox.showerror("错误", f"在工作目录下未找到配置文件: LanguageExport.xlsx")
        return
    try:
        config_df = pd.read_excel(config_path)
        preview_window = tk.Toplevel(app)
        preview_window.title("配置预览")
        preview_window.geometry("800x600")
        tree_frame = tk.Frame(preview_window)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        tree_scroll_y = tk.Scrollbar(tree_frame)
        tree_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        tree_scroll_x = tk.Scrollbar(tree_frame, orient=tk.HORIZONTAL)
        tree_scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        tree = ttk.Treeview(tree_frame, yscrollcommand=tree_scroll_y.set, xscrollcommand=tree_scroll_x.set)
        tree.pack(fill=tk.BOTH, expand=True)
        tree_scroll_y.config(command=tree.yview)
        tree_scroll_x.config(command=tree.xview)
        tree['columns'] = list(config_df.columns)
        tree['show'] = 'headings'
        for col in config_df.columns:
            tree.heading(col, text=col)
            tree.column(col, width=150)
        blacklist_count = 0
        for _, row in config_df.iterrows():
            table_name = str(row['TableName']).strip()
            values = list(row)
            target_filename = f"{table_name}.xlsx"
            search_pattern = os.path.join(base_dir, '**', target_filename)
            found_files = glob.glob(search_pattern, recursive=True)
            is_blacklisted = False
            if found_files:
                file_path = found_files[0]
                is_blacklisted, _ = is_in_blacklist_folder(file_path)
            if is_blacklisted:
                tree.insert('', tk.END, values=values, tags=('blacklist',))
                blacklist_count += 1
            else:
                tree.insert('', tk.END, values=values)
        tree.tag_configure('blacklist', background='#ffcccc', foreground='#666666')
        info_text = f"共 {len(config_df)} 条配置"
        if blacklist_count > 0:
            info_text += f" (其中 {blacklist_count} 条在黑名单文件夹中，标记为红色)"
        tk.Label(preview_window, text=info_text, fg="blue").pack(pady=5)
    except Exception as e:
        messagebox.showerror("预览失败", f"无法预览配置文件: {e}")

# --- 优化: P4 Check Out 功能 ---
def p4_checkout(file_path):
    """对指定文件执行 p4 checkout 命令，并提供更详细的错误处理"""
    if not os.path.exists(file_path):
        log_message(f"P4 Check Out 失败: 文件不存在 {file_path}", "ERROR")
        return

    log_message(f"尝试 Check Out: {os.path.basename(file_path)}", "P4")
    try:
        command = ['p4', 'checkout', file_path]
        
        # 在Windows上隐藏控制台窗口
        creationflags = 0
        if os.name == 'nt':
            creationflags = subprocess.CREATE_NO_WINDOW

        result = subprocess.run(
            command, 
            capture_output=True, 
            text=True, 
            encoding='utf-8', 
            check=False,
            creationflags=creationflags
        )

        stdout = result.stdout.strip()
        stderr = result.stderr.strip()

        if result.returncode != 0 or "error" in stderr.lower():
            error_message = stderr if stderr else "未知P4错误"
            log_message(f"P4 Check Out 失败: {error_message}", "ERROR")
        elif "not on client" in stdout or "not in client view" in stdout:
            log_message(f"P4 警告: 文件不在客户端视图中 - {os.path.basename(file_path)}", "WARNING")
        elif "already opened" in stdout:
            log_message(f"P4 信息: 文件已打开，无需 Check Out - {os.path.basename(file_path)}", "INFO")
        else:
            log_message(f"P4 Check Out 成功: {stdout}", "SUCCESS")

    except FileNotFoundError:
        log_message("P4命令执行失败: 'p4' 命令未找到。请确保P4命令行工具已安装并配置在系统PATH中。", "ERROR")
    except Exception as e:
        log_message(f"P4 Check Out 时发生未知异常: {e}", "ERROR")

def process_export():
    update_time_display()
    clear_log()
    global base_dir, export_dir

    if not base_dir or not export_dir:
        messagebox.showwarning("提示", "请先选择工作目录和默认导出路径")
        return

    config_path = os.path.join(base_dir, "LanguageExport.xlsx")
    if not os.path.exists(config_path):
        messagebox.showerror("错误", f"在工作目录下未找到配置文件: LanguageExport.xlsx")
        return

    try:
        status_label.config(text="状态: 正在读取配置...", fg="blue")
        log_message("开始读取配置文件...")
        app.update_idletasks()
        
        config_df = pd.read_excel(config_path)
        log_message(f"配置文件读取成功，共 {len(config_df)} 条配置")
        
        required_columns = ['TableName', 'SheetName', 'Type']
        if not all(col in config_df.columns for col in required_columns):
            missing_cols = [col for col in required_columns if col not in config_df.columns]
            messagebox.showerror("错误", f"配置文件缺少必要的列: {', '.join(missing_cols)}")
            log_message(f"配置文件缺少必要的列: {', '.join(missing_cols)}", "ERROR")
            return
        
        all_language_data = []
        error_log = []
        skipped_count = 0
        
        progress_bar['maximum'] = len(config_df)
        progress_bar['value'] = 0
        
        for index, row in config_df.iterrows():
            table_name = str(row['TableName']).strip()
            sheet_name = str(row['SheetName']).strip()
            column_name = str(row['Type']).strip()
            
            log_message(f"处理配置 [{index+1}/{len(config_df)}]: {table_name} - {sheet_name} - {column_name}")
            
            search_pattern = os.path.join(base_dir, '**', f"{table_name}.xlsx")
            found_files = glob.glob(search_pattern, recursive=True)
            
            if not found_files:
                error_msg = f"未找到文件: {table_name}.xlsx"
                error_log.append(error_msg)
                log_message(error_msg, "WARNING")
                progress_bar['value'] = index + 1
                continue
            
            source_xlsx_path = found_files[0]
            
            is_blacklisted, blacklist_folder = is_in_blacklist_folder(source_xlsx_path)
            if is_blacklisted:
                relative_file = os.path.relpath(source_xlsx_path, base_dir)
                relative_blacklist = os.path.relpath(blacklist_folder, base_dir)
                log_message(f"跳过黑名单 [{index+1}/{len(config_df)}]: {relative_file} (位于 {relative_blacklist})", "WARNING")
                skipped_count += 1
                progress_bar['value'] = index + 1
                continue
            
            log_message(f"  找到文件: {os.path.relpath(source_xlsx_path, base_dir)}")
            
            try:
                # --- 优化: 使用 header=0 和 skiprows=[1] 跳过第二行 ---
                source_df = pd.read_excel(
                    source_xlsx_path, 
                    sheet_name=sheet_name, 
                    header=0, 
                    skiprows=[1], 
                    dtype=str
                ).fillna('')
                log_message(f"  读取Sheet成功 (已跳过第二行备注)，共 {len(source_df)} 行数据")
            except Exception as e:
                error_msg = f"读取Sheet失败: {table_name} - {sheet_name}, 错误: {str(e)}"
                error_log.append(error_msg)
                log_message(error_msg, "ERROR")
                progress_bar['value'] = index + 1
                continue
            
            if column_name not in source_df.columns:
                error_msg = f"列不存在: {table_name} - {sheet_name} - {column_name}"
                error_log.append(error_msg)
                log_message(error_msg, "WARNING")
                progress_bar['value'] = index + 1
                continue
            
            first_column_name = source_df.columns[0]
            valid_count = 0
            empty_count = 0
            for _, source_row in source_df.iterrows():
                if pd.notna(source_row[first_column_name]) and source_row[first_column_name] != '':
                    unique_id = str(source_row[first_column_name]).strip()
                    text_content = str(source_row[column_name]).strip()
                    
                    if not text_content or text_content == 'nan':
                        empty_count += 1
                        continue
                    
                    key = f"{table_name}_{sheet_name}_{column_name}_{unique_id}"
                    all_language_data.append({'Key': key, 'Chinese Simplified': text_content})
                    valid_count += 1
            
            log_message(f"  提取有效数据: {valid_count} 条, 空值: {empty_count} 条")
            progress_bar['value'] = index + 1
        
        if skipped_count > 0:
            log_message(f"共跳过 {skipped_count} 条黑名单文件夹配置", "INFO")
        
        if not all_language_data:
            messagebox.showinfo("完成", "未提取到任何数据。")
            status_label.config(text="状态: 未提取到数据", fg="orange")
            log_message("未提取到任何有效数据", "WARNING")
            return
        
        log_message(f"数据提取完成，共 {len(all_language_data)} 条有效数据")
        
        result_df = pd.DataFrame(all_language_data)
        timestamp = "N/A"
        incremental_count = 0

        # --- 优化: 根据选项决定是否执行全量/增量导出 ---
        if not loc_only_var.get():
            log_message("开始执行全量和增量导出...", "INFO")
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            output_folder = os.path.join(export_dir, timestamp)
            os.makedirs(output_folder, exist_ok=True)
            log_message(f"创建导出文件夹: {output_folder}")

            full_export_path = os.path.join(output_folder, "full_export.csv")
            result_df.to_csv(full_export_path, index=False, encoding='utf-8-sig')
            log_message(f"全量导出完成: {len(all_language_data)} 条")   
            
            latest_folder = get_latest_export_folder(exclude_folder=output_folder)
            if latest_folder and latest_folder != output_folder:
                old_full_export = os.path.join(latest_folder, "full_export.csv")
                if os.path.exists(old_full_export):
                    log_message(f"对比上次导出: {os.path.basename(latest_folder)}")
                    old_df = pd.read_csv(old_full_export, dtype=str).fillna('')
                    old_dict = {str(k).strip(): str(v).strip() for k, v in zip(old_df['Key'], old_df['Chinese Simplified'])}
                    incremental_data = []
                    for _, row in result_df.iterrows():
                        key = str(row['Key']).strip()
                        text = str(row['Chinese Simplified']).strip()
                        if key not in old_dict or old_dict[key] != text:
                            incremental_data.append({'Key': key, 'Chinese Simplified': text})
                    if incremental_data:
                        incremental_df = pd.DataFrame(incremental_data)
                        incremental_export_path = os.path.join(output_folder, "incremental_export.csv")
                        incremental_df.to_csv(incremental_export_path, index=False, encoding='utf-8-sig')
                        incremental_count = len(incremental_data)
                        log_message(f"增量导出完成: {incremental_count} 条")
                    else:
                        log_message("无增量数据")
            else:
                log_message("首次导出，无增量对比")
            
            if error_log:
                error_log_path = os.path.join(output_folder, "error_log.txt")
                with open(error_log_path, 'w', encoding='utf-8') as f:
                    f.write(f"导出时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write(f"错误/警告数量: {len(error_log)}\n\n" + "\n".join(error_log))
                log_message(f"错误日志已保存: {len(error_log)} 条", "WARNING")
        else:
            log_message("'仅导出Loc文件' 已勾选，跳过全量和增量文件导出。", "INFO")

        # --- 拆分文件导出 (始终执行) ---
        log_message("开始导出拆分文件 (LocIndex.csv, Loc_zh-cn.csv)...", "INFO")
        norm_base_dir = os.path.normpath(base_dir)
        if os.path.basename(norm_base_dir).lower() != 'design':
            log_message(f"工作目录 '{os.path.basename(norm_base_dir)}' 不是 'Design'，无法自动定位Client路径。跳过拆分文件导出。", "WARNING")
        else:
            project_root = os.path.dirname(norm_base_dir)
            target_path = os.path.join(project_root, "Client", "Assets", "Resources", "Localization")
            os.makedirs(target_path, exist_ok=True)
            log_message(f"定位到目标路径: {target_path}", "INFO")

            loc_index_path = os.path.join(target_path, "LocIndex.csv")
            result_df[['Key']].to_csv(loc_index_path, index=False, header=False, encoding='utf-8-sig')
            log_message(f"成功导出: {loc_index_path}", "SUCCESS")

            loc_zh_cn_path = os.path.join(target_path, "Loc_zh-cn.csv")
            pd.DataFrame({'Text': result_df['Chinese Simplified'], 'Type': 'TEXT'}).to_csv(loc_zh_cn_path, index=False, header=False, encoding='utf-8-sig')
            log_message(f"成功导出: {loc_zh_cn_path}", "SUCCESS")

            if p4_checkout_var.get():
                p4_checkout(loc_index_path)
                p4_checkout(loc_zh_cn_path)
        
        # --- 显示最终信息 ---
        message = "导出完成!\n"
        if not loc_only_var.get():
            message += f"导出文件夹: {timestamp}\n"
            message += f"全量导出: {len(all_language_data)} 条\n"
            message += f"增量导出: {incremental_count} 条\n"
        message += f"Loc文件导出: {len(all_language_data)} 条\n"
        if skipped_count > 0:
            message += f"跳过黑名单: {skipped_count} 条\n"
        if error_log and not loc_only_var.get():
            message += f"警告/错误: {len(error_log)} 条 (详见error_log.txt)"
        
        messagebox.showinfo("成功", message)
        status_label.config(text=f"状态: 导出成功 (总计:{len(all_language_data)} 增量:{incremental_count} 跳过:{skipped_count})", fg="green")
        log_message("导出流程完成!", "SUCCESS")
        
    except Exception as e:
        messagebox.showerror("导出失败", f"发生错误: {e}")
        status_label.config(text="状态: 导出失败", fg="red")
        log_message(f"导出失败: {str(e)}", "ERROR")

# --- UI 界面代码 ---
app = tk.Tk()
app.title("Lockey语言文件导出工具 v2.0")
app.geometry("900x750")

time_label = tk.Label(app, text="当前时间: --", font=("Arial", 10), fg="gray")
time_label.pack(pady=5)

top_frame = tk.Frame(app)
top_frame.pack(pady=10, padx=10, fill=tk.X)
base_dir_var = tk.StringVar()
export_dir_var = tk.StringVar()
tk.Label(top_frame, text="工作目录:").grid(row=0, column=0, sticky=tk.W, pady=5)
tk.Entry(top_frame, textvariable=base_dir_var, width=50, state='readonly').grid(row=0, column=1, padx=5)
tk.Button(top_frame, text="选择", command=select_base_directory).grid(row=0, column=2)
tk.Label(top_frame, text="默认导出路径:").grid(row=1, column=0, sticky=tk.W, pady=5)
tk.Entry(top_frame, textvariable=export_dir_var, width=50, state='readonly').grid(row=1, column=1, padx=5)
tk.Button(top_frame, text="选择", command=select_export_directory).grid(row=1, column=2)

blacklist_frame = tk.LabelFrame(app, text="黑名单文件夹管理", padx=10, pady=10)
blacklist_frame.pack(pady=5, padx=10, fill=tk.BOTH)
tk.Label(blacklist_frame, text="以下文件夹内的所有文件将被跳过，不会导出", fg="gray").pack(anchor=tk.W, pady=2)
blacklist_content_frame = tk.Frame(blacklist_frame)
blacklist_content_frame.pack(fill=tk.BOTH, expand=True)
list_frame = tk.Frame(blacklist_content_frame)
list_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
blacklist_scroll = tk.Scrollbar(list_frame)
blacklist_scroll.pack(side=tk.RIGHT, fill=tk.Y)
blacklist_listbox = tk.Listbox(list_frame, height=4, yscrollcommand=blacklist_scroll.set, selectmode=tk.EXTENDED)
blacklist_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
blacklist_scroll.config(command=blacklist_listbox.yview)
button_frame_blacklist = tk.Frame(blacklist_content_frame)
button_frame_blacklist.pack(side=tk.RIGHT, padx=5)
tk.Button(button_frame_blacklist, text="添加文件夹", command=add_to_blacklist, width=12).pack(pady=2)
tk.Button(button_frame_blacklist, text="移除", command=remove_from_blacklist, width=12).pack(pady=2)
tk.Button(button_frame_blacklist, text="清空", command=clear_blacklist, width=12).pack(pady=2)
blacklist_count_label = tk.Label(blacklist_frame, text="黑名单文件夹数量: 0", fg="blue")
blacklist_count_label.pack(anchor=tk.W, pady=2)

separator = tk.Frame(app, height=2, bd=1, relief=tk.SUNKEN)
separator.pack(fill=tk.X, padx=10, pady=10)

export_frame = tk.LabelFrame(app, text="语言文件导出", padx=10, pady=10)
export_frame.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)
tk.Label(export_frame, text="根据配置文件 LanguageExport.xlsx 导出语言数据", fg="blue").pack(anchor=tk.W, pady=5)
tk.Label(export_frame, text="• 全量导出: 导出所有配置的语言数据", fg="gray").pack(anchor=tk.W, padx=20)
tk.Label(export_frame, text="• 增量导出: 与上次导出对比，仅导出新增或修改的数据", fg="gray").pack(anchor=tk.W, padx=20)
tk.Label(export_frame, text="• 拆分导出: 自动生成 LocIndex.csv 和 Loc_zh-cn.csv 到Client工程目录", fg="gray").pack(anchor=tk.W, padx=20)

button_frame = tk.Frame(export_frame)
button_frame.pack(pady=10)
tk.Button(button_frame, text="预览配置", command=preview_config, bg="lightgreen", width=15, height=2).pack(side=tk.LEFT, padx=5)
tk.Button(button_frame, text="执行导出", command=process_export, bg="lightblue", width=15, height=2).pack(side=tk.LEFT, padx=5)

# --- 新增/修改: 导出选项 ---
options_frame = tk.Frame(button_frame)
options_frame.pack(side=tk.LEFT, padx=10)
loc_only_var = tk.BooleanVar(value=False)
tk.Checkbutton(options_frame, text="仅导出Loc文件", variable=loc_only_var).pack(anchor=tk.W)
p4_checkout_var = tk.BooleanVar(value=True)
tk.Checkbutton(options_frame, text="自动P4 Check Out", variable=p4_checkout_var).pack(anchor=tk.W)

progress_frame = tk.Frame(export_frame)
progress_frame.pack(fill=tk.X, pady=5)
tk.Label(progress_frame, text="处理进度:").pack(side=tk.LEFT, padx=5)
progress_bar = ttk.Progressbar(progress_frame, mode='determinate')
progress_bar.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
status_label = tk.Label(export_frame, text="状态: 未执行", fg="gray", font=("Arial", 10))
status_label.pack(anchor=tk.W, pady=5)

log_frame = tk.LabelFrame(export_frame, text="处理日志", padx=5, pady=5)
log_frame.pack(fill=tk.BOTH, expand=True, pady=5)
log_scroll = tk.Scrollbar(log_frame)
log_scroll.pack(side=tk.RIGHT, fill=tk.Y)
log_text = tk.Text(log_frame, height=8, yscrollcommand=log_scroll.set, font=("Consolas", 9))
log_text.pack(fill=tk.BOTH, expand=True)
log_scroll.config(command=log_text.yview)

info_frame = tk.Frame(app)
info_frame.pack(pady=5, padx=10, fill=tk.X)
tk.Label(info_frame, text="导出格式: Key | Chinese Simplified", fg="darkgreen", font=("Arial", 9)).pack(anchor=tk.W)
tk.Label(info_frame, text="Key命名规则: 表名_Sheet名_字段名_首列值", fg="darkgreen", font=("Arial", 9)).pack(anchor=tk.W)

load_config()
app.mainloop()