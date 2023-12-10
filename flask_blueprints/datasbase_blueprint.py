import json

from flask import Blueprint, request, Response

from database.update_db_from_remote import run_update
from db_loader import db
from extensions import card_detector
from sql_models.card_model import *
from database.data_mapper import map_card_storage

bp = Blueprint('database', __name__)


@bp.route("/update_from_remote", methods=["GET"])
def update_from_remote():
    run_update()
    return []