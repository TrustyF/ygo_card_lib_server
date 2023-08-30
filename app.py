from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from sql_models.card_model import Card, CardSet

# from database import db
from constants import MAIN_DIR
from db_loader import db

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = f'sqlite:///{MAIN_DIR}/database/database.db'
CORS(app)

with app.app_context():
    db.init_app(app)

    # from sql_models.card_model import Card, CardSet
    # db.drop_all()
    # db.create_all()

    from flask_blueprints import card_finder_blueprint, card_detector_blueprint, datasbase_blueprint

    app.register_blueprint(card_finder_blueprint.bp, url_prefix='/card_finder')
    app.register_blueprint(card_detector_blueprint.bp, url_prefix='/card_detector')
    app.register_blueprint(datasbase_blueprint.bp, url_prefix='/database')
