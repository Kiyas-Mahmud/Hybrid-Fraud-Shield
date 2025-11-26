import sys
sys.path.insert(0, 'e:/Research/Biin/Fraud_Ditection_Enhance/backend')
import importlib
for mod in list(sys.modules.keys()):
    if 'services' in mod:
        del sys.modules[mod]

from services.fraud_detection import fraud_detection_service
from datetime import datetime, timedelta

# Velocity attack test
history = []
base_time = datetime.now() - timedelta(days=1)
for i in range(50):
    history.append({
        'amount': 42.5 * (0.5 + i*0.02),
        'created_at': base_time + timedelta(hours=24*i/50)
    })

txn = {'amount': 299, 'user_history': history, 'is_foreign_transaction': 0, 'transaction_hour': 12}
risk, preds = fraud_detection_service.predict(txn)

print(f'\nVelocity Test Result: {risk*100:.2f}%')
if 'risk_boosting' in preds:
    boost = preds['risk_boosting']
    print(f'Base score: {boost.get("base_score", 0)*100:.2f}%')
    print(f'Boost applied: {boost.get("applied", False)}')
    print(f'Boost amount: {boost.get("boost_amount", 0)*100:.2f}%')
    print(f'Reason: {boost.get("reason", "None")}')
    print(f'Factors: {boost.get("factors", {})}')
