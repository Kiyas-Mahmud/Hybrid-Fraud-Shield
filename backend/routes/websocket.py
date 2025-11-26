from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Query
from sqlalchemy.orm import Session
from database.connection import get_db
from services.websocket_manager import manager
from services.auth_service import auth_service
from models.user import User

router = APIRouter(tags=["WebSocket"])

@router.websocket("/ws/notifications")
async def websocket_notifications(
    websocket: WebSocket,
    token: str = Query(...),
    db: Session = Depends(get_db)
):
    payload = auth_service.decode_token(token)
    
    if not payload:
        await websocket.close(code=1008)
        return
    
    user_id = int(payload.get("sub"))
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user or not user.is_active or user.is_blocked:
        await websocket.close(code=1008)
        return
    
    await manager.connect(websocket, user_id)
    
    try:
        while True:
            data = await websocket.receive_text()
            
            if data == "ping":
                await websocket.send_json({"type": "pong"})
    
    except WebSocketDisconnect:
        manager.disconnect(websocket, user_id)
