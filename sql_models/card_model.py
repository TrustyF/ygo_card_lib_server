from main import db

from sql_models.base_model import TimeStampedModel


class Card(TimeStampedModel):
    __tablename__ = "Cards"

    card_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    card_name = db.Column(db.String(80), nullable=False)
    card_type = db.Column(db.String(80))
    card_desc = db.Column(db.String(255))
    card_race = db.Column(db.String(80))
    card_archetype = db.Column(db.String(80))
    card_price = db.Column(db.Float)
    card_image_hash = db.Column(db.Integer)

    sets = db.relationship("CardSet", secondary='card_set_association', back_populates="cards", passive_deletes=True)

    def __repr__(self):
        return f"{self.__class__.__name__},name: {self.card_name}, {self.card_type}"


class CardSet(TimeStampedModel):
    __tablename__ = "CardSets"

    set_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    set_name = db.Column(db.String(255), nullable=False)
    set_code = db.Column(db.String(80), nullable=False)
    set_rarity = db.Column(db.String(80))
    set_rarity_code = db.Column(db.String(80))
    set_price = db.Column(db.String(80))
    set_number_cards = db.Column(db.Integer)

    cards = db.relationship("Card", secondary='card_set_association', back_populates="sets", passive_deletes=True)

    db.UniqueConstraint('set_name', 'set_code', name="name_code_combo"),

    def __repr__(self):
        return f"{self.__class__.__name__},name: {self.set_name}, {self.set_code}"


class CardSetAssociation(db.Model):
    __tablename__ = "card_set_association"

    association_id = db.Column(db.Integer, primary_key=True)
    card_id = db.Column(db.Integer, db.ForeignKey('Cards.card_id'))
    set_id = db.Column(db.Integer, db.ForeignKey('CardSets.set_id'))
