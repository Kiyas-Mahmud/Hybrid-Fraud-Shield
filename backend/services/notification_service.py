from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from typing import List, Optional
from models.notification import Notification, NotificationType
from models.transaction import Transaction

class NotificationService:
    @staticmethod
    def create_notification(
        db: Session,
        transaction_id: int,
        user_id: int,
        notification_type: NotificationType,
        title: str,
        message: str,
        data: dict = None,
        requires_action: bool = False
    ) -> Notification:
        expires_at = datetime.utcnow() + timedelta(minutes=15) if requires_action else None
        
        notification = Notification(
            transaction_id=transaction_id,
            user_id=user_id,
            type=notification_type,
            title=title,
            message=message,
            data=data,
            requires_action=requires_action,
            expires_at=expires_at
        )
        
        db.add(notification)
        db.commit()
        db.refresh(notification)
        return notification
    
    @staticmethod
    def get_user_notifications(
        db: Session,
        user_id: int,
        unread_only: bool = False,
        limit: int = 50
    ) -> List[Notification]:
        query = db.query(Notification).filter(Notification.user_id == user_id)
        
        if unread_only:
            query = query.filter(Notification.is_read == False)
        
        return query.order_by(Notification.created_at.desc()).limit(limit).all()
    
    @staticmethod
    def mark_as_read(db: Session, notification_id: int, user_id: int) -> Optional[Notification]:
        notification = db.query(Notification).filter(
            Notification.id == notification_id,
            Notification.user_id == user_id
        ).first()
        
        if notification:
            notification.is_read = True
            db.commit()
            db.refresh(notification)
        
        return notification
    
    @staticmethod
    def respond_to_notification(
        db: Session,
        notification_id: int,
        user_id: int,
        response: str
    ) -> Optional[Notification]:
        notification = db.query(Notification).filter(
            Notification.id == notification_id,
            Notification.user_id == user_id,
            Notification.requires_action == True
        ).first()
        
        if notification:
            notification.user_response = response
            notification.responded_at = datetime.utcnow()
            notification.requires_action = False
            notification.is_read = True
            db.commit()
            db.refresh(notification)
        
        return notification
    
    @staticmethod
    def get_unread_count(db: Session, user_id: int) -> int:
        return db.query(Notification).filter(
            Notification.user_id == user_id,
            Notification.is_read == False
        ).count()

notification_service = NotificationService()
