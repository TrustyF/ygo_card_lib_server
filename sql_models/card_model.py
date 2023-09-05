from db_loader import db

from sql_models.base_model import TimeStampedModel
from dataclasses import dataclass


@dataclass
class CardSet(db.Model):
    __tablename__ = "CardSets"

    id: int = db.Column(db.Integer, primary_key=True, autoincrement=True)
    set_code: str = db.Column(db.String(80), nullable=False)
    name: str = db.Column(db.String(255), unique=True, nullable=False)

    cards = db.relationship("Card", back_populates="card_set", passive_deletes=True)

    def __repr__(self):
        return f" {self.id}-{self.__class__.__name__},name: {self.name}, {self.set_code}"


@dataclass
class CardStorage(db.Model):
    __tablename__ = "CardStorages"

    id: int = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name: str = db.Column(db.String(255), unique=True, nullable=False)

    cards = db.relationship("UserCard", back_populates="card_storage", passive_deletes=True)

    def __repr__(self):
        return f" {self.id}-{self.__class__.__name__},name: {self.name}"


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

    coded_cards = db.relationship("Card", back_populates="card_template", passive_deletes=True)
    users = db.relationship("UserCard", back_populates="card_template", passive_deletes=True)

    def __repr__(self):
        return f" {self.id}-{self.__class__.__name__},name: {self.name}, {self.type}"


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

    card_template = db.relationship("CardTemplate", back_populates="coded_cards", passive_deletes=True)
    card_set = db.relationship("CardSet", back_populates="cards", passive_deletes=True)
    users = db.relationship("UserCard", back_populates="card", passive_deletes=True)

    def __repr__(self):
        return f" {self.id}-{self.__class__.__name__},{self.card_template},code: {self.card_code}, {self.card_rarity}, {self.card_price}"


@dataclass
class UserCard(TimeStampedModel):
    __tablename__ = "UserCards"
    __table_args__ = (db.UniqueConstraint('card_id', 'storage_id', name="card_storage_combo"),)

    id: int = db.Column(db.Integer, primary_key=True, autoincrement=True)
    card_id: int = db.Column(db.Integer, db.ForeignKey('Cards.id'))
    card_template_id: int = db.Column(db.Integer, db.ForeignKey('CardTemplates.id'))
    storage_id: int = db.Column(db.Integer, db.ForeignKey('CardStorages.id'))

    card_language: str = db.Column(db.String(80))
    card_sell_price: float = db.Column(db.Float)
    card_amount: int = db.Column(db.Integer, default=1)

    is_deleted: bool = db.Column(db.Boolean, default=False)
    is_in_use: bool = db.Column(db.Boolean, default=False)

    card = db.relationship("Card", back_populates="users", passive_deletes=True)
    card_template = db.relationship("CardTemplate", back_populates="users", passive_deletes=True)
    card_storage = db.relationship("CardStorage", back_populates="cards", passive_deletes=True)

    def __repr__(self):
        return f" {self.id}-{self.__class__.__name__},card: {self.card}, {self.card_storage}"
