"""
Automated API Testing Script for Hybrid Fraud Shield
Tests all endpoints with different scenarios
"""

import requests
import json
import time
from typing import Dict, Any
from datetime import datetime

# Configuration
BASE_URL = "http://127.0.0.1:8000"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

# Color codes for output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

class APITester:
    def __init__(self):
        self.base_url = BASE_URL
        self.admin_token = None
        self.user_token = None
        self.test_user_id = None
        self.test_transaction_id = None
        self.test_notification_id = None
        self.passed_tests = 0
        self.failed_tests = 0
        self.test_results = []
        
    def print_header(self, text: str):
        """Print formatted header"""
        print(f"\n{Colors.CYAN}{Colors.BOLD}{'='*80}{Colors.RESET}")
        print(f"{Colors.CYAN}{Colors.BOLD}{text:^80}{Colors.RESET}")
        print(f"{Colors.CYAN}{Colors.BOLD}{'='*80}{Colors.RESET}\n")
    
    def print_test(self, test_name: str, status: str, message: str = ""):
        """Print test result"""
        if status == "PASS":
            icon = "✅"
            color = Colors.GREEN
            self.passed_tests += 1
        elif status == "FAIL":
            icon = "❌"
            color = Colors.RED
            self.failed_tests += 1
        else:
            icon = "⚠️"
            color = Colors.YELLOW
        
        print(f"{color}{icon} {test_name}{Colors.RESET}")
        if message:
            print(f"   {Colors.YELLOW}{message}{Colors.RESET}")
        
        self.test_results.append({
            "test": test_name,
            "status": status,
            "message": message
        })
    
    def make_request(self, method: str, endpoint: str, data: Dict = None, 
                    token: str = None, form_data: bool = False) -> Dict[str, Any]:
        """Make HTTP request"""
        url = f"{self.base_url}{endpoint}"
        headers = {}
        
        if token:
            headers["Authorization"] = f"Bearer {token}"
        
        try:
            if method == "GET":
                response = requests.get(url, headers=headers)
            elif method == "POST":
                if form_data:
                    response = requests.post(url, data=data, headers=headers)
                else:
                    headers["Content-Type"] = "application/json"
                    response = requests.post(url, json=data, headers=headers)
            elif method == "PUT":
                headers["Content-Type"] = "application/json"
                response = requests.put(url, json=data, headers=headers)
            elif method == "DELETE":
                response = requests.delete(url, headers=headers)
            else:
                return {"error": "Invalid method"}
            
            return {
                "status_code": response.status_code,
                "data": response.json() if response.text else {},
                "success": response.status_code < 400
            }
        except Exception as e:
            return {
                "error": str(e),
                "success": False
            }
    
    # ==================== AUTHENTICATION TESTS ====================
    
    def test_register_user(self):
        """Test user registration"""
        self.print_header("AUTHENTICATION TESTS")
        
        # Test 1: Register new user
        user_data = {
            "username": f"testuser_{int(time.time())}",
            "email": f"test_{int(time.time())}@example.com",
            "password": "TestPass123!",
            "full_name": "Test User",
            "phone": "+1-555-0199"
        }
        
        result = self.make_request("POST", "/api/v1/auth/register", user_data)
        
        if result.get("success") and result["status_code"] == 201:
            # Capture user_id from response
            response_data = result.get("data", {})
            self.test_user_id = response_data.get("user_id") or response_data.get("id")
            
            self.print_test(
                "User Registration", 
                "PASS", 
                f"User created: {user_data['username']} (ID: {self.test_user_id})"
            )
            return user_data
        else:
            self.print_test(
                "User Registration", 
                "FAIL", 
                f"Status: {result.get('status_code')}, Error: {result.get('data')}"
            )
            return None
    
    def test_login_admin(self):
        """Test admin login"""
        login_data = {
            "username": ADMIN_USERNAME,
            "password": ADMIN_PASSWORD
        }
        
        result = self.make_request("POST", "/auth/login", login_data, form_data=True)
        
        if result.get("success"):
            self.admin_token = result["data"].get("access_token")
            self.print_test(
                "Admin Login", 
                "PASS", 
                f"Token: {self.admin_token[:20]}..."
            )
            return True
        else:
            self.print_test("Admin Login", "FAIL", f"Error: {result.get('data')}")
            return False
    
    def test_login_user(self, user_data: Dict):
        """Test regular user login"""
        if not user_data:
            self.print_test("User Login", "FAIL", "No user data available")
            return False
        
        login_data = {
            "username": user_data["username"],
            "password": user_data["password"]
        }
        
        result = self.make_request("POST", "/auth/login", login_data, form_data=True)
        
        if result.get("success"):
            self.user_token = result["data"].get("access_token")
            self.print_test(
                "User Login", 
                "PASS", 
                f"Token: {self.user_token[:20]}..."
            )
            return True
        else:
            self.print_test("User Login", "FAIL", f"Error: {result.get('data')}")
            return False
    
    def test_invalid_login(self):
        """Test login with wrong credentials"""
        login_data = {
            "username": "wronguser",
            "password": "wrongpass"
        }
        
        result = self.make_request("POST", "/auth/login", login_data, form_data=True)
        
        if result.get("status_code") == 401:
            self.print_test(
                "Invalid Login (Should Fail)", 
                "PASS", 
                "Correctly rejected invalid credentials"
            )
        else:
            self.print_test(
                "Invalid Login (Should Fail)", 
                "FAIL", 
                "Should have rejected invalid credentials"
            )
    
    # ==================== TRANSACTION TESTS ====================
    
    def test_submit_safe_transaction(self):
        """Test submitting a SAFE transaction"""
        self.print_header("TRANSACTION TESTS - SAFE")
        
        transaction_data = {
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
        
        result = self.make_request("POST", "/transactions/submit", transaction_data, self.user_token)
        
        if result.get("success"):
            data = result["data"]
            classification = data.get("classification")
            risk_score = data.get("risk_score")
            
            if classification == "SAFE":
                self.test_transaction_id = data.get("id")
                self.print_test(
                    "Submit SAFE Transaction", 
                    "PASS", 
                    f"Classification: {classification}, Risk: {risk_score:.2f}"
                )
            else:
                self.print_test(
                    "Submit SAFE Transaction", 
                    "FAIL", 
                    f"Expected SAFE, got {classification}"
                )
        else:
            self.print_test("Submit SAFE Transaction", "FAIL", f"Error: {result.get('data')}")
    
    def test_submit_suspicious_transaction(self):
        """Test submitting a SUSPICIOUS transaction"""
        self.print_header("TRANSACTION TESTS - SUSPICIOUS")
        
        transaction_data = {
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
        
        result = self.make_request("POST", "/transactions/submit", transaction_data, self.user_token)
        
        if result.get("success"):
            data = result["data"]
            classification = data.get("classification")
            risk_score = data.get("risk_score")
            status = data.get("status")
            
            if classification in ["SUSPICIOUS", "FRAUD"]:
                self.test_transaction_id = data.get("id")
                self.print_test(
                    "Submit SUSPICIOUS Transaction", 
                    "PASS", 
                    f"Classification: {classification}, Status: {status}, Risk: {risk_score:.2f}"
                )
            else:
                self.print_test(
                    "Submit SUSPICIOUS Transaction", 
                    "FAIL", 
                    f"Expected SUSPICIOUS/FRAUD, got {classification}"
                )
        else:
            self.print_test("Submit SUSPICIOUS Transaction", "FAIL", f"Error: {result.get('data')}")
    
    def test_submit_fraud_transaction(self):
        """Test submitting a FRAUD transaction"""
        self.print_header("TRANSACTION TESTS - FRAUD")
        
        transaction_data = {
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
        
        result = self.make_request("POST", "/transactions/submit", transaction_data, self.user_token)
        
        if result.get("success"):
            data = result["data"]
            classification = data.get("classification")
            risk_score = data.get("risk_score")
            status = data.get("status")
            
            if classification == "FRAUD" or risk_score >= 0.7:
                self.print_test(
                    "Submit FRAUD Transaction", 
                    "PASS", 
                    f"Classification: {classification}, Status: {status}, Risk: {risk_score:.2f}"
                )
            else:
                self.print_test(
                    "Submit FRAUD Transaction", 
                    "FAIL", 
                    f"Expected FRAUD, got {classification} with risk {risk_score}"
                )
        else:
            self.print_test("Submit FRAUD Transaction", "FAIL", f"Error: {result.get('data')}")
    
    def test_submit_without_card_data(self):
        """Test submitting transaction without card data (backward compatibility)"""
        transaction_data = {
            "amount": 25.99,
            "merchant_name": "Shell Gas Station",
            "transaction_type": "IN_STORE",
            "description": "Fuel purchase",
            "location": "Chicago, IL, USA",
            "device_info": "Samsung Galaxy S23",
            "ip_address": "192.168.1.110"
        }
        
        result = self.make_request("POST", "/transactions/submit", transaction_data, self.user_token)
        
        if result.get("success"):
            self.print_test(
                "Submit Transaction (No Card Data)", 
                "PASS", 
                "Backward compatibility working"
            )
        else:
            self.print_test(
                "Submit Transaction (No Card Data)", 
                "FAIL", 
                f"Error: {result.get('data')}"
            )
    
    def test_view_my_transactions(self):
        """Test viewing user's own transactions"""
        self.print_header("TRANSACTION RETRIEVAL TESTS")
        
        result = self.make_request("GET", "/api/v1/transactions/my", token=self.user_token)
        
        if result.get("success"):
            transactions = result["data"]
            self.print_test(
                "View My Transactions", 
                "PASS", 
                f"Retrieved {len(transactions)} transactions"
            )
        else:
            self.print_test("View My Transactions", "FAIL", f"Error: {result.get('data')}")
    
    def test_unauthorized_transaction_access(self):
        """Test accessing transactions without token"""
        result = self.make_request("GET", "/transactions/")
        
        if result.get("status_code") in [401, 403]:
            self.print_test(
                "Unauthorized Access (Should Fail)", 
                "PASS", 
                "Correctly blocked unauthorized access"
            )
        else:
            self.print_test(
                "Unauthorized Access (Should Fail)", 
                "FAIL", 
                f"Should have blocked unauthorized access, got status {result.get('status_code')}"
            )
    
    # ==================== NOTIFICATION TESTS ====================
    
    def test_view_notifications(self):
        """Test viewing notifications"""
        self.print_header("NOTIFICATION TESTS")
        
        result = self.make_request("GET", "/api/v1/notifications/my", token=self.user_token)
        
        if result.get("success"):
            notifications = result["data"]
            if len(notifications) > 0:
                self.test_notification_id = notifications[0].get("id")
            self.print_test(
                "View Notifications", 
                "PASS", 
                f"Retrieved {len(notifications)} notifications"
            )
        else:
            self.print_test("View Notifications", "FAIL", f"Error: {result.get('data')}")
    
    def test_mark_notification_read(self):
        """Test marking notification as read"""
        if not self.test_notification_id:
            self.print_test("Mark Notification Read", "PASS", "No notifications to mark (skipped)")
            return
        
        result = self.make_request(
            "POST", 
            f"/notifications/{self.test_notification_id}/read",
            token=self.user_token
        )
        
        if result.get("success"):
            self.print_test(
                "Mark Notification Read", 
                "PASS", 
                f"Notification {self.test_notification_id} marked as read"
            )
        else:
            self.print_test("Mark Notification Read", "FAIL", f"Error: {result.get('data')}")
    
    # ==================== TRANSACTION RESPONSE TESTS ====================
    
    def test_respond_to_transaction(self):
        """Test responding to suspicious transaction"""
        self.print_header("TRANSACTION RESPONSE TESTS")
        
        if not self.test_transaction_id:
            self.print_test("Respond to Transaction", "PASS", "No pending transaction to respond to (skipped)")
            return
        
        # Respond YES (legitimate)
        response_data = {"response": "YES"}
        result = self.make_request(
            "POST",
            f"/transactions/{self.test_transaction_id}/respond",
            response_data,
            self.user_token
        )
        
        if result.get("success"):
            self.print_test(
                "Respond YES to Transaction", 
                "PASS", 
                f"Transaction {self.test_transaction_id} approved"
            )
        else:
            self.print_test("Respond YES to Transaction", "FAIL", f"Error: {result.get('data')}")
    
    # ==================== ADMIN TESTS ====================
    
    def test_admin_view_users(self):
        """Test admin viewing all users"""
        self.print_header("ADMIN TESTS - USER MANAGEMENT")
        
        result = self.make_request("GET", "/api/v1/admin/users", token=self.admin_token)
        
        if result.get("success"):
            users = result["data"]
            self.print_test(
                "Admin: View All Users", 
                "PASS", 
                f"Retrieved {len(users)} users"
            )
        else:
            self.print_test("Admin: View All Users", "FAIL", f"Error: {result.get('data')}")
    
    def test_admin_view_transactions(self):
        """Test admin viewing all transactions"""
        result = self.make_request("GET", "/api/v1/admin/transactions", token=self.admin_token)
        
        if result.get("success"):
            transactions = result["data"]
            self.print_test(
                "Admin: View All Transactions", 
                "PASS", 
                f"Retrieved {len(transactions)} transactions"
            )
        else:
            self.print_test("Admin: View All Transactions", "FAIL", f"Error: {result.get('data')}")
    
    def test_admin_filter_transactions(self):
        """Test admin filtering transactions"""
        # Filter by PENDING status
        result = self.make_request(
            "GET", 
            "/admin/transactions?status=PENDING", 
            token=self.admin_token
        )
        
        if result.get("success"):
            self.print_test(
                "Admin: Filter Transactions (PENDING)", 
                "PASS", 
                f"Retrieved {len(result['data'])} pending transactions"
            )
        else:
            self.print_test("Admin: Filter Transactions", "FAIL", f"Error: {result.get('data')}")
    
    def test_admin_statistics(self):
        """Test admin viewing statistics"""
        self.print_header("ADMIN TESTS - STATISTICS")
        
        result = self.make_request("GET", "/admin/dashboard/stats", token=self.admin_token)
        
        if result.get("success"):
            stats = result["data"]
            self.print_test(
                "Admin: View Statistics", 
                "PASS", 
                f"Total Users: {stats.get('total_users')}, Total Transactions: {stats.get('total_transactions')}"
            )
        else:
            self.print_test("Admin: View Statistics", "FAIL", f"Error: {result.get('data')}")
    
    def test_admin_block_user(self):
        """Test admin blocking a user"""
        if not self.test_user_id:
            self.print_test("Admin: Block User", "PASS", "No test user available (skipped)")
            return
        
        block_data = {"is_blocked": True}
        result = self.make_request(
            "POST",
            f"/admin/users/{self.test_user_id}/block",
            block_data,
            self.admin_token
        )
        
        if result.get("success"):
            self.print_test(
                "Admin: Block User", 
                "PASS", 
                f"User {self.test_user_id} blocked"
            )
        else:
            self.print_test("Admin: Block User", "FAIL", f"Error: {result.get('data')}")
    
    def test_admin_unblock_user(self):
        """Test admin unblocking a user"""
        if not self.test_user_id:
            self.print_test("Admin: Unblock User", "PASS", "No test user available (skipped)")
            return
        
        unblock_data = {"is_blocked": False}
        result = self.make_request(
            "POST",
            f"/admin/users/{self.test_user_id}/block",
            unblock_data,
            self.admin_token
        )
        
        if result.get("success"):
            self.print_test(
                "Admin: Unblock User", 
                "PASS", 
                f"User {self.test_user_id} unblocked"
            )
        else:
            self.print_test("Admin: Unblock User", "FAIL", f"Error: {result.get('data')}")
    
    def test_non_admin_access(self):
        """Test regular user accessing admin endpoints"""
        self.print_header("SECURITY TESTS")
        
        result = self.make_request("GET", "/api/v1/admin/users", token=self.user_token)
        
        if result.get("status_code") == 403:
            self.print_test(
                "Non-Admin Access (Should Fail)", 
                "PASS", 
                "Correctly blocked non-admin from admin endpoint"
            )
        else:
            self.print_test(
                "Non-Admin Access (Should Fail)", 
                "FAIL", 
                "Should have blocked non-admin access"
            )
    
    # ==================== MAIN TEST RUNNER ====================
    
    def run_all_tests(self):
        """Run all test suites"""
        print(f"\n{Colors.BOLD}{Colors.BLUE}")
        print("╔" + "═" * 78 + "╗")
        print("║" + " " * 78 + "║")
        print("║" + "HYBRID FRAUD SHIELD - AUTOMATED API TESTING".center(78) + "║")
        print("║" + f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}".center(78) + "║")
        print("║" + " " * 78 + "║")
        print("╚" + "═" * 78 + "╝")
        print(f"{Colors.RESET}\n")
        
        # Authentication Tests
        user_data = self.test_register_user()
        self.test_login_admin()
        self.test_login_user(user_data)
        self.test_invalid_login()
        
        # Transaction Tests
        self.test_submit_safe_transaction()
        self.test_submit_suspicious_transaction()
        self.test_submit_fraud_transaction()
        self.test_submit_without_card_data()
        self.test_view_my_transactions()
        self.test_unauthorized_transaction_access()
        
        # Notification Tests
        self.test_view_notifications()
        self.test_mark_notification_read()
        
        # Transaction Response Tests
        self.test_respond_to_transaction()
        
        # Admin Tests
        self.test_admin_view_users()
        self.test_admin_view_transactions()
        self.test_admin_filter_transactions()
        self.test_admin_statistics()
        self.test_admin_block_user()
        self.test_admin_unblock_user()
        
        # Security Tests
        self.test_non_admin_access()
        
        # Print Summary
        self.print_summary()
    
    def print_summary(self):
        """Print test summary"""
        total_tests = self.passed_tests + self.failed_tests
        pass_rate = (self.passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"\n{Colors.BOLD}{Colors.CYAN}")
        print("╔" + "═" * 78 + "╗")
        print("║" + " " * 78 + "║")
        print("║" + "TEST SUMMARY".center(78) + "║")
        print("║" + " " * 78 + "║")
        print("╚" + "═" * 78 + "╝")
        print(f"{Colors.RESET}")
        
        print(f"\n{Colors.BOLD}Total Tests:{Colors.RESET} {total_tests}")
        print(f"{Colors.GREEN}{Colors.BOLD}✅ Passed:{Colors.RESET} {self.passed_tests}")
        print(f"{Colors.RED}{Colors.BOLD}❌ Failed:{Colors.RESET} {self.failed_tests}")
        print(f"{Colors.CYAN}{Colors.BOLD}Pass Rate:{Colors.RESET} {pass_rate:.1f}%")
        
        if self.failed_tests > 0:
            print(f"\n{Colors.RED}{Colors.BOLD}Failed Tests:{Colors.RESET}")
            for result in self.test_results:
                if result["status"] == "FAIL":
                    print(f"  • {result['test']}: {result['message']}")
        
        print(f"\n{Colors.BOLD}Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Colors.RESET}\n")
        
        # Save results to file
        self.save_results()
    
    def save_results(self):
        """Save test results to JSON file"""
        results = {
            "timestamp": datetime.now().isoformat(),
            "total_tests": self.passed_tests + self.failed_tests,
            "passed": self.passed_tests,
            "failed": self.failed_tests,
            "pass_rate": (self.passed_tests / (self.passed_tests + self.failed_tests) * 100) if (self.passed_tests + self.failed_tests) > 0 else 0,
            "results": self.test_results
        }
        
        filename = f"test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"{Colors.BLUE}📄 Results saved to: {filename}{Colors.RESET}\n")


if __name__ == "__main__":
    print(f"{Colors.YELLOW}⚠️  Make sure the API server is running at {BASE_URL}{Colors.RESET}\n")
    
    # Wait a moment for user to read
    time.sleep(2)
    
    # Run tests
    tester = APITester()
    tester.run_all_tests()
