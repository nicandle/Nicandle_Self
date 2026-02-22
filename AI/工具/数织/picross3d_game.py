import tkinter as tk
from tkinter import messagebox, simpledialog
import random
from itertools import combinations
import numpy as np

try:
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d import Axes3D
    VISUALIZATION_AVAILABLE = True
except ImportError:
    VISUALIZATION_AVAILABLE = False

# --- 游戏核心状态定义 ---
# 0: 未知, 1: 空白, >1: 填充 (不同的数字代表不同颜色)
UNKNOWN = 0
EMPTY = 1
# --- 颜色定义 (从2开始) ---
FILLED_DEFAULT = 2 # 默认填充色 (用于随机生成)
COLOR_BROWN = 3
COLOR_RED = 4

# --- 颜色映射 ---
COLOR_MAP = {
    FILLED_DEFAULT: "#2a4d69", # 默认蓝色
    COLOR_BROWN: "#8B4513",    # 棕色
    COLOR_RED: "#DC143C",      # 红色
}

# --- 视觉样式定义 ---
CELL_SIZE = 40
GRID_COLOR = "#a0a0a0"
FILLED_COLOR_UI = "#2a4d69" # UI中统一用一种颜色显示填充
EMPTY_COLOR_UI = "white"
EMPTY_MARK_COLOR = "#cccccc"
HOVER_COLOR = "#e0e0e0"
CLUE_FONT = ("Arial", 9)
Z_CLUE_FONT = ("Arial", 10, "bold")
CLUE_ERROR_COLOR = "#e03f3f"
CLUE_NORMAL_COLOR = "black"
CLUE_DONE_COLOR = "gray"
STATUS_FONT = ("Arial", 10)


def show_3d_visualization(solution_grid, size):
    """使用 Matplotlib 渲染并显示带颜色的3D模型"""
    if not VISUALIZATION_AVAILABLE:
        messagebox.showinfo("3D视图", "未找到 Matplotlib 或 NumPy 库，无法显示3D模型。\n请运行 'pip install matplotlib numpy' 进行安装。")
        return

    w, h, d = size
    
    # 创建一个布尔掩码，标记哪些体素需要被绘制
    voxels_mask = np.array([[[cell > EMPTY for cell in row] for row in layer] for layer in solution_grid])
    
    # 创建一个颜色数组，为每个体素指定颜色
    colors = np.empty(voxels_mask.shape, dtype=object)
    for x in range(w):
        for y in range(h):
            for z in range(d):
                color_code = solution_grid[x][y][z]
                colors[x, y, z] = COLOR_MAP.get(color_code, "white") # 如果找不到颜色，默认为白色

    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    ax.set_box_aspect([w, h, d])
    ax.set_xlim(0, w)
    ax.set_ylim(0, h)
    ax.set_zlim(0, d)

    # 使用布尔掩码和颜色数组绘制体素
    ax.voxels(voxels_mask, facecolors=colors, edgecolor='k', linewidth=0.5)

    ax.set_title("恭喜！这是你的3D作品")
    ax.set_xlabel("宽度 (X)")
    ax.set_ylabel("高度 (Y)")
    ax.set_zlabel("深度 (Z)")
    
    plt.tight_layout()
    plt.show()


class PuzzleSolver:
    # 此类无变化
    def __init__(self, clues, size):
        self.clues = clues
        self.width, self.height, self.depth = size
        self.grid = [[[UNKNOWN for _ in range(self.depth)] for _ in range(self.height)] for _ in range(self.width)]
        self.changed_in_pass = True

    def solve(self):
        passes = 0
        max_passes = (self.width * self.height * self.depth)
        while self.changed_in_pass and passes < max_passes:
            self.changed_in_pass = False
            self._solve_axis('x')
            self._solve_axis('y')
            self._solve_axis('z')
            passes += 1
        
        for x in range(self.width):
            for y in range(self.height):
                for z in range(self.depth):
                    if self.grid[x][y][z] == UNKNOWN:
                        return False
        return True

    def _solve_axis(self, axis):
        if axis == 'x':
            for y in range(self.height):
                for z in range(self.depth):
                    line = [self.grid[x][y][z] for x in range(self.width)]
                    clue = self.clues['x'][y * self.depth + z]
                    new_line = self._solve_line(line, clue)
                    if new_line:
                        for x, val in enumerate(new_line):
                            if self.grid[x][y][z] != val:
                                self.grid[x][y][z] = val
                                self.changed_in_pass = True
        elif axis == 'y':
            for x in range(self.width):
                for z in range(self.depth):
                    line = [self.grid[x][y][z] for y in range(self.height)]
                    clue = self.clues['y'][x * self.depth + z]
                    new_line = self._solve_line(line, clue)
                    if new_line:
                        for y, val in enumerate(new_line):
                            if self.grid[x][y][z] != val:
                                self.grid[x][y][z] = val
                                self.changed_in_pass = True
        elif axis == 'z':
            for x in range(self.width):
                for y in range(self.height):
                    line = [self.grid[x][y][z] for z in range(self.depth)]
                    clue = self.clues['z'][y * self.width + x]
                    new_line = self._solve_line(line, clue)
                    if new_line:
                        for z, val in enumerate(new_line):
                            if self.grid[x][y][z] != val:
                                self.grid[x][y][z] = val
                                self.changed_in_pass = True

    def _solve_line(self, line, clue):
        n = len(line)
        k = len(clue)
        
        # 谜题逻辑中，所有 >1 的值都视为 FILLED_DEFAULT
        line_binary = [FILLED_DEFAULT if c > EMPTY else c for c in line]

        if not clue:
            return [EMPTY if cell == UNKNOWN else cell for cell in line]

        if UNKNOWN not in line_binary:
            return None

        total_blocks = sum(clue)
        empty_spaces = n - total_blocks
        
        possible_arrangements = []
        
        num_slots = empty_spaces + k
        if k == 0:
            if FILLED_DEFAULT in line_binary: return None
            return [EMPTY if c == UNKNOWN else c for c in line]
        
        for p in combinations(range(num_slots), k):
            arrangement = [EMPTY] * num_slots
            for i in p:
                arrangement[i] = FILLED_DEFAULT
            
            final_arrangement = []
            clue_idx = 0
            for item in arrangement:
                if item == FILLED_DEFAULT:
                    final_arrangement.extend([FILLED_DEFAULT] * clue[clue_idx])
                    clue_idx += 1
                else:
                    final_arrangement.append(EMPTY)
            
            if len(final_arrangement) > n:
                final_arrangement = final_arrangement[:n]
            while len(final_arrangement) < n:
                final_arrangement.append(EMPTY)

            compatible = True
            for i in range(n):
                if (line_binary[i] == FILLED_DEFAULT and final_arrangement[i] == EMPTY) or \
                   (line_binary[i] == EMPTY and final_arrangement[i] == FILLED_DEFAULT):
                    compatible = False
                    break
            if compatible:
                possible_arrangements.append(final_arrangement)

        if not possible_arrangements:
            return None

        new_line = list(line)
        changed = False
        for i in range(n):
            if new_line[i] == UNKNOWN:
                first_val = possible_arrangements[0][i]
                if all(arr[i] == first_val for arr in possible_arrangements):
                    new_line[i] = first_val
                    changed = True
        
        return new_line if changed else None


class PuzzleGenerator:
    def __init__(self, min_size=(4, 4, 3), max_size=(6, 6, 4)):
        self.min_w, self.min_h, self.min_d = min_size
        self.max_w, self.max_h, self.max_d = max_size

    ### NEW: 生成指定模型的方法 ###
    def generate_from_model(self, model_name):
        solution_grid, size = self._create_model_from_blueprint(model_name)
        if solution_grid is None:
            return None, None

        print(f"正在为模型 '{model_name}' ({size[0]}x{size[1]}x{size[2]}) 生成谜题...")
        clues = self._derive_clues_from_solution(solution_grid, size)
        
        solver = PuzzleSolver(clues, size)
        if solver.solve():
            print("... 谜题验证成功 (逻辑可解)！")
            puzzle_solution = {'size': size, 'grid': solution_grid}
            return clues, puzzle_solution
        else:
            print("... 此模型无法通过逻辑完全解决，无法生成谜题。")
            return None, None

    ### NEW: 模型蓝图库 ###
    def _create_model_from_blueprint(self, model_name):
        if model_name.lower() == 'chair':
            w, h, d = 5, 6, 5
            grid = [[[EMPTY for _ in range(d)] for _ in range(h)] for _ in range(w)]
            
            # 坐垫 (红色)
            for x in range(1, 4):
                for z in range(1, 4):
                    grid[x][2][z] = COLOR_RED
            
            # 四条腿 (棕色)
            for y in range(2):
                grid[1][y][1] = COLOR_BROWN
                grid[1][y][3] = COLOR_BROWN
                grid[3][y][1] = COLOR_BROWN
                grid[3][y][3] = COLOR_BROWN

            # 椅背 (棕色)
            for y in range(3, 5):
                for x in range(1, 4):
                    grid[x][y][1] = COLOR_BROWN
            
            return grid, (w, h, d)
        
        # 在这里可以添加更多模型，例如 'table', 'house' 等
        # if model_name.lower() == 'table':
        #     ...
        
        return None, None # 如果找不到模型

    def generate_random(self):
        retry_count = 0
        while True:
            width = random.randint(self.min_w, self.max_w)
            height = random.randint(self.min_h, self.max_h)
            depth = random.randint(self.min_d, self.max_d)
            size = (width, height, depth)
            
            print(f"({retry_count}) 尝试生成一个随机的 {width}x{height}x{depth} 谜题...")
            
            solution_grid = self._create_random_solution(width, height, depth)
            clues = self._derive_clues_from_solution(solution_grid, size)
            
            solver = PuzzleSolver(clues, size)
            if solver.solve():
                print("... 谜题验证成功 (逻辑可解)！")
                puzzle_solution = {'size': size, 'grid': solution_grid}
                return clues, puzzle_solution
            else:
                print("... 谜题无法通过逻辑完全解决，重新生成。")
                retry_count += 1
    
    def _create_random_solution(self, width, height, depth):
        grid = [[[EMPTY for _ in range(depth)] for _ in range(height)] for _ in range(width)]
        total_cells = width * height * depth
        fill_target = int(total_cells * random.uniform(0.3, 0.55))
        filled_count = 0
        if total_cells == 0: return grid
        
        start_x, start_y, start_z = (random.randint(0, width-1), random.randint(0, height-1), random.randint(0, depth-1))
        grid[start_x][start_y][start_z] = FILLED_DEFAULT
        filled_count += 1
        
        candidates = self._get_neighbors(start_x, start_y, start_z, width, height, depth, grid)
        
        while candidates and filled_count < fill_target:
            x, y, z = random.choice(candidates)
            candidates.remove((x, y, z))
            if grid[x][y][z] == EMPTY:
                grid[x][y][z] = FILLED_DEFAULT
                filled_count += 1
                new_neighbors = self._get_neighbors(x, y, z, width, height, depth, grid)
                for neighbor in new_neighbors:
                    if neighbor not in candidates:
                        candidates.append(neighbor)
        return grid

    def _get_neighbors(self, x, y, z, w, h, d, grid):
        neighbors = []
        for dx, dy, dz in [(1,0,0), (-1,0,0), (0,1,0), (0,-1,0), (0,0,1), (0,0,-1)]:
            nx, ny, nz = x + dx, y + dy, z + dz
            if 0 <= nx < w and 0 <= ny < h and 0 <= nz < d and grid[nx][ny][nz] == EMPTY:
                neighbors.append((nx, ny, nz))
        return neighbors

    def _derive_clues_from_solution(self, grid, size):
        width, height, depth = size
        clues = {'x': [], 'y': [], 'z': []}
        for y in range(height):
            for z in range(depth):
                clues['x'].append(self._get_clue_for_line([grid[x][y][z] for x in range(width)]))
        for x in range(width):
            for z in range(depth):
                clues['y'].append(self._get_clue_for_line([grid[x][y][z] for y in range(height)]))
        for y in range(height):
            for x in range(width):
                clues['z'].append(self._get_clue_for_line([grid[x][y][z] for z in range(depth)]))
        return clues

    def _get_clue_for_line(self, line):
        # 关键：任何 > EMPTY 的值都视为填充
        line_str = "".join(["F" if c > EMPTY else " " for c in line])
        groups = line_str.split()
        return [len(s) for s in groups]


class Picross3DGame:
    def __init__(self, clues, solution):
        self.clues = clues
        self.width, self.height, self.depth = solution['size']
        self.solution_grid = solution['grid']
        # 关键：统计所有 > EMPTY 的格子
        self.total_filled_blocks = sum(1 for x in self.solution_grid for y in x for c in y if c > EMPTY)
        
        self.player_grid = [[[UNKNOWN for _ in range(self.depth)] for _ in range(self.height)] for _ in range(self.width)]
        self.player_filled_count = 0
        self.current_z = 0

    def toggle_cell(self, x, y, z, button):
        current_state = self.player_grid[x][y][z]
        
        if button == 1: # 左键填充
            new_state = FILLED_DEFAULT if current_state <= EMPTY else UNKNOWN
        else: # 右键标记为空
            new_state = EMPTY if current_state != EMPTY else UNKNOWN
        
        if current_state <= EMPTY and new_state > EMPTY:
            self.player_filled_count += 1
        elif current_state > EMPTY and new_state <= EMPTY:
            self.player_filled_count -= 1
            
        self.player_grid[x][y][z] = new_state
        return new_state

    def change_layer(self, direction):
        self.current_z = (self.current_z + direction + self.depth) % self.depth

    def check_win(self):
        if self.player_filled_count != self.total_filled_blocks:
            return False
        for x in range(self.width):
            for y in range(self.height):
                for z in range(self.depth):
                    is_solution_filled = self.solution_grid[x][y][z] > EMPTY
                    is_player_filled = self.player_grid[x][y][z] > EMPTY
                    if is_solution_filled != is_player_filled:
                        return False
        return True

    def get_line_status(self, axis, idx1, idx2):
        if axis == 'x':
            line = [self.player_grid[i][idx1][idx2] for i in range(self.width)]
            clue = self.clues['x'][idx1 * self.depth + idx2]
        elif axis == 'y':
            line = [self.player_grid[idx1][i][idx2] for i in range(self.height)]
            clue = self.clues['y'][idx1 * self.depth + idx2]
        elif axis == 'z':
            line = [self.player_grid[idx1][idx2][i] for i in range(self.depth)]
            clue = self.clues['z'][idx2 * self.width + idx1]
        else:
            return False, False

        is_complete = UNKNOWN not in line
        if not is_complete:
            return False, False

        line_str = "".join(["F" if c > EMPTY else " " for c in line])
        groups = [len(s) for s in line_str.split()]
        
        clue_to_check = clue if clue else []
        is_error = (groups != clue_to_check)
        return is_complete, is_error


class Picross3D_UI(tk.Toplevel):
    def __init__(self, master, game, app_controller):
        super().__init__(master)
        self.game = game
        self.app = app_controller
        
        self.drag_mode = None
        self.drag_processed_cells = set()
        self.last_hover_coords = None

        self.title(f"3D数织 - {game.width}x{game.height}x{game.depth}")
        self.protocol("WM_DELETE_WINDOW", self.on_close)

        main_frame = tk.Frame(self, padx=10, pady=10)
        main_frame.pack(fill="both", expand=True)

        game_area = tk.Frame(main_frame)
        game_area.pack(side="left", fill="both", expand=True)

        self.x_clues_frame = tk.Frame(game_area)
        self.x_clues_frame.grid(row=0, column=1, sticky="s")
        self.y_clues_frame = tk.Frame(game_area)
        self.y_clues_frame.grid(row=1, column=0, sticky="e")

        canvas_width = self.game.width * CELL_SIZE
        canvas_height = self.game.height * CELL_SIZE
        self.canvas = tk.Canvas(game_area, width=canvas_width, height=canvas_height, bg=EMPTY_COLOR_UI)
        self.canvas.grid(row=1, column=1)
        
        self.status_bar = tk.Label(game_area, text="", font=STATUS_FONT, bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.grid(row=2, column=0, columnspan=2, sticky="ew")

        control_frame = tk.Frame(main_frame, padx=10)
        control_frame.pack(side="right", fill="y")

        layer_frame = tk.LabelFrame(control_frame, text="层控制", padx=5, pady=5)
        layer_frame.pack(fill="x", pady=5)
        self.layer_label = tk.Label(layer_frame, text="", font=("Arial", 12, "bold"))
        self.layer_label.pack(pady=5)
        tk.Button(layer_frame, text="上一层 (W)", command=lambda: self.change_layer_and_redraw(-1)).pack(fill="x")
        tk.Button(layer_frame, text="下一层 (S)", command=lambda: self.change_layer_and_redraw(1)).pack(fill="x")

        action_frame = tk.LabelFrame(control_frame, text="游戏操作", padx=5, pady=5)
        action_frame.pack(fill="x", pady=5)
        tk.Button(action_frame, text="新游戏", command=self.request_new_game).pack(fill="x", pady=2)
        tk.Button(action_frame, text="检查胜利", command=self.check_win_manually).pack(fill="x", pady=2)
        tk.Button(action_frame, text="玩法说明", command=self.show_help).pack(fill="x", pady=2)

        self.canvas.bind("<Button-1>", self.on_mouse_down)
        self.canvas.bind("<Button-3>", self.on_mouse_down)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<B3-Motion>", self.on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_mouse_up)
        self.canvas.bind("<ButtonRelease-3>", self.on_mouse_up)
        self.canvas.bind("<Motion>", self.on_mouse_hover)
        self.canvas.bind("<Leave>", self.on_mouse_leave)
        self.bind("<w>", lambda e: self.change_layer_and_redraw(-1))
        self.bind("<s>", lambda e: self.change_layer_and_redraw(1))

        self.redraw_all()

    def redraw_all(self):
        self.update_status_bar()
        self.draw_clues()
        self.draw_grid()

    def draw_grid(self):
        self.canvas.delete("all")
        z = self.game.current_z
        for y in range(self.game.height):
            for x in range(self.game.width):
                state = self.game.player_grid[x][y][z]
                self.draw_cell(x, y, state)

    def draw_cell(self, x, y, state, is_hover=False):
        x1, y1, x2, y2 = x * CELL_SIZE, y * CELL_SIZE, (x + 1) * CELL_SIZE, (y + 1) * CELL_SIZE
        fill = EMPTY_COLOR_UI
        if is_hover and state == UNKNOWN:
            fill = HOVER_COLOR
        elif state > EMPTY: # 任何填充状态
            fill = FILLED_COLOR_UI
        
        self.canvas.create_rectangle(x1, y1, x2, y2, fill=fill, outline=GRID_COLOR, tags=f"cell_{x}_{y}")
        
        if state == EMPTY:
            self.canvas.create_line(x1+5, y1+5, x2-5, y2-5, fill=EMPTY_MARK_COLOR, width=2, tags=f"cell_{x}_{y}")
            self.canvas.create_line(x1+5, y2-5, x2-5, y1+5, fill=EMPTY_MARK_COLOR, width=2, tags=f"cell_{x}_{y}")
        
        if state == UNKNOWN:
            clue = self.game.clues['z'][y * self.game.width + x]
            clue_text = " ".join(map(str, clue or ['0']))
            
            is_complete, is_error = self.game.get_line_status('z', x, y)
            color = CLUE_NORMAL_COLOR
            if is_error: color = CLUE_ERROR_COLOR
            elif is_complete: color = CLUE_DONE_COLOR
            
            self.canvas.create_text(x1 + CELL_SIZE/2, y1 + CELL_SIZE/2, text=clue_text, 
                                    font=Z_CLUE_FONT, fill=color, tags=f"cell_{x}_{y}")

    def handle_win(self):
        # 胜利时，我们用包含颜色信息的 solution_grid 来渲染
        show_3d_visualization(self.game.solution_grid, (self.game.width, self.game.height, self.game.depth))
        
        self.app.win_streak += 1
        play_again = messagebox.askyesno("恭喜!", f"你成功解决了这个谜题！\n当前连胜: {self.app.win_streak}\n\n要挑战下一个吗？", parent=self)
        self.destroy()
        if play_again:
            self.app.start_new_random_game(reset_streak=False)
        else:
            self.app.show_main_menu()

    def show_help(self):
        help_text = """
        【3D数织 - 玩法说明】

        1. 目标: 根据三种方向的线索填充方块，揭示隐藏的形状。

        2. 操作:
           - 左键点击/拖拽: 填充方块。
           - 右键点击/拖拽: 标记方块为空 (X)。

        3. 线索:
           - 顶部/左侧: 当前切片的行/列线索。
           - 单元格内数字: 贯穿所有层的Z轴线索。
           - 线索颜色会根据完成状态和正确性变化。

        4. 胜利:
           - 解开谜题后，会弹出一个可交互的3D模型窗口！
           - 如果是指定模型，会显示预设的颜色。
        """
        messagebox.showinfo("玩法说明", help_text, parent=self)

    def process_cell_action(self, x, y, button):
        z = self.game.current_z
        coords = (x, y, z)
        if coords in self.drag_processed_cells: return
        if 0 <= x < self.game.width and 0 <= y < self.game.height:
            new_state = self.game.toggle_cell(x, y, z, button)
            self.draw_cell(x, y, new_state)
            self.drag_processed_cells.add(coords)
    def on_mouse_down(self, event):
        self.drag_mode = event.num
        self.drag_processed_cells.clear()
        x, y = event.x // CELL_SIZE, event.y // CELL_SIZE
        self.process_cell_action(x, y, self.drag_mode)
    def on_mouse_drag(self, event):
        if self.drag_mode is None: return
        x, y = event.x // CELL_SIZE, event.y // CELL_SIZE
        self.process_cell_action(x, y, self.drag_mode)
    def on_mouse_up(self, event):
        self.drag_mode = None
        self.drag_processed_cells.clear()
        self.redraw_all()
        if self.game.check_win():
            self.handle_win()
    def on_mouse_hover(self, event):
        x, y = event.x // CELL_SIZE, event.y // CELL_SIZE
        if self.last_hover_coords and self.last_hover_coords != (x, y):
            lx, ly = self.last_hover_coords
            if 0 <= lx < self.game.width and 0 <= ly < self.game.height:
                self.draw_cell(lx, ly, self.game.player_grid[lx][ly][self.game.current_z])
        if 0 <= x < self.game.width and 0 <= y < self.game.height:
            self.draw_cell(x, y, self.game.player_grid[x][y][self.game.current_z], is_hover=True)
            self.last_hover_coords = (x, y)
        else:
            self.last_hover_coords = None
    def on_mouse_leave(self, event):
        if self.last_hover_coords:
            lx, ly = self.last_hover_coords
            if 0 <= lx < self.game.width and 0 <= ly < self.game.height:
                self.draw_cell(lx, ly, self.game.player_grid[lx][ly][self.game.current_z])
        self.last_hover_coords = None
    def update_status_bar(self):
        layer_text = f"当前层: {self.game.current_z + 1}/{self.game.depth}"
        filled_text = f"已填充: {self.game.player_filled_count}/{self.game.total_filled_blocks}"
        self.status_bar.config(text=f"  {layer_text}    |    {filled_text}")
        self.layer_label.config(text=f"{self.game.current_z + 1} / {self.game.depth}")
    def draw_clues(self):
        z = self.game.current_z
        for widget in self.x_clues_frame.winfo_children(): widget.destroy()
        for widget in self.y_clues_frame.winfo_children(): widget.destroy()
        for x in range(self.game.width):
            clue = self.game.clues['y'][x * self.game.depth + z]
            clue_text = "\n".join(map(str, clue or ['0']))
            is_complete, is_error = self.game.get_line_status('y', x, z)
            color = CLUE_NORMAL_COLOR
            if is_error: color = CLUE_ERROR_COLOR
            elif is_complete: color = CLUE_DONE_COLOR
            tk.Label(self.x_clues_frame, text=clue_text, font=CLUE_FONT, fg=color, width=4, height=5).grid(row=0, column=x, sticky="s")
        for y in range(self.game.height):
            clue = self.game.clues['x'][y * self.game.depth + z]
            clue_text = " ".join(map(str, clue or ['0']))
            is_complete, is_error = self.game.get_line_status('x', y, z)
            color = CLUE_NORMAL_COLOR
            if is_error: color = CLUE_ERROR_COLOR
            elif is_complete: color = CLUE_DONE_COLOR
            tk.Label(self.y_clues_frame, text=clue_text, font=CLUE_FONT, fg=color, height=2, width=6).grid(row=y, column=0, sticky="e")
    def change_layer_and_redraw(self, direction):
        self.game.change_layer(direction)
        self.redraw_all()
    def check_win_manually(self):
        if self.game.check_win():
            self.handle_win()
        else:
            messagebox.showinfo("检查结果", "谜题尚未完成或存在错误。", parent=self)
    def request_new_game(self):
        self.destroy()
        self.app.show_main_menu()
    def on_close(self):
        self.destroy()
        self.app.show_main_menu()


class GameApplication:
    def __init__(self, root):
        self.root = root
        self.root.title("AI聊天机器人 - 3D数织")
        self.generator = PuzzleGenerator()
        self.win_streak = 0
        self.current_game_window = None
        
        self.main_menu_frame = tk.Frame(root, padx=50, pady=30)
        
        tk.Label(self.main_menu_frame, text="欢迎来到3D数织!", font=("Arial", 20, "bold")).pack(pady=(0, 20))
        
        self.streak_label = tk.Label(self.main_menu_frame, text="", font=("Arial", 14))
        self.streak_label.pack(pady=10)
        
        # 随机游戏按钮
        tk.Button(self.main_menu_frame, text="开始随机游戏", font=("Arial", 16), command=self.start_new_random_game).pack(pady=10, ipadx=10, ipady=5)

        # 指定模型区域
        model_frame = tk.LabelFrame(self.main_menu_frame, text="从蓝图生成", padx=15, pady=10)
        model_frame.pack(pady=20, fill="x")
        tk.Label(model_frame, text="输入模型名称 (例如: chair):").pack(anchor="w")
        self.model_entry = tk.Entry(model_frame, font=("Arial", 14))
        self.model_entry.pack(fill="x", pady=5)
        tk.Button(model_frame, text="生成指定模型", font=("Arial", 14), command=self.start_new_model_game).pack(pady=5)
        
        self.show_main_menu()

    def show_main_menu(self):
        if self.current_game_window:
            self.current_game_window.destroy()
            self.current_game_window = None
        
        self.root.deiconify()
        self.main_menu_frame.pack()
        self.streak_label.config(text=f"当前连胜: {self.win_streak}")

    def start_new_random_game(self, reset_streak=True):
        if reset_streak:
            self.win_streak = 0
        
        self.main_menu_frame.pack_forget()
        
        clues, solution = self.generator.generate_random()
        self._launch_game(clues, solution)

    def start_new_model_game(self):
        model_name = self.model_entry.get()
        if not model_name:
            messagebox.showwarning("输入错误", "请输入一个模型名称。")
            return
        
        self.win_streak = 0 # 从模型开始，重置连胜
        self.main_menu_frame.pack_forget()
        
        clues, solution = self.generator.generate_from_model(model_name)
        
        if clues and solution:
            self._launch_game(clues, solution)
        else:
            messagebox.showerror("生成失败", f"无法为模型 '{model_name}' 生成可解的谜题。\n请检查模型名称是否正确，或该模型本身是否符合逻辑。")
            self.show_main_menu()

    def _launch_game(self, clues, solution):
        game = Picross3DGame(clues, solution)
        self.current_game_window = Picross3D_UI(self.root, game, self)

if __name__ == "__main__":
    root = tk.Tk()
    app = GameApplication(root)
    root.mainloop()