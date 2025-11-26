import sys
sys.path.insert(0, 'e:\\Research\\Biin\\Fraud_Ditection_Enhance\\backend')

from database.connection import get_db
from models.user import User

db = next(get_db())
users = db.query(User).all()

print("\n=== EXISTING USERS ===")
for user in users:
    print(f"ID: {user.id}")
    print(f"Username: {user.username}")
    print(f"Email: {user.email}")
    print(f"Full Name: {user.full_name}")
    print(f"Role: {user.role}")
    print(f"Active: {user.is_active}")
    print(f"Blocked: {user.is_blocked}")
    print("-" * 40)

print(f"\nTotal users: {len(users)}")
