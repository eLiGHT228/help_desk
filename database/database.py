import datetime

from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(String, primary_key=True)
    name = Column(String)
    email = Column(String)
    room_nr = Column(String)
    created_date = Column(DateTime, default=datetime.datetime.utcnow)

    tickets = relationship("Ticket", back_populates="user")

class Ticket(Base):
    __tablename__ = 'tickets'
    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey('users.id'))
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
    comments = relationship("Comment", back_populates="ticket")
    ticket_status = relationship("TicketStatus", back_populates="ticket_r")

class Comment(Base):
    __tablename__ = 'comments'
    id = Column(Integer, primary_key=True)
    ticket_id = Column(String, ForeignKey('tickets.id'))
    author = Column(String)
    author_type = Column(String)
    content = Column(Text)
    post_date = Column(DateTime, default=datetime.datetime.utcnow)

    ticket = relationship("Ticket", back_populates="comments")

class TicketStatus(Base):
    __tablename__ = 'ticket_status'
    id = Column(Integer, primary_key=True)
    ticket_id = Column(String, ForeignKey('tickets.id'))
    author = Column(String)
    status = Column(Text)
    status_date = Column(DateTime, default=datetime.datetime.utcnow)

    ticket_r = relationship("Ticket", back_populates="ticket_status")
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