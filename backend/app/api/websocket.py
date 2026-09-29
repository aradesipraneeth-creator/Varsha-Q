"""
VARSHA-Q Real-Time WebSocket Streaming Service
Handles live forecast streaming, stage-by-stage pipeline progress notifications,
and Judge Demo automated workflows.
"""
import asyncio
import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Set, Dict, Any
from ..services.forecast_service import forecast_service

ws_router = APIRouter()


class ConnectionManager:
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.add(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.discard(websocket)

    async def broadcast_json(self, message: Dict[str, Any]):
        for connection in list(self.active_connections):
            try:
                await connection.send_json(message)
            except Exception:
                self.disconnect(connection)


manager = ConnectionManager()


@ws_router.websocket("/ws/forecast")
async def websocket_forecast_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        # Send initial status on connection
        await websocket.send_json({
            "type": "CONNECTION_ESTABLISHED",
            "message": "Connected to VARSHA-Q Real-Time Meteorological Stream",
            "current_scenario": forecast_service.current_scenario,
            "mode": forecast_service.current_mode
        })

        while True:
            data = await websocket.receive_text()
            try:
                msg = json.loads(data)
                action = msg.get("action")

                if action == "RUN_DEMO":
                    # Judge Demo run
                    scenario = msg.get("scenario", "ACTIVE_MONSOON")
                    mode = msg.get("mode", "DEMO")

                    async def progress_notifier(stage: str, description: str):
                        await websocket.send_json({
                            "type": "PIPELINE_STAGE_UPDATE",
                            "stage": stage,
                            "description": description,
                            "timestamp": asyncio.get_event_loop().time()
                        })
                        # Small realistic atmospheric latency so judges see the animation
                        await asyncio.sleep(0.4)

                    result = await forecast_service.run_forecast(
                        scenario=scenario,
                        mode=mode,
                        progress_callback=progress_notifier
                    )

                    await websocket.send_json({
                        "type": "FORECAST_COMPLETE",
                        "data": result
                    })

                elif action == "GET_LATEST":
                    latest = await forecast_service.get_latest_forecast()
                    await websocket.send_json({
                        "type": "LATEST_FORECAST",
                        "data": latest
                    })

            except json.JSONDecodeError:
                pass

    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        manager.disconnect(websocket)
