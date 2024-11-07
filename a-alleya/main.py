import threading
import tempfile
import os
import cv2
import time
from stream_handler import StreamHandler
from models import YOLOProcessor
from display_handler import DisplayHandler

def process_video(stream_handler, yolo_processor, display_handler):
    temp_dir = tempfile.mkdtemp()
    temp_counter = 0
    frame_interval = 1  # Интервал между кадрами
    
    try:
        while stream_handler.running:
            try:
                # Получение сегмента из буфера
                current_segment = None
                with stream_handler.buffer_lock:
                    if stream_handler.segment_buffer:
                        current_segments = sorted(stream_handler.segment_buffer, key=lambda x: x[0])
                        current_segment = current_segments[0]
                        buffer_size = len(stream_handler.segment_buffer)
                        # Корректируем FPS на основе размера буфера
                        current_fps = stream_handler.adjust_fps(buffer_size)
                        frame_interval = 30 // current_fps  # Вычисляем интервал между кадрами
                        stream_handler.segment_buffer.remove(current_segment)
                
                if not current_segment:
                    time.sleep(0.1)
                    continue
                
                timestamp, segment_data = current_segment
                
                if timestamp in stream_handler.processed_segments:
                    continue
                    
                stream_handler.processed_segments.add(timestamp)
                
                temp_file = os.path.join(temp_dir, f'segment_{temp_counter}.ts')
                with open(temp_file, 'wb') as f:
                    f.write(segment_data)
                
                cap = cv2.VideoCapture(temp_file)
                frame_count = 0
                
                while cap.isOpened() and stream_handler.running:
                    success, frame = cap.read()
                    if not success:
                        break
                    
                    # Пропускаем кадры в соответствии с текущим FPS
                    frame_count += 1
                    if frame_count % frame_interval != 0:
                        continue
                    
                    annotated_frame = yolo_processor.process_frame(
                        frame, 
                        timestamp, 
                        len(stream_handler.segment_buffer)
                    )
                    
                    key = display_handler.show_frame(annotated_frame)
                    if key == ord("q"):
                        stream_handler.running = False
                        break
                
                cap.release()
                
                try:
                    os.remove(temp_file)
                except:
                    pass
                
                temp_counter = (temp_counter + 1) % 1000
                
                if len(stream_handler.processed_segments) > 100:
                    stream_handler.processed_segments.clear()
                
            except Exception as e:
                print(f"Error in video processing: {e}")
                time.sleep(0.1)
    
    finally:
        # Очистка временных файлов
        try:
            for filename in os.listdir(temp_dir):
                os.remove(os.path.join(temp_dir, filename))
            os.rmdir(temp_dir)
        except:
            pass

def main():
    # Конфигурация
    base_url = "url"
    model_path = "cherv11m.pt"
    window_name = "a-alleya"
    
    # Инициализация компонентов
    stream_handler = StreamHandler(base_url)
    yolo_processor = YOLOProcessor(model_path)
    display_handler = DisplayHandler(window_name)

    try:
        # Запуск потока загрузки буфера
        buffer_thread = threading.Thread(
            target=stream_handler.buffer_loader, 
            daemon=True
        )
        buffer_thread.start()

        # Запуск основного процесса обработки видео
        process_video(stream_handler, yolo_processor, display_handler)
    
    except KeyboardInterrupt:
        print("Shutting down...")
    except Exception as e:
        print(f"Error in main: {e}")
    finally:
        # Очистка и завершение
        stream_handler.running = False
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()