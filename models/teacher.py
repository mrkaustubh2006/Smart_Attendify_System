"""
models/teacher.py — Teacher profile linked to a User account.
"""

from datetime import datetime
from .base import db


class Teacher(db.Model):
    __tablename__ = "teachers"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    teacher_id = db.Column(db.String(20), unique=True, nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    department = db.Column(db.String(100), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    user = db.relationship("User", backref=db.backref("teacher_profile", uselist=False))
    attendance_sessions = db.relationship("Attendance", backref="teacher", lazy="dynamic")

    def __repr__(self):
        return f"<Teacher {self.teacher_id} - {self.name}>"
