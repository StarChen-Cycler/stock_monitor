from flask_login import login_user
from werkzeug.security import check_password_hash, generate_password_hash
from flask import flash
from models import User, db

# Authentication logic
def authenticate_user(username, password):
    user = User.query.filter_by(username=username).first()
    if user and user.check_password(password):
        return user  # Return the user object
    return None  # Return None if authentication fails

# Registration logic
def register_user(username, email, password):
    # Check if the user already exists
    if User.query.filter_by(username=username).first() or User.query.filter_by(email=email).first():
        return False  # User already exists

    # Create a new user
    user = User(username=username, email=email)
    user.set_password(password)  # Set the password using hash
    db.session.add(user)
    db.session.commit()  # Save the new user in the database
    return True
