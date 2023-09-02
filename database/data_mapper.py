from db_loader import db
from sql_models.card_model import *


def map_card(uc):
    card = uc.card
    card_sets = db.session.query(Card).filter_by(id=card.id).all()
    return {
        'id': card.id,
        'card_id': card.card_template.card_id,
        'set_id': card.set_id,
        'storage_id': uc.storage_id,
        'name': card.card_template.name,
        'type': card.card_template.type,
        'race': card.card_template.race,
        'archetype': card.card_template.archetype,
        'code': card.card_code,
        'rarity': card.card_rarity,
        'rarity_code': card.card_rarity_code,
        'language': uc.card_language,
        'price': uc.card_price,
        'sell_price': uc.card_sell_price,
        'amount': uc.card_amount,
        'is_in_use': uc.is_in_use,
        'is_deleted': uc.is_deleted,
        'sets': [{
            'set_id': cs.set_id,
            'card_code': cs.card_code,
        } for cs in card_sets]
    }
