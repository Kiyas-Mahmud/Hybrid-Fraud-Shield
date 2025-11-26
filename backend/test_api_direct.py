import requests
import json

# API endpoint
BASE_URL = "http://localhost:8000"

# Test data - $4.50 Starbucks transaction
test_transaction = {
    "card_number": "4111111111111111",
    "cardholder_name": "John Doe",
    "expiry_date": "12/26",
    "cvv": "123",
    "amount": 4.50,
    "merchant_name": "Starbucks",
    "transaction_type": "IN_STORE",
    "description": "Morning coffee"
}

print("=" * 80)
print("🧪 TESTING FRAUD DETECTION API")
print("=" * 80)

# Step 1: Login
print("\n1️⃣ Logging in as john_doe...")
login_response = requests.post(
    f"{BASE_URL}/api/v1/auth/login",
    data={
        "username": "john_doe",
        "password": "SecurePass123!"
    }
)

if login_response.status_code != 200:
    print(f"❌ Login failed: {login_response.status_code}")
    print(login_response.text)
    exit(1)

token = login_response.json()["access_token"]
print(f"✅ Login successful! Token: {token[:50]}...")

# Step 2: Submit transaction
print("\n2️⃣ Submitting $4.50 Starbucks transaction...")
print(f"   Transaction data:")
print(f"   - Amount: ${test_transaction['amount']}")
print(f"   - Merchant: {test_transaction['merchant_name']}")
print(f"   - Type: {test_transaction['transaction_type']}")

headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

transaction_response = requests.post(
    f"{BASE_URL}/api/v1/transactions/submit",
    headers=headers,
    json=test_transaction
)

print(f"\n3️⃣ API Response Status: {transaction_response.status_code}")

if transaction_response.status_code == 200 or transaction_response.status_code == 201:
    result = transaction_response.json()
    print(f"\n✅ Transaction submitted successfully!")
    print(f"\n📊 RESULT SUMMARY:")
    print(f"   Transaction ID: {result.get('transaction_id')}")
    print(f"   Classification: {result.get('classification')}")
    print(f"   Risk Score: {result.get('risk_score', 0) * 100:.2f}%")
    print(f"   Status: {result.get('status')}")
    print(f"   Requires Confirmation: {result.get('requires_confirmation')}")
    
    print(f"\n🎯 EXPECTED vs ACTUAL:")
    print(f"   Expected Classification: SAFE (green badge)")
    print(f"   Actual Classification: {result.get('classification')}")
    print(f"   Expected Risk Score: < 30%")
    print(f"   Actual Risk Score: {result.get('risk_score', 0) * 100:.2f}%")
    
    if result.get('classification') == 'SAFE':
        print(f"\n✅ TEST PASSED! Transaction correctly classified as SAFE")
    elif result.get('classification') == 'SUSPICIOUS':
        print(f"\n❌ TEST FAILED! Transaction incorrectly classified as SUSPICIOUS")
        print(f"   This should be SAFE because:")
        print(f"   - Amount ${test_transaction['amount']} < $150")
        print(f"   - Risk score {result.get('risk_score', 0) * 100:.2f}% should be < 30%")
    else:
        print(f"\n❌ TEST FAILED! Unexpected classification: {result.get('classification')}")
    
    # Show risk factors if available
    if 'risk_factors' in result and result['risk_factors']:
        print(f"\n⚠️ Risk Factors Detected:")
        for i, factor in enumerate(result['risk_factors'][:3], 1):
            print(f"   {i}. {factor.get('factor')}: {factor.get('description')}")
    
    # Show full response for debugging
    print(f"\n📋 Full API Response:")
    print(json.dumps(result, indent=2))
    
else:
    print(f"❌ Transaction submission failed!")
    print(f"Status code: {transaction_response.status_code}")
    print(f"Response: {transaction_response.text}")

print("\n" + "=" * 80)
print("🏁 TEST COMPLETE")
print("=" * 80)
