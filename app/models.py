import re
from typing import Optional
from app import db, login_manager
from flask_login import UserMixin

EMAIL_RE    = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
PASSWORD_RE = re.compile(r"^(?=.*[A-Z])(?=.*\d)(?=.*[\W_]).{8,32}$")
USERNAME_RE = re.compile(r"^[a-zA-Z0-9_]{3,20}$")

def validate_email(email: str) -> Optional[str]:
    if not email or len(email) > 120:
        return "Email must be under 120 characters."
    if not EMAIL_RE.match(email.strip().lower()):
        return "Enter a valid email address."
    return None

def validate_password(password: str) -> Optional[str]:
    if not password:
        return "Password is required."
    if not PASSWORD_RE.match(password):
        return (
            "Password must be 8–32 chars and include "
            "at least one uppercase letter, one number, and one special character."
        )
    return None

def validate_username(username: str) -> Optional[str]:
    if not username:
        return "Username is required."
    if not USERNAME_RE.match(username):
        return "Username must be 3–20 characters: letters, numbers, underscores only."
    return None


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id            = db.Column(db.Integer, primary_key=True)
    username      = db.Column(db.String(20),  unique=True, nullable=False)
    email         = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role          = db.Column(db.String(10),  default="user", nullable=False)
    created_at    = db.Column(db.DateTime,    server_default=db.func.now())

    profile       = db.relationship('TalentProfile', backref='user', uselist=False, cascade='all, delete-orphan')

    def __repr__(self):
        return f"<User {self.username}>"


class TalentProfile(db.Model):
    __tablename__ = "talent_profiles"

    id             = db.Column(db.Integer, primary_key=True)
    bio            = db.Column(db.Text, nullable=True)
    skills         = db.Column(db.Text, nullable=True)
    photo_filename = db.Column(db.String(255), nullable=True)
    links          = db.Column(db.JSON, nullable=True)
    user_id        = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)

    def __repr__(self):
        return f"<TalentProfile of user {self.user_id}>"


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))