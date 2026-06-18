import bcrypt
from collections import defaultdict
from time import time
from typing import Optional

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
<<<<<<< HEAD
from pydantic import ValidationError

from app import db
from app.models import User
from app.schemas import RegisterSchema, LoginSchema, ChangePasswordSchema, format_pydantic_errors
=======

from app import db
from app.models import User, validate_email, validate_password, validate_username
>>>>>>> ac1cc803711524f5e23023c04f966b9e0692bb22

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


<<<<<<< HEAD
=======
# ── Helpers ───────────────────────────────────────────────────────────────────

>>>>>>> ac1cc803711524f5e23023c04f966b9e0692bb22
def hash_password(plain: str) -> str:
    return bcrypt.hashpw(plain.encode("utf-8"), bcrypt.gensalt(rounds=12)).decode("utf-8")

def check_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))

def collect_errors(**fields) -> dict:
<<<<<<< HEAD
=======
    """
    Validates known fields (email, password, username).
    confirm_password is intentionally excluded — checked separately.
    """
>>>>>>> ac1cc803711524f5e23023c04f966b9e0692bb22
    errors = {}
    validators = {
        "email":    validate_email,
        "password": validate_password,
        "username": validate_username,
    }
    for field, value in fields.items():
        if field in validators:
            err = validators[field](value)
            if err:
                errors[field] = err
    return errors


<<<<<<< HEAD
_login_attempts: dict = defaultdict(list)
MAX_ATTEMPTS    = 5
WINDOW_SECONDS  = 60 * 10
=======
# ── Rate limiting ─────────────────────────────────────────────────────────────

_login_attempts: dict = defaultdict(list)
MAX_ATTEMPTS    = 5
WINDOW_SECONDS  = 60 * 10  # 10 minutes
>>>>>>> ac1cc803711524f5e23023c04f966b9e0692bb22

def is_rate_limited(ip: str) -> bool:
    now      = time()
    attempts = [t for t in _login_attempts[ip] if now - t < WINDOW_SECONDS]
    _login_attempts[ip] = attempts
    return len(attempts) >= MAX_ATTEMPTS

def record_attempt(ip: str):
    _login_attempts[ip].append(time())


<<<<<<< HEAD
=======
# ── Routes ────────────────────────────────────────────────────────────────────

>>>>>>> ac1cc803711524f5e23023c04f966b9e0692bb22
@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))

    errors    = {}
    form_data = {}

    if request.method == "POST":
<<<<<<< HEAD
        form_data = {
            "username": request.form.get("username", "").strip(),
            "email": request.form.get("email", "").strip().lower(),
            "password": request.form.get("password", ""),
            "confirm_password": request.form.get("confirm_password", "")
        }

        try:
            schema = RegisterSchema(**form_data)

            if User.query.filter(db.func.lower(User.username) == schema.username.lower()).first():
                errors["username"] = "Username already taken."
            if User.query.filter_by(email=schema.email).first():
                errors["email"] = "An account with this email already exists."

            if not errors:
                user = User(
                    username=schema.username,
                    email=schema.email,
                    password_hash=hash_password(schema.password),
                )
                db.session.add(user)
                db.session.commit()
                flash("Account created! Please log in.", "success")
                return redirect(url_for("auth.login"))
        except ValidationError as e:
            errors = format_pydantic_errors(e)

        form_data.pop("password", None)
        form_data.pop("confirm_password", None)
=======
        username = request.form.get("username", "").strip()
        email    = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm  = request.form.get("confirm_password", "")

        form_data = {"username": username, "email": email}

        errors = collect_errors(username=username, email=email, password=password)

        if not errors.get("password") and password != confirm:
            errors["confirm_password"] = "Passwords do not match."

        if not errors.get("username") and User.query.filter(db.func.lower(User.username) == username.lower()).first():
            errors["username"] = "Username already taken."
        if not errors.get("email") and User.query.filter_by(email=email).first():
            errors["email"] = "An account with this email already exists."

        if not errors:
            user = User(
                username=username,
                email=email,
                password_hash=hash_password(password),
            )
            db.session.add(user)
            db.session.commit()
            flash("Account created! Please log in.", "success")
            return redirect(url_for("auth.login"))
>>>>>>> ac1cc803711524f5e23023c04f966b9e0692bb22

    return render_template("auth/register.html", errors=errors, form_data=form_data)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))

    errors = {}

    if request.method == "POST":
        ip = request.remote_addr

        if is_rate_limited(ip):
            flash("Too many login attempts. Try again in 10 minutes.", "danger")
            return render_template("auth/login.html", errors=errors)

<<<<<<< HEAD
        form_data = {
            "identifier": request.form.get("identifier", "").strip(),
            "password": request.form.get("password", "")
        }
        remember = request.form.get("remember") == "on"

        try:
            schema = LoginSchema(**form_data)

            user = (
                User.query.filter_by(email=schema.identifier.lower()).first()
                or User.query.filter(db.func.lower(User.username) == schema.identifier.lower()).first()
            )

            if user and check_password(schema.password, user.password_hash):
=======
        identifier = request.form.get("identifier", "").strip().lower()
        password   = request.form.get("password", "")
        remember   = request.form.get("remember") == "on"

        if not identifier:
            errors["identifier"] = "Email or username is required."
        if not password:
            errors["password"] = "Password is required."

        if not errors:
            user = (
                User.query.filter_by(email=identifier).first()
                or User.query.filter(db.func.lower(User.username) == identifier).first()
            )

            if user and check_password(password, user.password_hash):
>>>>>>> ac1cc803711524f5e23023c04f966b9e0692bb22
                login_user(user, remember=remember)
                next_page = request.args.get("next")
                flash(f"Welcome back, {user.username}!", "success")
                return redirect(next_page or url_for("main.dashboard"))
            else:
                record_attempt(ip)
                errors["general"] = "Invalid credentials. Please try again."
<<<<<<< HEAD
        except ValidationError as e:
            errors = format_pydantic_errors(e)
=======
>>>>>>> ac1cc803711524f5e23023c04f966b9e0692bb22

    return render_template("auth/login.html", errors=errors)


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You've been logged out.", "info")
    return redirect(url_for("auth.login"))


@auth_bp.route("/change-password", methods=["GET", "POST"])
@login_required
def change_password():
    errors = {}

    if request.method == "POST":
<<<<<<< HEAD
        form_data = {
            "current_password": request.form.get("current_password", ""),
            "new_password": request.form.get("new_password", ""),
            "confirm_password": request.form.get("confirm_password", "")
        }

        try:
            schema = ChangePasswordSchema(**form_data)

            if not check_password(schema.current_password, current_user.password_hash):
                errors["current_password"] = "Current password is incorrect."

            if not errors:
                current_user.password_hash = hash_password(schema.new_password)
                db.session.commit()
                flash("Password updated successfully.", "success")
                return redirect(url_for("main.dashboard"))
        except ValidationError as e:
            errors = format_pydantic_errors(e)
=======
        current_pw = request.form.get("current_password", "")
        new_pw     = request.form.get("new_password", "")
        confirm_pw = request.form.get("confirm_password", "")

        if not check_password(current_pw, current_user.password_hash):
            errors["current_password"] = "Current password is incorrect."

        pw_err = validate_password(new_pw)
        if pw_err:
            errors["new_password"] = pw_err

        if not errors and new_pw != confirm_pw:
            errors["confirm_password"] = "Passwords do not match."

        if not errors:
            current_user.password_hash = hash_password(new_pw)
            db.session.commit()
            flash("Password updated successfully.", "success")
            return redirect(url_for("main.dashboard"))
>>>>>>> ac1cc803711524f5e23023c04f966b9e0692bb22

    return render_template("auth/change_password.html", errors=errors)