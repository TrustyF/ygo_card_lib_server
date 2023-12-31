from flask import Blueprint, request, Response
import time
import cv2

from detectors.tools import tools
from extensions import webcam, card_detector
from db_loader import db
from sql_models.card_model import Card, CardSet

bp = Blueprint('card_detector', __name__)


@bp.route("/get_webcam_feed", methods=["GET"])
def get_webcam_feed():
    return Response(webcam.get_stream(), mimetype='multipart/x-mixed-replace; boundary=frame')


@bp.route("/get_filter_feed", methods=["GET"])
def get_filter_feed():
    response = Response(card_detector.get_filter_feed(), mimetype='multipart/x-mixed-replace; boundary=frame')

    # todo deny frontend when not in use
    return response


@bp.route("/get_settings", methods=["GET"])
def get_settings():
    return tools.load_user_settings()


@bp.route("/set_settings", methods=["POST"])
def set_settings():
    response = request.json
    card_detector.update_detection_settings(response['slider_name'], response['slider_value'])
    return []


@bp.route("/start_detection", methods=["GET"])
def start_detection():
    state = request.args.get('state')

    if state == 'true':
        card_detector.start_scanning = True
    if state == 'false':
        card_detector.start_scanning = False

    print('card_detector.start_scanning', card_detector.start_scanning)
    return []


@bp.route("/toggle_feed", methods=["GET"])
def toggle_feed():
    state = request.args.get('state')

    if state == 'true':
        card_detector.is_getting_feed = True
    if state == 'false':
        card_detector.is_getting_feed = False

    print('card_detector.is_getting_feed', card_detector.is_getting_feed)
    return []
