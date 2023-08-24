import cv2
import os
import threading

main_dir = os.path.dirname(os.path.abspath(__file__))


class Webcam:
    def __init__(self, video_source):
        print(f'video source {video_source}')
        # Open the video source
        self.vid = cv2.VideoCapture(video_source)

        # Get video source width and height
        self.width = self.vid.get(cv2.CAP_PROP_FRAME_WIDTH)
        self.height = self.vid.get(cv2.CAP_PROP_FRAME_HEIGHT)

        print(f'webcam size {self.width} - {self.height}')

        self.frame = None
        self.status = False
        self.thread_running = False

    def start(self):
        self.thread_running = True
        threading.Thread(target=self.get_frame,daemon=True).start()
        print('webcam thread started')

    def stop(self):
        self.thread_running = False
        print('stopping video thread')

    def get_frame(self):
        while self.thread_running:

            if not self.vid.isOpened():
                print('error video not open')
                return

            status, fr = self.vid.read()
            if not status:
                return

            self.frame = cv2.cvtColor(fr, cv2.COLOR_BGR2RGB)

    def __del__(self):
        if self.vid.isOpened():
            self.vid.release()
