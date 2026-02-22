"""空白工具模板

使用方式：
  - CLI：py main.py blank [--echo TEXT]
  - 作为起点按需扩展参数与逻辑
"""

import argparse
import pandas as pd
import os
import tkinter as tk
from tkinter import filedialog, messagebox
from datetime import datetime

# --- 全局配置 ---
CONFIG_FILE_NAME = "LanguageExport.csv"
OUTPUT_FILE_PREFIX = "nvwa_lan_"
KEY_COLUMN_NAME = "Key"
VALUE_COLUMN_NAME = "Chinese Simplified"

def select_directory():
    """打开一个GUI窗口让用户选择工作目录"""
    root = tk.Tk()
    root.withdraw()  # 隐藏主窗口
    folder_path = filedialog.askdirectory(title="请选择包含 LanguageExport.csv 的根目录")
    return folder_path

def find_csv_file(root_path, file_name):
    """在指定目录及其子目录中递归搜索文件"""
    for dirpath, _, filenames in os.walk(root_path):
        for f in filenames:
            if f.lower() == file_name.lower():
                return os.path.join(dirpath, f)
    return None

def export_languages():
    """
    流程1：导出多语言文本
    1. 读取 LanguageExport.csv 配置。
    2. 遍历配置，查找对应的CSV文件。
    3. 提取指定列的数据。
    4. 生成唯一的Key。
    5. 合并所有数据并导出到一个带时间戳的CSV文件中。
    """
    # 1. 选择工作目录
    work_dir = select_directory()
    if not work_dir:
        print("未选择目录，操作已取消。")
        return

    print(f"工作目录: {work_dir}")

    # 2. 寻找并读取 LanguageExport.csv
    config_path = os.path.join(work_dir, CONFIG_FILE_NAME)
    if not os.path.exists(config_path):
        messagebox.showerror("错误", f"在选定目录中未找到配置文件: {CONFIG_FILE_NAME}")
        return

    try:
        # 跳过第二行中文备注
        config_df = pd.read_csv(config_path, skiprows=[1])
        print(f"成功读取配置文件: {config_path}")
    except Exception as e:
        messagebox.showerror("读取错误", f"读取 {CONFIG_FILE_NAME} 失败: {e}")
        return

    # 用于存储所有导出结果的列表
    all_exported_data = []

    # 3. 遍历配置文件的每一行
    for index, row in config_df.iterrows():
        table_name = row['TableName']
        sheet_name = row['SheetName']
        column_name = row['ColumnName']

        if pd.isna(table_name) or pd.isna(column_name):
            print(f"警告: 配置文件第 {index + 3} 行数据不完整，已跳过。")
            continue

        print(f"\n正在处理: 表名='{table_name}', Sheet名='{sheet_name}', 字段='{column_name}'")

        # 在整个工作目录中寻找目标CSV文件
        target_csv_name = f"{table_name}.csv"
        target_csv_path = find_csv_file(work_dir, target_csv_name)

        if not target_csv_path:
            print(f"  -> 错误: 未能在目录 {work_dir} 及其子目录中找到文件 {target_csv_name}，已跳过。")
            continue
        
        print(f"  -> 找到目标文件: {target_csv_path}")

        try:
            # 读取目标CSV，同样跳过第二行中文备注
            data_df = pd.read_csv(target_csv_path, skiprows=[1], dtype=str).fillna('')
            
            # 4. 检查所需列是否存在
            if data_df.empty:
                print(f"  -> 警告: 文件 {target_csv_name} 为空，已跳过。")
                continue

            id_column = data_df.columns[0] # 获取首列作为ID列
            if column_name not in data_df.columns:
                print(f"  -> 错误: 文件 {target_csv_name} 中不存在名为 '{column_name}' 的列，已跳过。")
                continue

            # 5. 提取数据并生成Key
            # 筛选出需要的列
            temp_df = data_df[[id_column, column_name]].copy()
            
            # 生成Key: 表名_Sheet名_字段名_首列ID
            temp_df[KEY_COLUMN_NAME] = temp_df.apply(
                lambda r: f"{table_name}_{sheet_name}_{column_name}_{r[id_column]}",
                axis=1
            )
            
            # 重命名列以匹配最终输出格式
            temp_df.rename(columns={column_name: VALUE_COLUMN_NAME}, inplace=True)
            
            # 只保留Key和翻译值两列
            exported_part = temp_df[[KEY_COLUMN_NAME, VALUE_COLUMN_NAME]]
            all_exported_data.append(exported_part)
            print(f"  -> 成功提取 {len(exported_part)} 条数据。")

        except Exception as e:
            print(f"  -> 处理文件 {target_csv_name} 时发生错误: {e}")

    # 6. 合并并导出最终结果
    if not all_exported_data:
        messagebox.showinfo("完成", "没有可导出的数据。")
        return

    final_df = pd.concat(all_exported_data, ignore_index=True)

    # 生成带时间戳的文件名
    timestamp = datetime.now().strftime("%Y%m%d%H%M")
    output_filename = f"{OUTPUT_FILE_PREFIX}{timestamp}.csv"
    output_path = os.path.join(work_dir, output_filename)

    try:
        # index=False表示不将DataFrame的索引写入CSV文件
        final_df.to_csv(output_path, index=False, encoding='utf-8-sig')
        messagebox.showinfo("导出成功", f"数据已成功导出到:\n{output_path}\n\n共导出 {len(final_df)} 条记录。")
    except Exception as e:
        messagebox.showerror("导出失败", f"无法写入文件 {output_path}: {e}")

def import_languages():
    """
    流程2：导入多语言文本 (功能预留)
    """
    messagebox.showinfo("提示", "导入功能正在开发中，敬请期待！")

def run_gui():
    """主函数，提供用户操作界面"""
    root = tk.Tk()
    root.title("多语言工具 v1.0")
    root.geometry("300x150")

    label = tk.Label(root, text="请选择要执行的操作", pady=20)
    label.pack()

    export_button = tk.Button(root, text="流程1: 导出语言文本", command=export_languages, width=20)
    export_button.pack(pady=5)

    import_button = tk.Button(root, text="流程2: 导入语言文本", command=import_languages, width=20, state="disabled")
    import_button.pack(pady=5)

    root.mainloop()


def register_subparser(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser(
        "blank-gui",
        help="启动空白工具的 GUI",
        description="启动空白工具（多语言导出原型）的图形界面",
    )
    parser.set_defaults(func=lambda _args: run_gui())