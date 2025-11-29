import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *

# --- Геометрия буквы (Без изменений) ---
vertices = (
    (-1.0, -1.5,  0.5), (-0.5, -1.5,  0.5), ( 0.0,  1.0,  0.5), ( 0.5, -1.5,  0.5),
    ( 1.0, -1.5,  0.5), ( 0.3,  1.5,  0.5), (-0.3,  1.5,  0.5),
    (-1.0, -1.5, -0.5), (-0.5, -1.5, -0.5), ( 0.0,  1.0, -0.5), ( 0.5, -1.5, -0.5),
    ( 1.0, -1.5, -0.5), ( 0.3,  1.5, -0.5), (-0.3,  1.5, -0.5),
)
edges = (
    (0,1), (1,2), (2,3), (3,4), (4,5), (5,6), (6,0),
    (7,8), (8,9), (9,10), (10,11), (11,12), (12,13), (13,7),
    (0,7), (1,8), (2,9), (3,10), (4,11), (5,12), (6,13)
)
surfaces = (
    (0,1,8,7), (1,2,9,8), (2,3,10,9), (3,4,11,10), (4,5,12,11), (5,6,13,12), (6,0,7,13),
    (0, 1, 2, 6), (3, 4, 5, 2), (6, 2, 5), (7, 8, 9, 13), (10, 11, 12, 9), (13, 9, 12)
)

def draw_grid_and_axes():
    """ Рисует сетку и полные оси (плюс и минус) """

    # 1. Сетка на полу (XZ) - Серый цвет
    glLineWidth(1)
    glColor3f(0.3, 0.3, 0.3)
    glBegin(GL_LINES)
    # Рисуем сетку от -20 до 20
    for i in range(-20, 21):
        glVertex3f(i, 0, -20); glVertex3f(i, 0, 20) # Вдоль Z
        glVertex3f(-20, 0, i); glVertex3f(20, 0, i) # Вдоль X
    glEnd()

    # 2. ДЛИННЫЕ ОСИ (от -100 до 100)
    glLineWidth(3)
    glBegin(GL_LINES)

    # Ось X - Красная (Влево и Вправо)
    glColor3f(1, 0, 0)
    glVertex3f(-100, 0, 0); glVertex3f(100, 0, 0)

    # Ось Y - Зеленая (Вверх и Вниз)
    glColor3f(0, 1, 0)
    glVertex3f(0, -100, 0); glVertex3f(0, 100, 0)

    # Ось Z - Синяя (Вдаль и К нам)
    glColor3f(0, 0, 1)
    glVertex3f(0, 0, -100); glVertex3f(0, 0, 100)
    glEnd()

    # 3. Деления (Риски) - и в плюс, и в минус
    glLineWidth(1)
    glColor3f(1, 1, 1) # Белый цвет
    glBegin(GL_LINES)

    # Рисуем риски от -15 до 15
    for i in range(-15, 16):
        if i == 0: continue # Пропускаем центр (там пересечение осей)

        # Риски на оси X (вертикальные черточки)
        glVertex3f(i, -0.2, 0); glVertex3f(i, 0.2, 0)

        # Риски на оси Y (горизонтальные черточки)
        glVertex3f(-0.2, i, 0); glVertex3f(0.2, i, 0)

        # Риски на оси Z
        glVertex3f(0, -0.2, i); glVertex3f(0, 0.2, i)
    glEnd()

def draw_letter():
    # Закраска
    glBegin(GL_POLYGON)
    for i, surface in enumerate(surfaces):
        if i >= 7: glColor3f(0.0, 0.6, 0.9)
        else: glColor3f(0.0, 0.4, 0.7)
        for vertex in surface:
            glVertex3fv(vertices[vertex])
        glEnd()
        glBegin(GL_POLYGON)
    glEnd()

    # Обводка
    glLineWidth(2)
    glColor3f(0, 0, 0)
    glBegin(GL_LINES)
    for edge in edges:
        for vertex in edge:
            glVertex3fv(vertices[vertex])
    glEnd()

def main():
    pygame.init()
    display = (800, 600)
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
    pygame.display.set_caption("Л")

    gluPerspective(45, (display[0] / display[1]), 0.1, 100.0)
    glTranslatef(0.0, -2.0, -20) # Отодвинул камеру еще чуть дальше

    glClearColor(0.2, 0.2, 0.2, 1.0) # Темно-серый фон

    cam_rot_x = 20
    cam_rot_y = -30

    obj_pos_x = 0
    obj_pos_y = 0
    obj_scale = 1.0
    obj_rot_self = 0

    clock = pygame.time.Clock()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); quit()
            if event.type == pygame.MOUSEWHEEL:
                if event.y > 0: obj_scale += 0.1
                else: obj_scale -= 0.1
                if obj_scale < 0.1: obj_scale = 0.1

        keys = pygame.key.get_pressed()

        # Камера (Стрелки)
        if keys[pygame.K_LEFT]:  cam_rot_y -= 2
        if keys[pygame.K_RIGHT]: cam_rot_y += 2
        if keys[pygame.K_UP]:    cam_rot_x -= 2
        if keys[pygame.K_DOWN]:  cam_rot_x += 2

        # Объект (WASD)
        if keys[pygame.K_a]: obj_pos_x -= 0.1
        if keys[pygame.K_d]: obj_pos_x += 0.1
        if keys[pygame.K_w]: obj_pos_y += 0.1
        if keys[pygame.K_s]: obj_pos_y -= 0.1

        # Вращение объекта (Z/C)
        if keys[pygame.K_z]: obj_rot_self -= 2
        if keys[pygame.K_c]: obj_rot_self += 2

        # Масштаб (Q/E)
        if keys[pygame.K_q]: obj_scale += 0.05
        if keys[pygame.K_e]: obj_scale -= 0.05
        if obj_scale < 0.1: obj_scale = 0.1

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glEnable(GL_DEPTH_TEST)

        # 1. Поворот мира (камеры)
        glPushMatrix()
        glRotatef(cam_rot_x, 1, 0, 0)
        glRotatef(cam_rot_y, 0, 1, 0)

        # 2. Рисуем оси (теперь они длинные во все стороны)
        draw_grid_and_axes()

        # 3. Рисуем объект
        glPushMatrix()
        glTranslatef(obj_pos_x, obj_pos_y, 0)
        glRotatef(obj_rot_self, 0, 1, 0)
        glScalef(obj_scale, obj_scale, obj_scale)
        draw_letter()
        glPopMatrix() # Объект

        glPopMatrix() # Камера

        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()
