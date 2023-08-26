from flask import Blueprint, request, Response
import time
import cv2

from card_matcher.webcam import Webcam
from card_matcher.card_detector import CardDetector

card_bp = Blueprint('card', __name__)

camera = Webcam()
detector = CardDetector(camera)


@card_bp.route("/get_webcam_feed", methods=["GET"])
def get_webcam_feed():
    return Response(camera.get_stream(), mimetype='multipart/x-mixed-replace; boundary=frame')


@card_bp.route("/get_filter_feed", methods=["GET"])
def get_filter_feed():
    return Response(detector.get_filter_view(), mimetype='multipart/x-mixed-replace; boundary=frame')
