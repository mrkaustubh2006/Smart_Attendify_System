from services.auth_service import hash_password, check_password

password = "Test12345"

hashed = hash_password(password)

print("HASH:")
print(hashed)

print("\nVERIFY:")
print(check_password(password, hashed))
