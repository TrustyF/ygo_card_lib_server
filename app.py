from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy

from constants import MAIN_DIR
from card_matcher.card_detector import CardDetector
from card_matcher.webcam import Webcam

db = SQLAlchemy()
webcam = Webcam()
card_detector = CardDetector(webcam)


def create_app():
    app = Flask(__name__)

    app.config["SQLALCHEMY_DATABASE_URI"] = f'sqlite:///{MAIN_DIR}/database/database.db'
    db.init_app(app)

    CORS(app)

    with app.app_context():
        from sql_models.card_model import Card, CardSet
        db.create_all()

        from flask_blueprints import card_finder_blueprint, card_detector_blueprint, datasbase_blueprint
        app.register_blueprint(card_finder_blueprint.bp, url_prefix='/card_finder')
        app.register_blueprint(card_detector_blueprint.bp, url_prefix='/card_detector')
        app.register_blueprint(datasbase_blueprint.bp, url_prefix='/database')

    return app
