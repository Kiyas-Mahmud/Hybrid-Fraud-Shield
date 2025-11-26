"""
Test the new feature engineering approach with real user data (NO TEMPLATES)
This test validates that models produce realistic risk scores when given actual transaction data
"""
import sys
sys.path.insert(0, 'E:/Research/Biin/Fraud_Ditection_Enhance/backend')

from datetime import datetime, timedelta
from services.fraud_detection import fraud_detection_service

def print_header(text):
    print(f"\n{'='*80}")
    print(f"  {text}")
    print(f"{'='*80}")

def test_scenario(name, transaction_data, expected_risk_range):
    """Test a transaction scenario and validate risk score"""
    print(f"\n🔍 Testing: {name}")
    print(f"   Amount: ${transaction_data['amount']:.2f}")
    print(f"   History: {len(transaction_data.get('user_history', []))} past transactions")
    print(f"   Expected Risk: {expected_risk_range}")
    print()
    
    # Predict
    risk_score, predictions = fraud_detection_service.predict(transaction_data)
    
    # Print results
    print(f"\n📊 RESULTS:")
    print(f"   Final Risk Score: {risk_score*100:.2f}%")
    
    # Show risk boost details if present
    if 'boost_details' in predictions:
        boost_info = predictions['boost_details']
        if boost_info['reasons']:
            print(f"\n   🚨 RISK BOOST APPLIED:")
            print(f"      Base Score: {boost_info['base_score']*100:.2f}%")
            print(f"      Total Boost: +{boost_info['total_boost']*100:.2f}%")
            print(f"      Reasons: {', '.join(boost_info['reasons'])}")
    
    # Show individual model predictions
    print(f"\n   Individual Model Predictions:")
    for model_name, pred in predictions.items():
        if model_name not in ['meta_learner', 'final_calibrated', 'boost_details']:
            if isinstance(pred, (int, float)):
                print(f"      {model_name}: {pred*100:.2f}%" if pred <= 1.0 else f"      {model_name}: {pred:.4f}")
    
    if 'meta_learner' in predictions:
        print(f"\n   Meta-Learner: {predictions['meta_learner']*100:.2f}%")
    
    # Validation
    min_risk, max_risk = expected_risk_range
    if min_risk <= risk_score <= max_risk:
        print(f"\n   ✅ PASS - Risk score within expected range ({min_risk*100:.0f}%-{max_risk*100:.0f}%)")
        return True
    else:
        print(f"\n   ❌ FAIL - Risk score outside expected range ({min_risk*100:.0f}%-{max_risk*100:.0f}%)")
        return False

def create_user_history(num_txns, avg_amount, time_gap_hours=24):
    """Create synthetic user transaction history"""
    history = []
    now = datetime.now()
    
    for i in range(num_txns):
        history.append({
            'amount': avg_amount * (0.8 + 0.4 * (i % 3) / 2),  # Varying amounts
            'created_at': now - timedelta(hours=time_gap_hours * (num_txns - i)),
            'merchant_name': f'Merchant_{i % 5}',
            'is_fraud': False
        })
    
    return history

print_header("REAL FEATURE ENGINEERING TEST - NO TEMPLATES")
print("Testing if models produce realistic risk scores from actual user data")

# ==================== TEST 1: Regular User - Coffee Purchase ====================
print_header("TEST 1: Regular User - Coffee Purchase ($4.50)")
print("User Profile: 20 past transactions, avg $25, buys coffee regularly")

coffee_data = {
    'amount': 4.50,
    'transaction_hour': 8,  # Morning
    'is_foreign_transaction': 0,
    'location': 'New York, USA',
    'device_info': 'iPhone 14',
    'ip_address': '192.168.1.1',
    'card_number_hash': 'user123_card',
    'user_history': create_user_history(num_txns=20, avg_amount=25, time_gap_hours=48)
}

test1_pass = test_scenario(
    "Regular Coffee Purchase",
    coffee_data,
    expected_risk_range=(0.05, 0.25)  # Should be 5-25% risk (SAFE)
)

# ==================== TEST 2: Moderate Purchase - Laptop ====================
print_header("TEST 2: Moderate User - Laptop Purchase ($1,899)")
print("User Profile: 15 past transactions, avg $100, now buying expensive item")

laptop_data = {
    'amount': 1899.00,
    'transaction_hour': 14,  # Afternoon
    'is_foreign_transaction': 0,
    'location': 'Los Angeles, USA',
    'device_info': 'Chrome on Windows',
    'ip_address': '10.0.0.1',
    'card_number_hash': 'user456_card',
    'user_history': create_user_history(num_txns=15, avg_amount=100, time_gap_hours=72)
}

test2_pass = test_scenario(
    "Laptop Purchase (Amount Spike)",
    laptop_data,
    expected_risk_range=(0.30, 0.70)  # Should be 30-70% risk (SUSPICIOUS)
)

# ==================== TEST 3: High Risk - Foreign + Large Amount ====================
print_header("TEST 3: High Risk - Foreign Transaction ($9,999)")
print("User Profile: 10 past transactions, avg $200, sudden large foreign purchase")

fraud_data = {
    'amount': 9999.00,
    'transaction_hour': 3,  # Late night
    'is_foreign_transaction': 1,
    'location': 'Dubai, UAE',
    'device_info': 'Unknown Device',
    'ip_address': '185.220.101.1',
    'card_number_hash': 'user789_card',
    'user_history': create_user_history(num_txns=10, avg_amount=200, time_gap_hours=120)
}

test3_pass = test_scenario(
    "Large Foreign Purchase",
    fraud_data,
    expected_risk_range=(0.65, 0.98)  # Should be 65-98% risk (FRAUD)
)

# ==================== TEST 4: New User - First Purchase ====================
print_header("TEST 4: New User - First Purchase ($50)")
print("User Profile: NO history, first transaction")

new_user_data = {
    'amount': 50.00,
    'transaction_hour': 12,
    'is_foreign_transaction': 0,
    'location': 'Chicago, USA',
    'device_info': 'Safari on Mac',
    'ip_address': '192.168.0.1',
    'card_number_hash': 'newuser_card',
    'user_history': []  # No history
}

test4_pass = test_scenario(
    "New User First Purchase",
    new_user_data,
    expected_risk_range=(0.15, 0.50)  # Should be 15-50% risk (SUSPICIOUS - no history)
)

# ==================== TEST 5: Velocity Attack ====================
print_header("TEST 5: Velocity Attack - Multiple Rapid Transactions")
print("User Profile: 50 transactions in last 24 hours (abnormal)")

# Create rapid transaction history
rapid_history = []
now = datetime.now()
for i in range(50):
    rapid_history.append({
        'amount': 20 + (i % 10) * 5,
        'created_at': now - timedelta(minutes=30 * (50 - i)),  # Every 30 minutes
        'merchant_name': f'Merchant_{i % 10}',
        'is_fraud': False
    })

velocity_data = {
    'amount': 299.00,
    'transaction_hour': 15,
    'is_foreign_transaction': 0,
    'location': 'Miami, USA',
    'device_info': 'Android Phone',
    'ip_address': '172.16.0.1',
    'card_number_hash': 'velocity_user_card',
    'user_history': rapid_history
}

test5_pass = test_scenario(
    "Velocity Attack (50 txns in 24h)",
    velocity_data,
    expected_risk_range=(0.50, 0.90)  # Should be 50-90% risk (HIGH)
)

# ==================== SUMMARY ====================
print_header("TEST SUMMARY")
tests_passed = sum([test1_pass, test2_pass, test3_pass, test4_pass, test5_pass])
total_tests = 5

print(f"\n✅ Tests Passed: {tests_passed}/{total_tests}")
print(f"❌ Tests Failed: {total_tests - tests_passed}/{total_tests}")

if tests_passed == total_tests:
    print(f"\n🎉 ALL TESTS PASSED - Feature engineering working correctly!")
    print(f"   Models are producing realistic risk scores from actual user data.")
else:
    print(f"\n⚠️ SOME TESTS FAILED - Review feature engineering logic")
    print(f"   Expected: Realistic risk scores based on user behavior")
    print(f"   Note: Scores should NOT be only 0% or 100%")

print(f"\n{'='*80}\n")
