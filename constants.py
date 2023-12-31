import os
from sqlalchemy import case
from dotenv import load_dotenv
from sql_models.card_model import CardTemplate

MAIN_DIR = os.path.dirname(os.path.abspath(__file__))
HASH_SIZE = 14

load_dotenv(os.path.join(MAIN_DIR, '.env'))

DB_USERNAME = os.getenv('MYSQL_DATABASE_USERNAME')
DB_PASSWORD = os.getenv('MYSQL_DATABASE_PASSWORD')
DB_NAME = 'TrustyFox$ygo_cards_library'

DATABASE_URI = f'mysql+pymysql://{DB_USERNAME}:{DB_PASSWORD}@TrustyFox.mysql.pythonanywhere-services.com:3306/{DB_NAME}'
LOCAL_DATABASE_URI = f'mysql+pymysql://root:{DB_PASSWORD}@127.0.0.1:3306/{DB_NAME}'

SMALL_IMAGES_PATH = os.path.join(MAIN_DIR, "assets", "card_images_cached")
DEV_MODE = os.path.exists(os.path.join(MAIN_DIR, 'devmode.txt'))

# noinspection PyTypeChecker
CARD_TYPE_PRIORITY = case(
    (CardTemplate.type == 'Normal Monster', 1),
    (CardTemplate.type == 'Effect Monster', 2),
    (CardTemplate.type == 'Flip Effect Monster', 2),
    (CardTemplate.type == 'Union Effect Monster', 2),
    (CardTemplate.type == 'Tuner Monster', 2),
    (CardTemplate.type == 'Gemini Monster', 2),
    (CardTemplate.type == 'Normal Tuner Monster', 1),
    (CardTemplate.type == 'Spirit Monster', 2),
    (CardTemplate.type == 'Normal Tuner Monster', 1),
    (CardTemplate.type == 'Toon Monster', 2),
    (CardTemplate.type == 'Pendulum Normal Monster', 3),
    (CardTemplate.type == 'Pendulum Effect Monster', 4),
    (CardTemplate.type == 'Pendulum Flip Effect Monster', 4),
    (CardTemplate.type == 'Pendulum Tuner Effect Monster', 4),
    (CardTemplate.type == 'Pendulum Effect Ritual Monster', 16),
    (CardTemplate.type == 'Synchro Pendulum Effect Monster', 17),
    (CardTemplate.type == 'XYZ Pendulum Effect Monster', 18),
    (CardTemplate.type == 'Fusion Monster', 19),
    (CardTemplate.type == 'Ritual Monster', 20),
    (CardTemplate.type == 'Synchro Monster', 21),
    (CardTemplate.type == 'Synchro Tuner Monster', 22),
    (CardTemplate.type == 'XYZ Monster', 23),
    (CardTemplate.type == 'Link Monster', 24),
    (CardTemplate.type == 'Spell Card', 25),
    (CardTemplate.type == 'Trap Card', 26),
    (CardTemplate.type == 'Token', 27),
)
