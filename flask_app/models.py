
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

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

# Initialize database (create tables)
def init_db(app):
    with app.app_context():
        db.create_all()  # This creates the tables in the database
