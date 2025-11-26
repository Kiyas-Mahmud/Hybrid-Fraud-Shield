"""
Prepare john_doe account for competition demo
- Clean transaction history
- Seed clean demo transactions
"""
from datetime import datetime, timedelta
from database.connection import SessionLocal
from models.user import User
from models.transaction import Transaction, TransactionStatus, RiskClassification, TransactionType
from models.notification import Notification

def prepare_demo():
    db = SessionLocal()
    
    try:
        # Get john_doe
        user = db.query(User).filter(User.username == "john_doe").first()
        if not user:
            print("❌ john_doe not found!")
            return
        
        print(f"✅ Found user: {user.username} (ID: {user.id})")
        
        # Check current transactions
        current_txns = db.query(Transaction).filter(Transaction.user_id == user.id).all()
        print(f"\n📊 Current transactions: {len(current_txns)}")
        
        # Delete notifications first (foreign key constraint)
        print("\n🗑️  Deleting notifications...")
        notifications = db.query(Notification).filter(Notification.user_id == user.id).all()
        for notif in notifications:
            db.delete(notif)
        db.commit()
        print(f"✅ Deleted {len(notifications)} notifications")
        
        # Delete all transactions
        print("\n🗑️  Deleting all transactions...")
        for txn in current_txns:
            db.delete(txn)
        db.commit()
        print(f"✅ Deleted {len(current_txns)} transactions")
        
        # Seed clean demo data
        print("\n🌱 Seeding demo transactions...")
        
        demo_transactions = [
            # 1. Previous Starbucks (builds merchant trust)
            {
                "amount": 4.50,
                "merchant_name": "Starbucks",
                "transaction_type": TransactionType.IN_STORE,
                "description": "Morning coffee",
                "classification": RiskClassification.SAFE,
                "status": TransactionStatus.APPROVED,
                "risk_score": 0.08,
                "days_ago": 7
            },
            # 2. McDonald's lunch
            {
                "amount": 12.99,
                "merchant_name": "McDonald's",
                "transaction_type": TransactionType.IN_STORE,
                "description": "Lunch meal",
                "classification": RiskClassification.SAFE,
                "status": TransactionStatus.APPROVED,
                "risk_score": 0.09,
                "days_ago": 5
            },
            # 3. Gas station
            {
                "amount": 45.00,
                "merchant_name": "Shell Gas Station",
                "transaction_type": TransactionType.IN_STORE,
                "description": "Fuel purchase",
                "classification": RiskClassification.SAFE,
                "status": TransactionStatus.APPROVED,
                "risk_score": 0.12,
                "days_ago": 3
            },
            # 4. Walmart groceries
            {
                "amount": 78.50,
                "merchant_name": "Walmart",
                "transaction_type": TransactionType.IN_STORE,
                "description": "Weekly groceries",
                "classification": RiskClassification.SAFE,
                "status": TransactionStatus.APPROVED,
                "risk_score": 0.15,
                "days_ago": 2
            }
        ]
        
        for txn_data in demo_transactions:
            days_ago = txn_data.pop('days_ago')
            created_at = datetime.utcnow() - timedelta(days=days_ago)
            
            txn = Transaction(
                user_id=user.id,
                **txn_data,
                location="",
                device_info="",
                ip_address="127.0.0.1",
                created_at=created_at
            )
            db.add(txn)
            print(f"  ✅ Added: ${txn.amount} at {txn.merchant_name} ({days_ago} days ago)")
        
        db.commit()
        
        print("\n✅ Demo preparation complete!")
        print("\n📋 Summary:")
        print(f"   User: john_doe")
        print(f"   Clean history: 4 approved SAFE transactions")
        print(f"   Ready for demo: SAFE → SUSPICIOUS → FRAUD")
        print("\n🎯 Demo transactions to use:")
        print("   1. SAFE: $4.50 at Starbucks (familiar merchant)")
        print("   2. SUSPICIOUS: $450 at Best Buy")
        print("   3. FRAUD: $5000 at Luxury Goods Store")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    prepare_demo()
