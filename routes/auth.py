"""
routes/auth.py
Registration, Login and Logout routes
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from pydantic import ValidationError

from models import (
    db,
    User,
    Student,
    Subject,
    StudentSubject,
    Class
)
from services.auth_service import (
hash_password,
check_password,
log_action
)

from services.validation import (
LoginSchema,
RegisterSchema
)

from services.qr_service import generate_student_qr

auth_bp = Blueprint("auth", __name__)

# ============================================================

# Home

# ============================================================

@auth_bp.route("/")
def index():


 if current_user.is_authenticated:
    return redirect(url_for(f"{current_user.role}.dashboard"))

 return redirect(url_for("auth.login"))


# ============================================================

# Login

# ============================================================

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("auth.index"))

    if request.method == "POST":
        raw = {
            "email": request.form.get("email", ""),
            "password": request.form.get("password", ""),
        }

        try:
            data = LoginSchema(**raw).model_dump()
        except ValidationError as e:
            print("=" * 60)
            print("VALIDATION ERROR")
            print(e)
            print("=" * 60)

            log_action(
                None,
                "validation_failure",
                details=e.json(),
                ip_address=request.remote_addr,
            )

            flash(
                "Invalid input. Please check your details and try again.",
                "danger",
            )
            return render_template("auth/login.html")

        email = data["email"]
        password = data["password"]

        user = User.query.filter_by(email=email).first()

        if user and user.is_active and check_password(password, user.password_hash):
            login_user(user, remember=bool(request.form.get("remember")))

            log_action(
                user.id,
                "login",
                ip_address=request.remote_addr,
            )

            flash(
                "Welcome back!",
                "success",
            )
            return redirect(url_for(f"{user.role}.dashboard"))

        flash(
            "Invalid email or password.",
            "danger",
        )
        return render_template("auth/login.html")

    return render_template("auth/login.html")


# ============================================================

# Register

# ============================================================

@auth_bp.route("/register", methods=["GET", "POST"])
def register():

    if current_user.is_authenticated:
        return redirect(url_for("auth.index"))

    if request.method == "POST":

        raw = {
            "name": request.form.get("name", ""),
            "email": request.form.get("email", ""),
            "password": request.form.get("password", ""),
            "student_id": request.form.get("student_id", ""),
            "class_name": request.form.get("class_name", ""),
            "roll_no": request.form.get("roll_no", ""),
            "department": request.form.get("department", ""),
        }

        try:
            data = RegisterSchema(**raw).model_dump()

        except ValidationError as e:

            log_action(
                None,
                "validation_failure",
                details=e.json(),
                ip_address=request.remote_addr,
            )

            flash(
                "Invalid input. Please check your details and try again.",
                "danger",
            )

            subjects = Subject.query.filter_by(
                is_active=True
            ).order_by(
                Subject.subject_name
            ).all()

            return render_template(
                "auth/register.html",
                subjects=subjects
            )

        if User.query.filter_by(email=data["email"]).first():

            flash(
                "Email already registered.",
                "danger",
            )

            subjects = Subject.query.filter_by(
                is_active=True
            ).all()

            return render_template(
                "auth/register.html",
                subjects=subjects
            )

        if Student.query.filter_by(
            student_id=data["student_id"]
        ).first():

            flash(
                "Student ID already exists.",
                "danger",
            )

            subjects = Subject.query.filter_by(
                is_active=True
            ).all()

            return render_template(
                "auth/register.html",
                subjects=subjects
            )

        user = User(
            email=data["email"],
            password_hash=hash_password(data["password"]),
            role="student",
        )

        db.session.add(user)
        db.session.flush()

        student = Student(
            user_id=user.id,
            student_id=data["student_id"],
            name=data["name"],
            email=data["email"],
            class_name=data["class_name"],
            roll_no=data["roll_no"],
            department=data.get("department"),
        )

        db.session.add(student)
        db.session.flush()

        selected_subjects = request.form.getlist("subjects")

        for subject_id in selected_subjects:

            enrollment = StudentSubject(
                student_id=student.id,
                subject_id=int(subject_id)
            )

            db.session.add(enrollment)

        try:
            qr_path = generate_student_qr(student)
            student.qr_image_path = qr_path

        except Exception:
            pass

        db.session.commit()

        log_action(
            user.id,
            "student_registered",
            "Student",
            student.id,
            request.remote_addr,
        )

        flash(
            "Registration successful! Please login.",
            "success",
        )

        return redirect(url_for("auth.login"))

    selected_class = request.args.get("class_name", "")

    classes = Class.query.order_by(
        Class.class_name
    ).all()

    subjects = []

    if selected_class:
        subjects = Subject.query.filter_by(
            class_name=selected_class,
            is_active=True
    ).order_by(
        Subject.subject_name
    ).all()

    classes = Class.query.order_by(Class.class_name).all()

    return render_template(
        "auth/register.html",
        classes=classes,
        subjects=subjects,
        selected_class=""
)



# ============================================================

# Logout

# ============================================================

@auth_bp.route("/logout")
@login_required
def logout():


    log_action(
    current_user.id,
    "logout",
    ip_address=request.remote_addr,
)

    logout_user()

    flash(
    "You have been logged out.",
    "info",
)

    return redirect(url_for("auth.login"))

