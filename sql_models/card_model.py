from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import Relationship

from sql_models.base_model import TimeStampedModel


class Card(TimeStampedModel):
    __tablename__ = "cards"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(80), nullable=False)
    type = Column(String(80), nullable=False)
    desc = Column(String(255), nullable=False)
    race = Column(String(80), nullable=False)
    archetype = Column(String(80), nullable=False)

    set = Relationship("Set", back_populates="card")

    def __repr__(self):
        return f"{self.__class__.__name__},name: {self.name}, {self.type}"


class Set(TimeStampedModel):
    __tablename__ = "sets"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(80), nullable=False)
    code = Column(String(80), nullable=False)
    rarity = Column(String(80), nullable=False)
    rarity_code = Column(String(80), nullable=False)
    price = Column(String(80), nullable=False)

    card_id = Column(Integer, ForeignKey("cards.id", ondelete="CASCADE"), nullable=False, index=True)
    card = Relationship("Card", back_populates="set")

    def __repr__(self):
        return f"{self.__class__.__name__},name: {self.name}, {self.type}"
