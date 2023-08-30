from flask import Blueprint, request, Response
import time
import cv2

from extensions import webcam

bp = Blueprint('card_finder', __name__)


@bp.route("/get_webcam_feed", methods=["GET"])
def get_webcam_feed():
    return Response(webcam.get_stream(), mimetype='multipart/x-mixed-replace; boundary=frame')
