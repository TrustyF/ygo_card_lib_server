from sqlalchemy import create_engine, ForeignKey, Column, String, Integer, CHAR
from sqlalchemy.orm import sessionmaker, declarative_base

Base = declarative_base()
engine = create_engine("sqlite:///database/cards_db.db", echo=True)
Session = sessionmaker(bind=engine)


class Card(Base):
    __tablename__ = "cards"
    id = Column("id", Integer, primary_key=True)
    name = Column('name', String)
    kind = Column('kind', String)

    def __init__(self, name, kind):
        self.name = name
        self.kind = kind

    def __repr__(self):
        return f'name={self.name} kind={self.kind}'


Base.metadata.create_all(engine)
session = Session()

# card = Card(name='test', kind='trap')
# session.add(card)
# session.commit()

# results = session.query(Card).all()
# print(results)
