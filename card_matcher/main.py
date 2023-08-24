import os
import json
import threading
import cv2
import time

import webcam_capture
import card_capture
import app_window
import tools

main_dir = os.path.dirname(os.path.abspath(__file__))

settings = tools.load_user_settings()

video = webcam_capture.Webcam(0)
card_reader = card_capture.CardReader(video, settings)


def gui():
    app = app_window.MainApplication(video, card_reader, settings)
    app.mainloop()
    video.stop()


if __name__ == '__main__':
    video.start()
    card_reader.start()
    gui()
