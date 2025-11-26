"""
Debug script to test transaction classification
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.fraud_detection import fraud_detection_service
from services.risk_classifier import RiskClassifier
from datetime import datetime

# Test the exact $4.50 Starbucks transaction
test_features = {
    "amount": 4.50,
    "transaction_hour": datetime.now().hour,
    "transaction_day": datetime.now().day,
    "transaction_month": datetime.now().month,
    "merchant_name": "Starbucks",
    "transaction_type": "IN_STORE",
    "location": "New York, NY",
    "device_info": "Chrome on Windows",
    "ip_address": "192.168.0.102",
    "is_foreign_transaction": 0,
    "distance_from_home": 100,
    "card_number_hash": "default",
    "user_history": []
}

print("="*60)
print("DEBUGGING $4.50 STARBUCKS TRANSACTION")
print("="*60)

print("\nInput Features:")
for key, value in test_features.items():
    print(f"  {key}: {value}")

# Get prediction from ML models
risk_score, model_predictions = fraud_detection_service.predict(test_features)

print(f"\n{'='*60}")
print("MODEL PREDICTIONS")
print("="*60)
print(f"\nFinal Risk Score: {risk_score:.6f}")
print(f"\nIndividual Model Predictions:")
for model_name, prediction in sorted(model_predictions.items()):
    print(f"  {model_name}: {prediction:.6f}")

# Test classification logic
classification_no_amount = RiskClassifier.classify(risk_score, amount=None)
classification_with_amount = RiskClassifier.classify(risk_score, amount=4.50)

print(f"\n{'='*60}")
print("CLASSIFICATION RESULTS")
print("="*60)
print(f"\nWithout amount parameter: {classification_no_amount}")
print(f"With amount=$4.50: {classification_with_amount}")

# Show thresholds
print(f"\n{'='*60}")
print("THRESHOLD ANALYSIS")
print("="*60)
print(f"\nSAFE threshold: < {RiskClassifier.SAFE_THRESHOLD}")
print(f"SUSPICIOUS threshold: {RiskClassifier.SAFE_THRESHOLD} to {RiskClassifier.SUSPICIOUS_THRESHOLD}")
print(f"FRAUD threshold: >= {RiskClassifier.SUSPICIOUS_THRESHOLD}")
print(f"\nAmount thresholds:")
print(f"  Small amounts (< $150): Usually SAFE if risk < 0.3")
print(f"  Medium amounts ($150-$2000): May be SUSPICIOUS")
print(f"  Large amounts (> $3000): Usually FRAUD")

print(f"\n{'='*60}")
print("DIAGNOSIS")
print("="*60)

if risk_score >= RiskClassifier.SAFE_THRESHOLD:
    print(f"❌ PROBLEM: Risk score {risk_score:.4f} is >= 0.3 (SAFE threshold)")
    print(f"   This means ML models think this is suspicious!")
    print(f"\n   Possible causes:")
    print(f"   1. Models were trained on different data distribution")
    print(f"   2. New user with no history (model sees as risky)")
    print(f"   3. Feature engineering issues")
    print(f"   4. Models need retraining with real transaction data")
else:
    print(f"✅ Risk score {risk_score:.4f} is < 0.3 (SAFE threshold)")
    print(f"   Classification should be SAFE")
    
    if classification_with_amount.value != "SAFE":
        print(f"\n❌ But classifier returned: {classification_with_amount.value}")
        print(f"   This is a logic error in risk_classifier.py!")

print("\n" + "="*60)
