"""
services/attendance_service.py — Core attendance business logic.
All attendance marking goes through this module so rules are enforced centrally.
"""

from datetime import date, datetime
from sqlalchemy.exc import IntegrityError
from models import db, Attendance, Student, Subject, Teacher, AuditLog


class AttendanceError(Exception):
    """Raised when attendance cannot be marked due to a business rule violation."""


def mark_attendance(qr_token: str, subject_id: int, teacher_id: int,
                    method: str = "qr_scan", ip_address: str = None) -> Attendance:
    """
    Verify a QR token, resolve the student, and create an attendance record.

    Raises AttendanceError on:
      - Invalid / unknown QR token
      - Subject not found
      - Duplicate attendance for today
    """
    # 1. Resolve student by token
    student = Student.query.filter_by(qr_token=qr_token).first()
    if not student:
        raise AttendanceError("Invalid QR code — student not found.")

    # 2. Verify subject exists
    subject = Subject.query.get(subject_id)
    if not subject or not subject.is_active:
        raise AttendanceError("Subject not found or inactive.")

    today = date.today()

    # 3. Duplicate check (DB unique constraint is the last line of defence)
    existing = Attendance.query.filter_by(
        student_id=student.id,
        subject_id=subject_id,
        date=today
    ).first()
    if existing:
        raise AttendanceError(
            f"Attendance for {student.name} in {subject.subject_name} already recorded today."
        )

    # 4. Create record
    record = Attendance(
        student_id=student.id,
        subject_id=subject_id,
        teacher_id=teacher_id,
        date=today,
        time=datetime.utcnow().time(),
        status="present",
        method=method,
    )
    db.session.add(record)

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        raise AttendanceError("Duplicate attendance detected (concurrent request).")

    # 5. Audit
    log = AuditLog(
        action="attendance_marked",
        target_type="Attendance",
        target_id=record.id,
        ip_address=ip_address,
        details=f"student={student.student_id} subject={subject.subject_code} method={method}"
    )
    db.session.add(log)
    db.session.commit()

    return record


def get_daily_report(target_date: date, subject_id: int = None, class_name: str = None):
    """Return attendance records for a given date, optionally filtered."""
    q = Attendance.query.filter_by(date=target_date)
    if subject_id:
        q = q.filter_by(subject_id=subject_id)
    if class_name:
        q = q.join(Student).filter(Student.class_name == class_name)
    return q.all()


def get_student_summary(student_id: int):
    """
    Return per-subject attendance stats for a student.
    [{ subject, total, present, percentage }, ...]
    """
    from models import Subject
    subjects = Subject.query.filter_by(is_active=True).all()
    result = []
    for subj in subjects:
        total = Attendance.query.filter_by(student_id=student_id, subject_id=subj.id).count()
        if total == 0:
            continue
        present = Attendance.query.filter_by(student_id=student_id, subject_id=subj.id, status="present").count()
        result.append({
            "subject": subj,
            "total": total,
            "present": present,
            "percentage": round((present / total) * 100, 1) if total else 0,
        })
    return result
