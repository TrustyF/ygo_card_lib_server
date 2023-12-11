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

bp = Blueprint('card', __name__)


def search_card_by_name(f_name):
    print('search by name')
    find_card = db.session.query(CardTemplate).filter(CardTemplate.name.like(f'{f_name}'))

    # expand search
    if len(find_card.all()) < 1:
        print('expanding search most')
        find_card = db.session.query(CardTemplate).filter(CardTemplate.name.like(f'%{f_name}%'))

    if len(find_card.all()) < 1:
        print(f'{f_name} not found')

    return find_card


@bp.route("/get")
def get():
    card_id = request.args.get('id')

    card = db.session.query(UserCard).filter_by(id=card_id).one()
    db.session.close()

    mapped_card = map_card(card)
    return mapped_card


@bp.route("/get_all")
def get_all():
    card_limit = request.args.get('card_limit')
    card_page = request.args.get('card_page')
    ordering = request.args.get('ordering')
    storage = request.args.get('storage')

    print(f'{card_limit =}', f'{ordering =}', f'{card_page =}', f'{storage =}')

    query = (
        db.session
        .query(UserCard).filter(UserCard.is_deleted == 0)
    )

    match ordering:
        case 'new_first':
            query = query.order_by(UserCard.created_at.desc(), UserCard.updated_at.desc())
        case 'updated':
            query = query.order_by(UserCard.updated_at.desc())
        case 'card_type':
            query = query.join(CardTemplate).order_by(CARD_TYPE_PRIORITY, CardTemplate.name)
        case 'card_archetype':
            query = query.join(CardTemplate).order_by(CardTemplate.archetype, CardTemplate.name)
            query = query.filter(CardTemplate.archetype != None)
        case _:
            query = query.join(Card).order_by(Card.card_price.desc())
            query = query.join(CardTemplate).order_by(UserCard.storage_id, CARD_TYPE_PRIORITY, CardTemplate.name)

    if storage != 'undefined':
        query = query.filter(UserCard.storage_id == storage)

    if card_limit != 'undefined':
        query = query.offset(int(card_limit) * int(card_page))
        query = query.limit(int(card_limit))

    user_cards = query.all()
    mapped_cards = [map_card(uc) for uc in user_cards]
    # print(mapped_cards)

    # for in case I fuck up the cards again
    # with open(f'{MAIN_DIR}/database/old_cards.json', 'w') as outfile:
    #     json.dump(mapped_cards, outfile, indent=1)

    return mapped_cards


@bp.route("/get_image")
def get_image():
    card_id = request.args.get('id')
    file_path = os.path.join(MAIN_DIR, "assets", "card_images_cached", f"{card_id}.jpg")

    if not os.path.exists(file_path):
        response = requests.get(f'https://images.ygoprodeck.com/images/cards_small/{card_id}.jpg')

        with open(file_path, 'wb') as outfile:
            outfile.write(response.content)

    return send_file(file_path, mimetype='image/jpg')


@bp.route("/add_by_name")
def add_by_name():
    card_name = request.args.get('name')
    print(f'searching for {card_name}')

    found_cards = search_card_by_name(card_name).all()

    new_card = UserCard(card_template_id=found_cards[0].id)

    db.session.add(new_card)
    db.session.commit()
    db.session.close()

    return []


@bp.route("/add")
def add():
    card_id = int(request.args.get('id'))
    card_storage = int(request.args.get('storage_id'))

    print(f'adding {card_id}')

    user_card = UserCard(card_template_id=card_id, storage_id=card_storage)
    db.session.add(user_card)
    db.session.commit()
    db.session.close()

    return []


@bp.route("/delete")
def delete():
    card_id = request.args.get('id')
    print(f'deleting {card_id}')

    db.session.query(UserCard).filter(UserCard.id == card_id).update({'is_deleted': 1})
    # db.session.update(UserCard).where(UserCard.id == card_id).values(is_deleted=1)
    # db.session.query(UserCard).filter_by(id=card_id).delete()
    db.session.commit()
    db.session.close()

    return []


@bp.route("/set_card_attrib")
def set_card_attrib():
    user_card_id = request.args.get('user_card_id')
    attr_name = request.args.get('attr_name')
    attribute = request.args.get('attribute')

    print(f'updating card {attr_name} of card {user_card_id} to {attribute}')

    if attribute == 'null':
        print('is null')
        db.session.query(UserCard).filter_by(id=user_card_id).update({str(attr_name): None})
    else:
        db.session.query(UserCard).filter_by(id=user_card_id).update({str(attr_name): attribute})

    db.session.commit()
    db.session.close()

    return []


@bp.route("/search_by_name")
def search_by_name():
    card_name = request.args.get('name')
    storage = request.args.get('storage')

    if card_name == '':
        return []

    print(f'searching for {card_name}')
    print(f'{storage =}')

    found_cards = search_card_by_name(card_name).all()
    found_cards_ids = [x.id for x in found_cards]

    query = (
        db.session
        .query(UserCard)
        .join(CardTemplate)
        .filter(UserCard.card_template_id.in_(found_cards_ids))
        # .filter(UserCard.storage_id.notin_([11]))
        .order_by(UserCard.storage_id, CARD_TYPE_PRIORITY, CardTemplate.name)
    )

    if storage != 'undefined':
        query = query.filter(UserCard.storage_id == storage)

    cards_in_user = query.all()

    mapped_cards = [map_card(uc) for uc in cards_in_user]

    return mapped_cards


@bp.route("/search_template_by_name")
def search_template_by_name():
    card_name = request.args.get('name')

    if card_name == '':
        return []

    print(f'searching for {card_name}')

    found_cards = search_card_by_name(card_name).all()

    real_cards = [UserCard(card_template_id=template.id) for template in found_cards]
    mapped_cards = [map_card(uc) for uc in real_cards]

    return mapped_cards
