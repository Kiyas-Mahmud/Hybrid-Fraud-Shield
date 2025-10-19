#!/usr/bin/env python3
"""
Test script for Fusion API endpoints
"""
import requests
import json
import time
import sys
from pathlib import Path

API_BASE = "http://127.0.0.1:8000"

def test_health_endpoint():
    """Test the health endpoint"""
    try:
        print("Testing /health endpoint...")
        response = requests.get(f"{API_BASE}/health", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print("PASS: Health endpoint working!")
            print(f"   Status: {data.get('status', 'N/A')}")
            print(f"   Models Ready: {data.get('models_loaded', 'N/A')}")
            print(f"   Total Models: {data.get('total_models', 'N/A')}")
            return True
        else:
            print(f"FAIL: Health endpoint failed with status: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("FAIL: Cannot connect to API server. Is it running?")
        return False
    except Exception as e:
        print(f"FAIL: Error testing health endpoint: {e}")
        return False

def test_prediction_endpoint():
    """Test the prediction endpoint with sample data"""
    try:
        print("\nTesting /predict endpoint...")
        
        # Load fraud sample
        fraud_sample_path = Path("../sample_requests/fraud_sample.json")
        if fraud_sample_path.exists():
            with open(fraud_sample_path, 'r') as f:
                fraud_data = json.load(f)
            
            print("Testing with fraud sample...")
            response = requests.post(f"{API_BASE}/predict", json=fraud_data, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                print("PASS: Fraud prediction successful!")
                print(f"   Prediction: {'FRAUD' if result.get('is_fraud', False) else 'LEGITIMATE'}")
                print(f"   Confidence: {result.get('fraud_probability', 0):.4f}")
                print(f"   Processing Time: {result.get('processing_time_ms', 0):.1f}ms")
            else:
                print(f"FAIL: Fraud prediction failed: {response.status_code}")
                print(f"   Error: {response.text}")
                return False
        
        # Load safe sample
        safe_sample_path = Path("../sample_requests/safe_sample.json")
        if safe_sample_path.exists():
            with open(safe_sample_path, 'r') as f:
                safe_data = json.load(f)
            
            print("\nTesting with safe sample...")
            response = requests.post(f"{API_BASE}/predict", json=safe_data, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                print("PASS: Safe prediction successful!")
                print(f"   Prediction: {'FRAUD' if result.get('is_fraud', False) else 'LEGITIMATE'}")
                print(f"   Confidence: {result.get('fraud_probability', 0):.4f}")
                print(f"   Processing Time: {result.get('processing_time_ms', 0):.1f}ms")
            else:
                print(f"FAIL: Safe prediction failed: {response.status_code}")
                print(f"   Error: {response.text}")
                return False
                
        return True
        
    except Exception as e:
        print(f"FAIL: Error testing prediction endpoint: {e}")
        return False

def test_info_endpoint():
    """Test the info endpoint"""
    try:
        print("\nTesting /info endpoint...")
        response = requests.get(f"{API_BASE}/info", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print("PASS: Info endpoint working!")
            print(f"   API Version: {data.get('version', 'N/A')}")
            print(f"   ML Models: {len(data.get('models', {}).get('ml_models', []))}")
            print(f"   DL Models: {len(data.get('models', {}).get('dl_models', []))}")
            return True
        else:
            print(f"FAIL: Info endpoint failed with status: {response.status_code}")
            return False
    except Exception as e:
        print(f"FAIL: Error testing info endpoint: {e}")
        return False

def main():
    """Main test function"""
    print("Starting Fusion API Tests...")
    print("=" * 50)
    
    # Wait a moment for server to start
    print("Waiting for server to start...")
    time.sleep(3)
    
    success_count = 0
    total_tests = 3
    
    # Test health endpoint
    if test_health_endpoint():
        success_count += 1
    
    # Test prediction endpoint
    if test_prediction_endpoint():
        success_count += 1
        
    # Test info endpoint
    if test_info_endpoint():
        success_count += 1
    
    print("\n" + "=" * 50)
    print(f"Test Results: {success_count}/{total_tests} passed")
    
    if success_count == total_tests:
        print("All tests passed! API is working correctly.")
        return 0
    else:
        print("Some tests failed. Check the API server and try again.")
        return 1

if __name__ == "__main__":
    sys.exit(main())