import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, abort
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from pydantic import ValidationError

from app import db
from app.models import TalentProfile, User
from app.schemas import ProfileSchema, format_pydantic_errors

profile_bp = Blueprint("profile", __name__, url_prefix="/profile")


def allowed_file(filename):
    return "." in filename and \
           filename.rsplit(".", 1)[1].lower() in current_app.config.get("ALLOWED_EXTENSIONS", {"png", "jpg", "jpeg", "webp"})


@profile_bp.route("/create", methods=["GET", "POST"])
@login_required
def create_profile():
    if current_user.profile:
        flash("You already have a profile. You can edit it here.", "info")
        return redirect(url_for("profile.edit_profile"))

    errors = {}
    if request.method == "POST":
        form_data = {
            "bio": request.form.get("bio", "").strip(),
            "skills": request.form.get("skills", "").strip(),
            "github": request.form.get("github", "").strip(),
            "linkedin": request.form.get("linkedin", "").strip(),
            "website": request.form.get("website", "").strip()
        }

        photo = request.files.get("photo")
        photo_filename = None

        try:
            schema = ProfileSchema(**form_data)

            if photo and photo.filename != "":
                if not allowed_file(photo.filename):
                    errors["photo"] = "Invalid file type. Allowed: PNG, JPG, JPEG, WEBP."
                else:
                    photo_filename = f"{current_user.id}_{secure_filename(photo.filename)}"

            if not errors:
                if photo and photo_filename:
                    upload_path = os.path.join(current_app.config["UPLOAD_FOLDER"], photo_filename)
                    os.makedirs(current_app.config["UPLOAD_FOLDER"], exist_ok=True)
                    photo.save(upload_path)

                profile = TalentProfile(
                    bio=schema.bio,
                    skills=schema.skills,
                    links={"github": schema.github, "linkedin": schema.linkedin, "website": schema.website},
                    photo_filename=photo_filename,
                    user_id=current_user.id
                )
                db.session.add(profile)
                db.session.commit()

                flash("Profile created successfully!", "success")
                return redirect(url_for("profile.view_profile", user_id=current_user.id))
        except ValidationError as e:
            errors = format_pydantic_errors(e)
            if photo and photo.filename != "" and not allowed_file(photo.filename):
                errors["photo"] = "Invalid file type. Allowed: PNG, JPG, JPEG, WEBP."

        temp_profile = TalentProfile(
            bio=form_data["bio"],
            skills=form_data["skills"],
            links={"github": form_data["github"], "linkedin": form_data["linkedin"], "website": form_data["website"]},
            photo_filename=photo_filename
        )
        return render_template("profile_form.html", profile=temp_profile, errors=errors)

    return render_template("profile_form.html", profile=None, errors=errors)


@profile_bp.route("/edit", methods=["GET", "POST"])
@login_required
def edit_profile():
    profile = current_user.profile
    if not profile:
        flash("Please create a profile first.", "warning")
        return redirect(url_for("profile.create_profile"))

    errors = {}
    if request.method == "POST":
        form_data = {
            "bio": request.form.get("bio", "").strip(),
            "skills": request.form.get("skills", "").strip(),
            "github": request.form.get("github", "").strip(),
            "linkedin": request.form.get("linkedin", "").strip(),
            "website": request.form.get("website", "").strip()
        }

        photo = request.files.get("photo")
        photo_filename = profile.photo_filename

        try:
            schema = ProfileSchema(**form_data)

            if photo and photo.filename != "":
                if not allowed_file(photo.filename):
                    errors["photo"] = "Invalid file type. Allowed: PNG, JPG, JPEG, WEBP."
                else:
                    photo_filename = f"{current_user.id}_{secure_filename(photo.filename)}"

            if not errors:
                if photo and photo.filename != "":
                    upload_path = os.path.join(current_app.config["UPLOAD_FOLDER"], photo_filename)
                    os.makedirs(current_app.config["UPLOAD_FOLDER"], exist_ok=True)
                    photo.save(upload_path)
                    profile.photo_filename = photo_filename

                profile.bio = schema.bio
                profile.skills = schema.skills
                profile.links = {"github": schema.github, "linkedin": schema.linkedin, "website": schema.website}
                db.session.commit()

                flash("Profile updated successfully!", "success")
                return redirect(url_for("profile.view_profile", user_id=current_user.id))
        except ValidationError as e:
            errors = format_pydantic_errors(e)
            if photo and photo.filename != "" and not allowed_file(photo.filename):
                errors["photo"] = "Invalid file type. Allowed: PNG, JPG, JPEG, WEBP."

        temp_profile = TalentProfile(
            id=profile.id,
            bio=form_data["bio"],
            skills=form_data["skills"],
            links={"github": form_data["github"], "linkedin": form_data["linkedin"], "website": form_data["website"]},
            photo_filename=photo_filename
        )
        return render_template("profile_form.html", profile=temp_profile, errors=errors)

    return render_template("profile_form.html", profile=profile, errors=errors)


@profile_bp.route("/<int:user_id>")
def view_profile(user_id):
    user = db.session.get(User, user_id)
    if not user:
        abort(404)
        
    profile = user.profile
    if not profile:
        abort(404)

    return render_template("profile_view.html", profile=profile, profile_user=user)

@profile_bp.route("/<int:user_id>/pdf")
def export_pdf(user_id):
    user = db.session.get(User, user_id)
    if not user:
        abort(404)
    profile = user.profile
    if not profile:
        abort(404)
    import io
    from flask import send_file
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=72)
    story = []
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Heading1'],
        fontSize=24,
        leading=28,
        spaceAfter=12
    )
    email_style = ParagraphStyle(
        'EmailStyle',
        parent=styles['Normal'],
        fontSize=12,
        leading=14,
        textColor='#555555',
        spaceAfter=20
    )
    h2_style = ParagraphStyle(
        'H2Style',
        parent=styles['Heading2'],
        fontSize=16,
        leading=20,
        spaceBefore=12,
        spaceAfter=6
    )
    body_style = ParagraphStyle(
        'BodyStyle',
        parent=styles['Normal'],
        fontSize=10,
        leading=14,
        spaceAfter=12
    )
    story.append(Paragraph(f"Talent Profile: {user.username}", title_style))
    story.append(Paragraph(f"Email: {user.email}", email_style))
    import os
    from flask import current_app
    if profile.photo_filename:
        photo_path = os.path.join(current_app.config["UPLOAD_FOLDER"], profile.photo_filename)
        if os.path.exists(photo_path):
            try:
                story.append(Image(photo_path, width=100, height=100))
                story.append(Spacer(1, 12))
            except Exception:
                pass
    story.append(Paragraph("Biography", h2_style))
    bio_text = profile.bio or "No biography provided."
    story.append(Paragraph(bio_text.replace('\n', '<br/>'), body_style))
    story.append(Paragraph("Skills", h2_style))
    skills_text = profile.skills or "No skills specified."
    story.append(Paragraph(skills_text, body_style))
    links = []
    if profile.links:
        for platform, url in profile.links.items():
            if url:
                links.append(f"<b>{platform.capitalize()}</b>: {url}")
    if links:
        story.append(Paragraph("Links", h2_style))
        for link in links:
            story.append(Paragraph(link, body_style))
    doc.build(story)
    buffer.seek(0)
    return send_file(
        buffer,
        as_attachment=True,
        download_name=f"{user.username}_profile.pdf",
        mimetype="application/pdf"
    )
