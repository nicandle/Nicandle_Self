import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageDraw, ImageTk
import pandas as pd
import os

# ================= 核心算法配置 =================
# 1. 面积强阈值：面积超过 30% -> 1
AREA_HIGH_THRESHOLD = 0.30 

# 2. 面积弱阈值：面积超过 10% 且满足补偿条件 -> 1
AREA_LOW_THRESHOLD = 0.10 

# 3. 骨架阈值：中心线覆盖率超过 60% -> 1 (针对极细线条)
SKELETON_THRESHOLD = 0.60

# 透明度灵敏度 (0-255)
ALPHA_SENSITIVITY = 20
# ===========================================

class GridToolApp:
    def __init__(self, root):
        self.root = root
        self.root.title(f"剪影网格工具 (V7: 裁切开关+骨架+空洞保留)")
        self.root.geometry("1100x800")

        self.data_list = []
        self.photo_refs = []

        # --- 顶部样式 ---
        top_frame = tk.Frame(root, pady=10, bg="#2b2b2b")
        top_frame.pack(side=tk.TOP, fill=tk.X)

        # 1. 导入按钮
        btn_import = tk.Button(top_frame, text="1. 批量导入图片", command=self.load_images, bg="#0277bd", fg="white", height=2, width=18, relief="flat")
        btn_import.pack(side=tk.LEFT, padx=15)

        # 2. 裁切开关 (新增)
        self.enable_trim_var = tk.BooleanVar(value=True) # 默认开启
        chk_trim = tk.Checkbutton(top_frame, text="启用自动裁切", variable=self.enable_trim_var, 
                                  bg="#2b2b2b", fg="#4fc3f7", selectcolor="#1e1e1e", activebackground="#2b2b2b",
                                  font=("Arial", 10, "bold"))
        chk_trim.pack(side=tk.LEFT, padx=10)

        # 3. 导出按钮
        btn_export = tk.Button(top_frame, text="2. 导出 Excel", command=self.export_excel, bg="#2e7d32", fg="white", height=2, width=18, relief="flat")
        btn_export.pack(side=tk.LEFT, padx=15)
        
        # 状态说明
        info_text = "绿色=强 | 青色=骨架 | 黄色=补偿\n(若四周全强则不补偿)"
        self.status_label = tk.Label(top_frame, text=info_text, fg="#ffca28", bg="#2b2b2b", font=("Arial", 9), justify=tk.LEFT)
        self.status_label.pack(side=tk.LEFT, padx=10)

        # --- 内容区 ---
        container = tk.Frame(root, bg="#1e1e1e")
        container.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(container, bg="#1e1e1e", highlightthickness=0)
        scrollbar = tk.Scrollbar(container, orient="vertical", command=self.canvas.yview, bg="#1e1e1e")
        self.scrollable_frame = tk.Frame(self.canvas, bg="#1e1e1e")

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def process_single_image(self, file_path):
        try:
            # 1. 打开原图
            original_img = Image.open(file_path).convert("RGBA")
            
            # --- 裁切逻辑分支 ---
            if self.enable_trim_var.get():
                # 如果开关开启，执行裁切
                bbox = original_img.getbbox()
                if bbox:
                    img = original_img.crop(bbox)
                else:
                    img = original_img
            else:
                # 如果开关关闭，直接使用原图
                img = original_img
            
            width, height = img.size
            alpha_channel = img.split()[-1]
            
            # --- 准备数据容器 ---
            final_grid = [[0]*5 for _ in range(5)]
            ratios = [[0.0]*5 for _ in range(5)]
            
            cell_w = width / 5.0
            cell_h = height / 5.0
            
            # --- Phase 1: 计算面积 & 骨架检测 ---
            for r in range(5):
                for c in range(5):
                    x1 = int(c * cell_w)
                    y1 = int(r * cell_h)
                    x2 = int((c + 1) * cell_w)
                    y2 = int((r + 1) * cell_h)
                    if c == 4: x2 = width
                    if r == 4: y2 = height

                    cell_crop = alpha_channel.crop((x1, y1, x2, y2))
                    cw, ch = cell_crop.size
                    
                    pixels = list(cell_crop.getdata())
                    total = len(pixels)
                    ratio = 0.0
                    if total > 0:
                        filled = sum(1 for p in pixels if p > ALPHA_SENSITIVITY)
                        ratio = filled / total
                    ratios[r][c] = ratio
                    
                    # 骨架检测
                    is_skeleton = False
                    if total > 0 and cw > 2 and ch > 2:
                        mid_x = cw // 2
                        mid_y = ch // 2
                        row_pixels = [cell_crop.getpixel((x, mid_y)) for x in range(cw)]
                        row_filled = sum(1 for p in row_pixels if p > ALPHA_SENSITIVITY)
                        col_pixels = [cell_crop.getpixel((mid_x, y)) for y in range(ch)]
                        col_filled = sum(1 for p in col_pixels if p > ALPHA_SENSITIVITY)
                        
                        if (row_filled / cw > SKELETON_THRESHOLD) or (col_filled / ch > SKELETON_THRESHOLD):
                            is_skeleton = True

                    if ratio > AREA_HIGH_THRESHOLD:
                        final_grid[r][c] = 1 # 绿色
                    elif is_skeleton:
                        final_grid[r][c] = 3 # 青色

            # --- Phase 2: 邻域补偿 (含空洞保留逻辑) ---
            for r in range(5):
                for c in range(5):
                    if final_grid[r][c] == 0 and ratios[r][c] > AREA_LOW_THRESHOLD:
                        
                        valid_neighbors_count = 0
                        strong_neighbors_count = 0
                        
                        neighbors = [(-1,0), (1,0), (0,-1), (0,1)]
                        for dr, dc in neighbors:
                            nr, nc = r+dr, c+dc
                            if 0 <= nr < 5 and 0 <= nc < 5:
                                valid_neighbors_count += 1
                                if final_grid[nr][nc] in [1, 3]: 
                                    strong_neighbors_count += 1
                        
                        # 空洞保留逻辑：如果所有存在的邻居都是强邻居，视为内部空洞，不补偿
                        if strong_neighbors_count == valid_neighbors_count:
                            pass 
                        elif strong_neighbors_count > 0:
                            final_grid[r][c] = 2 # 补偿

            # --- 生成预览图 ---
            black_bg = Image.new("RGBA", img.size, (0, 0, 0, 255))
            black_bg.paste(img, (0, 0), img)
            preview_img = black_bg
            draw = ImageDraw.Draw(preview_img)

            config_rows = []

            for r in range(5):
                row_str = ""
                for c in range(5):
                    status = final_grid[r][c]
                    ratio = ratios[r][c]
                    token = "1" if status > 0 else "0"
                    row_str += token

                    x1 = int(c * cell_w)
                    y1 = int(r * cell_h)
                    x2 = int((c + 1) * cell_w)
                    y2 = int((r + 1) * cell_h)
                    if c == 4: x2 = width
                    if r == 4: y2 = height

                    if status == 1: color = "#00e676" 
                    elif status == 3: color = "#00e5ff"
                    elif status == 2: color = "#ffea00"
                    else: color = "#d32f2f"

                    draw.rectangle([x1, y1, x2-1, y2-1], outline=color, width=2)
                    
                    cx, cy = (x1+x2)/2, (y1+y2)/2
                    percent_text = f"{int(ratio*100)}%"
                    draw.rectangle([cx-10, cy-6, cx+10, cy+6], fill="#333333")
                    draw.text((cx-8, cy-5), percent_text, fill="white", font_size=8)

                config_rows.append(row_str)
            
            final_config_str = "|".join(config_rows)
            return final_config_str, preview_img

        except Exception as e:
            print(f"Error: {e}")
            return "ERROR", None

    def load_images(self):
        file_paths = filedialog.askopenfilenames(
            title="选择图片",
            filetypes=[("Images", "*.png *.jpg *.jpeg *.bmp")]
        )
        if not file_paths: return

        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        self.data_list = []
        self.photo_refs = []
        
        header = tk.Frame(self.scrollable_frame, bg="#2b2b2b")
        header.pack(fill=tk.X, pady=2)
        
        # 更新表头提示
        mode_text = "自动裁切" if self.enable_trim_var.get() else "原图尺寸"
        tk.Label(header, text=f"预览 ({mode_text})", width=30, bg="#2b2b2b", fg="#bdbdbd", font=("Arial", 10, "bold")).pack(side=tk.LEFT)
        tk.Label(header, text="文件名", width=25, bg="#2b2b2b", fg="#bdbdbd", font=("Arial", 10, "bold")).pack(side=tk.LEFT)
        tk.Label(header, text="配置代码", width=40, bg="#2b2b2b", fg="#bdbdbd", font=("Arial", 10, "bold")).pack(side=tk.LEFT)

        for f_path in file_paths:
            filename = os.path.basename(f_path)
            config_str, preview_pil = self.process_single_image(f_path)
            
            if preview_pil:
                self.data_list.append({"文件名": filename, "配置代码": config_str})

                row_frame = tk.Frame(self.scrollable_frame, bg="#1e1e1e", pady=5)
                row_frame.pack(fill=tk.X, pady=1)
                
                base_height = 110
                h_percent = (base_height / float(preview_pil.size[1]))
                w_size = int((float(preview_pil.size[0]) * float(h_percent)))
                thumb = preview_pil.resize((w_size, base_height), Image.Resampling.LANCZOS)
                tk_thumb = ImageTk.PhotoImage(thumb)
                self.photo_refs.append(tk_thumb)
                
                tk.Label(row_frame, image=tk_thumb, bg="#1e1e1e").pack(side=tk.LEFT, padx=10)
                tk.Label(row_frame, text=filename, width=25, anchor="w", bg="#1e1e1e", fg="white").pack(side=tk.LEFT, padx=10)
                tk.Label(row_frame, text=config_str, width=40, anchor="w", bg="#1e1e1e", fg="#4fc3f7", font=("Consolas", 11)).pack(side=tk.LEFT, padx=10)

        messagebox.showinfo("完成", f"已处理 {len(self.data_list)} 张图片。\n当前模式：{'自动裁切' if self.enable_trim_var.get() else '原图尺寸'}")

    def export_excel(self):
        if not self.data_list: return
        save_path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx")])
        if save_path:
            try:
                pd.DataFrame(self.data_list).to_excel(save_path, index=False)
                messagebox.showinfo("成功", f"导出成功：{save_path}")
            except Exception as e:
                messagebox.showerror("错误", str(e))

if __name__ == "__main__":
    root = tk.Tk()
    app = GridToolApp(root)
    root.mainloop()