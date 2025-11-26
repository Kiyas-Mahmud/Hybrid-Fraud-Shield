from typing import Dict, List, Tuple
from models.transaction import RiskClassification

class RiskClassifier:
    # Three-tier classification thresholds
    SAFE_THRESHOLD = 0.3          # risk < 0.3 → SAFE (auto-approve)
    SUSPICIOUS_THRESHOLD = 0.7    # 0.3 ≤ risk < 0.7 → SUSPICIOUS (ask user)
                                   # risk ≥ 0.7 → FRAUD (auto-block)
    
    # Amount-based thresholds (backup logic when ML model is too aggressive)
    SUSPICIOUS_AMOUNT_MIN = 150.0   # Amounts >= $150 may be suspicious
    SUSPICIOUS_AMOUNT_MAX = 2000.0  # Amounts <= $2000 may be suspicious
    FRAUD_AMOUNT_THRESHOLD = 3000.0 # Amounts > $3000 are high risk
    
    @staticmethod
    def classify(risk_score: float, amount: float = None, merchant_name: str = None, user_history: list = None) -> RiskClassification:
        """
        Classify transaction based on risk score and amount:
        - SAFE (risk < 0.3 AND amount < $150): Automatically approved
        - SUSPICIOUS (0.3 ≤ risk < 0.7 OR $150-$2000 with high risk): Requires user confirmation
        - FRAUD (risk ≥ 0.7 OR amount > $3000): Automatically blocked
        
        Priority rules:
        0. Small amount at familiar merchant with approved history → Always SAFE (NEW!)
        1. Low amount (< $150) + Low risk (< 0.3) → Always SAFE
        2. Very high amount (> $3000) → Always FRAUD
        3. High risk score (≥ 0.7) → Always FRAUD
        4. Medium amount ($150-$2000) + High risk (≥ 0.3) → SUSPICIOUS
        """
        # DEBUG: Log input values
        print(f"\n🔍 CLASSIFICATION DEBUG:")
        print(f"   Risk Score: {risk_score:.4f} ({risk_score * 100:.2f}%)")
        print(f"   Amount: ${amount if amount else 'None'}")
        print(f"   Merchant: {merchant_name if merchant_name else 'None'}")
        
        # If amount is provided, use hybrid logic
        if amount is not None:
            # Rule 0: Small recurring transactions at familiar merchants → Always SAFE
            # This overrides ML predictions for trusted merchants with good history
            if merchant_name and user_history and amount < 100:
                # Check if user has approved transactions at this merchant
                approved_at_merchant = [
                    t for t in user_history 
                    if t.get('merchant_name', '').lower() == merchant_name.lower() 
                    and t.get('status') == 'APPROVED'
                ]
                if len(approved_at_merchant) > 0:
                    print(f"   ✅ Rule 0 matched: Small amount (${amount} < $100) at familiar merchant '{merchant_name}' with {len(approved_at_merchant)} approved transactions → SAFE (Override ML)")
                    return RiskClassification.SAFE
            
            # Rule 1: Small amounts with low risk → Always SAFE (most common case)
            if amount < RiskClassifier.SUSPICIOUS_AMOUNT_MIN and risk_score < RiskClassifier.SAFE_THRESHOLD:
                print(f"   ✅ Rule 1 matched: Small amount (${amount} < $150) + Low risk ({risk_score:.4f} < 0.3) → SAFE")
                return RiskClassification.SAFE
            
            # Rule 2: Very high amounts → Always FRAUD (regardless of risk score)
            if amount > RiskClassifier.FRAUD_AMOUNT_THRESHOLD:
                print(f"   🚨 Rule 2 matched: Very high amount (${amount} > $3000) → FRAUD")
                return RiskClassification.FRAUD
            
            # Rule 3: High risk score → FRAUD
            if risk_score >= RiskClassifier.SUSPICIOUS_THRESHOLD:
                print(f"   🚨 Rule 3 matched: High risk ({risk_score:.4f} ≥ 0.7) → FRAUD")
                return RiskClassification.FRAUD
            
            # Rule 4: Medium amounts ($150-$2000) with medium-to-high risk → SUSPICIOUS
            # This catches legitimate high-value purchases that need user confirmation
            if RiskClassifier.SUSPICIOUS_AMOUNT_MIN <= amount <= RiskClassifier.SUSPICIOUS_AMOUNT_MAX:
                if risk_score >= RiskClassifier.SAFE_THRESHOLD:  # Risk ≥ 0.3
                    print(f"   ⚠️ Rule 4 matched: Medium amount (${amount} in $150-$2000) + Medium risk ({risk_score:.4f} ≥ 0.3) → SUSPICIOUS")
                    return RiskClassification.SUSPICIOUS
                # If risk is very low (< 0.3), allow it to pass through to normal logic
        
        # Fall back to pure risk score thresholds
        if risk_score < RiskClassifier.SAFE_THRESHOLD:
            print(f"   ✅ Fallback: Low risk ({risk_score:.4f} < 0.3) → SAFE")
            return RiskClassification.SAFE
        elif risk_score < RiskClassifier.SUSPICIOUS_THRESHOLD:
            print(f"   ⚠️ Fallback: Medium risk (0.3 ≤ {risk_score:.4f} < 0.7) → SUSPICIOUS")
            return RiskClassification.SUSPICIOUS
        else:
            print(f"   🚨 Fallback: High risk ({risk_score:.4f} ≥ 0.7) → FRAUD")
            return RiskClassification.FRAUD
    
    @staticmethod
    def get_risk_factors(features: Dict, risk_score: float) -> List[Dict]:
        """
        Generate human-readable risk factors with severity levels.
        Returns detailed explanations of WHY a transaction is risky.
        """
        factors = []
        
        # 1. UNUSUAL TIME (Late night/early morning transactions)
        transaction_hour = features.get('transaction_hour', 12)
        if transaction_hour < 6 or transaction_hour > 22:
            severity = 'high' if (transaction_hour < 3 or transaction_hour > 23) else 'medium'
            factors.append({
                'factor': 'Unusual Transaction Time',
                'severity': severity,
                'description': f"Transaction at {transaction_hour}:00 is unusual (most fraud occurs between midnight and 6 AM)",
                'explanation': f"This transaction happened at {transaction_hour}:00, which is outside normal business hours. Fraudsters often operate at night when cardholders are asleep."
            })
        
        # 2. LARGE/UNUSUAL AMOUNT
        avg_amount = features.get('avg_transaction_amount', 0)
        current_amount = features.get('amount', 0)
        if avg_amount > 0 and current_amount > avg_amount * 2:
            percentage_increase = ((current_amount - avg_amount) / avg_amount) * 100
            severity = 'critical' if current_amount > avg_amount * 5 else 'high'
            factors.append({
                'factor': 'Abnormally Large Amount',
                'severity': severity,
                'description': f"Amount ${current_amount:.2f} is {percentage_increase:.0f}% higher than your average ${avg_amount:.2f}",
                'explanation': f"Your typical transaction is ${avg_amount:.2f}, but this one is ${current_amount:.2f} - that's {percentage_increase:.0f}% more than usual. Fraudsters typically make large purchases to maximize stolen card value."
            })
        elif current_amount > 1000:
            severity = 'medium'
            factors.append({
                'factor': 'High-Value Transaction',
                'severity': severity,
                'description': f"Transaction amount ${current_amount:.2f} exceeds $1,000",
                'explanation': f"This ${current_amount:.2f} transaction is considered high-value. Large purchases often require extra verification to prevent fraud."
            })
        
        # 3. NEW/FOREIGN LOCATION
        distance = features.get('distance_from_home', 0)
        is_foreign = features.get('is_foreign_transaction', 0)
        location = features.get('location', '')
        
        if is_foreign == 1:
            severity = 'high'
            factors.append({
                'factor': 'Foreign Transaction Location',
                'severity': severity,
                'description': f"Transaction from foreign location: {location}",
                'explanation': f"This transaction originated from {location}, which is outside your home country. Cross-border fraud is common, especially from high-risk regions."
            })
        elif distance > 500:
            severity = 'high'
            factors.append({
                'factor': 'Distant Location',
                'severity': severity,
                'description': f"Transaction {distance:.0f} miles from your usual location",
                'explanation': f"This transaction is {distance:.0f} miles away from where you normally shop. If you haven't traveled recently, this could indicate card theft."
            })
        elif distance > 200:
            severity = 'medium'
            factors.append({
                'factor': 'New Shopping Location',
                'severity': severity,
                'description': f"Transaction from unfamiliar area ({distance:.0f} miles away)",
                'explanation': f"This purchase is {distance:.0f} miles from your typical shopping locations. While not necessarily fraudulent, it's worth verifying."
            })
        
        # 4. HIGH FREQUENCY (Velocity check)
        freq_24h = features.get('transaction_frequency_24h', 0)
        freq_7d = features.get('transaction_frequency_7d', 0)
        
        if freq_24h > 10:
            severity = 'critical'
            factors.append({
                'factor': 'Rapid Transaction Burst',
                'severity': severity,
                'description': f"{freq_24h} transactions in last 24 hours",
                'explanation': f"You've made {freq_24h} transactions in the past day, which is highly unusual. Fraudsters often make multiple rapid purchases before a card is blocked."
            })
        elif freq_24h > 5:
            severity = 'high'
            factors.append({
                'factor': 'High Transaction Frequency',
                'severity': severity,
                'description': f"{freq_24h} transactions in last 24 hours",
                'explanation': f"You've made {freq_24h} transactions today. This unusual activity pattern may indicate unauthorized card use."
            })
        elif freq_7d > 20:
            severity = 'medium'
            factors.append({
                'factor': 'Increased Shopping Activity',
                'severity': severity,
                'description': f"{freq_7d} transactions in last 7 days",
                'explanation': f"You've made {freq_7d} transactions this week, which is higher than normal. This could indicate testing of stolen card credentials."
            })
        
        # 5. NEW/UNFAMILIAR DEVICE
        device = features.get('device_info', '')
        if device and 'Unknown' not in device:
            # Note: In real implementation, you'd compare against user's known devices
            factors.append({
                'factor': 'Device Information',
                'severity': 'low',
                'description': f"Transaction from: {device}",
                'explanation': f"This transaction was made using {device}. If this isn't your device, your card may be compromised."
            })
        
        # 6. RISK SCORE EXPLANATION
        if risk_score >= 0.9:
            factors.append({
                'factor': 'Extremely High Fraud Risk',
                'severity': 'critical',
                'description': f"AI fraud model confidence: {risk_score*100:.1f}%",
                'explanation': f"Our advanced AI models are {risk_score*100:.1f}% confident this is fraudulent based on analysis of millions of transactions. This is an extremely high-risk transaction."
            })
        elif risk_score >= 0.7:
            factors.append({
                'factor': 'High Fraud Risk',
                'severity': 'high',
                'description': f"AI fraud model confidence: {risk_score*100:.1f}%",
                'explanation': f"Our fraud detection system flagged this as high-risk ({risk_score*100:.1f}% confidence). Multiple red flags were detected."
            })
        elif risk_score >= 0.5:
            factors.append({
                'factor': 'Moderate Risk Detected',
                'severity': 'medium',
                'description': f"AI fraud model confidence: {risk_score*100:.1f}%",
                'explanation': f"This transaction shows some concerning patterns ({risk_score*100:.1f}% fraud probability). Please verify it was you."
            })
        
        return factors
    
    @staticmethod
    def generate_explanation(classification: RiskClassification, risk_factors: List[Dict], amount: float, merchant: str) -> str:
        """
        Generate a clear, human-readable explanation of WHY the transaction is classified this way.
        
        Returns:
            A detailed explanation string explaining the decision
        """
        if classification == RiskClassification.SAFE:
            if not risk_factors:
                return f"✅ This ${amount:.2f} transaction at {merchant} appears normal and matches your typical spending patterns. No fraud indicators detected."
            else:
                return f"✅ This ${amount:.2f} transaction at {merchant} has been approved. While some minor flags were detected ({len(risk_factors)} factors), the overall risk is low and within your normal behavior."
        
        elif classification == RiskClassification.SUSPICIOUS:
            reason_list = []
            for factor in risk_factors[:3]:  # Top 3 reasons
                if factor['severity'] in ['high', 'critical']:
                    reason_list.append(factor['description'])
            
            if reason_list:
                reasons = " | ".join(reason_list)
                return f"⚠️ This ${amount:.2f} transaction at {merchant} requires verification because: {reasons}. Please confirm if you made this purchase."
            else:
                return f"⚠️ This ${amount:.2f} transaction at {merchant} shows unusual patterns and requires your confirmation. Did you make this purchase?"
        
        else:  # FRAUD
            critical_factors = [f for f in risk_factors if f['severity'] in ['critical', 'high']]
            
            if len(critical_factors) >= 3:
                top_reasons = [f['description'] for f in critical_factors[:3]]
                reasons = " | ".join(top_reasons)
                return f"🚨 This ${amount:.2f} transaction at {merchant} has been BLOCKED for your protection due to multiple fraud indicators: {reasons}. If this was you, please contact support immediately."
            elif critical_factors:
                reason = critical_factors[0]['description']
                return f"🚨 This ${amount:.2f} transaction at {merchant} has been BLOCKED because: {reason}. This matches known fraud patterns. Contact support if this was a legitimate purchase."
            else:
                return f"🚨 This ${amount:.2f} transaction at {merchant} has been automatically blocked due to high fraud risk detected by our AI models. If you made this purchase, please contact support to verify your identity."
    
    @staticmethod
    def get_recommendation(classification: RiskClassification) -> str:
        """Get action recommendation based on classification"""
        recommendations = {
            RiskClassification.SAFE: "✅ Transaction approved automatically - No action required",
            RiskClassification.SUSPICIOUS: "⚠️ User verification required - Please confirm this transaction",
            RiskClassification.FRAUD: "🚨 Transaction blocked automatically - Contact support if legitimate"
        }
        return recommendations.get(classification, "Unknown")
