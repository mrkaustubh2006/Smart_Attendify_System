"""
routes/admin.py — Admin dashboard, CRUD for students/teachers/subjects/classes.
All routes protected by @admin_required.
"""

import os
from datetime import date
from flask import (Blueprint, render_template, redirect, url_for, flash,
                   request, jsonify, send_file, current_app)
from flask_login import current_user, login_required
from models import db, User, Student, Teacher, Subject, Class, Attendance, AuditLog
from services.auth_service import hash_password, log_action
from services.qr_service import generate_student_qr
from services.export_service import export_excel, export_pdf
from middleware.access import admin_required

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


# ── Dashboard ─────────────────────────────────────────────────────────────────

@admin_bp.route("/dashboard")
@login_required
@admin_required
def dashboard():
    stats = {
        "students": Student.query.count(),
        "teachers": Teacher.query.count(),
        "subjects": Subject.query.count(),
        "today_attendance": Attendance.query.filter_by(date=date.today()).count(),
    }
    recent_logs = AuditLog.query.order_by(AuditLog.timestamp.desc()).limit(10).all()
    # Monthly chart data (last 7 days)
    from sqlalchemy import func
    daily = (
        db.session.query(Attendance.date, func.count(Attendance.id))
        .group_by(Attendance.date)
        .order_by(Attendance.date.desc())
        .limit(14)
        .all()
    )
    chart_labels = [str(d) for d, _ in reversed(daily)]
    chart_data = [c for _, c in reversed(daily)]
    return render_template("admin/dashboard.html", stats=stats,
                           recent_logs=recent_logs,
                           chart_labels=chart_labels, chart_data=chart_data)


# ── Students ──────────────────────────────────────────────────────────────────

@admin_bp.route("/students")
@login_required
@admin_required
def students():
    q = request.args.get("q", "").strip()
    page = request.args.get("page", 1, type=int)
    query = Student.query
    if q:
        query = query.filter(
            (Student.name.ilike(f"%{q}%")) |
            (Student.student_id.ilike(f"%{q}%")) |
            (Student.email.ilike(f"%{q}%"))
        )
    students_page = query.order_by(Student.created_at.desc()).paginate(page=page, per_page=20)
    return render_template("admin/students.html", students=students_page, q=q)


@admin_bp.route("/students/add", methods=["GET", "POST"])
@login_required
@admin_required
def add_student():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        name = request.form.get("name", "").strip()
        student_id = request.form.get("student_id", "").strip()
        class_name = request.form.get("class_name", "").strip()
        roll_no = request.form.get("roll_no", "").strip()
        department = request.form.get("department", "").strip()
        password = request.form.get("password", "").strip()

        if User.query.filter_by(email=email).first():
            flash("Email already registered.", "danger")
            return redirect(request.url)
        if Student.query.filter_by(student_id=student_id).first():
            flash("Student ID already exists.", "danger")
            return redirect(request.url)

        user = User(email=email, password_hash=hash_password(password), role="student")
        db.session.add(user)
        db.session.flush()

        student = Student(
            user_id=user.id, student_id=student_id, name=name,
            email=email, class_name=class_name, roll_no=roll_no, department=department,
        )
        db.session.add(student)
        db.session.flush()

        try:
            student.qr_image_path = generate_student_qr(student)
        except Exception:
            pass

        db.session.commit()
        log_action(current_user.id, "admin_add_student", "Student", student.id, request.remote_addr)
        flash(f"Student {name} added successfully.", "success")
        return redirect(url_for("admin.students"))

    classes = Class.query.order_by(Class.class_name).all()
    return render_template("admin/student_form.html", student=None, classes=classes)


@admin_bp.route("/students/<int:sid>/edit", methods=["GET", "POST"])
@login_required
@admin_required
def edit_student(sid):
    student = Student.query.get_or_404(sid)
    if request.method == "POST":
        student.name = request.form.get("name", student.name).strip()
        student.class_name = request.form.get("class_name", student.class_name).strip()
        student.roll_no = request.form.get("roll_no", student.roll_no).strip()
        student.department = request.form.get("department", student.department).strip()
        db.session.commit()
        log_action(current_user.id, "admin_edit_student", "Student", sid, request.remote_addr)
        flash("Student updated.", "success")
        return redirect(url_for("admin.students"))
    classes = Class.query.order_by(Class.class_name).all()
    return render_template("admin/student_form.html", student=student, classes=classes)


@admin_bp.route("/students/<int:sid>/delete", methods=["POST"])
@login_required
@admin_required
def delete_student(sid):
    student = Student.query.get_or_404(sid)
    name = student.name
    user = student.user
    db.session.delete(student)
    if user:
        db.session.delete(user)
    db.session.commit()
    log_action(current_user.id, "admin_delete_student", "Student", sid, request.remote_addr)
    flash(f"Student {name} deleted.", "warning")
    return redirect(url_for("admin.students"))


@admin_bp.route("/students/<int:sid>/regenerate_qr", methods=["POST"])
@login_required
@admin_required
def regenerate_qr(sid):
    import secrets
    student = Student.query.get_or_404(sid)
    student.qr_token = secrets.token_hex(32)
    try:
        student.qr_image_path = generate_student_qr(student)
        db.session.commit()
        flash("QR code regenerated.", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"QR generation failed: {e}", "danger")
    return redirect(url_for("admin.students"))


# ── Teachers ──────────────────────────────────────────────────────────────────

@admin_bp.route("/teachers")
@login_required
@admin_required
def teachers():
    teachers_list = Teacher.query.order_by(Teacher.created_at.desc()).all()
    return render_template("admin/teachers.html", teachers=teachers_list)


@admin_bp.route("/teachers/add", methods=["GET", "POST"])
@login_required
@admin_required
def add_teacher():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        name = request.form.get("name", "").strip()
        teacher_id = request.form.get("teacher_id", "").strip()
        department = request.form.get("department", "").strip()
        password = request.form.get("password", "").strip()

        if User.query.filter_by(email=email).first():
            flash("Email already registered.", "danger")
            return redirect(request.url)

        user = User(email=email, password_hash=hash_password(password), role="teacher")
        db.session.add(user)
        db.session.flush()

        teacher = Teacher(
            user_id=user.id, teacher_id=teacher_id,
            name=name, email=email, department=department,
        )
        db.session.add(teacher)
        db.session.commit()
        log_action(current_user.id, "admin_add_teacher", "Teacher", teacher.id, request.remote_addr)
        flash(f"Teacher {name} added.", "success")
        return redirect(url_for("admin.teachers"))

    return render_template("admin/teacher_form.html", teacher=None)


@admin_bp.route("/teachers/<int:tid>/edit", methods=["GET", "POST"])
@login_required
@admin_required
def edit_teacher(tid):
    teacher = Teacher.query.get_or_404(tid)
    if request.method == "POST":
        teacher.name = request.form.get("name", teacher.name).strip()
        teacher.department = request.form.get("department", teacher.department).strip()
        db.session.commit()
        flash("Teacher updated.", "success")
        return redirect(url_for("admin.teachers"))
    return render_template("admin/teacher_form.html", teacher=teacher)


@admin_bp.route("/teachers/<int:tid>/delete", methods=["POST"])
@login_required
@admin_required
def delete_teacher(tid):
    teacher = Teacher.query.get_or_404(tid)
    name = teacher.name
    user = teacher.user
    db.session.delete(teacher)
    if user:
        db.session.delete(user)
    db.session.commit()
    log_action(current_user.id, "admin_delete_teacher", "Teacher", tid, request.remote_addr)
    flash(f"Teacher {name} deleted.", "warning")
    return redirect(url_for("admin.teachers"))


# ── Subjects ──────────────────────────────────────────────────────────────────

@admin_bp.route("/subjects")
@login_required
@admin_required
def subjects():
    subjects_list = Subject.query.order_by(Subject.subject_name).all()
    return render_template("admin/subjects.html", subjects=subjects_list)


@admin_bp.route("/subjects/add", methods=["GET", "POST"])
@login_required
@admin_required
def add_subject():
    if request.method == "POST":
        name = request.form.get("subject_name", "").strip()
        code = request.form.get("subject_code", "").strip().upper()
        class_name = request.form.get("class_name", "").strip()
        department = request.form.get("department", "").strip()

        if Subject.query.filter_by(subject_code=code).first():
            flash("Subject code already exists.", "danger")
            return redirect(request.url)

        subject = Subject(subject_name=name, subject_code=code,
                          class_name=class_name, department=department)
        db.session.add(subject)
        db.session.commit()
        flash(f"Subject {name} added.", "success")
        return redirect(url_for("admin.subjects"))

    classes = Class.query.order_by(Class.class_name).all()
    return render_template("admin/subject_form.html", subject=None, classes=classes)


@admin_bp.route("/subjects/<int:sid>/edit", methods=["GET", "POST"])
@login_required
@admin_required
def edit_subject(sid):
    subject = Subject.query.get_or_404(sid)
    if request.method == "POST":
        subject.subject_name = request.form.get("subject_name", subject.subject_name).strip()
        subject.class_name = request.form.get("class_name", subject.class_name).strip()
        subject.department = request.form.get("department", subject.department).strip()
        db.session.commit()
        flash("Subject updated.", "success")
        return redirect(url_for("admin.subjects"))
    classes = Class.query.order_by(Class.class_name).all()
    return render_template("admin/subject_form.html", subject=subject, classes=classes)


@admin_bp.route("/subjects/<int:sid>/delete", methods=["POST"])
@login_required
@admin_required
def delete_subject(sid):
    subject = Subject.query.get_or_404(sid)
    db.session.delete(subject)
    db.session.commit()
    flash("Subject deleted.", "warning")
    return redirect(url_for("admin.subjects"))


# ── Classes ───────────────────────────────────────────────────────────────────

@admin_bp.route("/classes")
@login_required
@admin_required
def classes():
    classes_list = Class.query.order_by(Class.class_name).all()
    return render_template("admin/classes.html", classes=classes_list)


@admin_bp.route("/classes/add", methods=["GET", "POST"])
@login_required
@admin_required
def add_class():
    if request.method == "POST":
        cls = Class(
            class_name=request.form.get("class_name", "").strip(),
            department=request.form.get("department", "").strip(),
            academic_year=request.form.get("academic_year", "").strip(),
        )
        db.session.add(cls)
        db.session.commit()
        flash("Class added.", "success")
        return redirect(url_for("admin.classes"))
    return render_template("admin/class_form.html", cls=None)


# ── Attendance records ────────────────────────────────────────────────────────

@admin_bp.route("/attendance")
@login_required
@admin_required
def attendance():
    page = request.args.get("page", 1, type=int)
    date_filter = request.args.get("date")
    subject_id = request.args.get("subject_id", type=int)

    q = Attendance.query
    if date_filter:
        from datetime import datetime as dt
        try:
            d = dt.strptime(date_filter, "%Y-%m-%d").date()
            q = q.filter_by(date=d)
        except ValueError:
            pass
    if subject_id:
        q = q.filter_by(subject_id=subject_id)

    records = q.order_by(Attendance.date.desc(), Attendance.time.desc()).paginate(page=page, per_page=30)
    subjects = Subject.query.order_by(Subject.subject_name).all()
    return render_template("admin/attendance.html", records=records,
                           subjects=subjects, date_filter=date_filter, subject_id=subject_id)


# ── Exports ───────────────────────────────────────────────────────────────────

@admin_bp.route("/export/excel")
@login_required
@admin_required
def export_excel_route():
    records = Attendance.query.order_by(Attendance.date.desc()).all()
    path = export_excel(records, "admin_attendance")
    return send_file(path, as_attachment=True, download_name=os.path.basename(path))


@admin_bp.route("/export/pdf")
@login_required
@admin_required
def export_pdf_route():
    records = Attendance.query.order_by(Attendance.date.desc()).all()
    path = export_pdf(records, "Full Attendance Report", "admin_attendance")
    return send_file(path, as_attachment=True, download_name=os.path.basename(path))


# ── Audit logs ────────────────────────────────────────────────────────────────

@admin_bp.route("/audit-logs")
@login_required
@admin_required
def audit_logs():
    page = request.args.get("page", 1, type=int)
    logs = AuditLog.query.order_by(AuditLog.timestamp.desc()).paginate(page=page, per_page=30)
    return render_template("admin/audit_logs.html", logs=logs)
