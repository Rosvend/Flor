from sqlalchemy import Column, Integer, Text, DateTime, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime
import os

Base = declarative_base()

class PQRSModel(Base):
    __tablename__ = "pqrs"
    id = Column(Integer, primary_key=True, index=True)
    original_text = Column(Text, nullable=False)
    improved_text = Column(Text, nullable=False)
    sentiment = Column(Text, nullable=True)
    is_offensive = Column(Integer, default=0)  # 0 = No, 1 = Sí
    toxicity_warning = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

class PQRSRepository:
    def __init__(self, db_url: str):
        self.engine = create_engine(db_url, connect_args={"check_same_thread": False})
        self.SessionLocal = sessionmaker(bind=self.engine)
        Base.metadata.create_all(bind=self.engine)

    def save(self, original: str, improved: str, sentiment: str, is_offensive: bool = False, toxicity_warning: str = None):
        db = self.SessionLocal()
        new_item = PQRSModel(
            original_text=original,
            improved_text=improved,
            sentiment=sentiment,
            is_offensive=1 if is_offensive else 0,
            toxicity_warning=toxicity_warning
        )
        db.add(new_item)
        db.commit()
        db.refresh(new_item)
        db.close()
        return new_item

    def get_all(self):
        db = self.SessionLocal()
        items = db.query(PQRSModel).all()
        db.close()
        return items
