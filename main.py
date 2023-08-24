from flask import Flask
from flask_cors import CORS

from flask_blueprints.card_blueprint import card_bp

app = Flask(__name__)
CORS(app)

app.register_blueprint(card_bp, url_prefix='/card')
