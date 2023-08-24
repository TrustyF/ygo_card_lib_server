import tkinter as tk
import time
import json
import os
from PIL import Image, ImageTk
import PIL
import threading

import webcam_capture
import card_capture
import match_image
import tools

main_dir = os.path.dirname(os.path.abspath(__file__))


class FpsCounter:
    def __init__(self, parent):
        self.parent = parent

        self.new_frame = 0
        self.prev_frame = 0
        self.timestamp = []
        self.fps_var = tk.IntVar()
        self.fps_label = tk.Label(self.parent, textvar=self.fps_var)
        self.fps()

    def fps(self):
        self.new_frame = time.time()
        if len(self.timestamp) == 30:
            self.timestamp.pop(0)
        self.timestamp.append(round(1 / (self.new_frame - self.prev_frame), 1))
        self.prev_frame = self.new_frame
        fps = round(sum(self.timestamp) / len(self.timestamp), 0)
        self.fps_var.set(fps)

        self.parent.after(10, self.fps)


class SettingsSliders:
    def __init__(self, parent):
        self.parent = parent
        self.root = tk.Toplevel()
        width, height = self.parent.geo_size
        x, y = self.parent.geo_pos

        self.root.geometry(f'{200}x{550}+{x + width + 50}+{y}')

        self.slider_exp = tk.Scale(self.root, label='exposure', from_=1, to=10,
                                   orient='horizontal', command=self.update_settings)
        self.slider_cont = tk.Scale(self.root, label='contrast', from_=0, to=500,
                                    orient='horizontal', command=self.update_settings)
        self.slider_med_blur = tk.Scale(self.root, label='median_blur', from_=0, to=20,
                                        orient='horizontal', command=self.update_settings)
        self.slider_gauss_blur = tk.Scale(self.root, label='gauss_blur', from_=1, to=100,
                                          orient='horizontal', command=self.update_settings)
        self.slider_auto_bright_bias = tk.Scale(self.root, label='auto_bright_bias', from_=1, to=100,
                                                orient='horizontal', command=self.update_settings)
        self.slider_canny = tk.Scale(self.root, label='canny', from_=1, to=1000,
                                     orient='horizontal', command=self.update_settings)
        self.slider_dilate = tk.Scale(self.root, label='dilate', from_=1, to=100,
                                      orient='horizontal', command=self.update_settings)
        self.slider_white_threshold = tk.Scale(self.root, label='cut_white', from_=10, to=255,
                                               orient='horizontal', command=self.update_settings)

        self.set_user_sliders()

    def update_settings(self, *args):
        self.parent.reader.settings['exposure'] = self.slider_exp.get()
        self.parent.reader.settings['contrast'] = self.slider_cont.get()
        self.parent.reader.settings['median_blur'] = self.slider_med_blur.get()
        self.parent.reader.settings['gauss_blur'] = self.slider_gauss_blur.get()
        self.parent.reader.settings['auto_bright_bias'] = self.slider_auto_bright_bias.get()
        self.parent.reader.settings['canny'] = self.slider_canny.get()
        self.parent.reader.settings['dilate'] = self.slider_dilate.get()
        self.parent.reader.settings['white_cut'] = self.slider_white_threshold.get()

    def set_user_sliders(self):
        self.slider_exp.set(self.parent.settings['exposure'])
        self.slider_cont.set(self.parent.settings['contrast'])
        self.slider_med_blur.set(self.parent.settings['median_blur'])
        self.slider_gauss_blur.set(self.parent.settings['gauss_blur'])
        self.slider_auto_bright_bias.set(self.parent.settings['auto_bright_bias'])
        self.slider_canny.set(self.parent.settings['canny'])
        self.slider_dilate.set(self.parent.settings['dilate'])
        self.slider_white_threshold.set(self.parent.settings['white_cut'])


class ThresholdSliders:
    def __init__(self, parent):
        self.parent = parent
        self.root = tk.Toplevel()

        width, height = self.parent.geo_size
        x, y = self.parent.geo_pos
        self.root.geometry(f'{200}x{350}+{x + width + 50}+{y + 650}')

        self.thresh_var = tk.IntVar()
        self.thresh_labels = tk.Label(self.root, textvar=self.thresh_var)

        self.solidity_slider = tk.Scale(self.root, label='Solidity Threshold', from_=0, to=100,
                                        orient='horizontal', command=self.update_settings)
        self.diameter_slider = tk.Scale(self.root, label='Diameter Threshold', from_=0, to=1000,
                                        orient='horizontal', command=self.update_settings)

        self.set_user_sliders()
        self.update()

    def update(self):
        self.thresh_var.set(self.parent.reader.stats)
        self.root.after(100, self.update)

    def update_settings(self, *args):
        self.parent.reader.settings['solidity'] = self.solidity_slider.get()
        self.parent.reader.settings['diameter'] = self.diameter_slider.get()

    def set_user_sliders(self):
        self.solidity_slider.set(self.parent.settings['solidity'])
        self.diameter_slider.set(self.parent.settings['diameter'])


class Library:
    def __init__(self, parent):
        self.parent = parent
        self.root = tk.Toplevel()

        width, height = self.parent.geo_size
        x, y = self.parent.geo_pos
        self.root.geometry(f'{600}x{900}+{x + width + 650}+{y}')

        self.images_label = tk.Label(self.root)

        self.update()

    def update(self):
        result = self.parent.matcher.scanned_cards

        if len(result) > 0:
            for card in result:
                self.found_card = PIL.ImageTk.PhotoImage(
                    image=PIL.Image.open(f'{main_dir}/data/images_small/{card}.jpg'))
                self.images_label.configure(image=self.found_card)

        self.root.after(100, self.update)


class Cams:
    def __init__(self, parent):
        self.parent = parent

        self.main_cam = tk.Label(self.parent)
        self.blur_cam = tk.Label(self.parent)
        self.canny_cam = tk.Label(self.parent)
        self.contour_cam = tk.Label(self.parent)

        self.cropped_cam = tk.Label(self.parent)
        self.final_cam = tk.Label(self.parent)

        self.frame = None
        self.blur_frame = None
        self.canny_frame = None
        self.contour_frame = None
        self.cropped_frame = None
        self.final_frame = None

        for frame in self.parent.children:
            self.parent.children[frame].pack()

        self.update_cams()

    def update_cams(self):

        if self.parent.reader.resized_frame is not None:
            self.frame = PIL.ImageTk.PhotoImage(image=PIL.Image.fromarray(self.parent.reader.resized_frame))
            self.main_cam.configure(image=self.frame)

        if self.parent.reader.blurred_frame is not None:
            self.blur_frame = PIL.ImageTk.PhotoImage(image=PIL.Image.fromarray(self.parent.reader.blurred_frame))
            self.blur_cam.configure(image=self.blur_frame)

        if self.parent.reader.canny_frame is not None:
            self.canny_frame = PIL.ImageTk.PhotoImage(image=PIL.Image.fromarray(self.parent.reader.canny_frame))
            self.canny_cam.configure(image=self.canny_frame)

        if self.parent.reader.contour_frame is not None:
            self.contour_frame = PIL.ImageTk.PhotoImage(image=PIL.Image.fromarray(self.parent.reader.contour_frame))
            self.contour_cam.configure(image=self.contour_frame)

        if self.parent.reader.cropped_frame is not None:
            self.cropped_frame = PIL.ImageTk.PhotoImage(image=PIL.Image.fromarray(self.parent.reader.cropped_frame))
            self.cropped_cam.configure(image=self.cropped_frame)

        if self.parent.reader.final_filter_frame is not None:
            self.final_frame = PIL.ImageTk.PhotoImage(image=PIL.Image.fromarray(self.parent.reader.final_filter_frame))
            self.final_cam.configure(image=self.final_frame)

        self.parent.after(10, self.update_cams)


class Match:
    def __init__(self, parent):
        self.parent = parent
        self.root = tk.Toplevel()

        width, height = self.parent.geo_size
        x, y = self.parent.geo_pos
        self.root.geometry(f'{300}x{400}+{x + width + 300}+{y}')

        self.matched_card = tk.Label(self.root)
        self.match_button = tk.Button(self.root, text="Match", command=self.parent.matcher.start)
        self.stop_button = tk.Button(self.root, text="stop Match", command=self.parent.matcher.stop)

        self.update_card()

    def update_card(self):
        # print(self.match_obj.result[1])
        result = self.parent.matcher.confirmed_card

        if result is not None:
            # return

            self.found_card = PIL.ImageTk.PhotoImage(
                image=PIL.Image.open(f'{main_dir}/data/images_small/{result}.jpg'))
            self.matched_card.configure(image=self.found_card)

        self.root.after(500, self.update_card)


class MainApplication(tk.Tk):
    def __init__(self, video, reader, settings):
        super().__init__()

        self.geo_size = (500, 950)
        self.geo_pos = (100, 50)
        width, height = self.geo_size
        x, y = self.geo_pos
        self.geometry(f'{width}x{height}+{x}+{y}')

        self.video = video
        self.reader = reader
        self.settings = settings
        self.matcher = match_image.CardFinder(self)

        self.fps = FpsCounter(self)
        self.cams = Cams(self)
        self.sliders = SettingsSliders(self)
        self.thresholds = ThresholdSliders(self)
        self.match = Match(self)
        self.library = Library(self)

        for frm in self.children:
            for child in self.children[frm].children:
                self.children[frm].children[child].pack()

        self.protocol("WM_DELETE_WINDOW", self.on_quit)

    def on_quit(self):
        self.matcher.stop()
        tools.save_user_settings(self.settings)
        self.quit()
