import streamlit as st
import cv2
import numpy as np
from PIL import Image

# --- ФУНКЦИИ ОБРАБОТКИ ---

def linear_contrasting(image):
    """
    Линейное контрастирование (растяжение гистограммы).
    Формула: g(x,y) = (f(x,y) - min) / (max - min) * 255
    """
    # Конвертируем в float для точности вычислений
    img_float = image.astype(float)
    min_val = np.min(img_float)
    max_val = np.max(img_float)

    # Защита от деления на ноль (если изображение однотонное)
    if max_val - min_val == 0:
        return image

    # Растяжение
    res = ((img_float - min_val) / (max_val - min_val)) * 255
    return res.astype(np.uint8)

def pixel_operation_brightness(image, value):
    """
    Поэлементная операция: изменение яркости.
    g(x,y) = f(x,y) + value
    """
    # Используем cv2.add для корректного насыщения (чтобы 250+10 стало 255, а не 4)
    if value >= 0:
        res = cv2.add(image, np.ones(image.shape, dtype="uint8") * abs(value))
    else:
        res = cv2.subtract(image, np.ones(image.shape, dtype="uint8") * abs(value))
    return res

def pixel_operation_invert(image):
    """
    Поэлементная операция: негатив (инверсия).
    g(x,y) = 255 - f(x,y)
    """
    return cv2.bitwise_not(image)

def global_threshold_manual(image, threshold):
    """
    Метод 1: Простая глобальная пороговая обработка с ручным порогом.
    """
    # Конвертируем в оттенки серого, если еще не
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    else:
        gray = image

    _, binary = cv2.threshold(gray, threshold, 255, cv2.THRESH_BINARY)
    return binary

def global_threshold_otsu(image):
    """
    Метод 2: Метод Оцу (Otsu's method).
    Автоматически ищет порог, минимизирующий внутриклассовую дисперсию.
    """
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    else:
        gray = image

    # thresh_val вернет вычисленный порог, binary - результат
    thresh_val, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return thresh_val, binary

# --- ИНТЕРФЕЙС ПРИЛОЖЕНИЯ ---

st.set_page_config(page_title="Лаб. работа - Вариант 6", layout="wide")
st.title("Обработка изображений: Вариант 6")
st.markdown("**Студент:** [Твое Имя] | **Группа:** [Твоя Группа]")

# Боковая панель для навигации
task = st.sidebar.selectbox(
    "Выберите метод обработки",
    ("1. Поэлементные операции + Линейное контрастирование",
     "2. Глобальная пороговая обработка (2 метода)")
)

# Загрузка изображения
uploaded_file = st.sidebar.file_uploader("Загрузите изображение", type=["jpg", "png", "jpeg", "bmp"])

if uploaded_file is not None:
    # Чтение изображения
    image = Image.open(uploaded_file)
    img_array = np.array(image) # RGB формат

    # Отображение оригинала
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Исходное изображение")
        st.image(image, use_container_width=True)
        # Гистограмма оригинала
        if len(img_array.shape) == 2: # Градации серого
             hist_vals, _ = np.histogram(img_array, bins=256, range=(0,256))
             st.bar_chart(hist_vals)

    # --- ЛОГИКА ЗАДАНИЯ 1 ---
    # Проверка по первому символу строки ("1")
    if task.startswith("1"):
        st.sidebar.header("Параметры")

        # Выбор подоперации
        op_mode = st.sidebar.radio("Операция:", ["Изменение яркости", "Инверсия (Негатив)", "Линейное контрастирование"])

        processed_img = img_array.copy()

        if op_mode == "Изменение яркости":
            st.info("Поэлементная операция: к значению каждого пикселя добавляется константа.")
            val = st.sidebar.slider("Уровень яркости", -100, 100, 0)
            processed_img = pixel_operation_brightness(img_array, val)

        elif op_mode == "Инверсия (Негатив)":
            st.info("Поэлементная операция: вычитание значения пикселя из 255.")
            processed_img = pixel_operation_invert(img_array)

        elif op_mode == "Линейное контрастирование":
            st.info("""
            **Линейное контрастирование:** Метод расширяет узкий диапазон яркостей изображения на весь доступный диапазон (0-255).
            Идеально подходит для малоконтрастных изображений.
            """)
            processed_img = linear_contrasting(img_array)

        with col2:
            st.subheader("Результат")
            st.image(processed_img, use_container_width=True)
            # Гистограмма результата для наглядности (особенно важно для контрастирования)
            if op_mode == "Линейное контрастирование":
                st.write("Гистограмма результата:")
                # Упрощаем до градаций серого для графика
                if len(processed_img.shape) == 3:
                    gray_res = cv2.cvtColor(processed_img, cv2.COLOR_RGB2GRAY)
                else:
                    gray_res = processed_img
                hist_vals_res, _ = np.histogram(gray_res, bins=256, range=(0,256))
                st.bar_chart(hist_vals_res)

    # --- ЛОГИКА ЗАДАНИЯ 2 ---
    # Проверка по первому символу строки ("2")
    elif task.startswith("2"):
        st.sidebar.header("Выбор метода бинаризации")
        thresh_method = st.sidebar.radio("Метод:", ["Ручной порог (Manual)", "Метод Оцу (Otsu)"])

        st.info("Обратите внимание: Пороговая обработка обычно применяется к полутоновым (gray-scale) изображениям.")

        if thresh_method == "Ручной порог (Manual)":
            st.write("""
            **Ручная глобальная бинаризация:**
            Пользователь задает порог $T$.
            Если $pixel > T$, то $pixel = 255$ (белый).
            Иначе $pixel = 0$ (черный).
            """)
            t_val = st.sidebar.slider("Значение порога (Threshold)", 0, 255, 127)
            res_binary = global_threshold_manual(img_array, t_val)

            with col2:
                st.subheader(f"Результат (Порог: {t_val})")
                st.image(res_binary, use_container_width=True, clamp=True)

        elif thresh_method == "Метод Оцу (Otsu)":
            st.write("""
            **Метод Оцу:**
            Алгоритм автоматически вычисляет оптимальный порог, разделяющий гистограмму на два класса (фон и объект)
            так, чтобы минимизировать внутриклассовую дисперсию.
            Хорошо работает на бимодальных гистограммах.
            """)
            calc_thresh, res_binary = global_threshold_otsu(img_array)

            with col2:
                st.subheader(f"Результат (Авто-порог: {calc_thresh})")
                st.image(res_binary, use_container_width=True, clamp=True)

else:
    st.warning("Пожалуйста, загрузите изображение для начала работы.")
    st.markdown("### Генерация тестовых изображений")
    st.markdown("Если у вас нет подходящих изображений, вы можете сгенерировать их скриптом в задании.")
