from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, status
import logging
from src.common.services.websocket_manager import manager
from src.api_server.api.auth import get_ws_user_id

logger = logging.getLogger(__name__)

router = APIRouter()

@router.websocket("/ws")
@router.websocket("/ws/")
async def websocket_endpoint(
    websocket: WebSocket,
    user_id: str = Depends(get_ws_user_id)
):
    await manager.connect(websocket, user_id)
    
    try:
        while True:
            try:
                data = await websocket.receive_text()
                # Echo or handle incoming client messages if needed
                await websocket.send_json({"type": "echo", "data": data})
            except Exception as e:
                if "disconnect" in str(e).lower():
                    break
                raise e

    except WebSocketDisconnect:
        manager.disconnect(websocket, user_id)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket, user_id)
