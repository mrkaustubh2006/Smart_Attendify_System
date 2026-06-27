from app import create_app
from models import User

app = create_app()

with app.app_context():


 teachers = User.query.filter_by(role="teacher").all()

for teacher in teachers:
    print("=" * 50)
    print("EMAIL :", teacher.email)
    print("ACTIVE:", teacher.is_active)
    print("HASH  :", teacher.password_hash)

