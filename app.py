from flask import Flask
from flask_cors import CORS

from constants import LOCAL_DATABASE_URI
from db_loader import db

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = LOCAL_DATABASE_URI

CORS(app)

with app.app_context():
    db.init_app(app)

    # db.drop_all()
    db.create_all()

    from flask_blueprints import card_blueprint

    app.register_blueprint(card_blueprint.bp, url_prefix='/card')
