from flask import Blueprint, request, Response
import time
import cv2

from card_matcher.tools import tools
from extensions import webcam, card_detector

bp = Blueprint('card_detector', __name__)


@bp.route("/get_webcam_feed", methods=["GET"])
def get_webcam_feed():
    return Response(webcam.get_stream(), mimetype='multipart/x-mixed-replace; boundary=frame')


@bp.route("/get_filter_feed", methods=["GET"])
def get_filter_feed():
    return Response(card_detector.get_filter_feed(), mimetype='multipart/x-mixed-replace; boundary=frame')


@bp.route("/get_settings", methods=["GET"])
def get_settings():
    return tools.load_user_settings()


@bp.route("/set_settings", methods=["POST"])
def set_settings():
    response = request.json
    card_detector.update_detection_settings(response['slider_name'], response['slider_value'])
    return []
