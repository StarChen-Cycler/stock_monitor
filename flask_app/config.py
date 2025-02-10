import os
from datetime import timedelta

class Config:
    SECRET_KEY = os.urandom(24)  # Used for encrypting sessions and tokens
    SQLALCHEMY_DATABASE_URI = 'sqlite:///site.db'  # SQLite database path
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # Disable SQLAlchemy's object modification tracking
    SESSION_COOKIE_NAME = 'flask_session_cookie'  # Custom cookie name
    REMEMBER_COOKIE_DURATION = timedelta(days=30)