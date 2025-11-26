"""
Check and create test users for the fraud detection system
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.connection import SessionLocal
from models.user import User, UserRole
from services.auth_service import auth_service

def check_and_create_users():
    db = SessionLocal()
    try:
        print("=" * 60)
        print("CHECKING EXISTING USERS")
        print("=" * 60)
        
        users = db.query(User).all()
        print(f"\nFound {len(users)} users in database:\n")
        
        for user in users:
            print(f"Username: {user.username}")
            print(f"Email: {user.email}")
            print(f"Role: {user.role}")
            print(f"Active: {user.is_active}")
            print("-" * 40)
        
        # Check if john_doe exists
        john_doe = db.query(User).filter(User.username == "john_doe").first()
        
        if not john_doe:
            print("\n" + "=" * 60)
            print("CREATING TEST USER: john_doe")
            print("=" * 60)
            
            john_doe = User(
                username="john_doe",
                email="john.doe@example.com",
                password_hash=auth_service.get_password_hash("SecurePass123!"),
                full_name="John Doe",
                phone="+1-555-0123",
                role=UserRole.CUSTOMER,
                is_active=True
            )
            db.add(john_doe)
            db.commit()
            db.refresh(john_doe)
            
            print("\n✅ User created successfully!")
            print(f"Username: john_doe")
            print(f"Password: SecurePass123!")
            print(f"Email: john.doe@example.com")
            print(f"User ID: {john_doe.id}")
        else:
            print("\n✅ john_doe already exists")
            print(f"User ID: {john_doe.id}")
            print(f"Email: {john_doe.email}")
            
            # Update password to ensure it's correct
            print("\n🔄 Updating password to: SecurePass123!")
            john_doe.password_hash = auth_service.get_password_hash("SecurePass123!")
            db.commit()
            print("✅ Password updated!")
        
        # Check if testuser2 exists
        testuser2 = db.query(User).filter(User.username == "testuser2").first()
        
        if not testuser2:
            print("\n" + "=" * 60)
            print("CREATING TEST USER: testuser2")
            print("=" * 60)
            
            testuser2 = User(
                username="testuser2",
                email="test2@example.com",
                password_hash=auth_service.get_password_hash("SecurePass123!"),
                full_name="Test User 2",
                phone="+1-555-0198",
                role=UserRole.CUSTOMER,
                is_active=True
            )
            db.add(testuser2)
            db.commit()
            db.refresh(testuser2)
            
            print("\n✅ User created successfully!")
            print(f"Username: testuser2")
            print(f"Password: SecurePass123!")
            print(f"Email: test2@example.com")
            print(f"User ID: {testuser2.id}")
        else:
            print("\n✅ testuser2 already exists")
            print(f"User ID: {testuser2.id}")
        
        # Check admin user
        admin = db.query(User).filter(User.username == "admin").first()
        if admin:
            print("\n✅ Admin user exists")
            print(f"Username: admin")
            print(f"Password: admin123")
        
        print("\n" + "=" * 60)
        print("FINAL USER LIST")
        print("=" * 60)
        
        users = db.query(User).all()
        print(f"\nTotal users: {len(users)}\n")
        
        for user in users:
            print(f"✓ {user.username} ({user.email}) - {user.role}")
        
        print("\n" + "=" * 60)
        print("TEST CREDENTIALS")
        print("=" * 60)
        print("\nCustomer Login:")
        print("  Username: john_doe")
        print("  Password: SecurePass123!")
        print("\nAlternative Customer:")
        print("  Username: testuser2")
        print("  Password: SecurePass123!")
        print("\nAdmin Login:")
        print("  Username: admin")
        print("  Password: admin123")
        print("\n" + "=" * 60)
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    check_and_create_users()
