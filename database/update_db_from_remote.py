import json
import os.path
from pprint import pprint

import sqlalchemy

from card_matcher.tools.settings_handler import SettingsHandler
from constants import MAIN_DIR
from main import db
from sql_models.card_model import CardSet, Card, CardSetAssociation
import requests

settings = SettingsHandler('remote_settings.json')


def check_remote_version_current():
    response = requests.get('https://db.ygoprodeck.com/api/v7/checkDBVer.php')
    remote_data = response.json()[0]

    if settings.get('remote_version') == remote_data['database_version']:
        return True
    else:
        settings.set('remote_version', remote_data['database_version'])
        return False


def get_card_sets():
    # request all sets
    # response = requests.get('https://db.ygoprodeck.com/api/v7/cardsets.php')
    # sets_data = response.json()
    #
    # with open('sets_temp.json', 'w') as outfile:
    #     json.dump(sets_data, outfile, indent=1)

    with open(os.path.join(MAIN_DIR, "database", 'sets_temp.json'), 'r') as infile:
        sets_data = json.load(infile)

    return sets_data


def map_card_set_from_remote_to_db(sets_data):
    for entry in sets_data:
        card_set = CardSet(
            name=entry['set_name'],
            set_code=entry['set_code'],
            cards_amount=entry['num_of_cards'],
        )
        db.session.add(card_set)


def get_cards():
    # request all cards
    # response = requests.get('https://db.ygoprodeck.com/api/v7/cardinfo.php')
    # cards_data = response.json()
    #
    # with open(f'{MAIN_DIR}/database/cards_temp.json', 'w') as outfile:
    #     json.dump(cards_data['data'], outfile, indent=1)

    with open(f'{MAIN_DIR}/database/cards_temp.json', 'r') as infile:
        cards_data = json.load(infile)

    return cards_data


def map_cards_from_remote_to_db(cards):
    # make card sets
    card_sets_raw = [x['card_sets'] for x in cards if 'card_sets' in x]
    card_sets = [item for sublist in card_sets_raw for item in sublist]

    for card_set in card_sets:
        # print(card_set)
        # Check if set already exists else make it
        set_entry = db.session.query(CardSet).filter_by(name=card_set['set_name']).first()

        # make new set
        if set_entry is None:
            set_entry = CardSet(
                name=card_set['set_name'],
                set_code=card_set['set_code'].split('-')[0])

            db.session.add(set_entry)

    db.session.commit()

    # make card
    # for i, card in enumerate(cards):
    #     if i % 100 == 0:
    #         print(f'card {i} of {len(cards)}')
    #
    #     if i > 10:
    #         break
    #
    #     # Check if card already exists
    #     # if len(db.session.query(Card).all()) > 0:
    #     #     card_entry = db.session.query(Card).filter_by(card_id=card['id']).first()
    #     #
    #     #     if card_entry:
    #     #         print('found skipping')
    #     #         continue
    #
    #     new_card = Card(
    #         name=card['name'],
    #         card_id=card['id'],
    #         type=card.get('type', None),
    #         desc=card.get('desc', None),
    #         race=card.get('race', None),
    #         archetype=card.get('archetype', None),
    #     )
    #     db.session.add(new_card)
    #
    #     # make sets
    #     if 'card_sets' in card:
    #         # Add mutual relationship
    #         for card_set in card['card_sets']:
    #             set_entry = db.session.query(CardSet).filter_by(name=card_set['set_name']).one()
    #
    #             print(set_entry.id, set_entry.name)
    #             card_set_relation = CardSetAssociation(
    #                 card_id=new_card.id,
    #                 set_id=set_entry.id,
    #                 card_code=card_set['set_code'],
    #                 card_rarity=card_set['set_rarity'],
    #                 card_rarity_code=card_set['set_rarity_code'],
    #                 card_price=card_set['set_price'],
    #             )
    #             db.session.add(card_set_relation)


def run():
    # if check_remote_version_current():
    #     print('current is up-to-date with remote')
    #     return

    # map_card_set_from_remote_to_db(get_card_sets())
    map_cards_from_remote_to_db(get_cards())
    db.session.commit()

    # entry = db.session.query(Card).filter_by(name='4-Starred Ladybug of Doom').first()
    # print(entry)
    # pprint(entry.sets)
    #
    # print('---')
    #
    # collection = db.session.query(CardSet).filter_by(set_code='PSV-EN088').first()
    collection = db.session.query(CardSet).filter_by(set_code='YS15').first()
    print(collection)
    # pprint(collection.cards)
