"""
routes/student.py — Student dashboard, profile, QR code display, attendance history.
"""

import os
from flask import Blueprint, render_template, redirect, url_for, flash, request, send_file
from flask_login import current_user, login_required
from models import Student, Attendance, Subject
from services.qr_service import generate_student_qr
from middleware.access import student_required

student_bp = Blueprint("student", __name__, url_prefix="/student")


@student_bp.route("/dashboard")
@login_required
@student_required
def dashboard():
    """Student home page with attendance summary."""
    student = Student.query.filter_by(user_id=current_user.id).first()
    if not student:
        flash("Student profile not found.", "danger")
        return redirect(url_for("auth.logout"))

    # Overall attendance percentage
    total_records = student.attendance_records.count()
    present_count = student.attendance_records.filter_by(status="present").count()
    overall_percentage = round((present_count / total_records) * 100, 1) if total_records > 0 else 0

    # Subject-wise breakdown
    subjects = Subject.query.filter_by(is_active=True).all()
    subject_stats = []
    for subj in subjects:
        count = student.attendance_records.filter_by(subject_id=subj.id).count()
        if count > 0:
            pres = student.attendance_records.filter_by(subject_id=subj.id, status="present").count()
            subject_stats.append({
                "subject": subj,
                "total": count,
                "present": pres,
                "percentage": round((pres / count) * 100, 1),
            })

    return render_template("student/dashboard.html", student=student,
                           overall_percentage=overall_percentage,
                           subject_stats=subject_stats)


@student_bp.route("/profile")
@login_required
@student_required
def profile():
    """Student profile with QR code."""
    student = Student.query.filter_by(user_id=current_user.id).first()
    if not student:
        flash("Student profile not found.", "danger")
        return redirect(url_for("auth.logout"))

    return render_template("student/profile.html", student=student)


@student_bp.route("/qr")
@login_required
@student_required
def qr_code():
    """Display and download QR code."""
    student = Student.query.filter_by(user_id=current_user.id).first()
    if not student:
        flash("Student profile not found.", "danger")
        return redirect(url_for("auth.logout"))

    # Regenerate if missing
    if not student.qr_image_path:
        try:
            student.qr_image_path = generate_student_qr(student)
            from models import db
            db.session.commit()
        except Exception as e:
            flash(f"QR generation error: {e}", "warning")

    return render_template("student/qr_code.html", student=student)


@student_bp.route("/qr/download")
@login_required
@student_required
def download_qr():
    """Download QR code as PNG."""
    student = Student.query.filter_by(user_id=current_user.id).first()
    if not student or not student.qr_image_path:
        flash("QR code not available.", "danger")
        return redirect(url_for("student.qr_code"))

    path = os.path.join(os.path.dirname(os.path.dirname(__file__)), student.qr_image_path)
    if not os.path.exists(path):
        flash("QR code file not found.", "danger")
        return redirect(url_for("student.qr_code"))

    return send_file(path, as_attachment=True,
                     download_name=f"QR_{student.student_id}.png")


@student_bp.route("/attendance")
@login_required
@student_required
def attendance():
    """View personal attendance history."""
    student = Student.query.filter_by(user_id=current_user.id).first()
    if not student:
        flash("Student profile not found.", "danger")
        return redirect(url_for("auth.logout"))

    page = request.args.get("page", 1, type=int)
    subject_id = request.args.get("subject_id", type=int)

    q = Attendance.query.filter_by(student_id=student.id)
    if subject_id:
        q = q.filter_by(subject_id=subject_id)

    records = q.order_by(Attendance.date.desc(), Attendance.time.desc()).paginate(page=page, per_page=20)
    subjects = Subject.query.filter_by(is_active=True).all()

    return render_template("student/attendance.html",
                           student=student, records=records,
                           subjects=subjects, subject_id=subject_id)
