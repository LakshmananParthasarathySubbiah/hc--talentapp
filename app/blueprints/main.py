from flask import Blueprint, render_template, redirect, url_for, request, abort, jsonify
from flask_login import login_required, current_user
from functools import wraps

from app import db
from app.models import User, TalentProfile

main_bp = Blueprint("main", __name__)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != "admin":
            abort(403)
        return f(*args, **kwargs)
    return decorated_function
@main_bp.route("/")
def index():
    return redirect(url_for("auth.login"))

@main_bp.route("/dashboard")
@login_required
def dashboard():
    return render_template("main/dashboard.html")

@main_bp.route("/browse")
def browse():
    q = request.args.get("q", "").strip()
    page = request.args.get("page", 1, type=int)

    query = db.session.query(TalentProfile).join(User)

    if q:
        query = query.filter(
            db.or_(
                User.username.ilike(f"%{q}%"),
                TalentProfile.skills.ilike(f"%{q}%"),
                TalentProfile.bio.ilike(f"%{q}%")
            )
        )

    pagination = query.paginate(page=page, per_page=6, error_out=False)
    return render_template("main/browse.html", pagination=pagination, q=q)

@main_bp.route("/admin/talents")
@login_required
@admin_required
def admin_talents():
    talents = db.session.query(TalentProfile).join(User).all()
    return render_template("admin_talents.html", talents=talents)

@main_bp.route("/admin/delete/<int:id>", methods=["POST"])
@login_required
@admin_required
def delete_talent(id):
    profile = db.session.get(TalentProfile, id)
    if profile:
        user = profile.user
        if profile.photo_filename:
            try:
                import os
                from flask import current_app
                photo_path = os.path.join(current_app.config["UPLOAD_FOLDER"], profile.photo_filename)
                if os.path.exists(photo_path):
                    os.remove(photo_path)
            except Exception:
                pass
        db.session.delete(user)
        db.session.commit()
    return redirect(url_for("main.admin_talents"))

@main_bp.route("/api/talents")
def api_talents():
    talents = db.session.query(TalentProfile).all()
    data = []
    for t in talents:
        data.append({
            "id": t.id,
            "username": t.user.username,
            "email": t.user.email,
            "bio": t.bio,
            "skills": t.skills,
            "links": t.links,
            "photo_filename": t.photo_filename
        })
    return jsonify(data)

@main_bp.route("/api/talents/<int:id>")
def api_talent_detail(id):
    t = db.session.get(TalentProfile, id)
    if not t:
        abort(404)
    return jsonify({
        "id": t.id,
        "username": t.user.username,
        "email": t.user.email,
        "bio": t.bio,
        "skills": t.skills,
        "links": t.links,
        "photo_filename": t.photo_filename
    })
