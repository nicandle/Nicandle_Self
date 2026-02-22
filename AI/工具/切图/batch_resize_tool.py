import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import os

class ResizeToolApp:
    def __init__(self, root):
        self.root = root
        self.root.title("批量图片压缩/转换工具 (PNG版)")
        self.root.geometry("600x500")
        
        self.file_paths = []
        self.output_dir = ""

        # ================= 设置区 =================
        setting_frame = tk.LabelFrame(root, text="输出设置", padx=10, pady=10, bg="#f0f0f0")
        setting_frame.pack(fill=tk.X, padx=10, pady=10)

        # 尺寸设置
        tk.Label(setting_frame, text="目标宽度:", bg="#f0f0f0").grid(row=0, column=0, padx=5)
        self.entry_w = tk.Entry(setting_frame, width=8)
        self.entry_w.insert(0, "350") # 默认 350
        self.entry_w.grid(row=0, column=1, padx=5)

        tk.Label(setting_frame, text="目标高度:", bg="#f0f0f0").grid(row=0, column=2, padx=5)
        self.entry_h = tk.Entry(setting_frame, width=8)
        self.entry_h.insert(0, "390") # 默认 390
        self.entry_h.grid(row=0, column=3, padx=5)

        # 模式选择
        self.keep_ratio_var = tk.BooleanVar(value=False)
        tk.Checkbutton(setting_frame, text="保持比例 (自动补透明背景)", variable=self.keep_ratio_var, bg="#f0f0f0").grid(row=0, column=4, padx=20)

        # ================= 列表区 =================
        list_frame = tk.Frame(root)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10)
        
        tk.Label(list_frame, text="待处理列表:", anchor="w").pack(fill=tk.X)
        
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set, selectmode=tk.EXTENDED, height=10)
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.listbox.yview)

        # ================= 按钮区 =================
        btn_frame = tk.Frame(root, pady=10)
        btn_frame.pack(fill=tk.X)

        tk.Button(btn_frame, text="1. 添加图片", command=self.add_images, height=2, width=15, bg="#2196f3", fg="white").pack(side=tk.LEFT, padx=20)
        tk.Button(btn_frame, text="2. 选择导出文件夹", command=self.select_output_folder, height=2, width=15, bg="#ff9800", fg="white").pack(side=tk.LEFT, padx=20)
        tk.Button(btn_frame, text="3. 开始处理", command=self.start_processing, height=2, width=15, bg="#4caf50", fg="white").pack(side=tk.RIGHT, padx=20)

        # 底部状态
        self.status_label = tk.Label(root, text="准备就绪", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X)

    def add_images(self):
        paths = filedialog.askopenfilenames(title="选择图片", filetypes=[("Images", "*.png *.jpg *.jpeg *.bmp *.webp")])
        if paths:
            for p in paths:
                if p not in self.file_paths:
                    self.file_paths.append(p)
                    self.listbox.insert(tk.END, os.path.basename(p))
            self.status_label.config(text=f"当前列表共有 {len(self.file_paths)} 张图片")

    def select_output_folder(self):
        path = filedialog.askdirectory()
        if path:
            self.output_dir = path
            self.status_label.config(text=f"输出目录: {path}")

    def start_processing(self):
        if not self.file_paths:
            messagebox.showwarning("提示", "请先添加图片！")
            return
        if not self.output_dir:
            messagebox.showwarning("提示", "请先选择导出文件夹！")
            return

        try:
            target_w = int(self.entry_w.get())
            target_h = int(self.entry_h.get())
        except ValueError:
            messagebox.showerror("错误", "宽度和高度必须是整数！")
            return

        success_count = 0
        
        for f_path in self.file_paths:
            try:
                img = Image.open(f_path).convert("RGBA") # 强制转为RGBA以支持透明
                filename = os.path.basename(f_path)
                name_no_ext = os.path.splitext(filename)[0]
                save_path = os.path.join(self.output_dir, name_no_ext + ".png")

                if self.keep_ratio_var.get():
                    # === 模式A: 保持比例 (Fit) ===
                    # 1. 创建透明底图
                    new_img = Image.new("RGBA", (target_w, target_h), (0, 0, 0, 0))
                    
                    # 2. 计算缩放比例
                    ratio = min(target_w / img.width, target_h / img.height)
                    new_size = (int(img.width * ratio), int(img.height * ratio))
                    
                    # 3. 缩放原图
                    resized_img = img.resize(new_size, Image.Resampling.LANCZOS)
                    
                    # 4. 居中粘贴
                    paste_x = (target_w - new_size[0]) // 2
                    paste_y = (target_h - new_size[1]) // 2
                    new_img.paste(resized_img, (paste_x, paste_y))
                    
                    new_img.save(save_path, "PNG")
                    
                else:
                    # === 模式B: 强制拉伸 (Stretch) ===
                    new_img = img.resize((target_w, target_h), Image.Resampling.LANCZOS)
                    new_img.save(save_path, "PNG")

                success_count += 1
                
            except Exception as e:
                print(f"Error processing {f_path}: {e}")

        messagebox.showinfo("完成", f"处理完成！\n成功导出 {success_count} 张图片到:\n{self.output_dir}")
        self.status_label.config(text=f"处理完成，共 {success_count} 张")

if __name__ == "__main__":
    root = tk.Tk()
    app = ResizeToolApp(root)
    root.mainloop()