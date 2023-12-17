import io
import json
import os.path
import time
from pprint import pprint
import requests

from flask import Blueprint, request, Response, jsonify, send_file

from constants import MAIN_DIR, CARD_TYPE_PRIORITY
from database.data_mapper import map_card
from db_loader import db
from sql_models.card_model import Card, CardTemplate, CardSet, UserCard
from sqlalchemy import nullsfirst
import logging

bp = Blueprint('card', __name__)


@bp.route("/get", methods=['GET'])
def get_card():
    card_id = request.args.get('id', type=int)
    search_text = request.args.get('search')
    card_limit = request.args.get('card_limit', type=int)
    card_page = request.args.get('card_page', type=int)
    ordering = request.args.get('ordering')
    storage = request.args.get('storage', type=int)

    print(f'{card_id =}', f'{search_text =}', f'{card_limit =}', f'{ordering =}', f'{card_page =}', f'{storage =}')

    # base query
    query = (
        db.session
        .query(UserCard).filter(UserCard.is_deleted == 0)
        .join(CardTemplate, CardTemplate.id == UserCard.card_template_id)
        .join(Card, Card.id == UserCard.card_id)
    )

    if card_id is not None:
        query = query.filter_by(id=card_id).one()

    if search_text is not None:
        query = query.filter(CardTemplate.name.like(f'%{search_text}%')
                             | CardTemplate.archetype.like(f'%{search_text}%')
                             | Card.card_rarity.like(f'%{search_text}%'))

    match ordering:
        case 'new':
            query = query.order_by(UserCard.created_at.desc(), UserCard.updated_at.desc())
        case 'updated':
            query = query.order_by(UserCard.updated_at.desc())
        case 'price':
            query = query.order_by(Card.card_price.desc())

    if storage is not None:
        query = query.filter(UserCard.storage_id == storage)

    if card_limit is not None and card_page is not None:
        query = query.offset(card_limit * card_page)
    else:
        query = query.offset(0)

    if card_limit is not None:
        query = query.limit(card_limit)
    else:
        query = query.limit(10)

    user_cards = query.all()
    mapped_cards = [map_card(uc) for uc in user_cards]

    return mapped_cards, 200


@bp.route("/get_template", methods=['GET'])
def get_template():
    template_id = request.args.get('id', type=int)
    search_text = request.args.get('search')
    limit = request.args.get('limit', type=int)

    print(f'{template_id =}', f'{search_text =}', f'{limit =}')

    # base query
    query = (
        db.session
        .query(CardTemplate)
        # .join(CardTemplate, CardTemplate.id == Card.card_id)
        # .join(Card, Card.id == UserCard.card_id)
    )

    if template_id is not None:
        query = query.filter_by(CardTemplate.id == template_id)

    if search_text is not None:
        query = query.filter(CardTemplate.name.like(f'%{search_text}%')
                             | CardTemplate.archetype.like(f'%{search_text}%'))

    if limit is not None:
        query = query.limit(limit)
    else:
        query = query.limit(10)

    card_templates = query.all()
    real_cards = [UserCard(card_template_id=template.id) for template in card_templates]
    mapped_cards = [map_card(uc) for uc in real_cards]

    return mapped_cards, 200


@bp.route("/get_image", methods=['GET'])
def get_image():
    card_id = request.args.get('id')
    file_path = os.path.join(MAIN_DIR, "assets", "card_images_cached", f"{card_id}.jpg")

    if not os.path.exists(file_path):
        response = requests.get(f'https://images.ygoprodeck.com/images/cards/{card_id}.jpg')

        with open(file_path, 'wb') as outfile:
            outfile.write(response.content)

    return send_file(file_path, mimetype='image/jpg'), 200


@bp.route("/add")
def add_card():
    card_id = int(request.args.get('id'))
    card_storage = int(request.args.get('storage_id'))

    print(f'adding {card_id}')

    user_card = UserCard(card_template_id=card_id, storage_id=card_storage)
    db.session.add(user_card)
    db.session.commit()
    db.session.close()

    return 'ok', 200


@bp.route("/delete")
def delete_card():
    card_id = request.args.get('id')
    print(f'deleting {card_id}')

    db.session.query(UserCard).filter(UserCard.id == card_id).update({'is_deleted': 1})
    db.session.commit()
    db.session.close()

    return 'ok', 200


@bp.route("/i_update")
def update_card_int():
    card_id = request.args.get('id', type=int)
    attrib = request.args.get('attrib')
    value = request.args.get('value', type=int)

    if value == 'null':
        value = None

    print(f'i_updating {card_id=} {value=} {attrib=}')

    db.session.query(UserCard).filter_by(id=card_id).update({attrib: value})
    db.session.commit()
    db.session.close()

    return 'ok', 200


@bp.route("/s_update")
def update_card_string():
    card_id = request.args.get('id', type=int)
    attrib = request.args.get('attrib')
    value = request.args.get('value', type=str)

    if value == 'null':
        value = None

    print(f's_updating {card_id=} {value=} {attrib=}')

    db.session.query(UserCard).filter_by(id=card_id).update({attrib: value})
    db.session.commit()
    db.session.close()

    return 'ok', 200
