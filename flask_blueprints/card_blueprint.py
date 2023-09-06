import io
import json
import os.path
from pprint import pprint

from flask import Blueprint, request, Response, jsonify, send_file
from sqlalchemy import and_

from constants import MAIN_DIR, CARD_TYPE_PRIORITY
from database.data_mapper import map_card
from db_loader import db
from sql_models.card_model import Card, CardTemplate, CardSet, UserCard

bp = Blueprint('card', __name__)


@bp.route("/get", methods=["GET"])
def get():
    card_id = request.args.get('id')

    card = db.session.query(UserCard).filter_by(id=card_id).one()
    db.session.close()

    mapped_card = map_card(card)
    return mapped_card


@bp.route("/get_all", methods=["GET"])
def get_all():
    card_limit = request.args.get('card_limit')
    page = request.args.get('page')

    query = (
        db.session
        .query(UserCard)
        .join(Card)
        .join(CardTemplate)
        # .order_by(Card.card_price.desc())
        .filter(CardTemplate.archetype != None)
        # .filter(UserCard.card_language == None)
        # .order_by(Card.card_price.desc(),CardTemplate.archetype, CARD_TYPE_PRIORITY, CardTemplate.name)
        .order_by(Card.card_price.desc())
    )

    if page:
        query = query.limit(int(page) * int(card_limit))
    elif card_limit:
        query = query.limit(int(card_limit))

    user_cards = query.all()
    mapped_cards = [map_card(uc) for uc in user_cards]

    # for in case I fuck up the cards again
    # with open(f'{MAIN_DIR}/database/old_cards.json', 'w') as outfile:
    #     json.dump(mapped_cards, outfile, indent=1)

    return mapped_cards


@bp.route("/get_image", methods=["GET"])
def get_image():
    card_id = request.args.get('id')
    file_path = os.path.join(MAIN_DIR, "assets", "images_small", f"{card_id}")
    return send_file(file_path, mimetype='image/jpg')


@bp.route("/delete", methods=["GET"])
def delete():
    card_id = request.args.get('id')
    print(f'deleting {card_id}')

    db.session.query(UserCard).filter_by(id=card_id).delete()
    db.session.commit()
    db.session.close()

    return []


@bp.route("/set_card_code", methods=["GET"])
def set_card_code():
    user_card_id = request.args.get('user_card_id')
    card_id = request.args.get('card_id')
    print(f'updating card to {card_id}')

    db.session.query(UserCard).filter_by(id=user_card_id).update({'card_id': card_id})
    db.session.commit()
    db.session.close()

    return []


@bp.route("/set_card_storage", methods=["GET"])
def set_card_storage():
    user_card_id = request.args.get('user_card_id')
    storage_id = request.args.get('storage_id')
    print(f'setting card in storage {storage_id}')

    db.session.query(UserCard).filter_by(id=user_card_id).update({'storage_id': storage_id})
    db.session.commit()
    db.session.close()

    return []


@bp.route("/set_card_language", methods=["GET"])
def set_card_language():
    user_card_id = request.args.get('user_card_id')
    language = request.args.get('language')
    print(f'setting card language to {language}')

    db.session.query(UserCard).filter_by(id=user_card_id).update({'card_language': language})
    db.session.commit()
    db.session.close()

    return []
