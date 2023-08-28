from main import db

from sql_models.base_model import TimeStampedModel


class Card(TimeStampedModel):
    __tablename__ = "Cards"

    card_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    card_name = db.Column(db.String(80), nullable=False)
    card_type = db.Column(db.String(80), nullable=False)
    card_desc = db.Column(db.String(255), nullable=False)
    card_race = db.Column(db.String(80), nullable=False)
    card_archetype = db.Column(db.String(80), nullable=False)

    card_price = db.Column(db.Float, nullable=True)
    card_image_hash = db.Column(db.Integer, nullable=True)

    set_id = db.Column(db.Integer, db.ForeignKey('CardSets.set_id'), nullable=False)
    set = db.Relationship("CardSet", back_populates="cards")

    def __repr__(self):
        return f"{self.__class__.__name__},name: {self.card_name}, {self.card_type}"


class CardSet(TimeStampedModel):
    __tablename__ = "CardSets"

    set_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    set_name = db.Column(db.String(80), nullable=False)
    set_code = db.Column(db.String(80), nullable=False)
    set_rarity = db.Column(db.String(80), nullable=True)
    set_rarity_code = db.Column(db.String(80), nullable=True)
    set_price = db.Column(db.String(80), nullable=True)
    set_number_cards = db.Column(db.Integer, nullable=True)

    cards = db.Relationship("Card", back_populates="set")

    __table_args__ = (
        db.UniqueConstraint('set_name', 'set_code', name="name_code_combo"),
    )

    def __repr__(self):
        return f"{self.__class__.__name__},name: {self.set_name}, {self.set_code}"
