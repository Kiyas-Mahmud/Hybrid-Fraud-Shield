from app.database import SessionLocal
from app.models import Transaction, User
from datetime import datetime

db = SessionLocal()

# Find john_doe
user = db.query(User).filter(User.username == 'john_doe').first()

if user:
    print(f"User: {user.username} (ID: {user.id})")
    print(f"Email: {user.email}")
    print("=" * 80)
    
    # Get all transactions
    txs = db.query(Transaction).filter(Transaction.user_id == user.id).order_by(Transaction.created_at).all()
    
    print(f"\nTotal Transactions: {len(txs)}")
    print("\nTransaction History:")
    print("-" * 80)
    
    for i, tx in enumerate(txs, 1):
        time = tx.created_at.strftime("%Y-%m-%d %I:%M %p") if tx.created_at else "N/A"
        print(f"\n{i}. Transaction #{tx.id}")
        print(f"   Amount: ${tx.amount}")
        print(f"   Merchant: {tx.merchant_name}")
        print(f"   Time: {time}")
        print(f"   Device: {tx.device_info or 'N/A'}")
        print(f"   Location: {tx.location or 'N/A'}")
        print(f"   Classification: {tx.classification}")
        print(f"   Risk Score: {tx.risk_score:.4f}")
        print(f"   Status: {tx.status}")
else:
    print("User 'john_doe' not found in database")

db.close()
