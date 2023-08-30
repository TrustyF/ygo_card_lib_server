from flask import Blueprint, request, Response

from database.update_db_from_remote import run_update

bp = Blueprint('database', __name__)


@bp.route("/update_from_remote", methods=["GET"])
def update_from_remote():
    run_update()
    return []
