from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Float, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(80), unique=True, nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    password_hash = Column(String(128))
    created_at = Column(DateTime, default=datetime.utcnow)
    cognitive_load_score = Column(Float, default=0.0)

class JournalEntry(Base):
    __tablename__ = 'journal_entries'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    sentiment_score = Column(Float)
    emotion_tags = Column(String(200))
    ai_response = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

class CalendarEvent(Base):
    __tablename__ = 'calendar_events'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    event_date = Column(DateTime, nullable=False)
    stress_level = Column(String(20), default='medium')
    cognitive_load_impact = Column(Float, default=0.5)
    created_at = Column(DateTime, default=datetime.utcnow)

class SupportSession(Base):
    __tablename__ = 'support_sessions'
    id = Column(Integer, primary_key=True)
    user1_id = Column(Integer, nullable=False)
    user2_id = Column(Integer, nullable=False)
    session_type = Column(String(50), default='peer')
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class Message(Base):
    __tablename__ = 'messages'
    id = Column(Integer, primary_key=True)
    session_id = Column(Integer, nullable=False)
    sender_id = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    sentiment_score = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)

engine = None
Session = None

def init_db(app):
    global engine, Session
    engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
    Session = sessionmaker(bind=engine)
    Base.metadata.create_all(engine)

def get_db_session():
    return Session()