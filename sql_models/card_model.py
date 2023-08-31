from db_loader import db

from sql_models.base_model import TimeStampedModel


class CardTemplate(db.Model):
    __tablename__ = "CardTemplates"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    card_id = db.Column(db.Integer, nullable=False, unique=True)
    name = db.Column(db.String(80), nullable=False)
    type = db.Column(db.String(80))
    desc = db.Column(db.String(255))
    race = db.Column(db.String(80))
    archetype = db.Column(db.String(80))

    image_hash = db.Column(db.String(255))

    association = db.relationship("Card", back_populates="card", passive_deletes=True)

    def __repr__(self):
        return f" {self.id}-{self.__class__.__name__},name: {self.name}, {self.type}"


class CardSet(db.Model):
    __tablename__ = "CardSets"
    # __table_args__ = (
    #     db.UniqueConstraint('name', 'set_code', name="name_code_combo"),
    # )

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    set_code = db.Column(db.String(80), nullable=False)
    name = db.Column(db.String(255), unique=True, nullable=False)
    cards_amount = db.Column(db.Integer)

    association = db.relationship("Card", back_populates="card_set", passive_deletes=True)

    def __repr__(self):
        return f" {self.id}-{self.__class__.__name__},name: {self.name}, {self.set_code}"


# class CardSetAssociation(TimeStampedModel):
class Card(db.Model):
    __tablename__ = "Cards"
    # __table_args__ = (
    #     db.UniqueConstraint('card_id', 'set_id', name="card_to_set_combo"),
    # )

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    card_id = db.Column(db.Integer, db.ForeignKey('CardTemplates.id'))
    set_id = db.Column(db.Integer, db.ForeignKey('CardSets.id'))

    card_code = db.Column(db.String(80))
    card_rarity = db.Column(db.String(80))
    card_rarity_code = db.Column(db.String(80))
    card_price = db.Column(db.Float)

    card = db.relationship("CardTemplate", back_populates="association", passive_deletes=True)
    card_set = db.relationship("CardSet", back_populates="association", passive_deletes=True)

    def __repr__(self):
        return f" {self.id}-{self.__class__.__name__},code: {self.card_code}, {self.card_rarity}, {self.card_price}"


class User(TimeStampedModel):
    __tablename__ = "Users"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)


class UserCards(TimeStampedModel):
    __tablename__ = "UserCards"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    card_id = db.Column(db.Integer, db.ForeignKey('CardTemplates.id'))
    is_deleted = db.Column(db.Boolean, default=False)
