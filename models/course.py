from .base import db

class Course(db.Model):
    __tablename__ = "courses"



id = db.Column(db.Integer, primary_key=True)

course_name = db.Column(
    db.String(100),
    nullable=False
)

course_code = db.Column(
    db.String(20),
    unique=True,
    nullable=False
)

class_id = db.Column(
    db.Integer,
    db.ForeignKey("classes.id"),
    nullable=False
)

def __repr__(self):
    return f"<Course {self.course_name}>"
