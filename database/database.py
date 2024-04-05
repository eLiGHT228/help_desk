import datetime

from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from werkzeug.security import generate_password_hash, check_password_hash

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    mail = Column(String)
    name = Column(String)
    email = Column(String)
    phone = Column(String)
    room_nr = Column(String)
    created_date = Column(DateTime, default=datetime.datetime.utcnow)

class Ticket(Base):
    __tablename__ = 'tickets'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    topic = Column(String)
    category = Column(String)
    category_type = Column(String)
    cat_type = Column(String)
    description = Column(String)
    image_path = Column(String)
    status = Column(String)
    responsible = Column(String)
    created_date = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User", back_populates="tickets")

class Admin(Base):

    __tablename__ = 'admins'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_name = Column(String(120), unique=True)
    name = Column(String(120))
    email = Column(String(120), unique=True)
    created_date = Column(DateTime, default=datetime.datetime.utcnow)

User.tickets = relationship("Ticket", order_by=Ticket.id, back_populates="user")

engine = create_engine('sqlite:///database/helpdesk.db')
Base.metadata.create_all(engine)