import cv2

class DisplayHandler:
    def __init__(self, window_name="YOLO11 Tracking"):
        self.window_name = window_name
        cv2.namedWindow(self.window_name, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(self.window_name, 1280, 720)

    def show_frame(self, frame):
        window_width = cv2.getWindowImageRect(self.window_name)[2]
        window_height = cv2.getWindowImageRect(self.window_name)[3]
        
        aspect_ratio = frame.shape[1] / frame.shape[0]
        
        if window_width/window_height > aspect_ratio:
            new_width = int(window_height * aspect_ratio)
            new_height = window_height
        else:
            new_width = window_width
            new_height = int(window_width / aspect_ratio)
        
        resized_frame = cv2.resize(frame, (new_width, new_height), 
                                 interpolation=cv2.INTER_LANCZOS4)
        
        cv2.imshow(self.window_name, resized_frame)
        return cv2.waitKey(1) & 0xFF