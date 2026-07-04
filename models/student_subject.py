from .base import db


class StudentSubject(db.Model):
    __tablename__ = "student_subjects"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    student_id = db.Column(
        db.Integer,
        db.ForeignKey("students.id", ondelete="CASCADE"),
        nullable=False
    )

    subject_id = db.Column(
        db.Integer,
        db.ForeignKey("subjects.id", ondelete="CASCADE"),
        nullable=False
    )

    __table_args__ = (
        db.UniqueConstraint(
            "student_id",
            "subject_id",
            name="uq_student_subject"
        ),
    )

    def __repr__(self):
        return f"<StudentSubject student={self.student_id} subject={self.subject_id}>"