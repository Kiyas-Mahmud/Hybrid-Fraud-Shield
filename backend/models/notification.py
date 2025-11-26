from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum as SQLEnum, ForeignKey, JSON, Text
from sqlalchemy.sql import func
from database.connection import Base
import enum

class NotificationType(str, enum.Enum):
    TRANSACTION_PENDING = "TRANSACTION_PENDING"
    TRANSACTION_BLOCKED = "TRANSACTION_BLOCKED"
    ACCOUNT_ALERT = "ACCOUNT_ALERT"

class Notification(Base):
    __tablename__ = "notifications"
    
    id = Column(Integer, primary_key=True, index=True)
    transaction_id = Column(Integer, ForeignKey("transactions.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    type = Column(SQLEnum(NotificationType), nullable=False)
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    data = Column(JSON, nullable=True)
    
    is_read = Column(Boolean, default=False, nullable=False)
    requires_action = Column(Boolean, default=False, nullable=False)
    user_response = Column(String(10), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    responded_at = Column(DateTime(timezone=True), nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)
