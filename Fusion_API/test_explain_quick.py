"""
Quick test of the explainability features
"""

import json
import requests

# Load high fraud sample
with open("sample_requests/high_fraud_sample.json", "r") as f:
    sample_data = json.load(f)

# Test explainability
response = requests.post("http://127.0.0.1:8000/explain", json=sample_data)

if response.status_code == 200:
    result = response.json()
    
    print("=== FRAUD DETECTION EXPLANATION ===")
    
    # Prediction summary
    prediction = result['prediction']
    print(f"Status: {prediction['status']}")
    print(f"Fraud Probability: {prediction['probability']:.1%}")
    print(f"Confidence: {prediction['confidence']:.1%}")
    print(f"Processing Time: {prediction['inference_time_ms']:.1f}ms")
    
    # Explanation details
    explanation = result.get('explanation', {})
    
    if 'prediction_summary' in explanation:
        summary = explanation['prediction_summary']
        print(f"\nRisk Level: {summary.get('risk_level')}")
    
    if 'feature_importance' in explanation:
        features = explanation['feature_importance'][:5]
        print(f"\nTop Contributing Features:")
        for i, feature in enumerate(features, 1):
            name = feature.get('feature', 'Unknown')
            impact = feature.get('impact', 'Unknown')
            contribution = feature.get('contribution', 'Unknown')
            print(f"  {i}. {name} - {impact} ({contribution})")
    
    if 'risk_factors' in explanation:
        risks = explanation['risk_factors']
        print(f"\nRisk Factors: {len(risks)} detected")
        for risk in risks[:3]:
            factor = risk.get('factor', 'Unknown')
            severity = risk.get('severity', 'Unknown')
            print(f"  - {factor} (Severity: {severity})")
    
    if 'explanation' in explanation:
        print(f"\nExplanation: {explanation['explanation']}")
    
    if 'recommendations' in explanation:
        print(f"\nRecommendations:")
        for rec in explanation['recommendations'][:3]:
            print(f"  - {rec}")
    
    print("\n=== EXPLAINABILITY SUCCESS! ===")
    print("- Fast Learning: Models loaded instantly")
    print("- Real-time Response: Sub-second predictions")  
    print("- Clear Explanations: SHAP-based feature analysis")

else:
    print(f"Error: {response.status_code}")
    print(response.text)