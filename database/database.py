import datetime

from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from config.config import SQLALCHEMY_DATABASE_URI

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'
    id = Column(String(36), primary_key=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    room_nr = Column(String(50))
    department = Column(String(50))
    company = Column(String(50))
    status = Column(String(50))
    created_date = Column(DateTime, default=datetime.datetime.utcnow)

    tickets = relationship("Ticket", back_populates="user")


class Ticket(Base):
    __tablename__ = 'tickets'
    id = Column(String(36), primary_key=True)
    user_id = Column(String(36), ForeignKey('users.id'))
    topic = Column(String(255))
    category = Column(String(255))
    category_type = Column(String(255))
    cat_type = Column(String(255))
    description = Column(Text)
    image_path = Column(String(255))
    status = Column(String(50))
    responsible = Column(String(255))
    created_date = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User", back_populates="tickets")
    comments = relationship("Comment", back_populates="ticket")
    ticket_status = relationship("TicketStatus", back_populates="ticket_r")


class Comment(Base):
    __tablename__ = 'comments'
    id = Column(Integer, primary_key=True, autoincrement=True)
    ticket_id = Column(String(36), ForeignKey('tickets.id'))
    author = Column(String(255))
    author_type = Column(String(50))
    content = Column(Text)
    post_date = Column(DateTime, default=datetime.datetime.utcnow)

    ticket = relationship("Ticket", back_populates="comments")


class TicketStatus(Base):
    __tablename__ = 'ticket_status'
    id = Column(Integer, primary_key=True, autoincrement=True)
    ticket_id = Column(String(36), ForeignKey('tickets.id'))
    author = Column(String(255))
    status = Column(Text)
    status_date = Column(DateTime, default=datetime.datetime.utcnow)

    ticket_r = relationship("Ticket", back_populates="ticket_status")

class Admin(Base):
    __tablename__ = 'admins'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_name = Column(String(120), unique=True, nullable=False)
    name = Column(String(120), nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    created_date = Column(DateTime, default=datetime.datetime.utcnow)

User.tickets = relationship("Ticket", order_by=Ticket.id, back_populates="user")

engine = create_engine(SQLALCHEMY_DATABASE_URI)
Base.metadata.create_all(engine)