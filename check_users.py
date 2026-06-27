from app import create_app
from models import User

app = create_app()

with app.app_context():


 users = User.query.all()

print("\nALL USERS")
print("=" * 50)

for user in users:
    print(
        f"ID={user.id} | EMAIL={user.email} | ROLE={user.role}"
    )

