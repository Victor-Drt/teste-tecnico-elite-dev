import logging

from fastapi import WebSocket, WebSocketDisconnect

logger = logging.getLogger(__name__)


class ConnectionManager:
    def __init__(self) -> None:
        self.active_connections: dict[int, set[WebSocket]] = {}

    async def connect(self, lote_id: int, websocket: WebSocket) -> None:
        await websocket.accept()
        self.active_connections.setdefault(lote_id, set()).add(websocket)

    def disconnect(self, lote_id: int, websocket: WebSocket) -> None:
        connections = self.active_connections.get(lote_id)
        if connections is None:
            return

        connections.discard(websocket)
        if not connections:
            self.active_connections.pop(lote_id, None)

    async def broadcast(self, lote_id: int, message: dict) -> None:
        for websocket in tuple(self.active_connections.get(lote_id, ())):
            try:
                await websocket.send_json(message)
            except (OSError, RuntimeError, WebSocketDisconnect):
                logger.warning(
                    "Não foi possível enviar mensagem WebSocket para o lote %s",
                    lote_id,
                    exc_info=True,
                )
                self.disconnect(lote_id, websocket)


connection_manager = ConnectionManager()