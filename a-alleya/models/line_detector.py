import numpy as np

class LineDetector:
    def __init__(self):
        self.line1 = {'start_x': 0.59, 'start_y': 0.28, 'end_x': 0.495, 'end_y': 1.0}
        self.line2 = {'start_x': 0.65, 'start_y': 0.3, 'end_x': 0.95, 'end_y': 0.35}
        self.line3 = {'start_x': 0.65, 'start_y': 0.5, 'end_x': 1.0, 'end_y': 0.55}

    def set_line_coordinates(self, line_num, start_x, start_y, end_x, end_y):
        coordinates = {'start_x': start_x, 'start_y': start_y, 'end_x': end_x, 'end_y': end_y}
        if line_num == 1:
            self.line1 = coordinates
        elif line_num == 2:
            self.line2 = coordinates
        elif line_num == 3:
            self.line3 = coordinates

    def is_on_line(self, box, line_start, line_end):
        # Получаем координаты бокса
        x1, y1, x2, y2 = map(int, box.xyxy[0])
        
        # Получаем координаты линии
        x3, y3 = line_start
        x4, y4 = line_end
        
        # Проверяем пересечение линии с каждой стороной прямоугольника
        def ccw(A, B, C):
            return (C[1] - A[1]) * (B[0] - A[0]) > (B[1] - A[1]) * (C[0] - A[0])
    
        def intersect(A, B, C, D):
            return ccw(A, C, D) != ccw(B, C, D) and ccw(A, B, C) != ccw(A, B, D)
        
        # Проверяем все стороны прямоугольника
        rect_lines = [
            ((x1, y1), (x2, y1)),  # верхняя сторона
            ((x2, y1), (x2, y2)),  # правая сторона
            ((x2, y2), (x1, y2)),  # нижняя сторона
            ((x1, y2), (x1, y1))   # левая сторона
        ]
        
        line_points = (line_start, line_end)
        
        # Если хотя бы одна сторона прямоугольника пересекается с линией
        for rect_line in rect_lines:
            if intersect(rect_line[0], rect_line[1], line_points[0], line_points[1]):
                return True
                
        return False

    def get_line_points(self, frame_shape):
        height, width = frame_shape[:2]
        
        points = {
            'line1': (
                (int(width * self.line1['start_x']), int(height * self.line1['start_y'])),
                (int(width * self.line1['end_x']), int(height * self.line1['end_y']))
            ),
            'line2': (
                (int(width * self.line2['start_x']), int(height * self.line2['start_y'])),
                (int(width * self.line2['end_x']), int(height * self.line2['end_y']))
            ),
            'line3': (
                (int(width * self.line3['start_x']), int(height * self.line3['start_y'])),
                (int(width * self.line3['end_x']), int(height * self.line3['end_y']))
            )
        }
        return points