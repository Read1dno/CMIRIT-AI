from ultralytics import YOLO
import cv2
import numpy as np
from collections import defaultdict
from models.line_detector import LineDetector
from models.curve_detector import CurveDetector
from models.traffic_light_detector import TrafficLightDetector
from utils.visualization import Visualizer
from config.settings import Settings

class YOLOProcessor:
    def __init__(self, model_path):
        self.model = YOLO(model_path)
        self.target_classes = Settings.TARGET_CLASSES
        self.trajectories = defaultdict(list)
        self.max_trajectory_length = Settings.MAX_TRAJECTORY_LENGTH
        self.traffic_light_detector = TrafficLightDetector()
        self.line_detector = LineDetector()
        self.curve_detector = CurveDetector()
        self.vehicles_crossed = 0
        self.crossed_ids = set()
        self.vehicles_on_line = set()
        self.pedestrians_crossed = 0
        self.crossed_pedestrian_ids = set()
        self.pedestrians_on_line = set()

    def process_frame(self, frame, timestamp, buffer_size):
        left_point, control_point, right_point = self.curve_detector.draw_curve(frame)
        mask = self.curve_detector.create_mask(frame, left_point, control_point, right_point)
        masked_frame = frame.copy()
        masked_frame[mask == 0] = 0
        
        results = self.model.track(masked_frame, persist=True)
        annotated_frame = frame.copy()
        
        annotated_frame = self.traffic_light_detector.process_frame(annotated_frame)
        traffic_light_state = self.traffic_light_detector.current_state
        line_points = self.line_detector.get_line_points(frame.shape)
        Visualizer.draw_detection_line(annotated_frame, line_points, traffic_light_state, self.vehicles_on_line, self.pedestrians_on_line)
        
        active_ids = set()
        self.vehicles_on_line.clear()
        self.pedestrians_on_line.clear()
    
        if results and len(results) > 0:
            boxes = results[0].boxes
            
            for box in boxes:
                cls = int(box.cls[0])
                
                if cls in self.target_classes:
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    bottom_center = (int((x1 + x2) / 2), y2)
                    
                    track_id = int(box.id[0]) if box.id is not None else None
                    color = Visualizer.get_color_for_class(cls)
                    
                    if track_id is not None and cls == 0:
                        active_ids.add(track_id)
                        self.trajectories[track_id].append(bottom_center)
                        if len(self.trajectories[track_id]) > self.max_trajectory_length:
                            self.trajectories[track_id].pop(0)
                        
                        points = np.array(self.trajectories[track_id], dtype=np.int32)
                        cv2.polylines(annotated_frame, [points], False, color, 2)
    
                    cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), color, 2)
                    label = f"{self.target_classes[cls]} id: {track_id}"
                    cv2.putText(annotated_frame, label, (x1, y1 - 10),
                              cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)
                
                if cls != 0:
                    track_id = int(box.id[0]) if box.id is not None else None
                    
                    if track_id is not None:
                        if self.line_detector.is_on_line(box, *line_points['line1']):
                            self.vehicles_on_line.add(track_id)
                            if track_id not in self.crossed_ids:
                                self.vehicles_crossed += 1
                                self.crossed_ids.add(track_id)

                if cls == 0:
                    if track_id is not None:
                        if self.line_detector.is_on_line(box, *line_points['line2']):
                            self.pedestrians_on_line.add(track_id)
                            if track_id not in self.crossed_pedestrian_ids:
                                self.pedestrians_crossed += 1
                                self.crossed_pedestrian_ids.add(track_id)

        inactive_ids = set(self.trajectories.keys()) - active_ids
        for inactive_id in inactive_ids:
            del self.trajectories[inactive_id]

        Visualizer.draw_info(annotated_frame, timestamp, buffer_size, self.vehicles_crossed, self.pedestrians_crossed)
        
        return annotated_frame