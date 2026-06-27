"""
routes/teacher.py — Teacher dashboard, attendance marking, session management.
QR scanner interface and reports.
"""

import os
from datetime import date, datetime
from flask import (Blueprint, render_template, redirect, url_for, flash,
                   request, jsonify, send_file)
from flask_login import current_user, login_required
from models import db, Subject, Teacher, Attendance, Student
from services.attendance_service import mark_attendance, AttendanceError
from services.export_service import export_excel, export_pdf
from services.auth_service import log_action
from middleware.access import teacher_required

teacher_bp = Blueprint("teacher", __name__, url_prefix="/teacher")


@teacher_bp.route("/dashboard")
@login_required
@teacher_required
def dashboard():
    """Teacher home page with quick stats."""
    teacher = Teacher.query.filter_by(user_id=current_user.id).first()
    today_count = (
        db.session.query(Attendance)
        .filter_by(teacher_id=teacher.id, date=date.today())
        .count()
    ) if teacher else 0
    subjects = Subject.query.filter_by(is_active=True).all()
    return render_template("teacher/dashboard.html",
                           teacher=teacher, today_count=today_count, subjects=subjects)


@teacher_bp.route("/attendance")
@login_required
@teacher_required
def attendance():
    """Attendance marking page with QR scanner."""
    teacher = Teacher.query.filter_by(user_id=current_user.id).first()
    if not teacher:
        flash("Teacher profile not found.", "danger")
        return redirect(url_for("teacher.dashboard"))

    subjects = Subject.query.filter_by(is_active=True).all()
    subject_id = request.args.get("subject_id", type=int)
    session_active = request.args.get("session", "").lower() == "true"

    marked_today = []
    if subject_id and session_active:
        marked_today = (
            db.session.query(Attendance)
            .filter_by(teacher_id=teacher.id, subject_id=subject_id, date=date.today())
            .join(Student)
            .add_columns(Student.name, Student.student_id)
            .all()
        )

    return render_template("teacher/attendance.html",
                           teacher=teacher, subjects=subjects,
                           subject_id=subject_id, session_active=session_active,
                           marked_today=marked_today)


@teacher_bp.route("/api/mark-attendance", methods=["POST"])
@login_required
@teacher_required
def api_mark_attendance():

    teacher = Teacher.query.filter_by(user_id=current_user.id).first()

    if not teacher:
        return jsonify({
            "success": False,
            "message": "Teacher not found."
        }), 403

    data = request.get_json()

    if not data:
        return jsonify({
            "success": False,
            "message": "No JSON data received."
        }), 400

    qr_token = str(data.get("qr_token", "")).strip()

    try:
        subject_id = int(data.get("subject_id", 0))
    except Exception:
        subject_id = 0

    if not qr_token:
        return jsonify({
            "success": False,
            "message": "QR Token missing."
        }), 400

    if subject_id == 0:
        return jsonify({
            "success": False,
            "message": "Subject not selected."
        }), 400

    try:

        record = mark_attendance(
            qr_token=qr_token,
            subject_id=subject_id,
            teacher_id=teacher.id,
            method="qr_scan",
            ip_address=request.remote_addr
        )

        return jsonify({
            "success": True,
            "message": f"{record.student.name} marked present",
            "student_name": record.student.name,
            "student_id": record.student.student_id
        })

    except AttendanceError as e:

        return jsonify({
            "success": False,
            "message": str(e)
        })

    except Exception as e:

        print("ATTENDANCE ERROR:", e)

        return jsonify({
            "success": False,
            "message": str(e)
        }), 500
@teacher_bp.route("/history")
@login_required
@teacher_required
def history():
    """View past attendance records marked by this teacher."""
    teacher = Teacher.query.filter_by(user_id=current_user.id).first()
    if not teacher:
        flash("Teacher profile not found.", "danger")
        return redirect(url_for("teacher.dashboard"))

    page = request.args.get("page", 1, type=int)
    subject_id = request.args.get("subject_id", type=int)

    q = Attendance.query.filter_by(teacher_id=teacher.id)
    if subject_id:
        q = q.filter_by(subject_id=subject_id)

    records = q.order_by(Attendance.date.desc(), Attendance.time.desc()).paginate(page=page, per_page=30)
    subjects = Subject.query.filter_by(is_active=True).all()
    return render_template("teacher/history.html", records=records,
                           subjects=subjects, subject_id=subject_id)


@teacher_bp.route("/reports")
@login_required
@teacher_required
def reports():
    """Generate reports for a specific subject."""
    teacher = Teacher.query.filter_by(user_id=current_user.id).first()
    subjects = Subject.query.filter_by(is_active=True).all()
    subject_id = request.args.get("subject_id", type=int)

    stats = None
    if subject_id:
        subject = Subject.query.get(subject_id)
        records = (
            Attendance.query
            .filter_by(teacher_id=teacher.id, subject_id=subject_id)
            .order_by(Attendance.date.desc())
            .all()
        )
        if records:
            # Per-student summary
            from collections import defaultdict
            by_student = defaultdict(lambda: {"total": 0, "present": 0})
            for r in records:
                by_student[r.student.id]["total"] += 1
                if r.status == "present":
                    by_student[r.student.id]["present"] += 1
            stats = [
                {
                    "student_id": Student.query.get(sid).student_id,
                    "student_name": Student.query.get(sid).name,
                    "total": data["total"],
                    "present": data["present"],
                    "percentage": round((data["present"] / data["total"]) * 100, 1),
                }
                for sid, data in sorted(by_student.items())
            ]

    return render_template("teacher/reports.html", subjects=subjects,
                           subject_id=subject_id, stats=stats)


@teacher_bp.route("/export/excel")
@login_required
@teacher_required
def export_excel_route():
    """Export teacher's own attendance records to Excel."""
    teacher = Teacher.query.filter_by(user_id=current_user.id).first()
    records = Attendance.query.filter_by(teacher_id=teacher.id).order_by(Attendance.date.desc()).all()
    path = export_excel(records, f"attendance_{teacher.teacher_id}")
    return send_file(path, as_attachment=True, download_name=os.path.basename(path))


@teacher_bp.route("/export/pdf")
@login_required
@teacher_required
def export_pdf_route():
    """Export teacher's attendance records to PDF."""
    teacher = Teacher.query.filter_by(user_id=current_user.id).first()
    records = Attendance.query.filter_by(teacher_id=teacher.id).order_by(Attendance.date.desc()).all()
    path = export_pdf(records, f"Attendance Report - {teacher.name}", f"attendance_{teacher.teacher_id}")
    return send_file(path, as_attachment=True, download_name=os.path.basename(path))
