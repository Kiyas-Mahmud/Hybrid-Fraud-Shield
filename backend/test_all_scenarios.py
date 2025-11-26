"""
Test Script for All Transaction Scenarios (SAFE, SUSPICIOUS, FRAUD)
This script submits transactions and shows the results with detailed breakdown
"""

import requests
import json
from datetime import datetime
import time

# API Configuration
BASE_URL = "http://localhost:8000"
LOGIN_URL = f"{BASE_URL}/auth/login"
TRANSACTION_URL = f"{BASE_URL}/transactions/submit"

# Test User Credentials
USERNAME = "john_doe"
PASSWORD = "SecurePass123!"

def login():
    """Login and get access token"""
    print("🔐 Logging in...")
    response = requests.post(LOGIN_URL, json={
        "username": USERNAME,
        "password": PASSWORD
    })
    
    if response.status_code == 200:
        data = response.json()
        token = data.get("access_token")
        print(f"✅ Login successful! Token: {token[:20]}...")
        return token
    else:
        print(f"❌ Login failed: {response.text}")
        return None

def submit_transaction(token, transaction_data, scenario_name):
    """Submit a transaction and display results"""
    print(f"\n{'='*80}")
    print(f"📝 Testing: {scenario_name}")
    print(f"{'='*80}")
    print(f"Amount: ${transaction_data['amount']}")
    print(f"Merchant: {transaction_data['merchant_name']}")
    print(f"Type: {transaction_data['transaction_type']}")
    print(f"Description: {transaction_data['description']}")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.post(TRANSACTION_URL, json=transaction_data, headers=headers)
        
        if response.status_code == 200:
            result = response.json()
            
            # Display results
            print(f"\n🎯 RESULT: {result.get('status', 'UNKNOWN')}")
            print(f"Risk Score: {result.get('risk_score', 0):.4f}")
            print(f"Confidence: {result.get('confidence', 0):.2f}%")
            
            # Display model predictions
            if 'model_predictions' in result:
                print(f"\n📊 Model Predictions:")
                for model_name, prediction in result['model_predictions'].items():
                    print(f"  - {model_name}: {prediction:.4f}")
            
            # Display reason
            if 'reason' in result:
                print(f"\n💡 Reason: {result['reason']}")
            
            print(f"\n✅ Transaction ID: {result.get('transaction_id', 'N/A')}")
            return result
        else:
            print(f"\n❌ Error: {response.status_code}")
            print(response.text)
            return None
            
    except Exception as e:
        print(f"\n❌ Exception: {str(e)}")
        return None

def run_tests():
    """Run all test scenarios"""
    
    # Login first
    token = login()
    if not token:
        print("❌ Cannot proceed without authentication")
        return
    
    print("\n" + "="*80)
    print("🚀 STARTING COMPREHENSIVE TRANSACTION TESTS")
    print("="*80)
    
    # ============================================================
    # SAFE TRANSACTIONS (Should Auto-Approve)
    # ============================================================
    print("\n\n")
    print("🟢 " + "="*76 + " 🟢")
    print("🟢 TESTING SAFE TRANSACTIONS (Expected: Auto-Approved)")
    print("🟢 " + "="*76 + " 🟢")
    
    safe_transactions = [
        {
            "name": "Small Coffee Purchase",
            "data": {
                "amount": 4.50,
                "merchant_name": "Starbucks",
                "transaction_type": "IN_STORE",
                "description": "Morning coffee"
            }
        },
        {
            "name": "Lunch Purchase",
            "data": {
                "amount": 12.99,
                "merchant_name": "McDonald's",
                "transaction_type": "IN_STORE",
                "description": "Lunch meal"
            }
        },
        {
            "name": "Gas Station",
            "data": {
                "amount": 45.00,
                "merchant_name": "Shell Gas Station",
                "transaction_type": "IN_STORE",
                "description": "Fuel purchase"
            }
        },
        {
            "name": "Grocery Shopping",
            "data": {
                "amount": 78.50,
                "merchant_name": "Walmart",
                "transaction_type": "IN_STORE",
                "description": "Weekly groceries"
            }
        },
        {
            "name": "Streaming Service",
            "data": {
                "amount": 15.99,
                "merchant_name": "Netflix",
                "transaction_type": "ONLINE",
                "description": "Monthly subscription"
            }
        }
    ]
    
    safe_results = []
    for transaction in safe_transactions:
        result = submit_transaction(token, transaction["data"], transaction["name"])
        safe_results.append({"name": transaction["name"], "result": result})
        time.sleep(1)  # Small delay between requests
    
    # ============================================================
    # SUSPICIOUS TRANSACTIONS (Should Require Confirmation)
    # ============================================================
    print("\n\n")
    print("🟡 " + "="*76 + " 🟡")
    print("🟡 TESTING SUSPICIOUS TRANSACTIONS (Expected: Requires Confirmation)")
    print("🟡 " + "="*76 + " 🟡")
    
    suspicious_transactions = [
        {
            "name": "Electronics Purchase",
            "data": {
                "amount": 450.00,
                "merchant_name": "Best Buy",
                "transaction_type": "IN_STORE",
                "description": "Electronics purchase"
            }
        },
        {
            "name": "High Restaurant Bill",
            "data": {
                "amount": 185.00,
                "merchant_name": "Fancy Restaurant",
                "transaction_type": "IN_STORE",
                "description": "Dinner for group"
            }
        },
        {
            "name": "Furniture Purchase",
            "data": {
                "amount": 899.99,
                "merchant_name": "IKEA",
                "transaction_type": "IN_STORE",
                "description": "Furniture purchase"
            }
        },
        {
            "name": "Jewelry Purchase",
            "data": {
                "amount": 650.00,
                "merchant_name": "Kay Jewelers",
                "transaction_type": "IN_STORE",
                "description": "Jewelry purchase"
            }
        },
        {
            "name": "Hotel Booking",
            "data": {
                "amount": 480.00,
                "merchant_name": "Marriott Hotel",
                "transaction_type": "ONLINE",
                "description": "Hotel reservation"
            }
        }
    ]
    
    suspicious_results = []
    for transaction in suspicious_transactions:
        result = submit_transaction(token, transaction["data"], transaction["name"])
        suspicious_results.append({"name": transaction["name"], "result": result})
        time.sleep(1)
    
    # ============================================================
    # FRAUD TRANSACTIONS (Should Auto-Block)
    # ============================================================
    print("\n\n")
    print("🔴 " + "="*76 + " 🔴")
    print("🔴 TESTING FRAUD TRANSACTIONS (Expected: Auto-Blocked)")
    print("🔴 " + "="*76 + " 🔴")
    
    fraud_transactions = [
        {
            "name": "Very High Amount",
            "data": {
                "amount": 5000.00,
                "merchant_name": "Luxury Goods Store",
                "transaction_type": "ONLINE",
                "description": "Expensive purchase"
            }
        },
        {
            "name": "Foreign High Amount",
            "data": {
                "amount": 3500.00,
                "merchant_name": "International Retailer",
                "transaction_type": "ONLINE",
                "description": "Overseas purchase"
            }
        },
        {
            "name": "Suspicious Merchant",
            "data": {
                "amount": 9999.99,
                "merchant_name": "SUSPICIOUS_MERCHANT_XYZ",
                "transaction_type": "ONLINE",
                "description": "Unauthorized transaction"
            }
        },
        {
            "name": "Cryptocurrency Exchange",
            "data": {
                "amount": 4500.00,
                "merchant_name": "Crypto Exchange Platform",
                "transaction_type": "ONLINE",
                "description": "Cryptocurrency purchase"
            }
        },
        {
            "name": "International Wire Transfer",
            "data": {
                "amount": 7500.00,
                "merchant_name": "International Wire Service",
                "transaction_type": "ONLINE",
                "description": "Wire transfer"
            }
        }
    ]
    
    fraud_results = []
    for transaction in fraud_transactions:
        result = submit_transaction(token, transaction["data"], transaction["name"])
        fraud_results.append({"name": transaction["name"], "result": result})
        time.sleep(1)
    
    # ============================================================
    # SUMMARY
    # ============================================================
    print("\n\n")
    print("="*80)
    print("📊 TEST SUMMARY")
    print("="*80)
    
    print("\n🟢 SAFE Transactions:")
    for item in safe_results:
        if item["result"]:
            status = item["result"].get("status", "UNKNOWN")
            risk_score = item["result"].get("risk_score", 0)
            print(f"  ✓ {item['name']}: {status} (Risk: {risk_score:.4f})")
        else:
            print(f"  ✗ {item['name']}: FAILED")
    
    print("\n🟡 SUSPICIOUS Transactions:")
    for item in suspicious_results:
        if item["result"]:
            status = item["result"].get("status", "UNKNOWN")
            risk_score = item["result"].get("risk_score", 0)
            print(f"  ⚠ {item['name']}: {status} (Risk: {risk_score:.4f})")
        else:
            print(f"  ✗ {item['name']}: FAILED")
    
    print("\n🔴 FRAUD Transactions:")
    for item in fraud_results:
        if item["result"]:
            status = item["result"].get("status", "UNKNOWN")
            risk_score = item["result"].get("risk_score", 0)
            print(f"  ✗ {item['name']}: {status} (Risk: {risk_score:.4f})")
        else:
            print(f"  ✗ {item['name']}: FAILED")
    
    print("\n" + "="*80)
    print("✅ Testing Complete!")
    print("="*80)
    print("\n💡 Next Steps:")
    print("1. Check Admin Panel: http://localhost:3001")
    print("2. Review transactions in dashboard")
    print("3. View user analytics for john_doe")
    print("4. Check transaction details with model explanations")

if __name__ == "__main__":
    run_tests()
