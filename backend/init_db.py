import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.connection import init_db, SessionLocal
from models.user import User, UserRole
from services.auth_service import auth_service

def create_admin_user():
    db = SessionLocal()
    try:
        existing_admin = db.query(User).filter(User.username == "admin").first()
        if not existing_admin:
            admin = User(
                username="admin",
                email="admin@fraudshield.com",
                password_hash=auth_service.get_password_hash("admin123"),
                full_name="System Administrator",
                role=UserRole.SUPER_ADMIN,
                is_active=True
            )
            db.add(admin)
            db.commit()
            print("Admin user created successfully")
            print("Username: admin")
            print("Password: admin123")
        else:
            print("Admin user already exists")
    except Exception as e:
        print(f"Error creating admin user: {str(e)}")
    finally:
        db.close()

if __name__ == "__main__":
    print("Initializing database...")
    init_db()
    print("Database initialized successfully")
    
    print("\nCreating admin user...")
    create_admin_user()
    
    print("\nSetup complete!")
