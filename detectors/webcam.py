import cv2


class Webcam:
    def __init__(self):
        self.video = None

    def __del__(self):
        if self.video is not None:
            self.video.release()

    def start_webcam(self):
        self.video = cv2.VideoCapture(0)

    def get_frame_bytes(self):
        ret, frame = self.video.read()
        ret, jpeg = cv2.imencode('.jpg', frame)
        return jpeg.tobytes()

    def get_stream(self):
        while True:
            frame = self.get_frame_bytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

    def get_frame_cv2(self):
        ret, frame = self.video.read()
        return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
