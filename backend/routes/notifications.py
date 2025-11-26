from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List
from datetime import datetime
from database.connection import get_db
from models.user import User
from models.notification import Notification
from middleware.auth import get_current_active_user
from services.notification_service import notification_service

router = APIRouter(prefix="/notifications", tags=["Notifications"])

class NotificationResponse(BaseModel):
    id: int
    transaction_id: int
    type: str
    title: str
    message: str
    data: dict | None
    is_read: bool
    requires_action: bool
    user_response: str | None
    created_at: datetime
    responded_at: datetime | None
    expires_at: datetime | None
    
    class Config:
        from_attributes = True

class NotificationMarkRead(BaseModel):
    notification_id: int

class NotificationRespond(BaseModel):
    response: str

@router.get("/", response_model=List[NotificationResponse])
async def get_notifications(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    unread_only: bool = False,
    limit: int = 50
):
    notifications = notification_service.get_user_notifications(
        db=db,
        user_id=current_user.id,
        unread_only=unread_only,
        limit=limit
    )
    return notifications

@router.get("/unread-count")
async def get_unread_count(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    count = notification_service.get_unread_count(db=db, user_id=current_user.id)
    return {"unread_count": count}

@router.post("/{notification_id}/read")
async def mark_as_read(
    notification_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    notification = notification_service.mark_as_read(
        db=db,
        notification_id=notification_id,
        user_id=current_user.id
    )
    
    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )
    
    return {"message": "Notification marked as read"}

@router.post("/{notification_id}/respond")
async def respond_to_notification(
    notification_id: int,
    response_data: NotificationRespond,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    response = response_data.response.upper()
    if response not in ["YES", "NO"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Response must be YES or NO"
        )
    
    notification = notification_service.respond_to_notification(
        db=db,
        notification_id=notification_id,
        user_id=current_user.id,
        response=response
    )
    
    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found or does not require action"
        )
    
    return {
        "message": "Response recorded",
        "notification_id": notification.id,
        "response": response
    }
