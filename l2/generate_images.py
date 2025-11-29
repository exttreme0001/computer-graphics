import cv2
import numpy as np

def create_low_contrast_image():
    # Создаем изображение
    img = np.zeros((300, 300), dtype=np.uint8)
    # Рисуем круги, но цвета очень близкие (например, 100 и 120)
    img[:] = 100 # Фон серый
    cv2.circle(img, (150, 150), 100, 120, -1) # Круг чуть светлее
    cv2.rectangle(img, (50, 50), (100, 100), 110, -1) # Квадрат

    # Добавим шум
    noise = np.random.normal(0, 5, img.shape).astype(np.uint8)
    img = cv2.add(img, noise)

    cv2.imwrite("low_contrast.png", img)
    print("Создано: low_contrast.png (Для линейного контрастирования)")

def create_threshold_test_image():
    # Создаем градиент (плохо для глобального порога) и четкие фигуры (хорошо для Оцу)
    img = np.zeros((300, 300), dtype=np.uint8)

    # Фон - градиент
    for i in range(300):
        img[:, i] = i * 0.5

    # Объекты (яркие на темном фоне и темные на ярком)
    cv2.circle(img, (150, 150), 50, 200, -1)
    cv2.putText(img, "TEST", (50, 250), cv2.FONT_HERSHEY_SIMPLEX, 2, 255, 3)

    cv2.imwrite("threshold_test.png", img)
    print("Создано: threshold_test.png (Для тестов пороговой обработки)")

if __name__ == "__main__":
    create_low_contrast_image()
    create_threshold_test_image()
