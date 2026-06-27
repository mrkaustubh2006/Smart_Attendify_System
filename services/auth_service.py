"""
services/auth_service.py — Password hashing and audit helpers.
"""

from flask_bcrypt import Bcrypt
from models import db, AuditLog

bcrypt = Bcrypt()


def hash_password(plain: str) -> str:
    return bcrypt.generate_password_hash(plain).decode("utf-8")


def check_password(plain: str, hashed: str) -> bool:
    return bcrypt.check_password_hash(hashed, plain)


def log_action(user_id, action, target_type=None, target_id=None,
               ip_address=None, details=None):
    """Write an AuditLog entry. Call from route handlers after DB commits."""
    entry = AuditLog(
        user_id=user_id,
        action=action,
        target_type=target_type,
        target_id=target_id,
        ip_address=ip_address,
        details=details,
    )
    db.session.add(entry)
    db.session.commit()
