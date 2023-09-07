import io
import json
import os.path
from pprint import pprint

from flask import Blueprint, request, Response, jsonify, send_file

from constants import MAIN_DIR, CARD_TYPE_PRIORITY
from database.data_mapper import map_card
from db_loader import db
from sql_models.card_model import Card, CardTemplate, CardSet, UserCard

bp = Blueprint('card', __name__)


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
    page = request.args.get('page')

    query = (
        db.session
        .query(UserCard)
        # .join(Card)
        # .join(CardTemplate)
        # .order_by(Card.card_price.desc())
        # .filter(CardTemplate.archetype != None)
        # .filter(UserCard.card_language == None)
        # .order_by(Card.card_price.desc(),CardTemplate.archetype, CARD_TYPE_PRIORITY, CardTemplate.name)
        # .order_by(Card.card_price.desc())
        .order_by(UserCard.created_at.desc())
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


@bp.route("/get_image")
def get_image():
    card_id = request.args.get('id')
    file_path = os.path.join(MAIN_DIR, "assets", "images_small", f"{card_id}")
    return send_file(file_path, mimetype='image/jpg')


@bp.route("/add_by_name")
def add_by_name():
    card_name = request.args.get('name')
    print(f'searching for {card_name}')

    find_card = db.session.query(CardTemplate).filter(CardTemplate.name.like(f'{card_name}')).all()

    # expand search
    if len(find_card) < 1:
        find_card = db.session.query(CardTemplate).filter(CardTemplate.name.like(f'%{card_name}%')).all()

    pprint(find_card)

    if len(find_card) < 1:
        print(f'{card_name} not found')
        return []

    new_card = UserCard(card_template_id=find_card[0].id)
    db.session.add(new_card)
    db.session.commit()
    db.session.close()

    return []


@bp.route("/delete")
def delete():
    card_id = request.args.get('id')
    print(f'deleting {card_id}')

    db.session.query(UserCard).filter_by(id=card_id).delete()
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
