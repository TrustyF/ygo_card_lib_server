from db_loader import db

from sql_models.base_model import TimeStampedModel
from dataclasses import dataclass


@dataclass
class CardTemplate(db.Model):
    __tablename__ = "CardTemplates"

    id: int = db.Column(db.Integer, primary_key=True, autoincrement=True)
    card_id: int = db.Column(db.Integer, nullable=False, unique=True)
    name: str = db.Column(db.String(80), nullable=False)
    type: str = db.Column(db.String(80))
    desc: str = db.Column(db.String(255))
    race: str = db.Column(db.String(80))
    archetype: str = db.Column(db.String(80))

    image_hash: str = db.Column(db.String(255))

    association = db.relationship("Card", back_populates="card", passive_deletes=True)
    user_card = db.relationship("UserCard", back_populates="card", passive_deletes=True)

    def __repr__(self):
        return f" {self.id}-{self.__class__.__name__},name: {self.name}, {self.type}"


@dataclass
class CardSet(db.Model):
    __tablename__ = "CardSets"

    id: int = db.Column(db.Integer, primary_key=True, autoincrement=True)
    set_code: str = db.Column(db.String(80), nullable=False)
    name: str = db.Column(db.String(255), unique=True, nullable=False)

    association = db.relationship("Card", back_populates="card_set", passive_deletes=True)

    def __repr__(self):
        return f" {self.id}-{self.__class__.__name__},name: {self.name}, {self.set_code}"


@dataclass
class Card(db.Model):
    __tablename__ = "Cards"

    id: int = db.Column(db.Integer, primary_key=True, autoincrement=True)
    card_id: int = db.Column(db.Integer, db.ForeignKey('CardTemplates.id'))
    set_id: int = db.Column(db.Integer, db.ForeignKey('CardSets.id'))

    card_code: str = db.Column(db.String(80))
    card_rarity: str = db.Column(db.String(80))
    card_rarity_code: str = db.Column(db.String(80))
    card_price: float = db.Column(db.Float)

    card = db.relationship("CardTemplate", back_populates="association", passive_deletes=True)
    card_set = db.relationship("CardSet", back_populates="association", passive_deletes=True)

    def __repr__(self):
        return f" {self.id}-{self.__class__.__name__},code: {self.card_code}, {self.card_rarity}, {self.card_price}"


# @dataclass
# class User(TimeStampedModel):
#     __tablename__ = "Users"
#
#     id: int = db.Column(db.Integer, primary_key=True, autoincrement=True)
#     name: str = db.Column(db.String(80))


@dataclass
class UserCard(TimeStampedModel):
    __tablename__ = "UserCards"

    id: int = db.Column(db.Integer, primary_key=True, autoincrement=True)
    card_id: int = db.Column(db.Integer, db.ForeignKey('CardTemplates.id'))

    card_code: str = db.Column(db.String(80))
    card_rarity: str = db.Column(db.String(80))
    card_rarity_code: str = db.Column(db.String(80))

    card_price: float = db.Column(db.Float)
    card_sell_price: float = db.Column(db.Float)

    card_amount: int = db.Column(db.Integer, default=1)

    is_deleted: bool = db.Column(db.Boolean, default=False)
    is_in_use: bool = db.Column(db.Boolean, default=False)

    card = db.relationship("CardTemplate", back_populates="user_card", passive_deletes=True)
