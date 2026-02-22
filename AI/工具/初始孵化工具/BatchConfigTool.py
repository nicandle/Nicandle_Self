import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
import itertools
import os
from PIL import Image, ImageTk
import threading

class BatchConfigTool:
    def __init__(self, root):
        self.root = root
        self.root.title("批量配置与看图工具")
        self.root.geometry("1000x700")

        self.notebook = ttk.Notebook(root)
        self.notebook.pack(expand=True, fill='both')

        self.tab1 = ttk.Frame(self.notebook)
        self.tab2 = ttk.Frame(self.notebook)

        self.notebook.add(self.tab1, text='生成配置')
        self.notebook.add(self.tab2, text='图片查看')

        self.setup_tab1()
        self.setup_tab2()

        # Data for Tab 2
        self.config_data = None
        self.image_references = [] # Keep refs to avoid GC
        self.selected_images = set() # Store filenames of selected (bad) images
        self.image_frame_container = None

    def setup_tab1(self):
        main_frame = ttk.Frame(self.tab1, padding="10")
        main_frame.pack(fill='both', expand=True)

        # Instructions
        ttk.Label(main_frame, text="请在下方分别输入数据 (每行格式: ID 名称)").pack(pady=5)

        # Import Source Excel Button
        ttk.Button(main_frame, text="导入源数据表格 (Excel)", command=self.import_source_excel).pack(pady=5)

        # Input Area Grid
        input_frame = ttk.Frame(main_frame)
        input_frame.pack(fill='both', expand=True)
        input_frame.columnconfigure(0, weight=1)
        input_frame.columnconfigure(1, weight=1)
        input_frame.columnconfigure(2, weight=1)

        # Column 1: Creature
        ttk.Label(input_frame, text="生物 (ID 名称)").grid(row=0, column=0)
        self.text_creature = tk.Text(input_frame, width=30, height=20)
        self.text_creature.grid(row=1, column=0, padx=5)

        # Column 2: Modifier
        ttk.Label(input_frame, text="修饰词 (ID 名称)").grid(row=0, column=1)
        self.text_modifier = tk.Text(input_frame, width=30, height=20)
        self.text_modifier.grid(row=1, column=1, padx=5)

        # Column 3: Entity
        ttk.Label(input_frame, text="实体词 (ID 名称)").grid(row=0, column=2)
        self.text_entity = tk.Text(input_frame, width=30, height=20)
        self.text_entity.grid(row=1, column=2, padx=5)

        # Generate Button
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(pady=10)
        ttk.Button(btn_frame, text="生成并导出Excel", command=self.generate_excel).pack()

    def parse_input(self, text_widget):
        content = text_widget.get("1.0", tk.END).strip()
        items = []
        
        if not content:
            return items
            
        for line in content.split('\n'):
            parts = line.strip().split(None, 1) # Split by first whitespace
            if not parts:
                continue
                
            id_val = parts[0]
            # Skip if ID is empty
            if not id_val:
                continue
            
            name_val = parts[1] if len(parts) > 1 else "Unknown"
            
            items.append((id_val, name_val))
            
        return items

    def import_source_excel(self):
        file_path = filedialog.askopenfilename(filetypes=[("Excel Files", "*.xlsx")])
        if not file_path:
            return
        
        try:
            # Read excel, header=0 (first row is header)
            df = pd.read_excel(file_path, header=0)
            
            # Check if we have at least 6 columns
            if len(df.columns) < 6:
                messagebox.showerror("错误", "Excel表格至少需要6列数据")
                return

            # Clear existing inputs
            self.text_creature.delete("1.0", tk.END)
            self.text_modifier.delete("1.0", tk.END)
            self.text_entity.delete("1.0", tk.END)

            # Helper to extract 2 columns and format
            def extract_cols(col_idx1, col_idx2):
                # Select columns by index
                sub_df = df.iloc[:, [col_idx1, col_idx2]].dropna().astype(str)
                text_lines = []
                for _, row in sub_df.iterrows():
                    # Check if empty string or "nan"
                    id_val = row.iloc[0].strip()
                    name_val = row.iloc[1].strip()
                    
                    # Remove .0 if it exists
                    if id_val.endswith(".0"):
                        id_val = id_val[:-2]
                        
                    if id_val and name_val and id_val.lower() != 'nan' and name_val.lower() != 'nan':
                        text_lines.append(f"{id_val} {name_val}")
                return "\n".join(text_lines)

            # Populate widgets
            # Col 1,2 -> Creature
            creature_text = extract_cols(0, 1)
            self.text_creature.insert("1.0", creature_text)

            # Col 3,4 -> Modifier
            modifier_text = extract_cols(2, 3)
            self.text_modifier.insert("1.0", modifier_text)

            # Col 5,6 -> Entity
            entity_text = extract_cols(4, 5)
            self.text_entity.insert("1.0", entity_text)
            
            messagebox.showinfo("成功", f"已从 {os.path.basename(file_path)} 导入数据")

        except Exception as e:
            messagebox.showerror("错误", f"导入失败: {str(e)}")

    def generate_excel(self):
        creatures = self.parse_input(self.text_creature)
        modifiers = self.parse_input(self.text_modifier)
        entities = self.parse_input(self.text_entity)

        if not creatures or not modifiers or not entities:
            messagebox.showerror("错误", "请确保所有三列都有数据输入！")
            return

        # Generate Combinations
        combinations = list(itertools.product(creatures, modifiers, entities))
        
        data = []
        start_id = 1000001
        
        # Counter for base resource names to handle duplicates gracefully
        # Key: base_res_name, Value: count
        res_name_counts = {}

        for i, (bio, mod, ent) in enumerate(combinations):
            bio_id, bio_name = bio
            mod_id, mod_name = mod
            ent_id, ent_name = ent

            uid = start_id + i
            combined_name = f"{bio_name} {mod_name} {ent_name}"
            combined_id_field = f"{mod_id}|{ent_id}"
            
            # Resource Name: Unique and recognizable
            # Strategy: Res_BioID_ModID_EntID
            base_res_name = f"Res_{bio_id}_{mod_id}_{ent_id}"
            
            if base_res_name in res_name_counts:
                res_name_counts[base_res_name] += 1
                count = res_name_counts[base_res_name]
                res_name = f"{base_res_name}_{count}"
            else:
                res_name_counts[base_res_name] = 1
                res_name = base_res_name

            data.append({
                "流水ID": uid,
                "组合名称": combined_name,
                "生物ID": bio_id,
                "组合ID": combined_id_field,
                "资源名称": res_name
            })

        df = pd.DataFrame(data)
        
        file_path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel Files", "*.xlsx")])
        if file_path:
            try:
                df.to_excel(file_path, index=False)
                messagebox.showinfo("成功", f"成功导出 {len(data)} 条数据到:\n{file_path}")
                
                # Auto-load into Tab 2 context
                self.config_df = df
                self.lbl_config_status.config(text=f"当前配置: {os.path.basename(file_path)} ({len(df)} 条)")
            except Exception as e:
                messagebox.showerror("错误", f"导出失败: {str(e)}")

    def setup_tab2(self):
        top_frame = ttk.Frame(self.tab2, padding="5")
        top_frame.pack(fill='x')

        ttk.Button(top_frame, text="1. 加载配置Excel", command=self.load_excel_config).pack(side='left', padx=5)
        self.lbl_config_status = ttk.Label(top_frame, text="未加载配置")
        self.lbl_config_status.pack(side='left', padx=5)

        ttk.Button(top_frame, text="2. 选择图片文件夹", command=self.load_images_dir).pack(side='left', padx=5)
        
        ttk.Button(top_frame, text="3. 导出选中(不合格)列表", command=self.export_bad_quality).pack(side='right', padx=5)

        # Scrollable Image Area
        self.canvas = tk.Canvas(self.tab2)
        self.scrollbar = ttk.Scrollbar(self.tab2, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        
        # Mousewheel scroll
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def load_excel_config(self):
        file_path = filedialog.askopenfilename(filetypes=[("Excel Files", "*.xlsx")])
        if file_path:
            try:
                self.config_df = pd.read_excel(file_path)
                # Ensure columns exist
                required = ["资源名称", "组合名称"]
                if not all(col in self.config_df.columns for col in required):
                    messagebox.showerror("错误", "Excel缺少必需列：'资源名称' 或 '组合名称'")
                    return
                self.config_df['资源名称'] = self.config_df['资源名称'].astype(str)
                self.lbl_config_status.config(text=f"当前配置: {os.path.basename(file_path)} ({len(self.config_df)} 条)")
            except Exception as e:
                messagebox.showerror("错误", f"读取失败: {str(e)}")

    def load_images_dir(self):
        if not hasattr(self, 'config_df') or self.config_df is None:
            messagebox.showwarning("警告", "请先加载配置Excel，以便匹配名称")
            return

        dir_path = filedialog.askdirectory()
        if not dir_path:
            return

        # Clear existing
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        self.image_references = []
        self.selected_images = set()

        # Threading for image loading to keep UI responsive
        threading.Thread(target=self._process_images, args=(dir_path,), daemon=True).start()

    def _process_images(self, dir_path):
        # Map resource name to display name
        res_map = dict(zip(self.config_df['资源名称'], self.config_df['组合名称']))
        
        row = 0
        col = 0
        max_cols = 4 # 4 images per row
        
        valid_extensions = {'.png', '.jpg', '.jpeg', '.bmp'}
        
        files = [f for f in os.listdir(dir_path) if os.path.splitext(f)[1].lower() in valid_extensions]
        
        for fname in files:
            name_no_ext = os.path.splitext(fname)[0]
            
            # Find matching combined name
            display_name = res_map.get(name_no_ext, "未找到配置匹配")
            
            # Load Image
            full_path = os.path.join(dir_path, fname)
            try:
                pil_img = Image.open(full_path)
                pil_img.thumbnail((200, 200)) # Resize for thumb
                tk_img = ImageTk.PhotoImage(pil_img)
                self.image_references.append(tk_img)
                
                # Update UI in main thread
                self.root.after(0, self._add_image_widget, row, col, tk_img, fname, display_name)
                
                col += 1
                if col >= max_cols:
                    col = 0
                    row += 1
            except Exception as e:
                print(f"Error loading {fname}: {e}")

    def _add_image_widget(self, row, col, tk_img, fname, display_name):
        frame = ttk.Frame(self.scrollable_frame, borderwidth=2, relief="flat")
        frame.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")
        
        # Image Label
        lbl_img = ttk.Label(frame, image=tk_img)
        lbl_img.pack()
        
        # Text Label
        lbl_text = tk.Label(frame, text=display_name, wraplength=180, justify="center")
        lbl_text.pack()
        
        # Selection logic
        def toggle_selection(e):
            if fname in self.selected_images:
                self.selected_images.remove(fname)
                frame.configure(relief="flat")
                lbl_text.configure(bg="SystemButtonFace", fg="black")
            else:
                self.selected_images.add(fname)
                frame.configure(relief="solid")
                lbl_text.configure(bg="red", fg="white") # Highlight
                
        lbl_img.bind("<Button-1>", toggle_selection)
        lbl_text.bind("<Button-1>", toggle_selection)

    def export_bad_quality(self):
        if not self.selected_images:
            messagebox.showinfo("提示", "未选中任何图片")
            return
            
        if not hasattr(self, 'config_df'):
            messagebox.showerror("错误", "配置丢失")
            return

        # Map resource name to display name
        # Filename might include extension, Config Resource Name usually doesn't (based on logic)
        # We need to strip extension from filename to match resource name
        
        res_map = dict(zip(self.config_df['资源名称'], self.config_df['组合名称']))
        
        export_data = []
        for fname in self.selected_images:
            name_no_ext = os.path.splitext(fname)[0]
            combined_name = res_map.get(name_no_ext, "未知组合")
            export_data.append({
                "文件名": fname,
                "组合名称": combined_name
            })
            
        df = pd.DataFrame(export_data)
        file_path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel Files", "*.xlsx")])
        if file_path:
            df.to_excel(file_path, index=False)
            messagebox.showinfo("成功", f"已导出 {len(df)} 条不合格记录")

if __name__ == "__main__":
    root = tk.Tk()
    app = BatchConfigTool(root)
    root.mainloop()
