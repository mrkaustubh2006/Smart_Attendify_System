"""
models/user.py — Central User model used for Flask-Login.
Role field drives access control: 'admin' | 'teacher' | 'student'.
"""

from datetime import datetime
from flask_login import UserMixin
from .base import db


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.Enum("admin", "teacher", "student"), nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    audit_logs = db.relationship("AuditLog", backref="user", lazy="dynamic")

    def __repr__(self):
        return f"<User {self.email} [{self.role}]>"

    # --- Role helpers ---
    @property
    def is_admin(self):
        return self.role == "admin"

    @property
    def is_teacher(self):
        return self.role == "teacher"

    @property
    def is_student(self):
        return self.role == "student"
