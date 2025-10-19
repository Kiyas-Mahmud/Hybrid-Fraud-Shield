"""
Simple demonstration of the Fraud Detection API explainability features
"""

import json
import requests
import time
from pathlib import Path

def test_explainability_demo():
    """Demonstrate the three key capabilities"""
    
    base_url = "http://127.0.0.1:8000"
    
    print("FRAUD DETECTION API - EXPLAINABILITY DEMONSTRATION")
    print("="*55)
    
    # 1. Check if API is ready (demonstrates fast learning)
    print("\n1. FAST LEARNING - Model Readiness Check")
    print("-" * 40)
    
    try:
        start_time = time.time()
        response = requests.get(f"{base_url}/health")
        ready_time = (time.time() - start_time) * 1000
        
        if response.status_code == 200:
            health = response.json()
            print(f"API Status: {health['status']}")
            print(f"Response Time: {ready_time:.2f} ms")
            
            models_info = health.get('models_loaded', {})
            print(f"Explainer Ready: {models_info.get('explainer_ready', False)}")
            
        else:
            print("API not ready. Please start the server first.")
            return
            
    except Exception as e:
        print(f"Cannot connect to API: {e}")
        print("Please make sure the server is running: python -m uvicorn main:app --reload")
        return
    
    # 2. Real-time prediction test
    print("\n2. REAL-TIME RESPONSE - Fraud Detection")
    print("-" * 40)
    
    # Use sample data (create a high-risk transaction)
    sample_transaction = {
        "v7_high_rank056": 2.5,
        "v19_high_rank055": 1.8,
        "v23_critical_rank017": 3.2,
        "v35_critical_rank039": 2.1,
        "v36_critical_rank037": 1.9,
        "v38_critical_rank021": 2.8,
        "v45_critical_rank006": 3.5,
        "v47_critical_rank019": 2.3
    }
    
    # Fill remaining features with normal values
    for i in range(len(sample_transaction), 63):
        sample_transaction[f"feature_{i}"] = 0.1
    
    try:
        start_time = time.time()
        response = requests.post(f"{base_url}/predict", json=sample_transaction)
        prediction_time = (time.time() - start_time) * 1000
        
        if response.status_code == 200:
            prediction = response.json()
            print(f"Prediction Time: {prediction_time:.2f} ms")
            print(f"Decision: {prediction['status']}")
            print(f"Fraud Probability: {prediction['probability']:.1%}")
            print(f"Confidence: {prediction['confidence']:.1%}")
            print(f"Real-time Capable: {'Yes' if prediction_time < 1000 else 'No'}")
        else:
            print("Prediction failed")
            return
            
    except Exception as e:
        print(f"Prediction error: {e}")
        return
    
    # 3. Clear explanations test
    print("\n3. CLEAR EXPLANATIONS - SHAP Analysis")
    print("-" * 40)
    
    try:
        start_time = time.time()
        response = requests.post(f"{base_url}/explain", json=sample_transaction)
        explanation_time = (time.time() - start_time) * 1000
        
        if response.status_code == 200:
            explanation = response.json()
            
            print(f"Explanation Time: {explanation_time:.2f} ms")
            
            # Extract key information
            exp_data = explanation.get('explanation', {})
            
            # Prediction summary
            if 'prediction_summary' in exp_data:
                summary = exp_data['prediction_summary']
                print(f"\nDecision Analysis:")
                print(f"  Status: {summary.get('status')}")
                print(f"  Risk Level: {summary.get('risk_level')}")
                print(f"  Confidence: {summary.get('confidence', 0):.1%}")
            
            # Top contributing features
            if 'feature_importance' in exp_data:
                features = exp_data['feature_importance'][:5]
                print(f"\nTop Contributing Factors:")
                for i, feature in enumerate(features, 1):
                    name = feature.get('feature', 'Unknown')
                    impact = feature.get('impact', 'Unknown')
                    contribution = feature.get('contribution', 'Unknown')
                    print(f"  {i}. {name} - {impact} ({contribution})")
            
            # Risk factors
            if 'risk_factors' in exp_data:
                risks = exp_data['risk_factors']
                print(f"\nRisk Factors Detected: {len(risks)}")
                for risk in risks[:3]:
                    factor = risk.get('factor', 'Unknown')
                    severity = risk.get('severity', 'Unknown')
                    print(f"  - {factor} (Severity: {severity})")
            
            # Human explanation
            if 'explanation' in exp_data:
                print(f"\nExplanation:")
                print(f"  {exp_data['explanation']}")
            
            # Recommendations
            if 'recommendations' in exp_data:
                recommendations = exp_data['recommendations']
                print(f"\nRecommendations:")
                for rec in recommendations[:3]:
                    print(f"  - {rec}")
                    
        else:
            print("Explanation failed")
            print(f"Error: {response.text}")
            return
            
    except Exception as e:
        print(f"Explanation error: {e}")
        return
    
    # Summary
    print(f"\n{'='*20} DEMONSTRATION SUMMARY {'='*20}")
    print("Successfully demonstrated all three capabilities:")
    print(f"  - Fast Learning: Pre-trained models ready in milliseconds")
    print(f"  - Real-time Response: {prediction_time:.0f}ms prediction time")
    print(f"  - Clear Explanations: {explanation_time:.0f}ms for detailed SHAP analysis")
    print("\nThe API provides enterprise-grade fraud detection with")
    print("transparent, explainable AI for regulatory compliance.")

def main():
    """Main demonstration"""
    test_explainability_demo()

if __name__ == "__main__":
    main()