"""
models/student.py — Student profile linked to a User account.
qr_token is a cryptographically random hex string embedded in the QR code;
it never leaks PII and is verified server-side before marking attendance.
"""

from datetime import datetime
import secrets
from .base import db


class Student(db.Model):
    __tablename__ = "students"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    student_id = db.Column(db.String(20), unique=True, nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    class_name = db.Column(db.String(50), nullable=False)
    department = db.Column(db.String(100), nullable=True)
    roll_no = db.Column(db.String(20), nullable=False)
    # Static, opaque token — the only data embedded in the QR code
    qr_token = db.Column(db.String(64), unique=True, nullable=False, default=lambda: secrets.token_hex(32))
    qr_image_path = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    user = db.relationship("User", backref=db.backref("student_profile", uselist=False))
    attendance_records = db.relationship("Attendance", backref="student", lazy="dynamic", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Student {self.student_id} - {self.name}>"

    def attendance_percentage(self, subject_id=None):
        """Calculate overall or per-subject attendance percentage."""
        query = self.attendance_records
        if subject_id:
            query = query.filter_by(subject_id=subject_id)
        total = query.count()
        if total == 0:
            return 0.0
        present = query.filter_by(status="present").count()
        return round((present / total) * 100, 2)
