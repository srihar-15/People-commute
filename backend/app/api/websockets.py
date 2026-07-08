from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.core.websocket_manager import manager

router = APIRouter()

@router.websocket("/ws/{role}")
async def websocket_endpoint(websocket: WebSocket, role: str):
    """
    WebSocket endpoint. Client establishes connection using role:
    ws://localhost:8000/ws/mp
    """
    if role not in ["admin", "mp", "officer", "citizen"]:
        # Fallback to general citizen role
        role = "citizen"
        
    await manager.connect(websocket, role)
    try:
        while True:
            # Wait for any incoming messages from client (usually just ping/keep-alive)
            data = await websocket.receive_text()
            # Send keep-alive echo
            await websocket.send_json({"type": "ping", "data": "alive"})
    except WebSocketDisconnect:
        manager.disconnect(websocket, role)
