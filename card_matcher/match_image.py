import imagehash
import os
import requests
import shutil
import json
import concurrent.futures
from PIL import Image
import cv2
import time
import hashlib
import numpy as np
import threading

import filters

main_dir = os.path.dirname(os.path.abspath(__file__))

hash_size = 14
type_crop = [[97, 97.5], [17, 70]]

curr_diff = 0


# type_crop = [[4, 5], [5, 95]]

class CardFinder:
    def __init__(self, parent):
        self.result = None
        self.reader = parent.reader

        self.thread_started = False
        self.similarity = 100

        self.perf_session = []
        self.sim_session = []

        self.found_cards = []
        self.scanned_cards = []
        self.confirmed_card = None
        self.last_card = None

        self.up = False
        self.all_hashes = self.load_hashes()
        self.rotation_hashes = self.load_rotations()

    def load_hashes(self):
        with open(f'{main_dir}/data/small_images_hashes.json', 'r')as f:
            all_hashes = json.load(f)
        hashes = []
        for code, name in all_hashes.items():
            converted = imagehash.hex_to_hash(code)
            hashes.append((converted, name))

        return hashes

    def load_rotations(self):
        rot_list = os.listdir(f'{main_dir}/data/images_rotation')
        all_rots = []

        for rot in rot_list:
            name, ext = rot.split('.')
            rot_hash = imagehash.phash(Image.open(f'{main_dir}/data/images_rotation/{rot}'), hash_size)
            all_rots.append((rot_hash, name))

        return all_rots

    def start(self):
        self.thread_started = True
        print('starting match thread')
        threading.Thread(target=self.match_image,daemon=True).start()

    def stop(self):
        self.thread_started = False
        print('stopping match thread')

    def match_image(self):
        while self.thread_started:

            # start = time.time()

            frame = self.reader.final_filter_frame
            if frame is None:
                return

            frame_hash = imagehash.phash(Image.fromarray(frame), hash_size)
            rotated_frame = Image.fromarray(frame).rotate(180)
            rotated_frame_hash = imagehash.phash(rotated_frame, hash_size)

            rot_result = []
            for rot in self.rotation_hashes:
                code = rot[0]
                name = rot[1]
                diff = frame_hash - code
                rot_result.append((int(diff), name))

            rotation = min(rot_result)
            if rotation[1] == 'Down':
                frame_hash = rotated_frame_hash

            result = []
            for elem in self.all_hashes:
                code = elem[0]
                name = elem[1]
                diff = frame_hash - code
                result.append((int(diff), name))

            final = min(result)

            self.result = (final[0], final[1])

            if len(self.found_cards) > 10:
                self.found_cards.pop(0)
                self.confirmed_card = max(set(self.found_cards), key=self.found_cards.count)
            self.found_cards.append(final[1])

            curr_card = self.confirmed_card

            if curr_card is not None:
                if curr_card != self.last_card:
                    self.scanned_cards.append(curr_card)
                    self.last_card = curr_card

            #
            # print(self.found_cards)
            # print(self.confirmed_card)
            # print(self.result)

            # time.sleep(0.2)

            # executionTime = (time.time() - start)
            # self.perf_session.append(executionTime)
            # self.sim_session.append(self.similarity)

        # self.log_perf(self.perf_session, self.sim_session, "Realtime")
        # print('logging')

    def log_perf(self, session, similarity, name):
        with open(f'{main_dir}/utils/performance.json', 'r') as infile:
            data = json.load(infile)

        data[name] = {}
        data[name]['time'] = session
        data[name]['sim'] = similarity

        with open(f'{main_dir}/utils/performance.json', 'w') as outfile:
            json.dump(data, outfile, indent=1)


# def download_images(f_card):
#     print('downloading...')
#     link = f_card['card_images'][0]['image_url_small']
#     card_id = f_card["id"]
#
#     response = requests.get(link, stream=True)
#     if response.status_code == 200:
#         with open(f'{main_dir}/data/images_small/{card_id}.jpg', 'wb') as f:
#             shutil.copyfileobj(response.raw, f)


# def check_for_images():
#     with open(f'{main_dir}/data/all_cards.json') as infile:
#         data = json.load(infile)
#     data = data['data']
#
#     with open(f'{main_dir}/data/type_images_hashes.json', 'r')as f:
#         all_types = json.load(f)
#
#     print(len(data), 'images to be loaded')
#
#     img_dir = os.listdir(f'{main_dir}/data/images_small')
#
#     counted = 0
#
#     for image in img_dir:
#         raw_name, ext = image.split('.')
#         for i, card in enumerate(data):
#             if int(raw_name) == int(card['id']):
#                 counted += 1
#                 del data[i]
#
#     print('I counted ', counted, 'files')
#     print(len(data), 'files to download')
#
#     # make directories
#     for f_hash, f_type in all_types.items():
#         target_dir = f'{main_dir}/data/ordered_images/{f_type}'
#         if not os.path.isdir(target_dir):
#             os.mkdir(target_dir)
#
#     with concurrent.futures.ProcessPoolExecutor() as executor:
#         executor.map(download_images, data)


def create_hashes():
    print('creating hashes')
    small_images = f'{main_dir}/data/images_small'
    # small_images = 'output/test/hashes'
    file_list = os.listdir(small_images)
    hashed_images = {}
    for file in file_list:
        raw_id, ext = file.split('.')
        val = imagehash.phash(Image.open(small_images + '/' + file), hash_size)
        hashed_images[str(val)] = raw_id

    with open(f'{main_dir}/data/small_images_hashes.json', 'w') as out:
        json.dump(hashed_images, out, indent=3)


def match_image_realtime(frame):
    global curr_diff
    with open(f'{main_dir}/data/small_images_hashes.json', 'r')as f:
        card_hashes = json.load(f)

    frame_hash = imagehash.phash(Image.fromarray(frame), hash_size)

    for card in card_hashes:
        card_hash = imagehash.hex_to_hash(card)
        diff = card_hash - frame_hash
        if diff < curr_diff:
            print("found at ", curr_diff)
            return diff, f'{card_hashes[card]}.jpg'

    curr_diff += 1
    print(curr_diff)
    return 0, f'10000.jpg'


def hash_card_types():
    type_dir = f'{main_dir}/data/images_types'
    type_images = os.listdir(type_dir)

    hashed_types = {}
    for ty in type_images:
        name, ext = ty.split('.')

        type_im = Image.open(f'{type_dir}/{ty}')
        type_cropped = filters.easy_crop_pil(type_im, type_crop)
        type_hash = imagehash.colorhash(type_cropped, binbits=hash_size)

        hashed_types[str(type_hash)] = name

    with open(f'{main_dir}/data/type_images_hashes.json', 'w') as out:
        json.dump(hashed_types, out, indent=3)


# def split_by_type():
#     card_dir = f'{main_dir}/data/images_small'
#     card_images = os.listdir(card_dir)
#
#     with open(f'{main_dir}/data/type_images_hashes.json', 'r') as infile:
#         type_hashes = json.load(infile)
#
#     # make directories
#     for f_hash, f_type in type_hashes.items():
#         target_dir = f'{main_dir}/data/ordered_images/{f_type}'
#         if not os.path.isdir(target_dir):
#             os.mkdir(target_dir)
#
#     for card in card_images:
#         card_im = Image.open(f'{card_dir}/{card}')
#         card_cropped = filters.easy_crop_pil(card_im, type_crop)
#         card_hash = imagehash.colorhash(card_cropped, binbits=hash_size)
#
#         result = []
#         for type_str in type_hashes:
#             type_hash = imagehash.hex_to_flathash(type_str, hash_size)
#             difference = type_hash - card_hash
#             result.append((difference, type_hashes[type_str]))
#
#         result = min(result)
#         print(result)
#
#         shutil.copy(f'{main_dir}/data/images_small/{card}', f'{main_dir}/data/ordered_images/{result[1]}/{card}')
#
#         # debug
#         debug = False
#         if debug:
#             test_im = cv2.imread(f'{card_dir}/{card}')
#             test_crop = filters.easy_crop_cv(test_im, type_crop)
#             try:
#                 cv2.destroyWindow("test")
#             except:
#                 pass
#             cv2.imshow('test', test_crop)
#             cv2.imshow('test2', test_im)
#             cv2.waitKey(0)


# def test_hashes():
#     type_dir = f'{main_dir}/data/images_types'
#     type_images = os.listdir(type_dir)
#
#     card_dir = f'{main_dir}/data/images_small'
#     card_images = os.listdir(card_dir)
#
#     crop = [[4, 10], [12, 73]]
#
#     for card in card_images:
#         card_im = Image.open(f'{card_dir}/{card}')
#         card_cropped = filters.easy_crop_pil(card_im, crop)
#         # card_cropped.show()
#
#         hash1 = imagehash.colorhash(card_cropped, hash_size)
#
#         result = []
#         for type in type_images:
#             type_im = Image.open(f'{type_dir}/{type}')
#             type_cropped = filters.easy_crop_pil(type_im, crop)
#
#             hash2 = imagehash.colorhash(type_cropped, hash_size)
#             result.append((hash1 - hash2, type))
#
#         print(result)
#         print(min(result))
#
#         os.system(f'{main_dir}/data/images_small/{card}')


if __name__ == '__main__':
    start = time.time()
    create_hashes()
    executionTime = (time.time() - start)
    print('Execution time in seconds: ' + str(round(executionTime, 1)))
    # test_hashes()
