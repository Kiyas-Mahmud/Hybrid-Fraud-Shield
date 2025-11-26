"""
Real-world scenario: Student with typical $20-50 spending suddenly has $300 transaction
This tests behavioral anomaly detection for amount spikes
"""
import sys
import os
from datetime import datetime, timedelta

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.fraud_detection import FraudDetectionService

# Initialize service
print("="*80)
print("🎓 STUDENT FRAUD DETECTION SCENARIO")
print("="*80)
print()

fraud_detection_service = FraudDetectionService()

# Create realistic student spending pattern
now = datetime.now()
student_data = {
    'amount': 300.00,  # 🚨 SUSPICIOUS - way higher than normal
    'merchant_category': 'shopping',
    'transaction_hour': 23,  # Late night (slightly suspicious)
    'is_foreign_transaction': 0,  # Domestic
    'user_id': 'student_123',
    'user_history': [
        # Regular small purchases over past 3 months
        {'amount': 25.50, 'created_at': now - timedelta(days=90)},  # Coffee shop
        {'amount': 18.00, 'created_at': now - timedelta(days=85)},  # Fast food
        {'amount': 42.00, 'created_at': now - timedelta(days=80)},  # Groceries
        {'amount': 30.00, 'created_at': now - timedelta(days=75)},  # Coffee
        {'amount': 22.50, 'created_at': now - timedelta(days=70)},  # Fast food
        {'amount': 35.00, 'created_at': now - timedelta(days=65)},  # Books
        {'amount': 28.00, 'created_at': now - timedelta(days=60)},  # Coffee
        {'amount': 45.00, 'created_at': now - timedelta(days=55)},  # Groceries
        {'amount': 20.00, 'created_at': now - timedelta(days=50)},  # Fast food
        {'amount': 38.50, 'created_at': now - timedelta(days=45)},  # Coffee
        {'amount': 24.00, 'created_at': now - timedelta(days=40)},  # Fast food
        {'amount': 32.00, 'created_at': now - timedelta(days=35)},  # Groceries
        {'amount': 27.50, 'created_at': now - timedelta(days=30)},  # Coffee
        {'amount': 41.00, 'created_at': now - timedelta(days=25)},  # Groceries
        {'amount': 19.00, 'created_at': now - timedelta(days=20)},  # Fast food
        {'amount': 33.00, 'created_at': now - timedelta(days=15)},  # Coffee
        {'amount': 29.50, 'created_at': now - timedelta(days=10)},  # Fast food
        {'amount': 36.00, 'created_at': now - timedelta(days=7)},   # Groceries
        {'amount': 23.00, 'created_at': now - timedelta(days=4)},   # Coffee
        {'amount': 40.00, 'created_at': now - timedelta(days=2)},   # Groceries
    ]
}

# Calculate user patterns
user_avg = sum(t['amount'] for t in student_data['user_history']) / len(student_data['user_history'])
user_min = min(t['amount'] for t in student_data['user_history'])
user_max = max(t['amount'] for t in student_data['user_history'])
amount_ratio = student_data['amount'] / user_avg

print("👤 USER PROFILE:")
print(f"   Type: Student")
print(f"   History: {len(student_data['user_history'])} transactions over 3 months")
print(f"   Typical spending: ${user_min:.2f} - ${user_max:.2f}")
print(f"   Average: ${user_avg:.2f}/transaction")
print()

print("🚨 SUSPICIOUS TRANSACTION:")
print(f"   Amount: ${student_data['amount']:.2f}")
print(f"   Time: 11:00 PM (late night)")
print(f"   Amount Ratio: {amount_ratio:.1f}x normal spending!")
print(f"   Previous max: ${user_max:.2f}")
print(f"   This transaction: ${student_data['amount']:.2f} ({(student_data['amount']/user_max):.1f}x previous max!)")
print()

print("❓ QUESTION: Is this the student, or someone who stole their card?")
print()
print("="*80)
print()

# Predict
risk_score, predictions = fraud_detection_service.predict(student_data)

print(f"\n📊 FRAUD DETECTION RESULTS:")
print(f"   Final Risk Score: {risk_score*100:.2f}%")

# Show boost details
if 'risk_boosting' in predictions:
    boost_info = predictions['risk_boosting']
    if boost_info['applied']:
        print(f"\n   🚨 RISK BOOSTING APPLIED:")
        print(f"      Base Score: {boost_info['base_score']*100:.2f}%")
        print(f"      Boosted Score: {boost_info['final_score']*100:.2f}%")
        print(f"      Total Boost: +{boost_info['boost_amount']*100:.2f}%")
        print(f"      Reason: {boost_info['reason']}")

print(f"\n   🎯 DECISION:")
if risk_score < 0.30:
    print(f"      ✅ APPROVE - Low risk ({risk_score*100:.0f}%)")
elif risk_score < 0.50:
    print(f"      ⚠️  REVIEW - Medium risk ({risk_score*100:.0f}%) - Request 2FA/SMS verification")
elif risk_score < 0.70:
    print(f"      🚨 BLOCK & VERIFY - High risk ({risk_score*100:.0f}%) - Call customer to confirm")
else:
    print(f"      ❌ BLOCK - Very high risk ({risk_score*100:.0f}%) - Likely fraud!")

print()
print("="*80)
print()
print("💡 BEHAVIORAL ANALYSIS:")
print(f"   • Student typically spends ${user_avg:.2f}")
print(f"   • This transaction is {amount_ratio:.1f}x higher than normal")
print(f"   • Late night transaction (11 PM) adds suspicion")
print(f"   • Could be: Laptop purchase, emergency, or STOLEN CARD")
print(f"   • Action: System flagged for {['APPROVAL', 'REVIEW', 'VERIFICATION', 'BLOCK'][min(3, int(risk_score*4))]}")
print()
