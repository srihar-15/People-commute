from fastapi import WebSocket
from typing import List, Dict

class ConnectionManager:
    def __init__(self):
        # Keep track of active connections grouped by user roles
        self.active_connections: Dict[str, List[WebSocket]] = {
            "admin": [],
            "mp": [],
            "officer": [],
            "citizen": []
        }
        self.main_loop = None

    async def connect(self, websocket: WebSocket, role: str):
        if self.main_loop is None:
            import asyncio
            self.main_loop = asyncio.get_running_loop()
        await websocket.accept()
        if role in self.active_connections:
            self.active_connections[role].append(websocket)
        else:
            self.active_connections[role] = [websocket]
        print(f"[WEBSOCKET] Connected user with role: {role}. Active connections: {len(self.active_connections[role])}")

    def disconnect(self, websocket: WebSocket, role: str):
        if role in self.active_connections and websocket in self.active_connections[role]:
            self.active_connections[role].remove(websocket)
            print(f"[WEBSOCKET] Disconnected user with role: {role}.")

    async def broadcast_to_role(self, role: str, message: dict):
        """
        Sends message to all connections under a specific role.
        """
        if role in self.active_connections:
            for connection in self.active_connections[role]:
                try:
                    await connection.send_json(message)
                except Exception as e:
                    # Connection might be closed, clean up happens on disconnect
                    pass

    async def broadcast_all(self, message: dict):
        """
        Sends message to all active connections.
        """
        for role, connections in self.active_connections.items():
            for connection in connections:
                try:
                    await connection.send_json(message)
                except Exception:
                    pass

    def broadcast_all_sync(self, message: dict):
        """
        Thread-safe wrapper to broadcast from synchronous background tasks or threadpools.
        """
        import asyncio
        if self.main_loop and self.main_loop.is_running():
            asyncio.run_coroutine_threadsafe(self.broadcast_all(message), self.main_loop)

manager = ConnectionManager()
