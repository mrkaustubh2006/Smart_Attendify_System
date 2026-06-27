"""
models/audit_log.py — Immutable audit trail for security-sensitive actions.
"""

from datetime import datetime
from .base import db


class AuditLog(db.Model):
    __tablename__ = "audit_logs"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    action = db.Column(db.String(255), nullable=False)
    target_type = db.Column(db.String(50), nullable=True)   # e.g. "Student", "Attendance"
    target_id = db.Column(db.Integer, nullable=True)
    ip_address = db.Column(db.String(45), nullable=True)    # Supports IPv6
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    details = db.Column(db.Text, nullable=True)             # JSON extra context

    def __repr__(self):
        return f"<AuditLog {self.action} by user={self.user_id} at {self.timestamp}>"
