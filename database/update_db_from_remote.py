import json
import os.path
from pprint import pprint
import requests
import imagehash
from PIL import Image

import sqlalchemy

from detectors.tools.settings_handler import SettingsHandler
from constants import MAIN_DIR, HASH_SIZE
from db_loader import db
from sql_models.card_model import CardSet, Card, CardTemplate

settings = SettingsHandler('remote_settings.json')
small_images_path = os.path.join(MAIN_DIR, "assets", "images_small")


def check_remote_version_current():
    print('Checking remote version')

    response = requests.get('https://db.ygoprodeck.com/api/v7/checkDBVer.php')
    remote_data = response.json()[0]

    if settings.get('remote_version') == remote_data['database_version']:
        print('remote and local up-to-date')
        return True
    else:
        settings.set('remote_version', remote_data['database_version'])
        return False


def get_cards():
    print('Requesting all cards')
    # request all cards
    # response = requests.get('https://db.ygoprodeck.com/api/v7/cardinfo.php')
    # cards_data = response.json()
    #
    # with open(f'{MAIN_DIR}/database/cards_temp.json', 'w') as outfile:
    #     json.dump(cards_data['data'], outfile, indent=1)

    with open(f'{MAIN_DIR}/database/cards_temp.json', 'r') as infile:
        cards_data = json.load(infile)

    return cards_data


def map_remote_to_db():
    print('Mapping info to db')
    cards = get_cards()

    # check all sets and make missing ones
    card_sets_raw = [x['card_sets'] for x in cards if 'card_sets' in x]
    card_sets = [item for sublist in card_sets_raw for item in sublist]
    db_card_sets = [db_set.name for db_set in db.session.query(CardSet).all()]

    # Check if set already exists else make it
    for card_set in card_sets:
        if card_set['set_name'] not in db_card_sets:
            print(f'creating {card_set["set_name"]}')

            set_check = db.session.query(CardSet).filter_by(name=card_set['set_name']).one_or_none()
            if set_check:
                continue

            new_set = CardSet(
                name=card_set['set_name'],
                set_code=card_set['set_code'].split('-')[0])

            db.session.add(new_set)
    db.session.commit()

    # check all cards and make missing ones
    db_card_names = [db_name.name for db_name in db.session.query(CardTemplate).all()]

    for i, card in enumerate(cards):

        # Check if set already exists else make it
        if card['name'] in db_card_names:
            # print(f'already found {card["name"]}')
            continue

        if i % 100 == 0:
            print(f'card {i} of {len(cards)}')

        if i > 50:
            break

        card_template = CardTemplate(
            name=card['name'],
            card_id=card['id'],
            type=card.get('type', None),
            desc=card.get('desc', None),
            race=card.get('race', None),
            archetype=card.get('archetype', None),
        )
        db.session.add(card_template)

        # Add mutual relationship
        if 'card_sets' in card:
            for card_set in card['card_sets']:
                new_set = db.session.query(CardSet).filter_by(name=card_set['set_name']).one()

                card = Card(
                    card_id=card_template.id,
                    set_id=new_set.id,
                    card_code=card_set['set_code'],
                    card_rarity=card_set['set_rarity'],
                    card_rarity_code=card_set['set_rarity_code'],
                    card_price=card_set['set_price'],
                )
                db.session.add(card)

    db.session.commit()


def download_images():
    print('Downloading card images')

    # get current images and all card ids
    downloaded_images_list = os.listdir(small_images_path)
    existing_images = [int(x.split('.')[0]) for x in downloaded_images_list]
    db_card_ids = [x.card_id for x in db.session.query(CardTemplate).all()]

    # compare current images to all ids
    for card_id in db_card_ids:

        # skip if existing
        if card_id not in existing_images:
            # save image
            print(f'requesting {card_id}')
            response = requests.get(f'https://images.ygoprodeck.com/images/cards_small/{card_id}.jpg')
            with open(os.path.join(small_images_path, f"{card_id}.jpg"), 'wb') as outfile:
                outfile.write(response.content)


def hash_images():
    print('Hashing card images')

    cards = db.session.query(CardTemplate).all()

    for i, card in enumerate(cards):

        # skip if existing
        if card.image_hash is None:

            if i % 100 == 0:
                print(f'card {i} of {len(cards)}')

            card_image = os.path.join(small_images_path, f'{card.card_id}.jpg')
            card_hash = imagehash.phash(Image.open(card_image), HASH_SIZE)
            card.image_hash = str(card_hash)

    db.session.commit()


def run_update():
    # if not check_remote_version_current():
    if True:
        map_remote_to_db()
        download_images()
        hash_images()
