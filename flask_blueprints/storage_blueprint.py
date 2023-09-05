import json
import os

from flask import Blueprint, request, Response, send_file

from constants import MAIN_DIR
from sql_models.card_model import *

bp = Blueprint('storage', __name__)


@bp.route("/get_all", methods=["GET"])
def get_all():
    storages = db.session.query(CardStorage).all()
    mapped_storage = [cs for cs in storages]
    return mapped_storage


@bp.route("/get_image", methods=["GET"])
def get_image():
    storage_id = request.args.get('id')
    print(storage_id)
    storage = db.session.query(CardStorage).filter_by(id=storage_id).one()
    file_path = os.path.join(MAIN_DIR, "assets", "images_storage", f"{storage.name}.png")
    return send_file(file_path, mimetype='image/png')
