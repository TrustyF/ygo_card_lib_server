import cv2
import threading
import os
import numpy as np
from PIL import Image

from card_matcher.tools import filters, tools
from card_matcher.constants import MAIN_DIR
from card_matcher.webcam import Webcam


class CardDetector:
    def __init__(self, video: Webcam):

        self.video = video
        self.settings = tools.load_user_settings()

        self.detection_stats = None

        self.resized_frame = None
        self.white_balanced_frame = None
        self.auto_contrast_frame = None
        self.gray_frame = None
        self.contrasted_frame = None
        self.blurred_frame = None
        self.canny_frame = None
        self.dilated_frame = None
        self.fil_frame = None

        self.final_filter_frame = None

        self.contour_frame = None
        self.cropped_frame = None

    def update_detection_settings(self, name, value):
        self.settings[name] = value
        tools.save_user_settings(self.settings)

    def detect_card(self):
        frame = self.video.get_frame_cv2()

        if frame is None:
            print('no frame found')
            return

            # Filtering
        self.resized_frame = filters.resize_with_aspect_ratio(frame, 200)
        self.white_balanced_frame = filters.auto_white_balance(self.resized_frame)
        self.auto_contrast_frame, _, _ = filters.automatic_brightness_and_contrast(self.white_balanced_frame,
                                                                                   self.settings.get(
                                                                                       'auto_bright_bias', 0))
        self.contrasted_frame = filters.contrast_and_exposure(self.auto_contrast_frame,
                                                              contrast=self.settings.get('contrast', 0),
                                                              exposure=self.settings.get('exposure', 0))
        self.gray_frame = cv2.cvtColor(self.contrasted_frame, cv2.COLOR_BGR2GRAY)
        self.blurred_frame = filters.custom_blur(self.gray_frame,
                                                 filters.modulo_2(self.settings.get('median_blur', 0)),
                                                 self.settings.get('gaussian_blur', 0))
        self.canny_frame = filters.canny(self.blurred_frame, 0, self.settings.get('canny', 0))
        self.dilated_frame = filters.dilate(self.canny_frame, self.settings.get('dilate', 1))
        self.fil_frame = self.dilated_frame

        # Prep contours
        for_find_cont = self.fil_frame.copy()
        for_draw_cont = self.resized_frame.copy()
        for_crop = self.resized_frame.copy()

        # find contours
        contours, hierarchy = cv2.findContours(for_find_cont, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        self.contour_frame = cv2.drawContours(for_draw_cont, contours, -1, (0, 255, 0), 1)

        # make bounding rect
        if len(contours) > 0:
            cnt = max(contours, key=cv2.contourArea)

            x, y, w, h = cv2.boundingRect(cnt)
            aspect_ratio = float(w) / h

            area = cv2.contourArea(cnt)
            x, y, w, h = cv2.boundingRect(cnt)
            rect_area = w * h
            extent = float(area) / rect_area

            hull = cv2.convexHull(cnt)
            hull_area = cv2.contourArea(hull)
            solidity = float(area) / hull_area

            equi_diameter = np.sqrt(4 * area / np.pi)

            (x, y), (MA, ma), orient = cv2.fitEllipse(cnt)

            rect = cv2.minAreaRect(cnt)

            self.detection_stats = (
                f" Width = {round(w, 1)}\n  Height = {round(h, 1)}\n area = {round(area, 1)}\n  aspect ration = "
                f"{round(aspect_ratio, 1)}\n  extent"
                f"  ="
                f" {round(extent, 1)}\n"
                f"solidity = {round(solidity, 1)}\n equi_diameter = {round(equi_diameter, 1)}\n orientation = "
                f"{round(orient, 1)}\n")

            if solidity > (self.settings.get('solidity', 0) / 100) and equi_diameter > self.settings.get('diameter',
                                                                                                         0):
                cropped_frame = filters.straighten_crop_image(rect, for_crop, 0)
                cropped_frame = cv2.rotate(cropped_frame, cv2.ROTATE_90_CLOCKWISE)
                self.cropped_frame = filters.resize_with_aspect_ratio(cropped_frame, width=168, height=249)

            if self.cropped_frame is not None:
                self.final_filter_frame = filters.crop_white(self.cropped_frame, self.settings['white_cut'])

    def get_detected_card(self):
        self.detect_card()
        return self.final_filter_frame

    def get_filter_feed(self):

        def resize_with_aspect_ratio(image, width):
            aspect_ratio = image.shape[1] / image.shape[0]
            new_height = int(width / aspect_ratio)

            if len(image.shape) < 3:
                formatted = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
            else:
                formatted = image

            resized_image = cv2.resize(formatted, (width, new_height))
            return resized_image

        while True:
            self.detect_card()

            if self.final_filter_frame is None:
                return

            stacked = np.vstack((
                resize_with_aspect_ratio(self.gray_frame, 100),
                resize_with_aspect_ratio(self.canny_frame, 100),
                resize_with_aspect_ratio(self.cropped_frame, 100),
                resize_with_aspect_ratio(self.final_filter_frame, 100),
            ))

            ret, buffer = cv2.imencode('.jpg', stacked)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
