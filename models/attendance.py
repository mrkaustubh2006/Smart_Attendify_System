"""
models/attendance.py — Attendance record.
Unique constraint on (student_id, subject_id, date) prevents duplicate marking.
"""

from datetime import datetime
from .base import db


class Attendance(db.Model):
    __tablename__ = "attendance"

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey("subjects.id", ondelete="CASCADE"), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey("teachers.id", ondelete="SET NULL"), nullable=True)
    date = db.Column(db.Date, nullable=False, default=datetime.utcnow().date)
    time = db.Column(db.Time, nullable=False, default=datetime.utcnow().time)
    status = db.Column(db.Enum("present", "absent", "late"), nullable=False, default="present")
    method = db.Column(db.Enum("qr_scan", "manual"), nullable=False, default="qr_scan")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Composite unique constraint — one record per student per subject per day
    __table_args__ = (
        db.UniqueConstraint("student_id", "subject_id", "date", name="uq_attendance_per_day"),
        db.Index("ix_attendance_date", "date"),
    )

    def __repr__(self):
        return f"<Attendance student={self.student_id} subject={self.subject_id} date={self.date} status={self.status}>"
