# -*- coding: utf-8 -*-
# @Author: AI聊天机器人
# @Date: Wed Oct 29 18:18:03 CST 2025

import tkinter as tk
from tkinter import ttk, messagebox
import random

# --- 全局配置 ---
CELL_SIZE = 35
BG_COLOR = "#f0f0f0"
GRID_LINE_COLOR = "#cccccc"
BOARD_AREA_COLOR = "#e0e0e0"
STAR_COLOR = "#ffd700"
STAR_LIT_COLOR = "#ff4500"
PIECE_COLORS = {"red": "#e74c3c", "blue": "#3498db"}
PIECE_OUTLINE_COLOR = "#2c3e50"
SELECTED_PIECE_OUTLINE_COLOR = "#f1c40f"

class PuzzleGame(tk.Tk):
    """主应用程序类 (v6 - 带旋转功能)"""
    def __init__(self):
        super().__init__()
        self.title("随机拼图游戏 (v6) by AI聊天机器人")
        self.geometry("1050x900")
        self.configure(bg=BG_COLOR)
        
        self.game_data = None
        self.placed_pieces = {}
        self.selected_piece = None
        self.star_status = {}
        self.game_active = False

        self._setup_ui()
        
        # 绑定键盘事件
        self.bind("<KeyPress-r>", self.rotate_selected_piece)
        self.bind("<KeyPress-R>", self.rotate_selected_piece) # 兼容大写R

    def _setup_ui(self):
        # --- 1. 控制面板 ---
        control_frame = ttk.Frame(self, padding="10")
        control_frame.pack(fill=tk.X, pady=5)
        
        # -- 棋盘定义 --
        board_def_frame = ttk.LabelFrame(control_frame, text="棋盘定义 (边界+总格数)", padding=5)
        board_def_frame.pack(side=tk.LEFT, padx=5, fill=tk.Y)
        
        ttk.Label(board_def_frame, text="行数 (边界):").grid(row=0, column=0, sticky='w', padx=5)
        self.rows_var = tk.StringVar(value="15")
        self.rows_entry = ttk.Entry(board_def_frame, textvariable=self.rows_var, width=5)
        self.rows_entry.grid(row=0, column=1)

        ttk.Label(board_def_frame, text="列数 (边界):").grid(row=1, column=0, sticky='w', padx=5)
        self.cols_var = tk.StringVar(value="15")
        self.cols_entry = ttk.Entry(board_def_frame, textvariable=self.cols_var, width=5)
        self.cols_entry.grid(row=1, column=1)
        
        ttk.Label(board_def_frame, text="总格数:").grid(row=2, column=0, sticky='w', padx=5, pady=(5,0))
        self.total_cells_var = tk.StringVar(value="120")
        self.total_cells_entry = ttk.Entry(board_def_frame, textvariable=self.total_cells_var, width=5)
        self.total_cells_entry.grid(row=2, column=1, pady=(5,0))

        # -- 拼图块定义 --
        piece_def_frame = ttk.LabelFrame(control_frame, text="拼图块 & 星星", padding=5)
        piece_def_frame.pack(side=tk.LEFT, padx=5, fill=tk.Y)
        
        ttk.Label(piece_def_frame, text="红色块数:").grid(row=0, column=0, sticky='w', padx=5)
        self.red_pieces_var = tk.StringVar(value="5")
        ttk.Entry(piece_def_frame, textvariable=self.red_pieces_var, width=5).grid(row=0, column=1)

        ttk.Label(piece_def_frame, text="蓝色块数:").grid(row=1, column=0, sticky='w', padx=5)
        self.blue_pieces_var = tk.StringVar(value="8")
        ttk.Entry(piece_def_frame, textvariable=self.blue_pieces_var, width=5).grid(row=1, column=1)

        ttk.Label(piece_def_frame, text="五角星数:").grid(row=2, column=0, sticky='w', padx=5, pady=(5,0))
        self.stars_var = tk.StringVar(value="10")
        ttk.Entry(piece_def_frame, textvariable=self.stars_var, width=5).grid(row=2, column=1, pady=(5,0))

        # -- 游戏操作 --
        action_frame = ttk.Frame(control_frame)
        action_frame.pack(side=tk.LEFT, padx=20, fill=tk.Y)
        
        generate_btn = ttk.Button(action_frame, text="生成新游戏", command=self.start_new_game)
        generate_btn.pack(fill=tk.X, pady=2)
        
        reset_btn = ttk.Button(action_frame, text="重置当前局", command=self.reset_board)
        reset_btn.pack(fill=tk.X, pady=2)
        
        # 新增旋转按钮
        rotate_btn = ttk.Button(action_frame, text="旋转选中块 (R)", command=self.rotate_selected_piece)
        rotate_btn.pack(fill=tk.X, pady=2)
        
        finish_btn = ttk.Button(action_frame, text="结束并计分", command=self.finish_game)
        finish_btn.pack(fill=tk.X, pady=2, ipady=5)
        
        self.status_label = ttk.Label(control_frame, text="欢迎！请设置参数并生成游戏。", font=("Arial", 12), anchor='e')
        self.status_label.pack(side=tk.RIGHT, padx=10, fill=tk.BOTH, expand=True)

        # --- 2. 游戏主画板 ---
        self.board_canvas = tk.Canvas(self, bg="white", highlightthickness=0)
        self.board_canvas.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        self.board_canvas.bind("<Button-1>", self.on_board_click)

        # --- 3. 待选拼图块区域 ---
        ttk.Label(self, text="待选拼图块 (选中后按 'R' 键旋转)", font=("Arial", 14)).pack(pady=(10, 5))
        self.pieces_canvas = tk.Canvas(self, height=120, bg=BG_COLOR, highlightthickness=0)
        self.pieces_canvas.pack(fill=tk.X, padx=10, pady=5)
        self.pieces_canvas.bind("<Button-1>", self.on_piece_select)

    def rotate_selected_piece(self, event=None):
        """旋转当前选中的拼图块"""
        if not self.game_active or not self.selected_piece:
            self.status_label.config(text="请先选择一个拼图块才能旋转！")
            return

        # 调用拼图块自身的旋转方法
        self.selected_piece.rotate()
        
        # 重新绘制待选区域以显示旋转后的样子
        self._draw_available_pieces()
        self.status_label.config(text=f"已旋转 {self.selected_piece.color} 块。请在棋盘上放置。")

    # --- 以下方法与 v5 版本基本相同，仅在 start_new_game 中为 piece 增加原始形状备份 ---
    def start_new_game(self):
        try:
            # ... (输入验证代码与v5相同)
            max_rows = int(self.rows_var.get())
            max_cols = int(self.cols_var.get())
            total_cells = int(self.total_cells_var.get())
            num_red = int(self.red_pieces_var.get())
            num_blue = int(self.blue_pieces_var.get())
            num_stars = int(self.stars_var.get())
            if not (3 <= max_rows <= 30 and 3 <= max_cols <= 30):
                raise ValueError("行/列数必须在 3-30 之间。")
            if not (5 <= total_cells <= max_rows * max_cols):
                raise ValueError(f"总格数必须在 5 - {max_rows * max_cols} (行×列)之间。")
        except ValueError as e:
            messagebox.showerror("输入错误", str(e))
            return

        self.status_label.config(text="正在生成游戏...")
        self.update_idletasks()

        self.game_data = self._generate_puzzle_data(max_rows, max_cols, total_cells, num_stars, num_red, num_blue)
        if not self.game_data:
            messagebox.showerror("生成失败", "无法根据当前参数生成有效的棋盘。\n\n请尝试调整参数（如增大边界或减小总格数）后重试。")
            self.status_label.config(text="生成失败，请调整参数。")
            return
        
        self.reset_board()
        self.game_active = True
        self.update_status()

    def reset_board(self):
        """重置游戏时，需要将所有拼图块恢复到原始形状"""
        if not self.game_data:
            self.status_label.config(text="请先生成一个新游戏！")
            return
        
        # 恢复所有拼图块的原始形状
        for piece in self.game_data['pieces']:
            piece.reset_shape()

        self.placed_pieces = {}
        self.selected_piece = None
        self.star_status = {loc: "unlit" for loc in self.game_data['star_locations']}
        self.game_active = True
        self._draw_board()
        self._draw_available_pieces()
        self.update_status()

    def _generate_puzzle_data(self, max_rows, max_cols, target_size, num_stars, num_red, num_blue):
        # ... (棋盘生成部分与v5相同)
        board_shape = None
        for _ in range(20): 
            start_node = (random.randint(0, max_rows - 1), random.randint(0, max_cols - 1))
            shape_try = {start_node}
            frontier = [n for n in self._get_neighbors(start_node, max_rows, max_cols) if n not in shape_try]
            while frontier and len(shape_try) < target_size:
                cell = random.choice(frontier)
                frontier.remove(cell)
                shape_try.add(cell)
                for neighbor in self._get_neighbors(cell, max_rows, max_cols):
                    if neighbor not in shape_try and neighbor not in frontier:
                        frontier.append(neighbor)
            if len(shape_try) == target_size:
                board_shape = shape_try
                break
        if not board_shape: return None

        # --- Part 2: 独立生成拼图块 ---
        red_sizes = [random.randint(2, 3) for _ in range(num_red)]
        blue_sizes = [random.randint(3, 5) for _ in range(num_blue)]
        piece_defs = [('red', s) for s in red_sizes] + [('blue', s) for s in blue_sizes]
        
        pieces = []
        for i, (color, size) in enumerate(piece_defs):
            shape = self._generate_random_connected_shape(size)
            if shape:
                pieces.append(PuzzlePiece(i, color, shape))
        
        # --- Part 3: 放置五角星 ---
        if len(board_shape) < num_stars:
            num_stars = len(board_shape)
        star_locations = random.sample(list(board_shape), num_stars)

        return {
            "max_rows": max_rows, "max_cols": max_cols,
            "board_shape": board_shape, "pieces": pieces,
            "star_locations": set(star_locations)
        }

    # --- 以下方法与之前版本相同，无需修改 ---
    # ... (此处省略 finish_game, on_board_click, update_status, 
    # _generate_random_connected_shape, _get_neighbors, _draw_board, _draw_stars, 
    # _draw_available_pieces, on_piece_select, _is_valid_placement, 
    # update_star_status)
    def finish_game(self):
        if not self.game_active:
            messagebox.showinfo("游戏结束", "游戏尚未开始或已经结束。")
            return
        self.game_active = False
        self.selected_piece = None
        self._draw_available_pieces()
        lit_stars = sum(1 for status in self.star_status.values() if status == "lit")
        total_stars = len(self.star_status)
        total_cells = len(self.game_data['board_shape'])
        covered_cells = sum(len(p.shape) for _, _, p in self.placed_pieces.values())
        coverage_percent = (covered_cells / total_cells * 100) if total_cells > 0 else 0
        score_message = (
            f"游戏结束！\n\n"
            f"点亮星星: {lit_stars} / {total_stars}\n"
            f"棋盘覆盖率: {covered_cells} / {total_cells} ({coverage_percent:.1f}%)\n\n"
            "您可以重置或生成一个新游戏。"
        )
        self.status_label.config(text=f"游戏结束！得分: {lit_stars}/{total_stars} 星")
        messagebox.showinfo("得分统计", score_message)

    def on_board_click(self, event):
        if not self.game_active:
            self.status_label.config(text="游戏已结束，请开始新游戏。")
            return
        if not self.selected_piece:
            self.status_label.config(text="请先从下方选择一个拼图块！")
            return
        row = event.y // CELL_SIZE
        col = event.x // CELL_SIZE
        if self._is_valid_placement(self.selected_piece, row, col):
            self.placed_pieces[self.selected_piece.id] = (row, col, self.selected_piece)
            abs_shape = self.selected_piece.get_absolute_shape(row, col)
            for r, c in abs_shape:
                x1, y1 = c * CELL_SIZE, r * CELL_SIZE
                x2, y2 = x1 + CELL_SIZE, y1 + CELL_SIZE
                self.board_canvas.create_rectangle(x1, y1, x2, y2, 
                                                   fill=PIECE_COLORS[self.selected_piece.color], 
                                                   outline=PIECE_OUTLINE_COLOR,
                                                   tags="placed_piece")
            self.selected_piece = None
            self._draw_available_pieces()
            self.update_star_status()
            self._draw_stars()
            self.update_status()
        else:
            self.status_label.config(text="无效位置！不能超出边界或重叠。")

    def update_status(self):
        if not self.game_data:
            self.status_label.config(text="欢迎！请设置参数并生成游戏。")
            return
        if not self.game_active:
            return
        lit_stars = sum(1 for status in self.star_status.values() if status == "lit")
        total_stars = len(self.star_status)
        if self.selected_piece:
            msg = f"已选择 {self.selected_piece.color} 块。点亮星星: {lit_stars}/{total_stars}"
        else:
            msg = f"请选择拼图块放置。点亮星星: {lit_stars}/{total_stars}"
        self.status_label.config(text=msg)

    def _generate_random_connected_shape(self, size):
        shape = {(0, 0)}
        max_dim = int(size * 1.5) + 2
        frontier = set(self._get_neighbors((0, 0), max_dim, max_dim))
        while len(shape) < size:
            if not frontier: return None
            cell = random.choice(list(frontier))
            frontier.remove(cell)
            shape.add(cell)
            for neighbor in self._get_neighbors(cell, max_dim, max_dim):
                if neighbor not in shape:
                    frontier.add(neighbor)
        min_r = min(r for r, c in shape)
        min_c = min(c for r, c in shape)
        return frozenset((r - min_r, c - min_c) for r, c in shape)

    def _get_neighbors(self, cell, max_rows, max_cols):
        r, c = cell
        neighbors = []
        for dr, dc in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < max_rows and 0 <= nc < max_cols:
                neighbors.append((nr, nc))
        return neighbors

    def _draw_board(self):
        self.board_canvas.delete("all")
        data = self.game_data
        if not data: return
        rows, cols = data['max_rows'], data['max_cols']
        self.board_canvas.config(width=cols * CELL_SIZE, height=rows * CELL_SIZE)
        for r, c in data['board_shape']:
            x1, y1 = c * CELL_SIZE, r * CELL_SIZE
            x2, y2 = x1 + CELL_SIZE, y1 + CELL_SIZE
            self.board_canvas.create_rectangle(x1, y1, x2, y2, fill=BOARD_AREA_COLOR, outline=GRID_LINE_COLOR)
        self._draw_stars()

    def _draw_stars(self):
        self.board_canvas.delete("star")
        if not self.game_data: return
        for (r, c), status in self.star_status.items():
            x, y = c * CELL_SIZE + CELL_SIZE / 2, r * CELL_SIZE + CELL_SIZE / 2
            color = STAR_LIT_COLOR if status == "lit" else STAR_COLOR
            self.board_canvas.create_text(x, y, text="★", font=("Arial", int(CELL_SIZE*0.6)), fill=color, tags="star")

    def _draw_available_pieces(self):
        self.pieces_canvas.delete("all")
        if not self.game_data: return
        available_pieces = [p for p in self.game_data['pieces'] if p.id not in self.placed_pieces]
        x_offset = 20
        for piece in available_pieces:
            is_selected = self.selected_piece and self.selected_piece.id == piece.id
            piece.draw(self.pieces_canvas, x_offset, 10, is_selected)
            bbox = self.pieces_canvas.bbox(f"piece_{piece.id}")
            if bbox:
                self.pieces_canvas.create_rectangle(bbox, fill="", outline="", tags=(f"clickable_{piece.id}", "piece_click_area"))
                x_offset = bbox[2] + 20

    def on_piece_select(self, event):
        if not self.game_active: return
        item = self.pieces_canvas.find_closest(event.x, event.y)
        if not item: return
        tags = self.pieces_canvas.gettags(item[0])
        clicked_piece_id = None
        for tag in tags:
            if tag.startswith("clickable_"):
                clicked_piece_id = int(tag.split("_")[1])
                break
        if clicked_piece_id is not None:
            self.selected_piece = next((p for p in self.game_data['pieces'] if p.id == clicked_piece_id), None)
            self._draw_available_pieces()
            self.update_status()

    def _is_valid_placement(self, piece, row, col):
        abs_shape = piece.get_absolute_shape(row, col)
        if not abs_shape.issubset(self.game_data['board_shape']):
            return False
        placed_cells = set()
        for p_id in self.placed_pieces:
            if self.selected_piece and p_id == self.selected_piece.id: continue
            p_row, p_col, p_obj = self.placed_pieces[p_id]
            placed_cells.update(p_obj.get_absolute_shape(p_row, p_col))
        if not abs_shape.isdisjoint(placed_cells):
            return False
        return True

    def update_star_status(self):
        covered_cells = set()
        for r, c, piece in self.placed_pieces.values():
            covered_cells.update(piece.get_absolute_shape(r, c))
        for star_loc in self.game_data['star_locations']:
            self.star_status[star_loc] = "lit" if star_loc in covered_cells else "unlit"

class PuzzlePiece:
    def __init__(self, piece_id, color, shape):
        self.id = piece_id
        self.color = color
        self.original_shape = shape  # 保存原始形状，用于重置
        self.shape = shape           # 当前形状，可以被旋转

    def rotate(self):
        """将拼图块顺时针旋转90度。"""
        if not self.shape:
            return
        
        # 找到当前形状边界框的高度，用于坐标变换
        max_r = max(r for r, c in self.shape)
        
        # 应用旋转公式: (r, c) -> (c, max_r - r)
        rotated_shape_raw = {(c, max_r - r) for r, c in self.shape}
        
        # 将旋转后的形状平移，使其左上角回到(0,0)
        min_r = min(r for r, c in rotated_shape_raw)
        min_c = min(c for r, c in rotated_shape_raw)
        
        self.shape = frozenset((r - min_r, c - min_c) for r, c in rotated_shape_raw)

    def reset_shape(self):
        """将拼图块恢复到其原始、未旋转的形状。"""
        self.shape = self.original_shape

    def get_absolute_shape(self, top_row, left_col):
        return set((top_row + r_off, left_col + c_off) for r_off, c_off in self.shape)

    def draw(self, canvas, x_offset, y_offset, is_selected):
        tag = f"piece_{self.id}"
        canvas.delete(tag)
        outline_color = SELECTED_PIECE_OUTLINE_COLOR if is_selected else PIECE_OUTLINE_COLOR
        outline_width = 3 if is_selected else 1.5
        for r_off, c_off in self.shape:
            x1 = x_offset + c_off * CELL_SIZE
            y1 = y_offset + r_off * CELL_SIZE
            x2 = x1 + CELL_SIZE
            y2 = y1 + CELL_SIZE
            canvas.create_rectangle(x1, y1, x2, y2, 
                                    fill=PIECE_COLORS[self.color], 
                                    outline=outline_color, 
                                    width=outline_width,
                                    tags=tag)

if __name__ == "__main__":
    app = PuzzleGame()
    app.mainloop()