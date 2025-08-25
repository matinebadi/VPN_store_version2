from sqlalchemy import Column, Integer, String, Boolean, DateTime, create_engine ,BigInteger
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime

engine = create_engine("sqlite:///bot_db.sqlite3")
Base = declarative_base()
Session = sessionmaker(bind=engine)
session = Session()

class Payment(Base):
    __tablename__ = "payments"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    username = Column(String)
    family_info = Column(String)
    receipt_path = Column(String)
    is_confirmed = Column(Boolean, default=False)
    confirmed_by = Column(String, nullable=True)
    rejected_by = Column(String, nullable=True)
    status = Column(String, default="pending")  
    handled_by = Column(BigInteger)  
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    reminder_sent = Column(Boolean, default=False)
    

class QRCode(Base):
    __tablename__ = "qrcodes"
    id = Column(Integer, primary_key=True)  
    filename = Column(String)
    is_used = Column(Boolean, default=False)

class Setting(Base):
    __tablename__ = "settings"
    key = Column(String, primary_key=True)
    value = Column(String)



Base.metadata.create_all(engine)

