from pprint import pprint

from db_loader import db
from sql_models.card_model import *


def map_card(uc):
    # print(uc)

    card_template = db.session.query(CardTemplate).filter_by(id=uc.card_template_id).one()
    card = db.session.query(Card).filter_by(id=uc.card_id).one_or_none()
    card_sets = db.session.query(Card).filter_by(card_id=uc.card_template_id).all()
    card_storage = db.session.query(CardStorage).filter_by(id=uc.storage_id).one_or_none()

    mapped = {
        'user_card_id': uc.id,
        'card_template_id': uc.card_template_id,
        'card_id': uc.card_id,
        'storage_id': uc.storage_id,
        'konami_id': card_template.card_id,

        'name': card_template.name,
        'type': card_template.type,
        'race': card_template.race,
        'archetype': card_template.archetype,

        'code': None,
        'rarity': None,
        'rarity_code': None,
        'price': None,

        'language': uc.card_language,
        'sell_price': uc.card_sell_price,
        'amount': uc.card_amount,

        'is_in_use': uc.is_in_use,
        'is_deleted': uc.is_deleted,

        'sets': [{
            'set_id': cs.set_id,
            'card_id': cs.id,
            'card_code': cs.card_code,
            'card_rarity': cs.card_rarity,
            'card_rarity_code': cs.card_rarity_code,
        } for cs in card_sets],

        'storage_name': None,
    }

    if card is not None:
        mapped = mapped | {
            'code': card.card_code,
            'rarity': card.card_rarity,
            'rarity_code': card.card_rarity_code,
            'price': card.card_price,
        }

    if card_storage is not None:
        mapped = mapped | {
            'storage_name': card_storage.name,
        }

    return mapped


def map_card_storage(cs):
    # print(cs)
    return cs
