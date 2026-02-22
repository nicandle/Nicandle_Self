# -----------------------------------------------------------------------------
# Excel to CSV Converter with UI (v2 - with Default Path)
# Author: AI聊天机器人
# Current Time: Thu Jul 17 20:14:01 CST 2025
# -----------------------------------------------------------------------------

import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import pandas as pd
import os
import threading

class ExcelConverterApp:
    """
    一个带有图形界面的应用程序，用于将Excel文件转换为UTF-8编码的CSV文件。
    """
    def __init__(self, root):
        self.root = root
        self.root.title("Excel 转 CSV 转换器 v2.0")
        self.root.geometry("500x250")
        self.root.resizable(False, False)

        # --- 新增：设置默认目录 ---
        # os.path.expanduser('~') 会获取用户的主目录 (e.g., C:/Users/YourUser)
        # 我们将其与 'Desktop' 结合，作为默认的文件对话框打开位置
        self.default_dir = os.path.join(os.path.expanduser('~'), 'Desktop')
        # 如果桌面不存在（例如在某些系统或语言环境下），则回退到用户主目录
        if not os.path.isdir(self.default_dir):
            self.default_dir = os.path.expanduser('~')

        # --- 变量 ---
        self.source_excel_path = tk.StringVar()
        self.target_csv_path = tk.StringVar()

        # --- UI 布局 ---
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # --- 源文件选择 ---
        source_label = ttk.Label(main_frame, text="源 Excel 文件:")
        source_label.grid(row=0, column=0, sticky="w", padx=5, pady=10)

        source_entry = ttk.Entry(main_frame, textvariable=self.source_excel_path, width=40)
        source_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=10)

        source_button = ttk.Button(main_frame, text="选择文件", command=self.select_source_file)
        source_button.grid(row=0, column=2, sticky="w", padx=5, pady=10)

        # --- 目标文件保存 ---
        target_label = ttk.Label(main_frame, text="目标 CSV 文件:")
        target_label.grid(row=1, column=0, sticky="w", padx=5, pady=10)

        target_entry = ttk.Entry(main_frame, textvariable=self.target_csv_path, width=40)
        target_entry.grid(row=1, column=1, sticky="ew", padx=5, pady=10)

        target_button = ttk.Button(main_frame, text="另存为", command=self.select_target_path)
        target_button.grid(row=1, column=2, sticky="w", padx=5, pady=10)

        # --- 转换按钮 ---
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, columnspan=3, pady=20)
        
        self.convert_button = ttk.Button(button_frame, text="开始转换", command=self.start_conversion_thread)
        self.convert_button.pack()
        
        # --- 进度条 ---
        self.progress = ttk.Progressbar(main_frame, orient="horizontal", length=300, mode="indeterminate")
        self.progress.grid(row=3, column=0, columnspan=3, pady=10)


    def select_source_file(self):
        """打开文件对话框选择源Excel文件，默认打开桌面"""
        file_path = filedialog.askopenfilename(
            # --- 修改点 ---
            initialdir=self.default_dir,
            title="请选择一个 Excel 文件",
            filetypes=[("Excel 文件", "*.xlsx *.xls")]
        )
        if file_path:
            self.source_excel_path.set(file_path)
            dir_name = os.path.dirname(file_path)
            base_name = os.path.basename(file_path)
            file_name_without_ext = os.path.splitext(base_name)[0]
            default_csv_path = os.path.join(dir_name, f"{file_name_without_ext}.csv")
            self.target_csv_path.set(default_csv_path)

    def select_target_path(self):
        """打开文件对话框选择保存CSV的路径，默认打开桌面"""
        source_path = self.source_excel_path.get()
        if source_path:
            initial_dir = os.path.dirname(source_path) # 如果有源文件，就用源文件目录
            base_name = os.path.basename(source_path)
            file_name_without_ext = os.path.splitext(base_name)[0]
        else:
            initial_dir = self.default_dir # 否则用默认目录（桌面）
            file_name_without_ext = "output"

        file_path = filedialog.asksaveasfilename(
            # --- 修改点 ---
            initialdir=initial_dir,
            title="请选择保存位置",
            defaultextension=".csv",
            initialfile=f"{file_name_without_ext}.csv",
            filetypes=[("CSV 文件 (UTF-8)", "*.csv")]
        )
        if file_path:
            self.target_csv_path.set(file_path)

    def start_conversion_thread(self):
        """使用新线程来执行转换，防止UI卡死"""
        self.convert_button.config(state="disabled")
        self.progress.start(10)
        
        conversion_thread = threading.Thread(target=self.convert_excel_to_csv)
        conversion_thread.daemon = True
        conversion_thread.start()

    def convert_excel_to_csv(self):
        """核心转换逻辑"""
        source_file = self.source_excel_path.get()
        target_file = self.target_csv_path.get()

        if not source_file or not target_file:
            messagebox.showerror("错误", "源文件和目标路径都不能为空！")
            self.reset_ui_state()
            return

        try:
            df = pd.read_excel(source_file)
            df.to_csv(target_file, index=False, encoding='utf-8-sig')
            messagebox.showinfo("成功", f"文件已成功转换并保存至:\n{target_file}")
        except Exception as e:
            messagebox.showerror("转换失败", f"发生错误: \n{e}")
        finally:
            self.reset_ui_state()
            
    def reset_ui_state(self):
        """重置UI组件到初始状态"""
        self.progress.stop()
        self.convert_button.config(state="normal")


if __name__ == "__main__":
    root = tk.Tk()
    app = ExcelConverterApp(root)
    root.mainloop()