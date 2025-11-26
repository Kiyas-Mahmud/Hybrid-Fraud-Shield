"""
Test foreign transaction with $500 (smaller amount)
Check if risk boosting works appropriately for lower-value foreign transactions
"""
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.fraud_detection import FraudDetectionService

# Initialize service
print("Initializing Fraud Detection Service...")
fraud_detection_service = FraudDetectionService()

# TEST: Foreign transaction with $500 (below $1000 threshold)
print("\n" + "="*80)
print("TEST: Foreign Transaction - $500 USD")
print("="*80)
print("User Profile: 10 past transactions, avg $100, foreign purchase")
print()

from datetime import datetime, timedelta

# Create realistic timestamps (recent transactions)
now = datetime.now()
foreign_500_data = {
    'amount': 500.00,
    'merchant_category': 'shopping',
    'transaction_hour': 14,
    'is_foreign_transaction': 1,  # 🚨 FOREIGN (correct key name)
    'user_id': 'user_foreign_500',
    'user_history': [
        {'amount': 50, 'created_at': now - timedelta(days=30)},
        {'amount': 75, 'created_at': now - timedelta(days=25)},
        {'amount': 120, 'created_at': now - timedelta(days=20)},
        {'amount': 90, 'created_at': now - timedelta(days=18)},
        {'amount': 110, 'created_at': now - timedelta(days=15)},
        {'amount': 85, 'created_at': now - timedelta(days=12)},
        {'amount': 95, 'created_at': now - timedelta(days=10)},
        {'amount': 130, 'created_at': now - timedelta(days=7)},
        {'amount': 105, 'created_at': now - timedelta(days=5)},
        {'amount': 140, 'created_at': now - timedelta(days=2)},
    ]
}

print(f"🔍 Testing: Foreign Transaction $500")
print(f"   Amount: ${foreign_500_data['amount']}")
print(f"   Is Foreign: {foreign_500_data['is_foreign_transaction']}")
print(f"   History: {len(foreign_500_data['user_history'])} past transactions")
print(f"   User Average: ${sum(t['amount'] for t in foreign_500_data['user_history']) / len(foreign_500_data['user_history']):.2f}")
print(f"\n   📌 BEHAVIORAL ANOMALY:")
print(f"      • User normally spends: $50-$140 (avg $100)")
print(f"      • This transaction: $500 (5x spike!)")
print(f"      • User NEVER transacted foreign before")
print(f"      • This is SUSPICIOUS behavior!")
print()

# Predict
risk_score, predictions = fraud_detection_service.predict(foreign_500_data)

# Calculate amount ratio
user_avg = sum(t['amount'] for t in foreign_500_data['user_history']) / len(foreign_500_data['user_history'])
amount_ratio = foreign_500_data['amount'] / user_avg

print(f"\n📊 RESULTS:")
print(f"   Final Risk Score: {risk_score*100:.2f}%")
print(f"   Amount Ratio: {amount_ratio:.1f}x user average")

# Show boost details if present
if 'risk_boosting' in predictions:
    boost_info = predictions['risk_boosting']
    print(f"\n   Risk Boosting Applied: {boost_info['applied']}")
    if boost_info['applied']:
        print(f"      Base Score: {boost_info['base_score']*100:.2f}%")
        print(f"      Total Boost: +{boost_info['boost_amount']*100:.2f}%")
        print(f"      Reason: {boost_info['reason']}")
        print(f"      Factors:")
        for factor, boost_val in boost_info['factors'].items():
            if boost_val > 0:
                print(f"        • {factor}: +{boost_val*100:.1f}%")

# Expected behavior
print(f"\n   📌 Expected Behavior:")
print(f"      • Foreign transaction: YES (should get some boost)")
print(f"      • Amount $500: BELOW $1K threshold (may get 0% foreign boost)")
print(f"      • Amount spike 5x: Should trigger amount spike boost (+10%)")
print(f"      • Total expected risk: 30-60% (foreign flag + moderate amount)")

# Comparison with larger amounts
print(f"\n   💡 For Comparison:")
print(f"      • $500 foreign: {risk_score*100:.2f}%")
print(f"      • $1,000 foreign: Would get +15% foreign boost")
print(f"      • $5,000 foreign: Would get +25% foreign boost")
print(f"      • $10,000 foreign: Would get +35% foreign boost")

print("\n" + "="*80)
