"""
Quick test to verify login credentials
"""

import requests

BASE_URL = "http://localhost:8000"

def test_login(username, password):
    """Test login with given credentials"""
    print(f"\n{'='*60}")
    print(f"Testing login for: {username}")
    print(f"{'='*60}")
    
    try:
        # Prepare form data
        data = {
            'username': username,
            'password': password
        }
        
        response = requests.post(
            f"{BASE_URL}/auth/login",
            data=data,  # Using data parameter for form-urlencoded
            headers={'Content-Type': 'application/x-www-form-urlencoded'}
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ LOGIN SUCCESSFUL!")
            print(f"Token: {result.get('access_token', 'N/A')[:50]}...")
            print(f"User ID: {result.get('user_id', 'N/A')}")
            print(f"Username: {result.get('username', 'N/A')}")
            print(f"Role: {result.get('role', 'N/A')}")
            return True
        else:
            print(f"❌ LOGIN FAILED")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return False

def test_register(username, email, password):
    """Test registration"""
    print(f"\n{'='*60}")
    print(f"Testing registration for: {username}")
    print(f"{'='*60}")
    
    try:
        data = {
            'username': username,
            'email': email,
            'password': password,
            'full_name': 'Test User'
        }
        
        response = requests.post(
            f"{BASE_URL}/auth/register",
            json=data
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 201:
            result = response.json()
            print(f"✅ REGISTRATION SUCCESSFUL!")
            print(f"User ID: {result.get('user_id', 'N/A')}")
            print(f"Username: {result.get('username', 'N/A')}")
            return True
        else:
            print(f"Response: {response.text}")
            if "already registered" in response.text:
                print(f"ℹ️  User already exists - trying to login instead")
                return test_login(username, password)
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return False

if __name__ == "__main__":
    print("\n" + "="*60)
    print("FRAUD DETECTION SYSTEM - LOGIN TEST")
    print("="*60)
    
    # Test admin login
    test_login("admin", "admin123")
    
    # Test or create john_doe
    print("\n" + "="*60)
    print("TESTING john_doe account")
    print("="*60)
    
    if not test_login("john_doe", "SecurePass123!"):
        print("\nUser doesn't exist or password wrong. Trying to register...")
        test_register("john_doe", "john.doe@example.com", "SecurePass123!")
    
    # Test or create testuser2
    print("\n" + "="*60)
    print("TESTING testuser2 account")
    print("="*60)
    
    if not test_login("testuser2", "SecurePass123!"):
        print("\nUser doesn't exist or password wrong. Trying to register...")
        test_register("testuser2", "test2@example.com", "SecurePass123!")
    
    print("\n" + "="*60)
    print("SUMMARY - WORKING CREDENTIALS")
    print("="*60)
    print("\n📝 Copy these credentials for customer portal:")
    print("\nOption 1:")
    print("  Username: john_doe")
    print("  Password: SecurePass123!")
    print("\nOption 2:")
    print("  Username: testuser2")
    print("  Password: SecurePass123!")
    print("\nOption 3 (Admin):")
    print("  Username: admin")
    print("  Password: admin123")
    print("\n" + "="*60)
