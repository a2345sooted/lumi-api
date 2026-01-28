from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import logging
from src.api.websockets.manager import manager

logger = logging.getLogger(__name__)

router = APIRouter()

@router.websocket("/ws")
@router.websocket("/ws/")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    
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
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)
