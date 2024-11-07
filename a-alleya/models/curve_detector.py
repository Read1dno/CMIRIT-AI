import cv2
import numpy as np

class CurveDetector:
    def draw_curve(self, frame):
        height, width = frame.shape[:2]
        left_point = (0, int(height * 0.27))
        control_point = (width // 2, int(height * 0.1))
        right_point = (width, int(height * 0.25))
        
        # Adding intermediate points
        mid_left = (left_point[0] + control_point[0]) // 2, (left_point[1] + control_point[1]) // 2 - 50
        mid_right = (control_point[0] + right_point[0]) // 2, (control_point[1] + right_point[1]) // 2 - 50
        
        # Store all points in class variables
        self.all_points = [left_point, mid_left, control_point, mid_right, right_point]
        
        curve_points = np.array(self.all_points, dtype=np.int32)
        cv2.polylines(frame, [curve_points], False, (0, 255, 255), 2)
        
        # Return only the original three points for backward compatibility
        return left_point, control_point, right_point

    def create_mask(self, frame, left_point, control_point, right_point):
        height, width = frame.shape[:2]
        mask = np.zeros((height, width), dtype=np.uint8)
        
        points = []
        # Use all points stored in the class
        for i in range(len(self.all_points)-1):
            pt1 = self.all_points[i]
            pt2 = self.all_points[i+1]
            # Generate points between two consecutive points
            for t in np.linspace(0, 1, 25):
                x = int(pt1[0] * (1-t) + pt2[0] * t)
                y = int(pt1[1] * (1-t) + pt2[1] * t)
                points.append([x, y])
        
        # Add bottom points to create a closed polygon
        points.append([width, height])
        points.append([0, height])
        points = np.array(points, dtype=np.int32)
        
        cv2.fillPoly(mask, [points], 255)
        return mask