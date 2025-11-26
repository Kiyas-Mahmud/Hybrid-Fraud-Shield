"""
Real-World User Scenario Testing
Simulates actual user behavior: Login → Make Purchase → See Fraud Detection Result
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://127.0.0.1:8000"

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    MAGENTA = '\033[95m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    print(f"\n{Colors.CYAN}{Colors.BOLD}{'='*100}{Colors.RESET}")
    print(f"{Colors.CYAN}{Colors.BOLD}{text.center(100)}{Colors.RESET}")
    print(f"{Colors.CYAN}{Colors.BOLD}{'='*100}{Colors.RESET}\n")

def print_section(text):
    print(f"\n{Colors.BLUE}{Colors.BOLD}{text}{Colors.RESET}")
    print(f"{Colors.BLUE}{'-'*100}{Colors.RESET}\n")

def print_result(classification, risk_score, status, explanation):
    """Print fraud detection result with colors"""
    if classification == "SAFE":
        color = Colors.GREEN
        icon = "✅"
    elif classification == "SUSPICIOUS":
        color = Colors.YELLOW
        icon = "⚠️"
    else:  # FRAUD
        color = Colors.RED
        icon = "🚨"
    
    print(f"{color}{Colors.BOLD}{icon} FRAUD DETECTION RESULT:{Colors.RESET}")
    print(f"{color}{'─'*100}{Colors.RESET}")
    print(f"{Colors.BOLD}Classification:{Colors.RESET} {color}{classification}{Colors.RESET}")
    print(f"{Colors.BOLD}Risk Score:{Colors.RESET} {color}{risk_score:.2%}{Colors.RESET}")
    print(f"{Colors.BOLD}Status:{Colors.RESET} {color}{status}{Colors.RESET}")
    print(f"{Colors.BOLD}Explanation:{Colors.RESET}\n{explanation}")
    print(f"{color}{'─'*100}{Colors.RESET}\n")

def scenario_1_safe_coffee_purchase():
    """Scenario 1: Normal user buys coffee - Should be SAFE"""
    
    print_header("SCENARIO 1: NORMAL COFFEE PURCHASE (SHOULD BE SAFE)")
    
    # Step 1: User Registration
    print_section("Step 1: New User Registration")
    user_data = {
        "username": "sarah_johnson",
        "email": "sarah.j@example.com",
        "password": "SecurePass123!",
        "full_name": "Sarah Johnson",
        "phone": "+1-555-0123"
    }
    
    print(f"{Colors.MAGENTA}Registering user: {user_data['full_name']}{Colors.RESET}")
    register_response = requests.post(f"{BASE_URL}/auth/register", json=user_data)
    
    if register_response.status_code == 201:
        print(f"{Colors.GREEN}✅ Registration successful!{Colors.RESET}")
        user_info = register_response.json()
        print(f"   User ID: {user_info.get('user_id', 'N/A')}")
        print(f"   Username: {user_info.get('username', user_data['username'])}")
        print(f"   Email: {user_info.get('email', user_data['email'])}")
    else:
        # User might already exist, try to login
        print(f"{Colors.YELLOW}⚠️ User might already exist, proceeding to login...{Colors.RESET}")
    
    # Step 2: User Login
    print_section("Step 2: User Login")
    print(f"{Colors.MAGENTA}Logging in as: {user_data['username']}{Colors.RESET}")
    
    login_response = requests.post(
        f"{BASE_URL}/auth/login",
        data={"username": user_data['username'], "password": user_data['password']}
    )
    
    if login_response.status_code != 200:
        print(f"{Colors.RED}❌ Login failed! Using admin instead...{Colors.RESET}")
        login_response = requests.post(
            f"{BASE_URL}/auth/login",
            data={"username": "admin", "password": "admin123"}
        )
    
    token = login_response.json()["access_token"]
    print(f"{Colors.GREEN}✅ Login successful!{Colors.RESET}")
    print(f"   Token: {token[:30]}...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Step 3: User Makes Purchase
    print_section("Step 3: Making Coffee Purchase")
    
    transaction_data = {
        "amount": 4.50,
        "merchant_name": "Starbucks",
        "transaction_type": "IN_STORE",
        "description": "Morning latte",
        "card_number": "4532-1234-5678-9010",
        "cardholder_name": "Sarah Johnson",
        "cvv": "123",
        "expiry_date": "12/26",
        "billing_address": "742 Evergreen Terrace, Springfield, IL 62701"
    }
    
    print(f"{Colors.MAGENTA}Purchase Details:{Colors.RESET}")
    print(f"   Merchant: {transaction_data['merchant_name']}")
    print(f"   Amount: ${transaction_data['amount']:.2f}")
    print(f"   Type: {transaction_data['transaction_type']}")
    print(f"   Card: **** **** **** {transaction_data['card_number'][-4:]}")
    print(f"   Description: {transaction_data['description']}\n")
    
    print(f"{Colors.CYAN}⏳ Processing transaction through AI fraud detection system...{Colors.RESET}")
    print(f"{Colors.CYAN}   Analyzing with 11 ML/DL models...{Colors.RESET}\n")
    
    response = requests.post(
        f"{BASE_URL}/transactions/submit",
        json=transaction_data,
        headers=headers
    )
    
    # Step 4: Show Result
    if response.status_code in [200, 201]:
        result = response.json()
        
        print_result(
            result['classification'],
            result['risk_score'],
            result['status'],
            result['explanation']
        )
        
        # Show risk factors
        if result.get('risk_factors'):
            print(f"{Colors.BOLD}Risk Factors Detected:{Colors.RESET}")
            for factor in result['risk_factors'][:5]:  # Show top 5
                severity_color = Colors.GREEN if factor['severity'] == 'low' else Colors.YELLOW if factor['severity'] == 'medium' else Colors.RED
                print(f"  {severity_color}• {factor['factor']}{Colors.RESET} ({factor['severity']})")
                print(f"    {factor['explanation']}")
            print()
        
        return result
    else:
        print(f"{Colors.RED}❌ Transaction failed!{Colors.RESET}")
        print(f"   Error: {response.text}")
        return None


def scenario_2_suspicious_laptop():
    """Scenario 2: User buys expensive laptop - Should be SUSPICIOUS"""
    
    print_header("SCENARIO 2: HIGH-VALUE LAPTOP PURCHASE (SHOULD BE SUSPICIOUS)")
    
    # Login as existing user
    print_section("Step 1: User Login")
    login_response = requests.post(
        f"{BASE_URL}/auth/login",
        data={"username": "admin", "password": "admin123"}
    )
    
    token = login_response.json()["access_token"]
    print(f"{Colors.GREEN}✅ Logged in as admin{Colors.RESET}")
    headers = {"Authorization": f"Bearer {token}"}
    
    # Make purchase
    print_section("Step 2: Making Laptop Purchase")
    
    transaction_data = {
        "amount": 1899.99,
        "merchant_name": "Best Buy Electronics",
        "transaction_type": "ONLINE",
        "description": "MacBook Pro 16-inch",
        "card_number": "4532-1234-5678-9010",
        "cardholder_name": "Admin User",
        "cvv": "456",
        "expiry_date": "12/26",
        "billing_address": "123 Tech Street, San Francisco, CA 94102"
    }
    
    print(f"{Colors.MAGENTA}Purchase Details:{Colors.RESET}")
    print(f"   Merchant: {transaction_data['merchant_name']}")
    print(f"   Amount: ${transaction_data['amount']:.2f}")
    print(f"   Type: {transaction_data['transaction_type']}")
    print(f"   Description: {transaction_data['description']}\n")
    
    print(f"{Colors.CYAN}⏳ Processing high-value transaction...{Colors.RESET}\n")
    
    response = requests.post(
        f"{BASE_URL}/transactions/submit",
        json=transaction_data,
        headers=headers
    )
    
    if response.status_code in [200, 201]:
        result = response.json()
        
        print_result(
            result['classification'],
            result['risk_score'],
            result['status'],
            result['explanation']
        )
        
        # If suspicious, show what user needs to do
        if result['classification'] == 'SUSPICIOUS':
            print(f"{Colors.YELLOW}{Colors.BOLD}⚠️ USER ACTION REQUIRED:{Colors.RESET}")
            print(f"{Colors.YELLOW}You should receive a notification asking you to confirm this purchase.{Colors.RESET}")
            print(f"{Colors.YELLOW}To approve: POST /api/v1/transactions/{result['id']}/respond with {{'response': 'YES'}}{Colors.RESET}\n")
        
        return result
    else:
        print(f"{Colors.RED}❌ Transaction failed!{Colors.RESET}")
        print(f"   Error: {response.text}")
        return None


def scenario_3_fraud_international():
    """Scenario 3: International high-value purchase - Should be FRAUD"""
    
    print_header("SCENARIO 3: SUSPICIOUS INTERNATIONAL PURCHASE (SHOULD BE FRAUD)")
    
    # Login
    print_section("Step 1: User Login")
    login_response = requests.post(
        f"{BASE_URL}/auth/login",
        data={"username": "admin", "password": "admin123"}
    )
    
    token = login_response.json()["access_token"]
    print(f"{Colors.GREEN}✅ Logged in{Colors.RESET}")
    headers = {"Authorization": f"Bearer {token}"}
    
    # Fraudulent purchase attempt
    print_section("Step 2: Attempting International High-Value Purchase")
    
    transaction_data = {
        "amount": 9999.99,
        "merchant_name": "Luxury Goods Dubai LLC",
        "transaction_type": "ONLINE",
        "description": "Expensive jewelry purchase",
        "card_number": "4532-1234-5678-9010",
        "cardholder_name": "Admin User",
        "cvv": "789",
        "expiry_date": "12/26",
        "billing_address": "Unknown Address, Dubai, UAE",
        "location": "Dubai, United Arab Emirates",
        "ip_address": "85.12.34.56",  # UAE IP
        "device_info": "Unknown Device"
    }
    
    print(f"{Colors.MAGENTA}Purchase Details:{Colors.RESET}")
    print(f"   Merchant: {transaction_data['merchant_name']}")
    print(f"   Amount: ${transaction_data['amount']:.2f}")
    print(f"   Location: {transaction_data['location']}")
    print(f"   IP: {transaction_data['ip_address']}")
    print(f"   Description: {transaction_data['description']}\n")
    
    print(f"{Colors.RED}🚨 Fraud indicators detected:{Colors.RESET}")
    print(f"{Colors.RED}   • Unusual location (Dubai, UAE){Colors.RESET}")
    print(f"{Colors.RED}   • Very high amount ($9,999.99){Colors.RESET}")
    print(f"{Colors.RED}   • Unknown device{Colors.RESET}")
    print(f"{Colors.RED}   • Foreign IP address{Colors.RESET}\n")
    
    print(f"{Colors.CYAN}⏳ Running fraud detection algorithms...{Colors.RESET}\n")
    
    response = requests.post(
        f"{BASE_URL}/transactions/submit",
        json=transaction_data,
        headers=headers
    )
    
    if response.status_code in [200, 201]:
        result = response.json()
        
        print_result(
            result['classification'],
            result['risk_score'],
            result['status'],
            result['explanation']
        )
        
        # If fraud, show what happened
        if result['classification'] == 'FRAUD':
            print(f"{Colors.RED}{Colors.BOLD}🚨 TRANSACTION BLOCKED!{Colors.RESET}")
            print(f"{Colors.RED}This transaction has been automatically blocked for your protection.{Colors.RESET}")
            print(f"{Colors.RED}A notification has been sent to the account holder.{Colors.RESET}")
            print(f"{Colors.RED}If this was a legitimate purchase, please contact customer support.{Colors.RESET}\n")
        
        return result
    else:
        print(f"{Colors.RED}❌ Transaction failed!{Colors.RESET}")
        print(f"   Error: {response.text}")
        return None


def scenario_4_user_confirms_suspicious():
    """Scenario 4: User confirms a suspicious transaction"""
    
    print_header("SCENARIO 4: USER CONFIRMS SUSPICIOUS TRANSACTION")
    
    # Login
    login_response = requests.post(
        f"{BASE_URL}/auth/login",
        data={"username": "admin", "password": "admin123"}
    )
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create a suspicious transaction first
    print_section("Step 1: Creating Suspicious Transaction")
    transaction_data = {
        "amount": 599.99,
        "merchant_name": "Electronics Store",
        "transaction_type": "ONLINE",
        "description": "Gaming Console",
        "card_number": "4532-1234-5678-9010",
        "cardholder_name": "Admin User",
        "cvv": "123",
        "expiry_date": "12/26"
    }
    
    response = requests.post(
        f"{BASE_URL}/transactions/submit",
        json=transaction_data,
        headers=headers
    )
    
    if response.status_code in [200, 201]:
        result = response.json()
        transaction_id = result['id']
        
        print(f"{Colors.YELLOW}Transaction Status: {result['status']}{Colors.RESET}")
        print(f"{Colors.YELLOW}Classification: {result['classification']}{Colors.RESET}\n")
        
        if result['status'] == 'PENDING':
            # User confirms the transaction
            print_section("Step 2: User Confirms Transaction")
            print(f"{Colors.MAGENTA}User receives notification: 'Did you make this $599.99 purchase?'{Colors.RESET}")
            print(f"{Colors.GREEN}User responds: YES, I made this purchase{Colors.RESET}\n")
            
            confirm_response = requests.post(
                f"{BASE_URL}/transactions/{transaction_id}/respond",
                json={"response": "YES"},
                headers=headers
            )
            
            if confirm_response.status_code == 200:
                confirmed = confirm_response.json()
                print(f"{Colors.GREEN}✅ Transaction Approved!{Colors.RESET}")
                print(f"   Status: {confirmed['status']}")
                print(f"   Message: {confirmed.get('message', 'Transaction confirmed by user')}\n")
            else:
                print(f"{Colors.RED}❌ Confirmation failed: {confirm_response.text}{Colors.RESET}\n")
    else:
        print(f"{Colors.RED}❌ Transaction creation failed{Colors.RESET}\n")


def run_all_scenarios():
    """Run all user scenarios"""
    
    print(f"\n{Colors.BOLD}{Colors.BLUE}")
    print("╔" + "═" * 98 + "╗")
    print("║" + " " * 98 + "║")
    print("║" + "HYBRID FRAUD SHIELD - REAL-WORLD USER SCENARIO TESTING".center(98) + "║")
    print("║" + f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}".center(98) + "║")
    print("║" + " " * 98 + "║")
    print("╚" + "═" * 98 + "╝")
    print(f"{Colors.RESET}\n")
    
    results = []
    
    # Scenario 1: Safe
    try:
        result1 = scenario_1_safe_coffee_purchase()
        results.append(("Coffee Purchase", result1))
    except Exception as e:
        print(f"{Colors.RED}❌ Scenario 1 Error: {e}{Colors.RESET}\n")
    
    input(f"{Colors.CYAN}Press Enter to continue to Scenario 2...{Colors.RESET}")
    
    # Scenario 2: Suspicious
    try:
        result2 = scenario_2_suspicious_laptop()
        results.append(("Laptop Purchase", result2))
    except Exception as e:
        print(f"{Colors.RED}❌ Scenario 2 Error: {e}{Colors.RESET}\n")
    
    input(f"{Colors.CYAN}Press Enter to continue to Scenario 3...{Colors.RESET}")
    
    # Scenario 3: Fraud
    try:
        result3 = scenario_3_fraud_international()
        results.append(("International Purchase", result3))
    except Exception as e:
        print(f"{Colors.RED}❌ Scenario 3 Error: {e}{Colors.RESET}\n")
    
    input(f"{Colors.CYAN}Press Enter to continue to Scenario 4...{Colors.RESET}")
    
    # Scenario 4: User confirmation
    try:
        scenario_4_user_confirms_suspicious()
    except Exception as e:
        print(f"{Colors.RED}❌ Scenario 4 Error: {e}{Colors.RESET}\n")
    
    # Summary
    print_header("TEST SUMMARY")
    
    for name, result in results:
        if result:
            color = Colors.GREEN if result['classification'] == 'SAFE' else Colors.YELLOW if result['classification'] == 'SUSPICIOUS' else Colors.RED
            print(f"{color}• {name}:{Colors.RESET}")
            print(f"  Classification: {color}{result['classification']}{Colors.RESET}")
            print(f"  Risk Score: {result['risk_score']:.2%}")
            print(f"  Status: {result['status']}\n")
    
    print(f"{Colors.BOLD}Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Colors.RESET}\n")


if __name__ == "__main__":
    print(f"{Colors.YELLOW}⚠️ Make sure the API server is running at {BASE_URL}{Colors.RESET}\n")
    
    try:
        # Test connection
        response = requests.get(f"{BASE_URL}/docs", timeout=2)
        print(f"{Colors.GREEN}✅ API server is running!{Colors.RESET}\n")
    except:
        print(f"{Colors.RED}❌ Cannot connect to API server!{Colors.RESET}")
        print(f"{Colors.RED}Please start the server first:{Colors.RESET}")
        print(f"{Colors.CYAN}cd backend && E:/Research/Biin/Fraud_Ditection_Enhance/.venv/Scripts/python.exe -m uvicorn app.main:app --reload{Colors.RESET}\n")
        exit(1)
    
    import time
    time.sleep(1)
    
    run_all_scenarios()
