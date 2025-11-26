"""
Real-world scenario: User always transacts from same 2-3 IPs/locations
Suddenly: Transaction from unknown IP in different city/country

This tests IP/Location behavioral anomaly detection
"""
import sys
import os
from datetime import datetime, timedelta

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.fraud_detection import FraudDetectionService

print("="*80)
print("🌍 IP/LOCATION ANOMALY DETECTION SCENARIO")
print("="*80)
print()

fraud_detection_service = FraudDetectionService()

# ===========================================================================
# SCENARIO 1: Domestic IP Change (Same country, different city)
# ===========================================================================
print("📍 SCENARIO 1: Same Country, Different City")
print("-" * 80)

# User's normal pattern: Home WiFi + Office WiFi in New York
now = datetime.now()
user_history_domestic = [
    # Last 2 months - all from New York area (2 IPs: home + office)
    {'amount': 45.00, 'created_at': now - timedelta(days=60), 'ip_address': '192.168.1.100', 'location': 'New York, NY'},
    {'amount': 38.50, 'created_at': now - timedelta(days=55), 'ip_address': '10.0.0.50', 'location': 'New York, NY'},  # Office
    {'amount': 52.00, 'created_at': now - timedelta(days=50), 'ip_address': '192.168.1.100', 'location': 'New York, NY'},  # Home
    {'amount': 41.00, 'created_at': now - timedelta(days=45), 'ip_address': '192.168.1.100', 'location': 'New York, NY'},
    {'amount': 48.50, 'created_at': now - timedelta(days=40), 'ip_address': '10.0.0.50', 'location': 'New York, NY'},
    {'amount': 55.00, 'created_at': now - timedelta(days=35), 'ip_address': '192.168.1.100', 'location': 'New York, NY'},
    {'amount': 42.00, 'created_at': now - timedelta(days=30), 'ip_address': '192.168.1.100', 'location': 'New York, NY'},
    {'amount': 50.00, 'created_at': now - timedelta(days=25), 'ip_address': '10.0.0.50', 'location': 'New York, NY'},
    {'amount': 46.00, 'created_at': now - timedelta(days=20), 'ip_address': '192.168.1.100', 'location': 'New York, NY'},
    {'amount': 53.00, 'created_at': now - timedelta(days=15), 'ip_address': '192.168.1.100', 'location': 'New York, NY'},
    {'amount': 47.00, 'created_at': now - timedelta(days=10), 'ip_address': '10.0.0.50', 'location': 'New York, NY'},
    {'amount': 51.00, 'created_at': now - timedelta(days=5), 'ip_address': '192.168.1.100', 'location': 'New York, NY'},
]

# SUSPICIOUS: Transaction from Los Angeles (still USA, but unusual)
domestic_anomaly_data = {
    'amount': 85.00,
    'merchant_category': 'shopping',
    'transaction_hour': 15,
    'is_foreign_transaction': 0,  # Still domestic
    'ip_address': '173.45.92.180',  # NEW IP!
    'location': 'Los Angeles, CA',  # Different city!
    'user_id': 'user_traveler',
    'user_history': user_history_domestic
}

user_avg = sum(t['amount'] for t in user_history_domestic) / len(user_history_domestic)
unique_ips = set(t.get('ip_address', '') for t in user_history_domestic)
unique_locations = set(t.get('location', '') for t in user_history_domestic)

print("👤 USER PROFILE:")
print(f"   History: {len(user_history_domestic)} transactions over 2 months")
print(f"   Average amount: ${user_avg:.2f}")
print(f"   Known IPs: {len(unique_ips)} addresses")
for ip in unique_ips:
    print(f"      • {ip}")
print(f"   Known Locations: {unique_locations}")
print()

print("🚨 SUSPICIOUS TRANSACTION:")
print(f"   Amount: ${domestic_anomaly_data['amount']:.2f}")
print(f"   IP: {domestic_anomaly_data['ip_address']} ⚠️ UNKNOWN!")
print(f"   Location: {domestic_anomaly_data['location']} ⚠️ NEW CITY!")
print(f"   Previous locations: {unique_locations}")
print()

print("❓ QUESTION: User traveling, or stolen card?")
print()

# Predict
risk_score_1, predictions_1 = fraud_detection_service.predict(domestic_anomaly_data)

print(f"📊 RESULTS:")
print(f"   Risk Score: {risk_score_1*100:.2f}%")
if 'risk_boosting' in predictions_1 and predictions_1['risk_boosting']['applied']:
    boost_info = predictions_1['risk_boosting']
    print(f"   Base Score: {boost_info['base_score']*100:.2f}%")
    print(f"   Boost Applied: +{boost_info['boost_amount']*100:.2f}%")
    print(f"   Reason: {boost_info['reason']}")
print()

if risk_score_1 < 0.30:
    decision_1 = "✅ APPROVE"
elif risk_score_1 < 0.50:
    decision_1 = "⚠️ REVIEW - Request SMS verification"
elif risk_score_1 < 0.70:
    decision_1 = "🚨 VERIFY - Call customer"
else:
    decision_1 = "❌ BLOCK - High fraud risk"

print(f"   Decision: {decision_1}")
print()

# ===========================================================================
# SCENARIO 2: International IP Change (Foreign country)
# ===========================================================================
print("="*80)
print("📍 SCENARIO 2: International - Different Country")
print("-" * 80)

# VERY SUSPICIOUS: Same user, but transaction from Russia
international_anomaly_data = {
    'amount': 450.00,  # Larger amount too
    'merchant_category': 'electronics',
    'transaction_hour': 3,  # 3 AM (suspicious time)
    'is_foreign_transaction': 1,  # FOREIGN!
    'ip_address': '91.108.56.123',  # Russian IP
    'location': 'Moscow, Russia',  # VERY different!
    'user_id': 'user_traveler',
    'user_history': user_history_domestic  # Same NY-based user
}

print("👤 SAME USER PROFILE:")
print(f"   Normal location: New York, NY (USA)")
print(f"   Known IPs: 2 addresses (home + office)")
print(f"   Average: ${user_avg:.2f}")
print()

print("🚨🚨 HIGHLY SUSPICIOUS TRANSACTION:")
print(f"   Amount: ${international_anomaly_data['amount']:.2f} (9.4x normal!)")
print(f"   IP: {international_anomaly_data['ip_address']} ⚠️⚠️ RUSSIAN IP!")
print(f"   Location: {international_anomaly_data['location']} ⚠️⚠️ MOSCOW!")
print(f"   Time: 3:00 AM (late night)")
print(f"   User NEVER left USA before!")
print()

print("❓ QUESTION: User suddenly in Russia at 3 AM? Almost certainly FRAUD!")
print()

# Predict
risk_score_2, predictions_2 = fraud_detection_service.predict(international_anomaly_data)

print(f"📊 RESULTS:")
print(f"   Risk Score: {risk_score_2*100:.2f}%")
if 'risk_boosting' in predictions_2 and predictions_2['risk_boosting']['applied']:
    boost_info = predictions_2['risk_boosting']
    print(f"   Base Score: {boost_info['base_score']*100:.2f}%")
    print(f"   Boost Applied: +{boost_info['boost_amount']*100:.2f}%")
    print(f"   Reason: {boost_info['reason']}")
    if boost_info['factors']:
        print(f"   Boost Factors:")
        for factor, boost_val in boost_info['factors'].items():
            if boost_val > 0:
                print(f"      • {factor}: +{boost_val*100:.1f}%")
print()

if risk_score_2 < 0.30:
    decision_2 = "✅ APPROVE"
elif risk_score_2 < 0.50:
    decision_2 = "⚠️ REVIEW - Request SMS verification"
elif risk_score_2 < 0.70:
    decision_2 = "🚨 VERIFY - Call customer"
else:
    decision_2 = "❌ BLOCK - High fraud risk"

print(f"   Decision: {decision_2}")
print()

# ===========================================================================
# SCENARIO 3: VPN/Proxy Detection (Rapid IP switching)
# ===========================================================================
print("="*80)
print("📍 SCENARIO 3: Rapid IP Switching (VPN/Proxy)")
print("-" * 80)

# Create history with rapid IP changes (last 24 hours)
vpn_history = [
    # Normal history (2 months ago)
    {'amount': 45.00, 'created_at': now - timedelta(days=60), 'ip_address': '192.168.1.100', 'location': 'New York, NY'},
    {'amount': 50.00, 'created_at': now - timedelta(days=50), 'ip_address': '192.168.1.100', 'location': 'New York, NY'},
    {'amount': 48.00, 'created_at': now - timedelta(days=40), 'ip_address': '10.0.0.50', 'location': 'New York, NY'},
    
    # RECENT: Rapid IP switching (last 24 hours) - fraud pattern!
    {'amount': 25.00, 'created_at': now - timedelta(hours=20), 'ip_address': '203.45.12.90', 'location': 'Singapore'},
    {'amount': 30.00, 'created_at': now - timedelta(hours=18), 'ip_address': '87.120.45.67', 'location': 'Germany'},
    {'amount': 28.00, 'created_at': now - timedelta(hours=15), 'ip_address': '45.89.123.45', 'location': 'Brazil'},
    {'amount': 35.00, 'created_at': now - timedelta(hours=12), 'ip_address': '91.234.56.78', 'location': 'Russia'},
    {'amount': 22.00, 'created_at': now - timedelta(hours=8), 'ip_address': '123.45.67.89', 'location': 'Japan'},
    {'amount': 40.00, 'created_at': now - timedelta(hours=4), 'ip_address': '198.45.23.12', 'location': 'Canada'},
    {'amount': 33.00, 'created_at': now - timedelta(hours=1), 'ip_address': '156.78.90.12', 'location': 'UK'},
]

vpn_transaction = {
    'amount': 150.00,
    'merchant_category': 'electronics',
    'transaction_hour': 14,
    'is_foreign_transaction': 1,
    'ip_address': '77.88.99.100',  # Yet another new IP!
    'location': 'France',
    'user_id': 'user_vpn_fraudster',
    'user_history': vpn_history
}

recent_ips = [t.get('ip_address', '') for t in vpn_history[-7:]]  # Last 7 transactions
recent_locations = [t.get('location', '') for t in vpn_history[-7:]]

print("👤 USER PROFILE:")
print(f"   Normal: New York resident")
print(f"   Recent activity: HIGHLY SUSPICIOUS!")
print(f"   Last 7 transactions from 7 DIFFERENT countries:")
for i, loc in enumerate(recent_locations, 1):
    print(f"      {i}. {loc}")
print()

print("🚨🚨🚨 FRAUD PATTERN DETECTED:")
print(f"   • 7 countries in 24 hours (impossible!)")
print(f"   • Using VPN/Proxy to hide location")
print(f"   • Card testing or carding attack")
print(f"   • Amount: ${vpn_transaction['amount']:.2f}")
print()

print("❓ QUESTION: Clear fraud pattern - block immediately!")
print()

# Predict
risk_score_3, predictions_3 = fraud_detection_service.predict(vpn_transaction)

print(f"📊 RESULTS:")
print(f"   Risk Score: {risk_score_3*100:.2f}%")
if 'risk_boosting' in predictions_3 and predictions_3['risk_boosting']['applied']:
    boost_info = predictions_3['risk_boosting']
    print(f"   Base Score: {boost_info['base_score']*100:.2f}%")
    print(f"   Boost Applied: +{boost_info['boost_amount']*100:.2f}%")
    print(f"   Reason: {boost_info['reason']}")
print()

if risk_score_3 < 0.30:
    decision_3 = "✅ APPROVE"
elif risk_score_3 < 0.50:
    decision_3 = "⚠️ REVIEW"
elif risk_score_3 < 0.70:
    decision_3 = "🚨 VERIFY"
else:
    decision_3 = "❌ BLOCK"

print(f"   Decision: {decision_3}")
print()

# ===========================================================================
# SUMMARY
# ===========================================================================
print("="*80)
print("📊 SUMMARY: IP/LOCATION ANOMALY DETECTION")
print("="*80)
print()
print(f"1. Domestic City Change (NY → LA):")
print(f"   Risk: {risk_score_1*100:.1f}% - {decision_1}")
print()
print(f"2. International (NY → Moscow, 3 AM, $450):")
print(f"   Risk: {risk_score_2*100:.1f}% - {decision_2}")
print()
print(f"3. VPN/Proxy (7 countries in 24h):")
print(f"   Risk: {risk_score_3*100:.1f}% - {decision_3}")
print()
print("💡 KEY INSIGHTS:")
print("   • IP changes are encoded in features (location risk)")
print("   • Foreign transactions get automatic +15-35% boost")
print("   • High velocity (multiple countries/IPs) triggers boost")
print("   • System learns normal IP/location patterns from history")
print("   • Deviation from pattern increases risk score")
print()
print("="*80)
