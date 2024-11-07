import requests
import m3u8
import urllib3
from collections import deque
import threading
import re

class StreamHandler:
    def __init__(self, base_url):
        self.base_url = base_url
        self.playlist_url = base_url + "playlist.m3u8"
        self.segment_buffer = deque(maxlen=10)
        self.buffer_lock = threading.Lock()
        self.processed_segments = set()
        self.running = True
        self.current_fps = 30  # Добавляем отслеживание текущего FPS
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    def adjust_fps(self, buffer_size):
        if buffer_size > 5:
            self.current_fps = 15
        else:
            self.current_fps = 30
        return self.current_fps

    def extract_timestamp(self, segment_uri):
        match = re.search(r'media_\w+_(\d+)\.ts', segment_uri)
        return int(match.group(1)) if match else 0

    def get_segments_playlist(self):
        try:
            response = requests.get(self.playlist_url, verify=False, timeout=5)
            playlist = m3u8.loads(response.text)
            first_playlist_url = self.base_url + playlist.playlists[0].uri
            response = requests.get(first_playlist_url, verify=False, timeout=5)
            return m3u8.loads(response.text)
        except Exception as e:
            print(f"Error getting playlist: {e}")
            return None

    def download_segment(self, segment_url, timestamp):
        try:
            response = requests.get(segment_url, verify=False, timeout=5)
            if response.status_code == 200:
                return (timestamp, response.content)
            return None
        except Exception as e:
            print(f"Error downloading segment: {e}")
            return None

    def buffer_loader(self):
        while self.running:
            try:
                segments_playlist = self.get_segments_playlist()
                if segments_playlist and segments_playlist.segments:
                    segments = [(self.extract_timestamp(segment.uri), segment) 
                              for segment in segments_playlist.segments]
                    segments.sort(key=lambda x: x[0])
                    
                    current_segments = segments[-3:]
                    
                    for timestamp, segment in current_segments:
                        if timestamp not in self.processed_segments:
                            segment_url = self.base_url + segment.uri
                            segment_data = self.download_segment(segment_url, timestamp)
                            
                            if segment_data:
                                with self.buffer_lock:
                                    existing_timestamps = [s[0] for s in self.segment_buffer]
                                    if timestamp not in existing_timestamps:
                                        self.segment_buffer.append(segment_data)
                
            except Exception as e:
                print(f"Error in buffer loader: {e}")