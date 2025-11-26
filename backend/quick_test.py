"""
Quick API Test - Tests main card payment functionality
"""

import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def test_card_payment():
    """Quick test of card payment flow"""
    
    print("\n" + "="*80)
    print("QUICK CARD PAYMENT TEST")
    print("="*80 + "\n")
    
    # Step 1: Login as admin
    print("1️⃣  Logging in as admin...")
    login_response = requests.post(
        f"{BASE_URL}/auth/login",
        data={"username": "admin", "password": "admin123"}
    )
    
    if login_response.status_code != 200:
        print("❌ Login failed!")
        print(login_response.text)
        return
    
    token = login_response.json()["access_token"]
    print(f"✅ Login successful! Token: {token[:20]}...\n")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Step 2: Test SAFE transaction with card data
    print("2️⃣  Testing SAFE transaction (Coffee - $4.50)...")
    safe_transaction = {
        "amount": 4.5,
        "merchant_name": "Starbucks",
        "transaction_type": "IN_STORE",
        "description": "Morning coffee",
        "card_number": "4532-1234-5678-9010",
        "cardholder_name": "John Doe",
        "cvv": "123",
        "expiry_date": "12/26",
        "billing_address": "123 Main St, New York, NY 10001",
        "location": "New York, NY, USA",
        "device_info": "iPhone 14 Pro",
        "ip_address": "192.168.1.100"
    }
    
    response = requests.post(
        f"{BASE_URL}/transactions/submit",
        json=safe_transaction,
        headers=headers
    )
    
    if response.status_code == 200 or response.status_code == 201:
        result = response.json()
        print(f"✅ Transaction submitted!")
        print(f"   ID: {result.get('id')}")
        print(f"   Classification: {result.get('classification')}")
        print(f"   Risk Score: {result.get('risk_score'):.2f}")
        print(f"   Status: {result.get('status')}")
        print(f"   Explanation: {result.get('explanation')}\n")
    else:
        print(f"❌ Transaction failed!")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text}\n")
    
    # Step 3: Test SUSPICIOUS transaction
    print("3️⃣  Testing SUSPICIOUS transaction (Laptop - $1,299)...")
    suspicious_transaction = {
        "amount": 1299.99,
        "merchant_name": "Best Buy Electronics",
        "transaction_type": "ONLINE",
        "description": "Laptop Purchase",
        "card_number": "4532-1234-5678-9010",
        "cardholder_name": "John Doe",
        "cvv": "456",
        "expiry_date": "12/26",
        "billing_address": "456 Oak Ave, Miami, FL 33101",
        "location": "Miami, FL, USA",
        "device_info": "Chrome on Windows 11",
        "ip_address": "192.168.1.120"
    }
    
    response = requests.post(
        f"{BASE_URL}/transactions/submit",
        json=suspicious_transaction,
        headers=headers
    )
    
    if response.status_code == 200 or response.status_code == 201:
        result = response.json()
        print(f"✅ Transaction submitted!")
        print(f"   ID: {result.get('id')}")
        print(f"   Classification: {result.get('classification')}")
        print(f"   Risk Score: {result.get('risk_score'):.2f}")
        print(f"   Status: {result.get('status')}")
        print(f"   Explanation: {result.get('explanation')}\n")
    else:
        print(f"❌ Transaction failed!")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text}\n")
    
    # Step 4: Test FRAUD transaction
    print("4️⃣  Testing FRAUD transaction (Dubai - $9,999)...")
    fraud_transaction = {
        "amount": 9999.99,
        "merchant_name": "Luxury Goods Dubai",
        "transaction_type": "ONLINE",
        "description": "High-value international purchase",
        "card_number": "4532-1234-5678-9010",
        "cardholder_name": "John Doe",
        "cvv": "789",
        "expiry_date": "12/26",
        "billing_address": "Unknown Address",
        "location": "Dubai, UAE",
        "device_info": "Unknown Device",
        "ip_address": "85.12.34.56"
    }
    
    response = requests.post(
        f"{BASE_URL}/transactions/submit",
        json=fraud_transaction,
        headers=headers
    )
    
    if response.status_code == 200 or response.status_code == 201:
        result = response.json()
        print(f"✅ Transaction submitted!")
        print(f"   ID: {result.get('id')}")
        print(f"   Classification: {result.get('classification')}")
        print(f"   Risk Score: {result.get('risk_score'):.2f}")
        print(f"   Status: {result.get('status')}")
        print(f"   Explanation: {result.get('explanation')}\n")
    else:
        print(f"❌ Transaction failed!")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text}\n")
    
    # Step 5: View statistics
    print("5️⃣  Fetching system statistics...")
    stats_response = requests.get(f"{BASE_URL}/admin/statistics", headers=headers)
    
    if stats_response.status_code == 200:
        stats = stats_response.json()
        print("✅ Statistics:")
        print(f"   Total Users: {stats.get('total_users')}")
        print(f"   Total Transactions: {stats.get('total_transactions')}")
        print(f"   Safe: {stats.get('safe_transactions')}")
        print(f"   Suspicious: {stats.get('suspicious_transactions')}")
        print(f"   Fraud: {stats.get('fraud_transactions')}")
        print(f"   Fraud Detection Rate: {stats.get('fraud_detection_rate'):.2f}%\n")
    else:
        print(f"❌ Failed to get statistics\n")
    
    print("="*80)
    print("✅ QUICK TEST COMPLETED!")
    print("="*80 + "\n")


if __name__ == "__main__":
    try:
        test_card_payment()
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Could not connect to API server!")
        print("   Make sure the server is running at http://127.0.0.1:8000")
        print("   Run: cd backend && ..\.venv\Scripts\python.exe -m uvicorn app.main:app --reload\n")
    except Exception as e:
        print(f"\n❌ Error: {e}\n")
