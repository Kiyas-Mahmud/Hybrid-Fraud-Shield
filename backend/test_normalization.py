"""
Quick test to verify adaptive normalization is working
"""
import sys
sys.path.insert(0, 'e:/Research/Biin/Fraud_Ditection_Enhance/backend')
from services.fraud_detection import fraud_detection_service
from datetime import datetime, timedelta

# Test: Coffee purchase $4.50 (should be SAFE, 5-25%)
print("\n" + "="*70)
print("TEST: Coffee Purchase $4.50")
print("="*70)

history = []
base_time = datetime.now() - timedelta(days=30)
for i in range(20):
    history.append({
        'amount': 25 * (0.5 + i*0.05),
        'created_at': base_time + timedelta(hours=24*i/20)
    })

txn = {
    'amount': 4.50,
    'user_history': history,
    'is_foreign_transaction': 0,
    'transaction_hour': 12
}

risk, preds = fraud_detection_service.predict(txn)

print(f"\n{'='*70}")
print(f"RESULTS:")
print(f"{'='*70}")
print(f"Final Risk Score: {risk*100:.2f}%")
print(f"Meta-learner raw output: {preds.get('meta_learner', 0)*100:.2f}%")
if 'final_calibrated' in preds:
    print(f"Calibrated output: {preds.get('final_calibrated', 0)*100:.2f}%")

print(f"\nExpected: 5-25% (SAFE)")
print(f"Status: {'PASS ✅' if 0.05 <= risk <= 0.25 else 'FAIL ❌'}")
print(f"{'='*70}\n")
