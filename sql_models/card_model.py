from app import db

from sql_models.base_model import TimeStampedModel


class Card(TimeStampedModel):
    __tablename__ = "Cards"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    card_id = db.Column(db.Integer, nullable=False)
    name = db.Column(db.String(80), nullable=False)
    type = db.Column(db.String(80))
    desc = db.Column(db.String(255))
    race = db.Column(db.String(80))
    archetype = db.Column(db.String(80))

    image_hash = db.Column(db.Integer)

    sets = db.relationship("CardSet", secondary='card_set_association', back_populates="cards", passive_deletes=True)

    def __repr__(self):
        return f" {self.id}-{self.__class__.__name__},name: {self.name}, {self.type}"


class CardSet(TimeStampedModel):
    __tablename__ = "CardSets"
    # __table_args__ = (
    #     db.UniqueConstraint('name', 'set_code', name="name_code_combo"),
    # )

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    set_code = db.Column(db.String(80), nullable=False)
    name = db.Column(db.String(255), unique=True, nullable=False)
    cards_amount = db.Column(db.Integer)

    cards = db.relationship("Card", secondary='card_set_association', back_populates="sets", passive_deletes=True)

    def __repr__(self):
        return f" {self.id}-{self.__class__.__name__},name: {self.name}, {self.set_code}"


class CardSetAssociation(db.Model):
    __tablename__ = "card_set_association"
    # __table_args__ = (
    #     db.UniqueConstraint('card_id', 'set_id', name="card_to_set_combo"),
    # )

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    card_id = db.Column(db.Integer, db.ForeignKey('Cards.id', ondelete="CASCADE"))
    set_id = db.Column(db.Integer, db.ForeignKey('CardSets.id', ondelete="CASCADE"))

    card_code = db.Column(db.String(80))
    card_rarity = db.Column(db.String(80))
    card_rarity_code = db.Column(db.String(80))
    card_price = db.Column(db.Float)

    def __repr__(self):
        return f" {self.id}-{self.__class__.__name__},code: {self.card_code}, {self.card_rarity}, {self.card_price}"
