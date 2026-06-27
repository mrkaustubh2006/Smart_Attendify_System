"""
models/class_model.py
"""

from .base import db

class Class(db.Model):
    __tablename__ = "classes"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

class_name = db.Column(
    db.String(50),
    nullable=False,
    unique=True
)

department = db.Column(
    db.String(100),
    nullable=False
)

academic_year = db.Column(
    db.String(20),
    nullable=True
)

def __repr__(self):
    return f"<Class {self.class_name}>"

