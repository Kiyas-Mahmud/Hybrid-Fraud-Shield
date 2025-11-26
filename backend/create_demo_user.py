"""
Create a fresh demo user for competition presentation
"""
from database.connection import SessionLocal
from models.user import User
from utils.security import hash_password

def create_demo_user():
    db = SessionLocal()
    
    # Check if demo user exists
    existing_user = db.query(User).filter(User.username == "demo_user").first()
    if existing_user:
        print(f"Demo user already exists (ID: {existing_user.id})")
        print(f"Username: demo_user")
        print(f"Password: Demo2025!")
        db.close()
        return
    
    # Create fresh demo user
    demo_user = User(
        username="demo_user",
        email="demo@fraudshield.com",
        password_hash=hash_password("Demo2025!"),
        role="user",
        full_name="Demo User"
    )
    
    db.add(demo_user)
    db.commit()
    db.refresh(demo_user)
    
    print(f"✅ Demo user created successfully!")
    print(f"   ID: {demo_user.id}")
    print(f"   Username: demo_user")
    print(f"   Password: Demo2025!")
    print(f"   Email: demo@fraudshield.com")
    
    db.close()

if __name__ == "__main__":
    create_demo_user()
