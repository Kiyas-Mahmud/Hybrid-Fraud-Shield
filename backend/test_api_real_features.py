"""
Quick API Test - Real Feature Engineering
Test the actual API endpoint with realistic scenarios
"""
import requests
import json
from datetime import datetime

API_BASE = "http://127.0.0.1:8000/api/v1"

def print_header(text):
    print(f"\n{'='*80}")
    print(f"  {text}")
    print(f"{'='*80}\n")

def login():
    """Login and get token"""
    response = requests.post(
        f"{API_BASE}/auth/login",
        data={"username": "testuser@example.com", "password": "password123"}
    )
    if response.status_code == 200:
        token = response.json()["access_token"]
        print("✅ Logged in successfully")
        return token
    else:
        print(f"❌ Login failed: {response.status_code}")
        return None

def test_transaction(token, scenario_name, transaction_data):
    """Submit a transaction and check fraud detection"""
    print_header(f"Testing: {scenario_name}")
    print(f"Amount: ${transaction_data['amount']:.2f}")
    print(f"Merchant: {transaction_data['merchant_name']}")
    print(f"Location: {transaction_data.get('location', 'N/A')}")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(
        f"{API_BASE}/transactions/submit",
        headers=headers,
        json=transaction_data
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"\n📊 FRAUD DETECTION RESULTS:")
        print(f"   Status: {result['status']}")
        print(f"   Risk Score: {result['risk_score']:.2f}%")
        print(f"   Classification: {result['fraud_status']}")
        
        print(f"\n📋 Risk Factors:")
        for factor in result.get('risk_factors', []):
            print(f"   • {factor}")
        
        print(f"\n🤖 Model Predictions:")
        predictions = result.get('model_predictions', {})
        if predictions:
            # Show top 5 model predictions
            sorted_preds = sorted(predictions.items(), key=lambda x: x[1] if isinstance(x[1], (int, float)) else 0, reverse=True)[:5]
            for model, score in sorted_preds:
                if isinstance(score, (int, float)) and 0 <= score <= 1:
                    print(f"   {model}: {score*100:.2f}%")
        
        return result
    else:
        print(f"❌ Transaction failed: {response.status_code}")
        print(response.text)
        return None

# ==================== MAIN TEST ====================
print_header("REAL FEATURE ENGINEERING API TEST")
print("Testing fraud detection with actual user data (NO TEMPLATES)")

# Login
token = login()
if not token:
    print("❌ Cannot proceed without authentication")
    exit(1)

# Test 1: Small Safe Purchase
test_transaction(token, "Safe Purchase - Coffee", {
    "amount": 4.50,
    "merchant_name": "Starbucks",
    "transaction_type": "PURCHASE",
    "location": "New York, USA",
    "device_info": "iPhone 14 Pro",
    "ip_address": "192.168.1.1",
    "description": "Morning coffee"
})

# Test 2: Moderate Purchase
test_transaction(token, "Suspicious Purchase - Laptop", {
    "amount": 1899.00,
    "merchant_name": "Best Buy",
    "transaction_type": "PURCHASE",
    "location": "Los Angeles, USA",
    "device_info": "Chrome on Windows",
    "ip_address": "10.0.0.1",
    "description": "MacBook Pro purchase"
})

# Test 3: High Risk Purchase
test_transaction(token, "Fraud Alert - Large Foreign Purchase", {
    "amount": 9999.00,
    "merchant_name": "Luxury Store",
    "transaction_type": "PURCHASE",
    "location": "Dubai, UAE",
    "device_info": "Unknown Device",
    "ip_address": "185.220.101.1",
    "description": "Expensive jewelry"
})

print_header("TEST COMPLETE")
print("✅ All transactions processed")
print("📊 Check the risk scores above - they should be realistic (not just 0% or 100%)")
print("\nExpected Results:")
print("  • Coffee ($4.50): 5-45% risk (SAFE or SUSPICIOUS)")
print("  • Laptop ($1,899): 30-70% risk (SUSPICIOUS)")
print("  • Dubai ($9,999): 50-95% risk (SUSPICIOUS or FRAUD)")
