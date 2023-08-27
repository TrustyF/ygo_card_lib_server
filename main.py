from flask import Flask
from flask_cors import CORS
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from constants import MAIN_DIR
from flask_blueprints.card_finder_blueprint import card_finder_bp
from flask_blueprints.card_detector_blueprint import card_detector_bp
from card_matcher.webcam import Webcam
from card_matcher.card_detector import CardDetector

db_engine = create_engine(f'sqlite:///{MAIN_DIR}/database', echo=True)
db_session = scoped_session(
    sessionmaker(
        autoflush=False,
        autocommit=False,
        bind=db_engine
    )
)

camera = Webcam()
detector = CardDetector(camera)

app = Flask(__name__)
CORS(app)

app.register_blueprint(card_finder_bp, url_prefix='/card_finder')
app.register_blueprint(card_detector_bp, url_prefix='/card_detector')
