from pprint import pprint

from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from sql_models.card_model import *

# from database import db
from constants import MAIN_DIR
from db_loader import db

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = f'sqlite:///{MAIN_DIR}/database/database.db'
CORS(app)


@app.route("/test")
def test():
    return "test", 200


with app.app_context():
    # app.config['SQLALCHEMY_POOL_SIZE'] = 1
    # app.config['SQLALCHEMY_MAX_OVERFLOW'] = 0
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {"pool_size": 100, "max_overflow": 0}
    db.init_app(app)

    # db.drop_all()
    db.create_all()

    from flask_blueprints import card_detector_blueprint, datasbase_blueprint, card_blueprint, storage_blueprint

    app.register_blueprint(card_detector_blueprint.bp, url_prefix='/card_detector')
    app.register_blueprint(datasbase_blueprint.bp, url_prefix='/database')
    app.register_blueprint(card_blueprint.bp, url_prefix='/card')
    app.register_blueprint(storage_blueprint.bp, url_prefix='/storage')
