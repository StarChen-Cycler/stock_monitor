from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from datetime import datetime

# Initialize the SQLAlchemy instance
db = SQLAlchemy()

# User model
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"

    # Set password (hash the password)
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    # Check password (validate if the entered password is correct)
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class StrategyResult(db.Model):
    """Model for storing strategy calculation results."""
    __tablename__ = 'strategy_results'

    id = db.Column(db.Integer, primary_key=True)
    ts_code = db.Column(db.String(10), nullable=False)
    strategy_name = db.Column(db.String(50), nullable=False)
    params_hash = db.Column(db.String(64), nullable=False)  # Hash of strategy parameters
    result_data = db.Column(db.JSON, nullable=False)  # Store strategy results as JSON
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        db.Index('idx_strategy_lookup', 'ts_code', 'strategy_name', 'params_hash', unique=True),
    )

    def __repr__(self):
        return f'<StrategyResult {self.strategy_name} for {self.ts_code}>'

# Initialize database (create tables)
def init_db(app):
    with app.app_context():
        db.create_all()  # This creates the tables in the database
