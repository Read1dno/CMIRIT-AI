import cv2
from config.settings import Settings

class Visualizer:
    @staticmethod
    def draw_detection_line(frame, line_points, traffic_light_state, vehicles_on_line, pedestrians_on_line):
        if traffic_light_state == "RED":
            car_line_color = (0, 255, 0)
            pedestrian_line_color = (0, 0, 255)
        elif traffic_light_state == "GREEN":
            car_line_color = (0, 0, 255)
            pedestrian_line_color = (0, 255, 0)
        else:
            car_line_color = pedestrian_line_color = (255, 255, 255)
    
        line1_color = (0, 165, 255) if vehicles_on_line else car_line_color
        line2_color = (0, 165, 255) if pedestrians_on_line else pedestrian_line_color
    
        cv2.line(frame, *line_points['line1'], line1_color, 2)
        cv2.line(frame, *line_points['line2'], line2_color, 2)
        cv2.line(frame, *line_points['line3'], pedestrian_line_color, 2)
    
    @staticmethod
    def draw_info(frame, timestamp, buffer_size, vehicles_crossed, pedestrians_crossed):
        cv2.putText(frame, f"Segment Time: {timestamp}", 
                    (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.putText(frame, f"Buffer Size: {buffer_size}", 
                    (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.putText(frame, f"Vehicles: {vehicles_crossed}", 
                    (10, 110), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.putText(frame, f"Pedestrians: {pedestrians_crossed}", 
                    (10, 150), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    @staticmethod
    def get_color_for_class(cls):
        return Settings.COLORS.get(cls, (128, 128, 128))