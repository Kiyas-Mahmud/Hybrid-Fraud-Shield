from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from database.connection import get_db
from models.user import User
from models.transaction import Transaction, TransactionType, TransactionStatus, RiskClassification
from models.notification import NotificationType
from middleware.auth import get_current_active_user
from services.fraud_detection import fraud_detection_service
from services.risk_classifier import RiskClassifier
from services.notification_service import notification_service
from utils.geolocation import get_location_from_ip, parse_user_agent
from utils.encryption import encrypt_card_data, mask_card_for_display

router = APIRouter(prefix="/transactions", tags=["Transactions"])

class TransactionSubmit(BaseModel):
    amount: float
    merchant_name: str
    transaction_type: TransactionType
    description: Optional[str] = None
    location: Optional[str] = None
    device_info: Optional[str] = None
    ip_address: Optional[str] = None
    
    # Card payment fields (will be encrypted before storage)
    card_number: Optional[str] = None  # Format: 1234-5678-9012-3456
    cardholder_name: Optional[str] = None
    cvv: Optional[str] = None  # 3-4 digits
    expiry_date: Optional[str] = None  # Format: MM/YY
    billing_address: Optional[str] = None

class TransactionResponse(BaseModel):
    id: int
    amount: float
    merchant_name: str
    transaction_type: str
    status: str
    classification: Optional[str] = None
    risk_score: Optional[float] = None
    risk_factors: Optional[List[dict]] = None
    model_predictions: Optional[dict] = None
    explanation: Optional[str] = None  # ← NEW: Human-readable explanation of why this is fraud/safe/suspicious
    created_at: datetime
    
    class Config:
        from_attributes = True
        
    @classmethod
    def from_orm(cls, transaction):
        # Generate explanation using RiskClassifier
        explanation = None
        if transaction.classification and transaction.risk_factors:
            explanation = RiskClassifier.generate_explanation(
                classification=transaction.classification,
                risk_factors=transaction.risk_factors,
                amount=transaction.amount,
                merchant=transaction.merchant_name
            )
        
        return cls(
            id=transaction.id,
            amount=transaction.amount,
            merchant_name=transaction.merchant_name,
            transaction_type=transaction.transaction_type.value if hasattr(transaction.transaction_type, 'value') else transaction.transaction_type,
            status=transaction.status.value if hasattr(transaction.status, 'value') else transaction.status,
            classification=transaction.classification.value if transaction.classification and hasattr(transaction.classification, 'value') else transaction.classification,
            risk_score=transaction.risk_score,
            risk_factors=transaction.risk_factors,
            model_predictions=transaction.model_predictions,
            explanation=explanation,
            created_at=transaction.created_at
        )

class RespondTransaction(BaseModel):
    response: str

@router.post("/submit", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
async def submit_transaction(
    request: Request,  # ← Add Request to access HTTP headers and client info
    transaction_data: TransactionSubmit,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    try:
        from datetime import datetime
        import hashlib
        
        # ============================================================
        # AUTO-CAPTURE: IP, Device, Location (Production-Ready)
        # ============================================================
        
        # 1. Auto-capture IP address from HTTP request (if not provided)
        if not transaction_data.ip_address:
            transaction_data.ip_address = request.client.host if request.client else "0.0.0.0"
        
        # 2. Auto-capture device info from User-Agent header (if not provided)
        if not transaction_data.device_info:
            user_agent = request.headers.get("user-agent", "")
            transaction_data.device_info = parse_user_agent(user_agent)
        
        # 3. Auto-capture location from IP geolocation (if not provided)
        if not transaction_data.location:
            transaction_data.location = await get_location_from_ip(transaction_data.ip_address)
        
        # ============================================================
        # ENCRYPT CARD DATA (PCI-DSS Compliance)
        # ============================================================
        encrypted_card_number = None
        encrypted_cvv = None
        masked_card = None
        
        if transaction_data.card_number and transaction_data.cvv:
            # Encrypt card number and CVV before storage
            encrypted_card_number, encrypted_cvv = encrypt_card_data(
                transaction_data.card_number,
                transaction_data.cvv
            )
            # Create masked version for logging/display
            masked_card = mask_card_for_display(transaction_data.card_number)
        
        # ============================================================
        # Continue with existing fraud detection logic
        # ============================================================
        
        # Get user's transaction history for feature engineering
        user_transactions = db.query(Transaction).filter(
            Transaction.user_id == current_user.id
        ).order_by(Transaction.created_at.desc()).limit(100).all()
        
        # Extract time features
        now = datetime.utcnow()
        transaction_hour = now.hour
        transaction_day = now.day
        transaction_month = now.month
        
        # Calculate user behavior features
        if user_transactions:
            amounts = [t.amount for t in user_transactions]
            avg_amount = sum(amounts) / len(amounts)
            std_amount = (sum((x - avg_amount) ** 2 for x in amounts) / len(amounts)) ** 0.5
            
            # Count recent transactions
            from datetime import timedelta
            day_ago = now - timedelta(days=1)
            week_ago = now - timedelta(days=7)
            freq_24h = len([t for t in user_transactions if t.created_at >= day_ago])
            freq_7d = len([t for t in user_transactions if t.created_at >= week_ago])
        else:
            avg_amount = transaction_data.amount
            std_amount = 0
            freq_24h = 0
            freq_7d = 0
        
        # Encode categorical features
        merchant_encoded = hash(transaction_data.merchant_name) % 1000
        device_encoded = hash(transaction_data.device_info or "unknown") % 1000
        
        # Simple foreign transaction detection
        location = transaction_data.location or ""
        is_foreign = 1 if "UK" in location or "UAE" in location or "Mexico" in location or "Singapore" in location else 0
        
        # Distance from home (simplified - just flag foreign)
        distance_from_home = 5000 if is_foreign else 100
        
        # Create rich feature set for ML models - using actual user data
        features = {
            # Transaction details
            "amount": transaction_data.amount,
            "transaction_hour": transaction_hour,
            "transaction_day": transaction_day,
            "transaction_month": transaction_month,
            "merchant_name": transaction_data.merchant_name,
            "transaction_type": transaction_data.transaction_type.value,
            
            # Location and device
            "location": transaction_data.location or "",
            "device_info": transaction_data.device_info or "",
            "ip_address": transaction_data.ip_address or "0.0.0.0",
            "is_foreign_transaction": is_foreign,
            "distance_from_home": distance_from_home,
            
            # Card information (hashed for privacy)
            "card_number_hash": hash(transaction_data.card_number) if hasattr(transaction_data, 'card_number') and transaction_data.card_number else "default",
            
            # User transaction history for behavioral features
            "user_history": [
                {
                    "amount": t.amount,
                    "created_at": t.created_at,
                    "merchant_name": t.merchant_name,
                    "is_fraud": t.fraud_status == "FRAUD" if hasattr(t, 'fraud_status') else False
                }
                for t in user_transactions
            ] if user_transactions else []
        }
        
        # Also keep raw data for storage
        raw_features = {
            "amount": transaction_data.amount,
            "merchant_name": transaction_data.merchant_name,
            "transaction_type": transaction_data.transaction_type.value,
            "description": transaction_data.description or "",
            "location": transaction_data.location or "",
            "device_info": transaction_data.device_info or "",
            "ip_address": transaction_data.ip_address or "0.0.0.0"
        }
        
        # Predict fraud using actual user data (NO TEMPLATES)
        risk_score, model_predictions = fraud_detection_service.predict(features)
        
        # DEBUG: Log before classification
        print(f"\n💳 TRANSACTION SUBMITTED:")
        print(f"   Amount: ${transaction_data.amount}")
        print(f"   Merchant: {transaction_data.merchant_name}")
        print(f"   Risk Score from ML: {risk_score:.4f} ({risk_score * 100:.2f}%)")
        
        # Prepare user history for classification (include status)
        user_history_for_classifier = [
            {
                "amount": t.amount,
                "merchant_name": t.merchant_name,
                "status": t.status.value if hasattr(t.status, 'value') else str(t.status),
                "classification": t.classification.value if hasattr(t.classification, 'value') else str(t.classification)
            }
            for t in user_transactions
        ] if user_transactions else []
        
        # Pass amount, merchant name, and user history to classifier for smart classification
        classification = RiskClassifier.classify(
            risk_score, 
            amount=transaction_data.amount,
            merchant_name=transaction_data.merchant_name,
            user_history=user_history_for_classifier
        )
        risk_factors = RiskClassifier.get_risk_factors(raw_features, risk_score)
        
        # Add specific risk factor for high amounts that trigger automatic FRAUD
        if transaction_data.amount > RiskClassifier.FRAUD_AMOUNT_THRESHOLD:
            risk_factors.insert(0, {
                'factor': 'Extremely High Transaction Amount',
                'severity': 'critical',
                'description': f'Transaction amount ${transaction_data.amount:.2f} exceeds ${RiskClassifier.FRAUD_AMOUNT_THRESHOLD:.2f}',
                'explanation': f'This ${transaction_data.amount:.2f} transaction exceeds our security threshold of ${RiskClassifier.FRAUD_AMOUNT_THRESHOLD:.2f}. High-value purchases are automatically blocked to protect against fraud and require additional verification.'
            })
        
        # Three-tier status logic:
        # SAFE (risk < 0.3) → Auto-approve
        # SUSPICIOUS (0.3 ≤ risk < 0.7) → Pending, requires user confirmation
        # FRAUD (risk ≥ 0.7) → Auto-block
        if classification == RiskClassification.SAFE:
            initial_status = TransactionStatus.APPROVED
        elif classification == RiskClassification.SUSPICIOUS:
            initial_status = TransactionStatus.PENDING
        else:  # FRAUD
            initial_status = TransactionStatus.BLOCKED
        
        new_transaction = Transaction(
            user_id=current_user.id,
            amount=transaction_data.amount,
            merchant_name=transaction_data.merchant_name,
            transaction_type=transaction_data.transaction_type,
            description=transaction_data.description,
            location=transaction_data.location,
            device_info=transaction_data.device_info,
            ip_address=transaction_data.ip_address,
            risk_score=risk_score,
            classification=classification,
            status=initial_status,
            features=raw_features,
            model_predictions=model_predictions,
            risk_factors=risk_factors,
            # Card payment data (encrypted)
            card_number_encrypted=encrypted_card_number,
            cardholder_name=transaction_data.cardholder_name,
            cvv_encrypted=encrypted_cvv,
            expiry_date=transaction_data.expiry_date,
            billing_address=transaction_data.billing_address
        )
        
        db.add(new_transaction)
        db.commit()
        db.refresh(new_transaction)
        
        # Send notifications based on classification
        if classification == RiskClassification.SUSPICIOUS:
            # SUSPICIOUS: Ask user to confirm
            notification_service.create_notification(
                db=db,
                transaction_id=new_transaction.id,
                user_id=current_user.id,
                notification_type=NotificationType.TRANSACTION_PENDING,
                title="⚠️ Transaction Verification Required",
                message=f"We noticed a ${transaction_data.amount:.2f} transaction at {transaction_data.merchant_name}. Did you make this purchase?",
                data={
                    "transaction_id": new_transaction.id,
                    "amount": transaction_data.amount,
                    "merchant": transaction_data.merchant_name,
                    "risk_score": risk_score,
                    "classification": classification.value,
                    "risk_factors": risk_factors,
                    "action_required": "Please confirm if you made this transaction",
                    "workflow": "Click YES if you made this purchase → Approved. Click NO if you did not → Blocked."
                },
                requires_action=True
            )
        elif classification == RiskClassification.FRAUD:
            # FRAUD: Notify user of blocked transaction
            notification_service.create_notification(
                db=db,
                transaction_id=new_transaction.id,
                user_id=current_user.id,
                notification_type=NotificationType.TRANSACTION_BLOCKED,
                title="🚨 Suspicious Transaction Blocked",
                message=f"We blocked a suspicious ${transaction_data.amount:.2f} transaction at {transaction_data.merchant_name} for your security.",
                data={
                    "transaction_id": new_transaction.id,
                    "amount": transaction_data.amount,
                    "merchant": transaction_data.merchant_name,
                    "risk_score": risk_score,
                    "classification": classification.value,
                    "risk_factors": risk_factors,
                    "action_required": "If this was you, please contact support to unblock",
                    "reason": "High fraud risk detected by our AI models"
                },
                requires_action=False
            )
        
        return TransactionResponse.from_orm(new_transaction)
    
    except Exception as e:
        import traceback
        print(f"Error in submit_transaction: {str(e)}")
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Transaction processing error: {str(e)}"
        )

@router.get("/{transaction_id}", response_model=TransactionResponse)
async def get_transaction(
    transaction_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    transaction = db.query(Transaction).filter(
        Transaction.id == transaction_id,
        Transaction.user_id == current_user.id
    ).first()
    
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found"
        )
    
    return TransactionResponse.from_orm(transaction)

@router.get("/", response_model=List[TransactionResponse])
async def get_user_transactions(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    limit: int = 50
):
    transactions = db.query(Transaction).filter(
        Transaction.user_id == current_user.id
    ).order_by(Transaction.created_at.desc()).limit(limit).all()
    
    return [TransactionResponse.from_orm(t) for t in transactions]

@router.post("/{transaction_id}/respond")
async def respond_to_transaction(
    transaction_id: int,
    response_data: RespondTransaction,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    transaction = db.query(Transaction).filter(
        Transaction.id == transaction_id,
        Transaction.user_id == current_user.id,
        Transaction.status == TransactionStatus.PENDING
    ).first()
    
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found or already processed"
        )
    
    response = response_data.response.upper()
    if response not in ["YES", "NO"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Response must be YES or NO"
        )
    
    if response == "YES":
        transaction.status = TransactionStatus.APPROVED
    else:
        transaction.status = TransactionStatus.REJECTED
    
    transaction.user_response = response
    transaction.responded_at = datetime.utcnow()
    
    db.commit()
    db.refresh(transaction)
    
    return {
        "message": "Transaction response recorded",
        "transaction_id": transaction.id,
        "status": transaction.status.value
    }
