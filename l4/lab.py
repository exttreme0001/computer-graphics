import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

# ==========================================
# ЧТЕНИЕ ДАННЫХ
# ==========================================
def read_data(filename):
    lines_coords = []
    window = []
    try:
        with open(filename, 'r') as f:
            lines = f.readlines()
            # Читаем количество отрезков (хотя в питоне можно просто итерировать)
            n = int(lines[0].strip())

            # Читаем отрезки
            for i in range(1, n + 1):
                coords = list(map(float, lines[i].strip().split()))
                lines_coords.append(coords) # [x1, y1, x2, y2]

            # Читаем окно (последняя строка)
            window = list(map(float, lines[n+1].strip().split())) # [xmin, ymin, xmax, ymax]

    except Exception as e:
        print(f"Ошибка чтения файла: {e}")
        return [], []
    return lines_coords, window

# ==========================================
# ЧАСТЬ 1: АЛГОРИТМ СРЕДНЕЙ ТОЧКИ (Midpoint Subdivision)
# Для прямоугольного окна
# ==========================================

INSIDE = 0  # 0000
LEFT   = 1  # 0001
RIGHT  = 2  # 0010
BOTTOM = 4  # 0100
TOP    = 8  # 1000

def compute_code(x, y, xmin, ymin, xmax, ymax):
    code = INSIDE
    if x < xmin:      # слева от окна
        code |= LEFT
    elif x > xmax:    # справа от окна
        code |= RIGHT
    if y < ymin:      # ниже окна
        code |= BOTTOM
    elif y > ymax:    # выше окна
        code |= TOP
    return code

def midpoint_clip_recursive(x1, y1, x2, y2, xmin, ymin, xmax, ymax, results, depth=0):
    """
    Рекурсивная реализация алгоритма средней точки.
    Идея: Если отрезок тривиально видим - рисуем.
          Если тривиально невидим - выкидываем.
          Иначе делим пополам и проверяем половинки.
    """
    # Ограничение глубины рекурсии для предотвращения зависания и точности (epsilon)
    if depth > 100 or (abs(x1 - x2) < 0.1 and abs(y1 - y2) < 0.1):
        # Если отрезок очень маленький, проверяем, внутри ли он, и добавляем
        code1 = compute_code(x1, y1, xmin, ymin, xmax, ymax)
        code2 = compute_code(x2, y2, xmin, ymin, xmax, ymax)
        if (code1 | code2) == 0:
            results.append((x1, y1, x2, y2))
        return

    code1 = compute_code(x1, y1, xmin, ymin, xmax, ymax)
    code2 = compute_code(x2, y2, xmin, ymin, xmax, ymax)

    # 1. Тривиальное принятие (оба конца внутри)
    if (code1 | code2) == 0:
        results.append((x1, y1, x2, y2))
        return

    # 2. Тривиальное отвержение (оба конца с одной стороны снаружи)
    if (code1 & code2) != 0:
        return

    # 3. Отрезок частично внутри или пересекает окно -> делим пополам
    xm = (x1 + x2) / 2
    ym = (y1 + y2) / 2

    midpoint_clip_recursive(x1, y1, xm, ym, xmin, ymin, xmax, ymax, results, depth+1)
    midpoint_clip_recursive(xm, ym, x2, y2, xmin, ymin, xmax, ymax, results, depth+1)

# ==========================================
# ЧАСТЬ 2: АЛГОРИТМ КИРУСА-БЕКА (Cyrus-Beck)
# Для выпуклого многоугольника
# ==========================================

def cyrus_beck_clip(x1, y1, x2, y2, poly_points):
    """
    poly_points: список кортежей [(x,y), (x,y)...] вершин выпуклого многоугольника (по часовой или против)
    """
    t_enter = 0.0
    t_leave = 1.0

    dx = x2 - x1
    dy = y2 - y1

    # Вектор направления отрезка
    p_line = np.array([dx, dy])

    n = len(poly_points)

    for i in range(n):
        # Текущая вершина и следующая (образуют ребро)
        p_curr = np.array(poly_points[i])
        p_next = np.array(poly_points[(i + 1) % n])

        # Вектор ребра
        edge = p_next - p_curr

        # Вектор нормали (повернут на 90 градусов внутрь)
        # Предполагаем обход против часовой стрелки: нормаль (-dy, dx)
        # Для универсальности лучше вычислить нормаль и проверить знак с любой внутренней точкой,
        # но для выпуклого с правильным обходом:
        normal = np.array([-edge[1], edge[0]])

        # Вектор от вершины ребра к началу отрезка
        w = np.array([x1, y1]) - p_curr

        # Скалярные произведения
        num = -np.dot(normal, w)   # числитель
        den = np.dot(normal, p_line) # знаменатель

        if den == 0:
            # Отрезок параллелен ребру
            if num < 0:
                # Отрезок снаружи (для нормали направленной внутрь)
                return None
            # Иначе внутри, продолжаем
        else:
            t = num / den
            if den > 0:
                # Входим в многоугольник (знаменатель > 0 при внутренней нормали)
                t_enter = max(t_enter, t)
            else:
                # Выходим из многоугольника
                t_leave = min(t_leave, t)

    if t_enter > t_leave:
        return None

    # Вычисляем новые координаты
    new_x1 = x1 + t_enter * dx
    new_y1 = y1 + t_enter * dy
    new_x2 = x1 + t_leave * dx
    new_y2 = y1 + t_leave * dy

    return (new_x1, new_y1, new_x2, new_y2)

# ==========================================
# ВИЗУАЛИЗАЦИЯ
# ==========================================

def main():
    # 1. Загрузка данных
    segments, window_rect = read_data('input.txt')
    if not segments:
        print("Нет данных для отображения. Создайте файл input.txt.")
        return

    xmin, ymin, xmax, ymax = window_rect

    # Создаем фигуру с двумя графиками (для двух алгоритмов)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    # -------------------------------------------------------
    # ГРАФИК 1: Алгоритм средней точки (Прямоугольное окно)
    # -------------------------------------------------------
    ax1.set_title("Вариант 6, Ч.1: Алгоритм Средней точки (Прямоугольник)")
    ax1.set_xlabel("X")
    ax1.set_ylabel("Y")

    # Рисуем окно
    width = xmax - xmin
    height = ymax - ymin
    rect_patch = patches.Rectangle((xmin, ymin), width, height, linewidth=2, edgecolor='r', facecolor='none', label='Окно')
    ax1.add_patch(rect_patch)

    # Обработка и отрисовка отрезков
    for seg in segments:
        x1, y1, x2, y2 = seg
        # Рисуем исходный (серый, тонкий)
        ax1.plot([x1, x2], [y1, y2], color='gray', linestyle='--', alpha=0.5)

        # Алгоритм
        clipped_parts = []
        midpoint_clip_recursive(x1, y1, x2, y2, xmin, ymin, xmax, ymax, clipped_parts)

        # Рисуем видимые части (зеленый, жирный)
        # Так как алгоритм делит на кусочки, мы рисуем каждый видимый микро-кусочек
        # Визуально они сольются в одну линию
        if clipped_parts:
            # Сортируем кусочки, чтобы "склеить" их визуально (опционально, matplotlib и так нарисует)
            # Для оптимизации отрисовки можно было бы объединять коллинеарные смежные, но для лабы это не обязательно
            for part in clipped_parts:
                px1, py1, px2, py2 = part
                ax1.plot([px1, px2], [py1, py2], color='green', linewidth=2)

    ax1.grid(True)
    ax1.set_aspect('equal', adjustable='datalim')

    # -------------------------------------------------------
    # ГРАФИК 2: Алгоритм Кируса-Бека (Выпуклый многоугольник)
    # -------------------------------------------------------
    ax2.set_title("Вариант 6, Ч.2: Кирус-Бек (Выпуклый многоугольник)")

    # Определяем произвольный ВЫПУКЛЫЙ многоугольник (например, повернутый ромб или пятиугольник)
    # Т.к. в файле дано прямоугольное окно, для Части 2 мы "придумываем" свой многоугольник,
    # который попадает примерно в те же координаты.
    cx, cy = (xmin + xmax)/2, (ymin + ymax)/2
    r = (xmax - xmin) / 1.5
    # Создаем пятиугольник
    angles = np.linspace(0, 2*np.pi, 6)[:-1]
    poly_verts = []
    for ang in angles:
        poly_verts.append((cx + r * np.cos(ang), cy + r * np.sin(ang)))

    # Рисуем многоугольник
    poly_patch = patches.Polygon(poly_verts, closed=True, linewidth=2, edgecolor='purple', facecolor='none', label='Многоугольник')
    ax2.add_patch(poly_patch)

    # Обработка отрезков
    for seg in segments:
        x1, y1, x2, y2 = seg
        # Рисуем исходный
        ax2.plot([x1, x2], [y1, y2], color='gray', linestyle='--', alpha=0.5)

        # Алгоритм
        res = cyrus_beck_clip(x1, y1, x2, y2, poly_verts)

        if res:
            rx1, ry1, rx2, ry2 = res
            ax2.plot([rx1, rx2], [ry1, ry2], color='blue', linewidth=2)

    ax2.grid(True)
    ax2.set_aspect('equal', adjustable='datalim')

    # Легенды
    # Создаем фиктивные линии для легенды, чтобы не дублировать
    custom_lines1 = [patches.Patch(facecolor='none', edgecolor='red', label='Окно'),
                     plt.Line2D([0], [0], color='gray', linestyle='--', label='Исходные'),
                     plt.Line2D([0], [0], color='green', lw=2, label='Видимые')]
    ax1.legend(handles=custom_lines1)

    custom_lines2 = [patches.Patch(facecolor='none', edgecolor='purple', label='Многоугольник'),
                     plt.Line2D([0], [0], color='gray', linestyle='--', label='Исходные'),
                     plt.Line2D([0], [0], color='blue', lw=2, label='Видимые')]
    ax2.legend(handles=custom_lines2)

    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    main()
