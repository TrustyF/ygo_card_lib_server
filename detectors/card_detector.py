import cv2
import numpy as np

from detectors.tools import filters, tools
from detectors.webcam import Webcam
from detectors.card_matcher import CardMatcher


class CardDetector:
    def __init__(self, video: Webcam):
        self.matcher = CardMatcher()
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

        self.card_locked = False
        self.solidity_timer = 0
        self.start_scanning = False

    def update_detection_settings(self, name, value):
        self.settings[name] = value
        tools.save_user_settings(self.settings)

    def detect_card(self):
        frame = self.video.get_frame_cv2()

        if frame is None:
            print('no frame found')
            return

            # Filtering
        self.resized_frame = filters.resize_with_aspect_ratio(frame, width=200)
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

            self.solidity_timer = max(min(10, self.solidity_timer), 0)

            if solidity > (self.settings.get('solidity', 0) / 100) and equi_diameter > self.settings.get('diameter',
                                                                                                         0):
                cropped_frame = filters.straighten_crop_image(rect, for_crop, 0)
                cropped_frame = cv2.rotate(cropped_frame, cv2.ROTATE_90_CLOCKWISE)
                self.cropped_frame = filters.resize_with_aspect_ratio(cropped_frame, width=168, height=249)

                if self.cropped_frame is not None:
                    self.final_filter_frame = filters.crop_white(self.cropped_frame, self.settings['white_cut'])
                    self.solidity_timer += 1

                    if self.solidity_timer >= 10 and self.start_scanning and not self.card_locked:
                        self.card_locked = True
                        print('card locked')
                        self.matcher.match_card(self.final_filter_frame)

            else:
                if self.card_locked:
                    self.solidity_timer -= 1

                    if self.solidity_timer <= 0:
                        self.card_locked = False
                        print('card unlocked')

                self.cropped_frame = for_find_cont
                self.final_filter_frame = for_find_cont

    def find_card(self):
        while self.start_scanning:
            # find the card
            if not self.card_locked and self.solidity_timer >= 10:
                self.card_locked = True
                print('card locked')
                self.matcher.match_card(self.final_filter_frame)

    def get_filter_feed(self):

        while True:
            self.detect_card()

            if self.final_filter_frame is None:
                return

            stacked1 = np.vstack((
                filters.resize_with_aspect_ratio(self.gray_frame, width=200),
                filters.resize_with_aspect_ratio(self.canny_frame, width=200),
            ))
            stacked2 = np.vstack((
                filters.resize_with_aspect_ratio(self.cropped_frame, width=200),
                filters.resize_with_aspect_ratio(self.final_filter_frame, width=200),
            ))
            stacked = np.hstack((
                filters.resize_with_aspect_ratio(stacked1, height=300),
                filters.resize_with_aspect_ratio(stacked2, height=300),
            ))
            formatted = cv2.cvtColor(stacked, cv2.COLOR_BGR2RGB)

            ret, buffer = cv2.imencode('.jpg', formatted)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
