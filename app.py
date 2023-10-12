import os
from pprint import pprint
import sshtunnel
from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from sql_models.card_model import *
from dotenv import load_dotenv

# from database import db
from constants import MAIN_DIR
from db_loader import db

load_dotenv()

app = Flask(__name__)

# create ssh tunnel if used locally
if __name__ == '__main__':

    print('Making ssh tunnel')
    server = sshtunnel.SSHTunnelForwarder(
        ('ssh.pythonanywhere.com', 22),
        ssh_username=os.getenv('MYSQL_DATABASE_USERNAME'),
        ssh_password=os.getenv('MYSQL_DATABASE_PASSWORD'),
        remote_bind_address=('TrustyFox.mysql.pythonanywhere-services.com', 3306)
    )

    server.start()
    local_port = str(server.local_bind_port)

    print('Tunnel started')
    app.config[
        "SQLALCHEMY_DATABASE_URI"] = 'mysql+pymysql://{username}:{password}@{hostname}:{ssh}/{databasename}'.format(
        username=os.getenv('SSH_USERNAME'),
        password=os.getenv('SSH_PASSWORD'),
        hostname="127.0.0.1",
        ssh=local_port,
        databasename="TrustyFox$ygo_cards_library",
    )

else:
    print('no tunnel needed')
    app.config[
        "SQLALCHEMY_DATABASE_URI"] = 'mysql+pymysql://{username}:{password}@{hostname}/{databasename}'.format(
        username=os.getenv('SSH_USERNAME'),
        password=os.getenv('SSH_PASSWORD'),
        hostname="TrustyFox.mysql.pythonanywhere-services.com",
        databasename="TrustyFox$ygo_cards_library",
    )

CORS(app)


@app.route("/test")
def test():
    return "test", 200


with app.app_context():
    # app.config['SQLALCHEMY_POOL_SIZE'] = 1
    # app.config['SQLALCHEMY_MAX_OVERFLOW'] = 0
    # app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {"pool_size": 100, "max_overflow": 0}
    db.init_app(app)

    # db.drop_all()
    # db.create_all()

    from flask_blueprints import card_detector_blueprint, datasbase_blueprint, card_blueprint, storage_blueprint

    app.register_blueprint(card_detector_blueprint.bp, url_prefix='/card_detector')
    app.register_blueprint(datasbase_blueprint.bp, url_prefix='/database')
    app.register_blueprint(card_blueprint.bp, url_prefix='/card')
    app.register_blueprint(storage_blueprint.bp, url_prefix='/storage')
