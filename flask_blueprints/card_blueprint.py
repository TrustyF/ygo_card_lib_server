import json

from flask import Blueprint, request, Response, jsonify

from db_loader import db
from sql_models.card_model import Card, CardTemplate, CardSet

bp = Blueprint('card', __name__)


@bp.route("/get_all", methods=["GET"])
def get_all():
    associations = db.session.query(Card).all()

    mapped_cards = [{
        'name': association.card.name,
        'type': association.card.type,
        'race': association.card.race,
        'archetype': association.card.archetype,
        'code': association.card_code,
    } for association in associations]

    # print(associations[0].card_set)

    return mapped_cards
