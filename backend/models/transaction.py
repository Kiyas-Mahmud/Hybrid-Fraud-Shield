from sqlalchemy import Column, Integer, String, Float, DateTime, Enum as SQLEnum, ForeignKey, JSON, Text
from sqlalchemy.sql import func
from database.connection import Base
import enum

class TransactionType(str, enum.Enum):
    ONLINE = "ONLINE"
    IN_STORE = "IN_STORE"
    ATM = "ATM"
    TRANSFER = "TRANSFER"

class TransactionStatus(str, enum.Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    BLOCKED = "BLOCKED"

class RiskClassification(str, enum.Enum):
    SAFE = "SAFE"
    SUSPICIOUS = "SUSPICIOUS"
    FRAUD = "FRAUD"

class Transaction(Base):
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    amount = Column(Float, nullable=False)
    merchant_name = Column(String(200), nullable=False)
    transaction_type = Column(SQLEnum(TransactionType), nullable=False)
    description = Column(Text, nullable=True)
    
    risk_score = Column(Float, nullable=True)
    classification = Column(SQLEnum(RiskClassification), nullable=True)
    status = Column(SQLEnum(TransactionStatus), default=TransactionStatus.PENDING, nullable=False)
    user_response = Column(String(10), nullable=True)
    
    features = Column(JSON, nullable=True)
    model_predictions = Column(JSON, nullable=True)
    risk_factors = Column(JSON, nullable=True)
    
    location = Column(String(100), nullable=True)
    device_info = Column(String(200), nullable=True)
    ip_address = Column(String(45), nullable=True)
    
    # Card payment fields (encrypted)
    card_number_encrypted = Column(String(500), nullable=True)  # Encrypted card number
    cardholder_name = Column(String(200), nullable=True)
    cvv_encrypted = Column(String(500), nullable=True)  # Encrypted CVV
    expiry_date = Column(String(10), nullable=True)  # Format: MM/YY
    billing_address = Column(Text, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    responded_at = Column(DateTime(timezone=True), nullable=True)
