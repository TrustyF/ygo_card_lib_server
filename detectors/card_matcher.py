import cv2
import imagehash
from PIL import Image
import os

from constants import HASH_SIZE, MAIN_DIR
from db_loader import db
from globals import db_status
from sql_models.card_model import Card, CardSet, UserCard, CardTemplate
from app import app


class CardMatcher:
    def __init__(self):
        self.card_hashes = [imagehash.hex_to_hash(x.image_hash) for x in db.session.query(CardTemplate).all()
                            if x.image_hash is not None]

    def match_card(self, frame):
        app.app_context().push()

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
            print('card upside down')
            image_hash = rotated_image_hash

        # find card
        closest_hash = min(self.card_hashes, key=lambda x: abs(x - image_hash))
        closest_card = db.session.query(CardTemplate).filter(CardTemplate.image_hash == str(closest_hash)).first()

        # add to lib
        # todo increase card counter if it exists
        # todo make function
        # closest_coded_card = db.session.query(Card).filter_by(card_id=closest_card.id).first()
        # scanned = UserCard(card_template_id=closest_card.id, card_id=closest_coded_card.id)
        scanned = UserCard(card_template_id=closest_card.id)
        db.session.add(scanned)
        db.session.commit()
        db_status.modified = True
        print(f"{closest_card.name} {closest_card.card_id} added")
