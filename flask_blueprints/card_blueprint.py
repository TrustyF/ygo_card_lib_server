import io
import json
import os.path

from flask import Blueprint, request, Response, jsonify, send_file

from constants import MAIN_DIR
from database.data_mapper import map_card
from db_loader import db
from globals import db_status
from sql_models.card_model import Card, CardTemplate, CardSet, UserCard

bp = Blueprint('card', __name__)


@bp.route("/get_all", methods=["GET"])
def get_all():
    card_limit = request.args.get('limit')
    card_offset = request.args.get('offset')

    user_cards = db.session.query(UserCard) \
        .order_by(UserCard.created_at.desc()) \
        .limit(card_limit) \
        .all()

    # print(user_cards[0].card.association[0].card_code)
    mapped_cards = [map_card(uc) for uc in user_cards]

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
    db.session.query(UserCard) \
        .filter_by(card_id=card_id) \
        .where(UserCard.card_amount <= 1) \
        .delete()
    db.session.commit()
    db_status.modified = True
    return []


@bp.route("/set_card_code", methods=["GET"])
def set_card_code():
    card_id = request.args.get('id')
    card_code = request.args.get('code')
    print(f'updating code of {card_id} to {card_code}')
    db.session.query(UserCard) \
        .filter_by(card_id=card_id) \
        .update({'card_code': card_code})
    db.session.commit()
    db_status.modified = True
    return []
