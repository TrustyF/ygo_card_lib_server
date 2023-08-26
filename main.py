from flask import Flask
from flask_cors import CORS

from flask_blueprints.card_finder_blueprint import card_bp
from flask_blueprints.card_detector_blueprint import card_detector_bp

app = Flask(__name__)
CORS(app)

app.register_blueprint(card_bp, url_prefix='/card')
app.register_blueprint(card_detector_bp, url_prefix='/card_detector')
