import tkinter as tk
from tkinter import ttk, messagebox
import math
import time

class RasterizationApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Алгоритмы Растеризации (Lab)")
        self.root.geometry("1000x700")

        # --- ИСПРАВЛЕНИЕ 1: Уменьшили начальный размер клетки ---
        self.pixel_size = 10  # Было 25, стало 10 (чтобы влезало больше)

        self.offset_x = 0     # Смещение центра
        self.offset_y = 0
        self.show_grid = True

        # Данные для отрисовки
        self.drawn_pixels = [] # Список (x, y, color, alpha)

        # GUI Layout
        self.setup_ui()

        # Привязка событий
        self.canvas.bind("<Configure>", self.on_resize)
        self.canvas.bind("<MouseWheel>", self.on_zoom)
        self.canvas.bind("<ButtonPress-1>", self.on_drag_start)
        self.canvas.bind("<B1-Motion>", self.on_drag_motion)

        self.redraw()

    def setup_ui(self):
        # Панель управления (слева)
        control_panel = ttk.Frame(self.root, padding="10")
        control_panel.pack(side=tk.LEFT, fill=tk.Y)

        # Ввод координат
        ttk.Label(control_panel, text="Координаты:").pack(pady=5)

        coord_frame = ttk.Frame(control_panel)
        coord_frame.pack()

        ttk.Label(coord_frame, text="X1:").grid(row=0, column=0)
        self.entry_x1 = ttk.Entry(coord_frame, width=5)
        self.entry_x1.grid(row=0, column=1)
        self.entry_x1.insert(0, "-5")

        ttk.Label(coord_frame, text="Y1:").grid(row=0, column=2)
        self.entry_y1 = ttk.Entry(coord_frame, width=5)
        self.entry_y1.grid(row=0, column=3)
        self.entry_y1.insert(0, "-3")

        ttk.Label(coord_frame, text="X2 / R:").grid(row=1, column=0)
        self.entry_x2 = ttk.Entry(coord_frame, width=5)
        self.entry_x2.grid(row=1, column=1)
        self.entry_x2.insert(0, "8")

        ttk.Label(coord_frame, text="Y2:").grid(row=1, column=2)
        self.entry_y2 = ttk.Entry(coord_frame, width=5)
        self.entry_y2.grid(row=1, column=3)
        self.entry_y2.insert(0, "5")

        ttk.Label(control_panel, text="(Для окружности X2 это Радиус)", font=("Arial", 8)).pack()

        # Выбор алгоритма
        ttk.Label(control_panel, text="Алгоритм:").pack(pady=10)
        self.algo_var = tk.StringVar(value="bresenham")

        algos = [
            ("Пошаговый (Step-by-Step)", "step"),
            ("ЦДА (DDA)", "dda"),
            ("Брезенхем (Линия)", "bresenham"),
             ("Кастла-Питвея (Линия)", "castle"),
            ("Брезенхем (Окружность)", "circle"),
            ("Сглаживание (Ву)", "wu") # Бонус
        ]

        for text, val in algos:
            ttk.Radiobutton(control_panel, text=text, variable=self.algo_var, value=val).pack(anchor=tk.W)

        # Кнопки
        ttk.Button(control_panel, text="Построить", command=self.run_algorithm).pack(pady=10, fill=tk.X)
        ttk.Button(control_panel, text="Очистить", command=self.clear_canvas).pack(pady=5, fill=tk.X)

        # Лог
        ttk.Label(control_panel, text="Отчет (Время):").pack(pady=10)
        self.log_text = tk.Text(control_panel, height=15, width=30, font=("Consolas", 9))
        self.log_text.pack()

        # Холст (справа)
        self.canvas = tk.Canvas(self.root, bg="white")
        self.canvas.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

    # --- Логика отрисовки сетки и осей ---
    def redraw(self):
        self.canvas.delete("all")
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()

        # Центр координат
        cx, cy = w // 2 + self.offset_x, h // 2 + self.offset_y

        # Рисуем сетку
        # Если слишком мелко (<5), сетку отключаем, но оси оставляем
        if self.pixel_size >= 5:

            # --- Вертикальные линии ---
            start_x = cx % self.pixel_size
            for x in range(start_x, w, self.pixel_size):
                grid_x = round((x - cx) / self.pixel_size)

                color = "#eee" # Светло-серый для сетки
                width = 1

                if grid_x == 0:
                    color = "black" # Ось Y черная
                    width = 2

                self.canvas.create_line(x, 0, x, h, fill=color, width=width)

                # Цифры на оси X (рисуем если масштаб позволяет и это не 0)
                if self.pixel_size >= 20 and grid_x != 0:
                    self.canvas.create_text(x, cy + 12, text=str(grid_x), font=("Arial", 8), fill="#555")
                # Если масштаб мелкий, рисуем цифры реже (каждые 5)
                elif self.pixel_size >= 10 and grid_x != 0 and grid_x % 5 == 0:
                    self.canvas.create_text(x, cy + 12, text=str(grid_x), font=("Arial", 8), fill="#555")


            # --- Горизонтальные линии ---
            start_y = cy % self.pixel_size
            for y in range(start_y, h, self.pixel_size):
                grid_y = round((cy - y) / self.pixel_size)

                color = "#eee"
                width = 1

                if grid_y == 0:
                    color = "black" # Ось X черная
                    width = 2

                self.canvas.create_line(0, y, w, y, fill=color, width=width)

                # Цифры на оси Y
                if self.pixel_size >= 20 and grid_y != 0:
                     self.canvas.create_text(cx - 15, y, text=str(grid_y), font=("Arial", 8), fill="#555")
                elif self.pixel_size >= 10 and grid_y != 0 and grid_y % 5 == 0:
                     self.canvas.create_text(cx - 15, y, text=str(grid_y), font=("Arial", 8), fill="#555")

        # Ноль в центре
        if self.pixel_size >= 10:
            self.canvas.create_text(cx - 10, cy + 12, text="0", font=("Arial", 8, "bold"))

        # Стрелочки (буквы) на концах
        self.canvas.create_text(w-20, cy-20, text="X", fill="red", font=("Arial", 12, "bold"))
        self.canvas.create_text(cx+20, 20, text="Y", fill="red", font=("Arial", 12, "bold"))

        # Отрисовка пикселей
        for (px, py, color, alpha) in self.drawn_pixels:
            screen_x = cx + px * self.pixel_size
            screen_y = cy - py * self.pixel_size # Y вверх

            # Эмуляция прозрачности для Ву
            fill_color = color
            if alpha < 1.0:
                intensity = int((1 - alpha) * 255)
                # Защита от выхода за границы 255
                intensity = max(0, min(255, intensity))
                hex_c = f"#{intensity:02x}{intensity:02x}{intensity:02x}"
                if color != "black" and color != "#000000":
                    fill_color = color
                else:
                    fill_color = hex_c

            self.canvas.create_rectangle(
                screen_x, screen_y,
                screen_x + self.pixel_size, screen_y - self.pixel_size,
                fill=fill_color, outline=""
            )

        # Инфо
        self.canvas.create_text(10, 10, anchor=tk.NW, text=f"Масштаб: {self.pixel_size}px/ед.\nЗум: Колесико мыши", fill="blue")

    # --- Алгоритмы ---

    def algo_step_by_step(self, x1, y1, x2, y2):
        points = []
        if x1 == x2: # Вертикальная линия
            start, end = min(y1, y2), max(y1, y2)
            for y in range(start, end + 1):
                points.append((x1, y, "black", 1.0))
        else:
            k = (y2 - y1) / (x2 - x1)
            b = y1 - k * x1
            start_x, end_x = min(x1, x2), max(x1, x2)
            for x in range(start_x, end_x + 1):
                y = k * x + b
                points.append((x, round(y), "black", 1.0))
        return points

    def algo_dda(self, x1, y1, x2, y2):
        points = []
        length = max(abs(x2 - x1), abs(y2 - y1))
        if length == 0:
            return [(x1, y1, "black", 1.0)]

        dx = (x2 - x1) / length
        dy = (y2 - y1) / length

        x, y = x1, y1
        for _ in range(length + 1):
            points.append((round(x), round(y), "black", 1.0))
            x += dx
            y += dy
        return points

    def algo_bresenham(self, x1, y1, x2, y2):
        points = []
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        sx = 1 if x1 < x2 else -1
        sy = 1 if y1 < y2 else -1
        err = dx - dy

        while True:
            points.append((x1, y1, "black", 1.0))
            if x1 == x2 and y1 == y2:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x1 += sx
            if e2 < dx:
                err += dx
                y1 += sy
        return points

    def algo_bresenham_circle(self, xc, yc, r):
        points = []
        x = 0
        y = r
        d = 3 - 2 * r

        def add_octants(cx, cy, x, y):
            pts = [
                (cx+x, cy+y), (cx-x, cy+y), (cx+x, cy-y), (cx-x, cy-y),
                (cx+y, cy+x), (cx-y, cy+x), (cx+y, cy-x), (cx-y, cy-x)
            ]
            for p in pts:
                points.append((p[0], p[1], "black", 1.0))

        add_octants(xc, yc, x, y)
        while y >= x:
            x += 1
            if d > 0:
                y -= 1
                d = d + 4 * (x - y) + 10
            else:
                d = d + 4 * x + 6
            add_octants(xc, yc, x, y)
        return points

    def algo_wu(self, x1, y1, x2, y2):
        # Бонус: Сглаживание (Исправленная версия)
        points = []

        def plot(x, y, c):
            # c - это прозрачность от 0.0 до 1.0
            # Если c выходит за границы из-за ошибок округления, ограничиваем
            c = max(0.0, min(1.0, c))
            points.append((x, y, "black", c))

        # ВАЖНО: Используем math.floor вместо int для корректной работы
        # с отрицательными координатами
        def ipart(x): return math.floor(x)
        def fpart(x): return x - math.floor(x)
        def rfpart(x): return 1 - fpart(x)

        steep = abs(y2 - y1) > abs(x2 - x1)
        if steep:
            x1, y1 = y1, x1
            x2, y2 = y2, x2
        if x1 > x2:
            x1, x2 = x2, x1
            y1, y2 = y2, y1

        dx = x2 - x1
        dy = y2 - y1
        if dx == 0.0:
            gradient = 1.0
        else:
            gradient = dy / dx

        # --- Обработка первой точки ---
        xend = round(x1)
        yend = y1 + gradient * (xend - x1)
        xgap = rfpart(x1 + 0.5)
        xpxl1 = xend
        ypxl1 = ipart(yend)

        if steep:
            plot(ypxl1,   xpxl1, rfpart(yend) * xgap)
            plot(ypxl1+1, xpxl1,  fpart(yend) * xgap)
        else:
            plot(xpxl1, ypxl1,   rfpart(yend) * xgap)
            plot(xpxl1, ypxl1+1,  fpart(yend) * xgap)

        intery = yend + gradient

        # --- Обработка второй точки ---
        xend = round(x2)
        yend = y2 + gradient * (xend - x2)
        xgap = fpart(x2 + 0.5)
        xpxl2 = xend
        ypxl2 = ipart(yend)

        if steep:
            plot(ypxl2,   xpxl2, rfpart(yend) * xgap)
            plot(ypxl2+1, xpxl2,  fpart(yend) * xgap)
        else:
            plot(xpxl2, ypxl2,   rfpart(yend) * xgap)
            plot(xpxl2, ypxl2+1,  fpart(yend) * xgap)

        # --- Основной цикл ---
        for x in range(xpxl1 + 1, xpxl2):
            if steep:
                plot(ipart(intery),   x, rfpart(intery))
                plot(ipart(intery)+1, x,  fpart(intery))
            else:
                plot(x, ipart(intery),   rfpart(intery))
                plot(x, ipart(intery)+1,  fpart(intery))
            intery = intery + gradient

        return points

    def algo_castle_pitteway(self, x1, y1, x2, y2):
        """
        Алгоритм Кастла-Питвея для линии.
        Математически эквивалентен Брезенхему, но строится на логике 'средней точки'.
        """
        points = []

        dx = abs(x2 - x1)
        dy = abs(y2 - y1)

        step_x = 1 if x2 > x1 else -1
        step_y = 1 if y2 > y1 else -1

        x = x1
        y = y1

        points.append((x, y, "black", 1.0))

        # Случай 1: Ось X является ведущей (угол наклона <= 45 градусов)
        if dy <= dx:
            d = 2 * dy - dx  # Начальное значение решающей функции
            for _ in range(dx):
                if d >= 0:
                    y += step_y
                    d += 2 * (dy - dx)
                else:
                    d += 2 * dy
                x += step_x
                points.append((x, y, "black", 1.0))

        # Случай 2: Ось Y является ведущей (угол наклона > 45 градусов)
        else:
            d = 2 * dx - dy
            for _ in range(dy):
                if d >= 0:
                    x += step_x
                    d += 2 * (dx - dy)
                else:
                    d += 2 * dx
                y += step_y
                points.append((x, y, "black", 1.0))

        return points

    # --- Обработка действий ---

    def run_algorithm(self):
        try:
            mode = self.algo_var.get()
            x1 = int(self.entry_x1.get())
            y1 = int(self.entry_y1.get())
            x2 = int(self.entry_x2.get())

            # Для окружности Y2 не нужен, но чтобы не ломать логику чтения
            if mode != 'circle':
                y2 = int(self.entry_y2.get())
            else:
                y2 = 0 # Заглушка

            # Замер времени
            start_time = time.perf_counter_ns()

            new_pixels = []
            if mode == 'step':
                new_pixels = self.algo_step_by_step(x1, y1, x2, y2)
            elif mode == 'dda':
                new_pixels = self.algo_dda(x1, y1, x2, y2)
            elif mode == 'bresenham':
                new_pixels = self.algo_bresenham(x1, y1, x2, y2)
            elif mode == 'castle':
                new_pixels = self.algo_castle_pitteway(x1, y1, x2, y2)
            elif mode == 'circle':
                # x2 используется как Radius
                r = abs(x2)
                new_pixels = self.algo_bresenham_circle(x1, y1, r)
            elif mode == 'wu':
                new_pixels = self.algo_wu(x1, y1, x2, y2)

            end_time = time.perf_counter_ns()
            duration_mcs = (end_time - start_time) / 1000.0 # в микросекундах

            # Добавляем к уже нарисованному
            self.drawn_pixels.extend(new_pixels)
            self.redraw()

            self.log_text.insert(tk.END, f"{mode.upper()}: {duration_mcs:.3f} мкс\n")
            self.log_text.see(tk.END)

        except ValueError:
            messagebox.showerror("Ошибка", "Введите корректные целые числа")

    def clear_canvas(self):
        self.drawn_pixels = []
        self.redraw()

    # --- Управление видом ---
    def on_resize(self, event):
        self.redraw()

    def on_zoom(self, event):
        # --- ИСПРАВЛЕНИЕ 2: Разрешили уменьшать до 1 пикселя ---
        if event.delta > 0:
            self.pixel_size += 1
        else:
            if self.pixel_size > 1: # Было > 4, что мешало отдалять
                self.pixel_size -= 1
        self.redraw()

    def on_drag_start(self, event):
        self.last_mouse_x = event.x
        self.last_mouse_y = event.y

    def on_drag_motion(self, event):
        dx = event.x - self.last_mouse_x
        dy = event.y - self.last_mouse_y
        self.offset_x += dx
        self.offset_y += dy
        self.last_mouse_x = event.x
        self.last_mouse_y = event.y
        self.redraw()

if __name__ == "__main__":
    root = tk.Tk()
    app = RasterizationApp(root)
    root.mainloop()
