import cv2
import numpy as np

class TrafficLightDetector:
    def __init__(self):
        # Относительные координаты области светофора (в процентах)
        self.roi_x_percent = 0.898
        self.roi_y_percent = 0.165
        self.roi_width_percent = 0.01 
        self.roi_height_percent = 0.035 
        
        # Реальные координаты (будут вычислены при первом кадре)
        self.roi_x = None
        self.roi_y = None
        self.roi_width = None
        self.roi_height = None
        
        # Текущее состояние светофора
        self.current_state = "UNKNOWN"
        
        # Пороговые значения для определения цветов
        self.color_thresholds = {
            'red': {'low': np.array([0, 100, 100]), 'high': np.array([10, 255, 255])},
            'red2': {'low': np.array([170, 100, 100]), 'high': np.array([180, 255, 255])},
            'green': {'low': np.array([40, 100, 100]), 'high': np.array([80, 255, 255])},
        }
        
        # Пороговые значения для ночного режима
        self.night_brightness_threshold = 200

    def calculate_roi_coordinates(self, frame):
        height, width = frame.shape[:2]
        
        # Вычисляем реальные координаты на основе процентов
        self.roi_x = int(width * self.roi_x_percent)
        self.roi_y = int(height * self.roi_y_percent)
        self.roi_width = int(width * self.roi_width_percent)
        self.roi_height = int(height * self.roi_height_percent)
        
        # Проверяем, не выходит ли ROI за пределы кадра
        self.roi_x = min(self.roi_x, width - self.roi_width)
        self.roi_y = min(self.roi_y, height - self.roi_height)
        
    def get_traffic_light_state(self, frame):
        # Если координаты ещё не вычислены или изменился размер кадра
        if self.roi_x is None:
            self.calculate_roi_coordinates(frame)
            
        # Выделяем область светофора
        roi = frame[self.roi_y:self.roi_y+self.roi_height, 
                   self.roi_x:self.roi_x+self.roi_width]
        
        # Конвертируем в HSV
        hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
        
        # Проверяем на ночной режим
        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        max_brightness = np.max(gray)
        
        if max_brightness > self.night_brightness_threshold:
            # Ночной режим
            return self._detect_night_mode(roi)
        else:
            # Дневной режим
            return self._detect_day_mode(hsv)
    
    def _detect_night_mode(self, roi):
        # Конвертируем в оттенки серого
        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        
        # Находим яркие области
        _, bright_mask = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY)
        
        # Проверяем цвета по краям ярких областей
        if np.sum(bright_mask) > 100:  # если есть яркая область
            # Проверяем края на преобладание красного или зеленого
            edges = cv2.Canny(roi, 100, 200)
            colored_edges = cv2.bitwise_and(roi, roi, mask=edges)
            
            # Анализируем цвета краев
            b, g, r = cv2.split(colored_edges)
            if np.sum(r) > np.sum(g):
                return "RED"
            elif np.sum(g) > np.sum(r):
                return "GREEN"
        
        return "OFF"
    
    def _detect_day_mode(self, hsv):
        # Маски для каждого цвета
        red_mask1 = cv2.inRange(hsv, self.color_thresholds['red']['low'], 
                               self.color_thresholds['red']['high'])
        red_mask2 = cv2.inRange(hsv, self.color_thresholds['red2']['low'], 
                               self.color_thresholds['red2']['high'])
        red_mask = cv2.bitwise_or(red_mask1, red_mask2)
        
        green_mask = cv2.inRange(hsv, self.color_thresholds['green']['low'], 
                                self.color_thresholds['green']['high'])
        
        # Подсчет пикселей каждого цвета
        red_pixels = cv2.countNonZero(red_mask)
        green_pixels = cv2.countNonZero(green_mask)
        
        # Определение состояния
        threshold = 50  # минимальное количество пикселей для определения цвета
        if red_pixels > threshold and red_pixels > green_pixels:
            return "RED"
        elif green_pixels > threshold and green_pixels > red_pixels:
            return "GREEN"
        else:
            return "OFF"
    
    def process_frame(self, frame):
        # Получаем высоту кадра
        height, _ = frame.shape[:2]

        # Если размер кадра изменился, пересчитываем координаты
        if self.roi_x is None:
            self.calculate_roi_coordinates(frame)

        # Определяем состояние светофора
        self.current_state = self.get_traffic_light_state(frame)

        # Отрисовываем прямоугольник вокруг области светофора
        color = {
            "RED": (0, 0, 255),
            "GREEN": (0, 255, 0),
            "OFF": (128, 128, 128),
            "UNKNOWN": (0, 0, 0)
        }[self.current_state]

        cv2.rectangle(frame, 
                     (self.roi_x, self.roi_y), 
                     (self.roi_x + self.roi_width, self.roi_y + self.roi_height),
                     color, 2)

        # Выводим текущее состояние в левом нижнем углу
        # height - 30 разместит текст на 30 пикселей выше нижнего края
        cv2.putText(frame, f"Traffic Light: {self.current_state}", 
                    (10, height - 10), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)

        return frame