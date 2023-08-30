import cv2
import imagehash
from PIL import Image
import os

from constants import HASH_SIZE, MAIN_DIR
from db_loader import db
from sql_models.card_model import Card, CardSet


class CardMatcher:
    def __init__(self):
        self.card_hashes = [imagehash.hex_to_hash(x.image_hash) for x in db.session.query(Card).all()]

    def match_card(self, frame):

        if frame is None:
            print('image is none, cant match')
            return None

        image = Image.fromarray(frame)

        # check image rotation
        image_hash = imagehash.phash(image, HASH_SIZE)
        rotated_image_hash = imagehash.phash(image.rotate(180), HASH_SIZE)
        control_card_hash = self.card_hashes[0]

        upright_distance = image_hash - control_card_hash
        reversed_distance = rotated_image_hash - control_card_hash

        if upright_distance > reversed_distance:
            image_hash = rotated_image_hash

        # find card
        closest_hash = min(self.card_hashes, key=lambda x: abs(x - image_hash))
        closest_card = db.session.query(Card).filter(Card.image_hash == str(closest_hash)).all()

        return closest_card
