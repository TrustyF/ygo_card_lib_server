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

        from sql_models import card_model, base_model
        db.create_all()

        # todo remove this
        from database import update_db_from_remote
        update_db_from_remote.run()

        from flask_blueprints.card_finder_blueprint import card_finder_bp
        from flask_blueprints.card_detector_blueprint import card_detector_bp

        app.register_blueprint(card_finder_bp, url_prefix='/card_finder')
        app.register_blueprint(card_detector_bp, url_prefix='/card_detector')

    return app
