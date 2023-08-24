from flask import Blueprint, request
import time
import cv2

card_bp = Blueprint('card', __name__)


@card_bp.route("/get_feed", methods=["GET"])
def get_feed():
    return []
