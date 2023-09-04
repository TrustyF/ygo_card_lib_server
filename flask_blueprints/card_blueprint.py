import io
import json
import os.path
from pprint import pprint

from flask import Blueprint, request, Response, jsonify, send_file

from constants import MAIN_DIR
from database.data_mapper import map_card
from db_loader import db
from globals import db_status
from sql_models.card_model import Card, CardTemplate, CardSet, UserCard

bp = Blueprint('card', __name__)


@bp.route("/get", methods=["GET"])
def get():
    card_id = request.args.get('id')

    card = db.session.query(UserCard).filter_by(id=card_id).one()
    mapped_card = map_card(card)
    return mapped_card


@bp.route("/get_all", methods=["GET"])
def get_all():
    card_limit = request.args.get('limit')
    card_offset = request.args.get('offset')

    user_cards = db.session.query(UserCard).order_by(UserCard.card_id).all()
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

    db.session.query(UserCard).filter_by(id=card_id).delete()
    db.session.commit()
    db_status.modified = True
    return []


@bp.route("/set_card_code", methods=["GET"])
def set_card_code():
    card_id = request.args.get('id')
    card_code = request.args.get('code')
    print(f'updating code of {card_id} to {card_code}')

    card = db.session.query(UserCard).filter_by(id=card_id).one()
    coded_card = db.session.query(Card).filter_by(card_id=card.card_template_id, card_code=card_code).first()

    db.session.query(UserCard).filter_by(id=card_id).update({'card_id': coded_card.id})
    db.session.commit()
    db_status.modified = True
    return []
