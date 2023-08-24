import cv2
import threading
import os
import numpy as np

import webcam_capture
import filters

main_dir = os.path.dirname(os.path.abspath(__file__))


class CardReader:
    def __init__(self, video, settings):

        self.video = video
        self.settings = settings

        self.thread_running = False
        self.stats = None

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

    def start(self):
        self.thread_running = True
        threading.Thread(target=self.filter_frame,daemon=True).start()

    def stop(self):
        self.thread_running = False
        print('stopping filter thread')

    def filter_frame(self):

        def filtering(f_frame):

            self.resized_frame = filters.resize_with_aspect_ratio(f_frame, 200)

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

        def contouring():
            for_find_cont = self.fil_frame.copy()
            for_draw_cont = self.resized_frame.copy()
            for_crop = self.resized_frame.copy()

            # find contours
            contours, hierarchy = cv2.findContours(for_find_cont, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            self.contour_frame = cv2.drawContours(for_draw_cont, contours, -1, (0, 255, 0), 1)

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

                self.stats = (
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

        while self.thread_running:

            frame = self.video.frame

            if frame is not None:
                filtering(frame)
                contouring()

            # for_detection = cv2.copyMakeBorder(filtered_frame, 10, 10, 10, 10, cv2.BORDER_CONSTANT, value=(0, 0, 0))

            # contours, hierarchy = cv2.findContours(for_find_cont, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            #
            # if len(contours) > 0:
            #     contour = max(contours, key=cv2.contourArea)
            #
            #     self.contour_frame = cv2.drawContours(for_draw_cont, contour, -1, (0, 0, 255), 10)
            #
            #     rect = cv2.minAreaRect(contour)
            #     box = cv2.boxPoints(rect)
            #     box = np.int0(box)
            #
            #     (center), (dim1, dim2), angle = rect
            #
            #     max_dim = max(dim1, dim2)
            #     min_dim = min(dim1, dim2)
            #     area = dim1 * dim2
            #     if area > 0:
            #         aspect = max_dim / min_dim
            #
            #     _, safe_size, _ = rect
            #     safe_width, safe_height = tuple(map(int, safe_size))
            #
            #     if safe_width > 1 and safe_height > 1:
            #         cropped_frame = filters.straighten_crop_image(rect, for_crop, 0)
            #         cropped_frame = cv2.rotate(cropped_frame, cv2.ROTATE_90_CLOCKWISE)
            #         self.cropped_frame = filters.resize_with_aspect_ratio(cropped_frame, width=168, height=249)
            #
            #     else:
            #         self.cropped_frame = for_crop

            # self.final_filter_frame = filters.crop_white(self.cropped_frame, white_cut)
