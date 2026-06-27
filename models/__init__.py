# models/__init__.py
from .base import db
from .user import User
from .student import Student
from .teacher import Teacher
from .subject import Subject
from .class_model import Class
from .attendance import Attendance
from .audit_log import AuditLog

__all__ = ["db", "User", "Student", "Teacher", "Subject", "Class", "Attendance", "AuditLog"]
