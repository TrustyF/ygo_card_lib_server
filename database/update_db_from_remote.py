import json

from card_matcher.tools.settings_handler import SettingsHandler
from constants import MAIN_DIR
from main import db
from sql_models.card_model import CardSet, Card
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
    response = requests.get('https://db.ygoprodeck.com/api/v7/cardsets.php')
    sets_data = response.json()
    return sets_data


def map_card_set_from_remote_to_db(sets_data):
    for entry in sets_data:
        card_set = CardSet(
            set_name=entry['set_name'],
            set_code=entry['set_code'],
            set_number_cards=entry['num_of_cards'],
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
    for i, card in enumerate(cards):
        if i > 10:
            break

        new_card = Card(card_name=card['name'])

        if 'card_sets' in card:
            for card_set in card['card_sets']:

                # Check if set already exists
                set_entry = db.session.query(CardSet).filter_by(set_code=card_set['set_code']).first()

                # Make set if none
                if set_entry is None:
                    set_entry = CardSet(set_name=card_set['set_name'], set_code=card_set['set_code'])
                    db.session.add(set_entry)

                # Add mutual relationship
                new_card.sets.append(set_entry)
                set_entry.cards.append(new_card)

        db.session.add(new_card)
        db.session.commit()


def run():
    # if check_remote_version_current():
    #     print('current is up-to-date with remote')
    #     return

    # map_cards_from_remote_to_db(get_cards())
    q = db.session.query(Card.card_name)
