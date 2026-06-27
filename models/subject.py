"""
models/subject.py — Academic subject / course.
"""

from .base import db


class Subject(db.Model):
    __tablename__ = "subjects"

    id = db.Column(db.Integer, primary_key=True)
    subject_name = db.Column(db.String(100), nullable=False)
    subject_code = db.Column(db.String(20), unique=True, nullable=False, index=True)
    class_name = db.Column(db.String(50), nullable=True)
    department = db.Column(db.String(100), nullable=True)
    is_active = db.Column(db.Boolean, default=True)

    attendance_records = db.relationship("Attendance", backref="subject", lazy="dynamic")

    def __repr__(self):
        return f"<Subject {self.subject_code} - {self.subject_name}>"
