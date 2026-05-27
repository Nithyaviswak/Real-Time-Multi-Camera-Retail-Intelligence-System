from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, List, Set
import asyncio
import json
import logging
from datetime import datetime
from contextlib import asynccontextmanager
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from common.config import settings
from common.utils import get_logger

logger = get_logger(__name__)


class ConnectionManager:
    """Manage WebSocket connections."""

    def __init__(self):
        self.active_connections: Dict[str, Set[WebSocket]] = {
            "metrics": set(),
            "alerts": set(),
            "video": set()
        }

    async def connect(self, websocket: WebSocket, channel: str = "metrics"):
        """Connect a new WebSocket client."""
        await websocket.accept()
        if channel not in self.active_connections:
            self.active_connections[channel] = set()
        self.active_connections[channel].add(websocket)
        logger.info(f"Client connected to {channel}. Total: {len(self.active_connections[channel])}")

    def disconnect(self, websocket: WebSocket, channel: str = "metrics"):
        """Disconnect a WebSocket client."""
        if channel in self.active_connections:
            self.active_connections[channel].discard(websocket)
            logger.info(f"Client disconnected from {channel}. Total: {len(self.active_connections[channel])}")

    async def broadcast(self, message: dict, channel: str = "metrics"):
        """Broadcast message to all clients in a channel."""
        if channel not in self.active_connections:
            return

        disconnected = set()
        for connection in self.active_connections[channel]:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Error sending message: {e}")
                disconnected.add(connection)

        for conn in disconnected:
            self.disconnect(conn, channel)


connection_manager = ConnectionManager()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    logger.info("Starting API Gateway")
    metrics_task = asyncio.create_task(broadcast_metrics())
    alerts_task = asyncio.create_task(broadcast_alerts())
    yield
    logger.info("Shutting down API Gateway")
    metrics_task.cancel()
    alerts_task.cancel()


app = FastAPI(
    title="Retail Intelligence API",
    description="Real-time retail analytics API",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": "Retail Intelligence API",
        "version": "1.0.0",
        "status": "running",
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/api/cameras")
async def list_cameras():
    """List all cameras."""
    return {
        "cameras": [
            {"camera_id": "cam_01", "name": "Entrance", "status": "active"},
            {"camera_id": "cam_02", "name": "Floor 1", "status": "active"},
            {"camera_id": "cam_03", "name": "Checkout", "status": "active"},
            {"camera_id": "cam_04", "name": "Shelves", "status": "active"}
        ]
    }


@app.get("/api/cameras/{camera_id}")
async def get_camera(camera_id: str):
    """Get camera details."""
    return {
        "camera_id": camera_id,
        "name": f"Camera {camera_id}",
        "status": "active",
        "resolution": {"width": 1920, "height": 1080}
    }


@app.get("/api/metrics")
async def get_current_metrics():
    """Get current metrics for all cameras."""
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "cameras": {
            "cam_01": {
                "current_people": 12,
                "total_footfall": 156,
                "avg_dwell_time": 245.5,
                "queue_length": 3,
                "alerts": []
            },
            "cam_02": {
                "current_people": 8,
                "total_footfall": 89,
                "avg_dwell_time": 180.2,
                "queue_length": 0,
                "alerts": []
            },
            "cam_03": {
                "current_people": 5,
                "total_footfall": 234,
                "avg_dwell_time": 120.0,
                "queue_length": 4,
                "alerts": ["queue_warning"]
            },
            "cam_04": {
                "current_people": 15,
                "total_footfall": 312,
                "avg_dwell_time": 300.5,
                "queue_length": 0,
                "alerts": []
            }
        }
    }


@app.get("/api/metrics/{camera_id}")
async def get_camera_metrics(camera_id: str):
    """Get metrics for a specific camera."""
    return {
        "camera_id": camera_id,
        "timestamp": datetime.utcnow().isoformat(),
        "current_people": 12,
        "total_footfall": 156,
        "avg_dwell_time": 245.5,
        "queue_length": 3,
        "heatmap_data": [[0.1, 0.2, 0.3], [0.2, 0.5, 0.2], [0.1, 0.3, 0.4]],
        "alerts": []
    }


@app.get("/api/analytics/footfall")
async def get_footfall_analytics():
    """Get footfall analytics."""
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "hourly": [
            {"hour": i, "count": 10 + (i * 3) % 20}
            for i in range(24)
        ],
        "daily": [
            {"day": i, "count": 100 + (i * 15) % 50}
            for i in range(7)
        ]
    }


@app.get("/api/analytics/heatmap")
async def get_heatmap():
    """Get heatmap data."""
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "heatmap": [
            [0.1, 0.2, 0.3, 0.2, 0.1],
            [0.2, 0.5, 0.7, 0.5, 0.2],
            [0.3, 0.7, 1.0, 0.7, 0.3],
            [0.2, 0.5, 0.7, 0.5, 0.2],
            [0.1, 0.2, 0.3, 0.2, 0.1]
        ],
        "resolution": {"width": 5, "height": 5}
    }


@app.get("/api/alerts")
async def get_alerts():
    """Get recent alerts."""
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "alerts": [
            {
                "id": "alert_1",
                "camera_id": "cam_03",
                "alert_type": "queue_warning",
                "severity": "warning",
                "message": "Queue building: 4 people waiting",
                "timestamp": datetime.utcnow().isoformat()
            }
        ]
    }


@app.websocket("/ws/metrics")
async def websocket_metrics(websocket: WebSocket):
    """WebSocket endpoint for real-time metrics."""
    await connection_manager.connect(websocket, "metrics")
    try:
        while True:
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        connection_manager.disconnect(websocket, "metrics")


@app.websocket("/ws/alerts")
async def websocket_alerts(websocket: WebSocket):
    """WebSocket endpoint for real-time alerts."""
    await connection_manager.connect(websocket, "alerts")
    try:
        while True:
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        connection_manager.disconnect(websocket, "alerts")


async def broadcast_metrics():
    """Broadcast metrics to all connected clients."""
    while True:
        metrics = {
            "type": "metrics_update",
            "timestamp": datetime.utcnow().isoformat(),
            "data": {
                "cam_01": {
                    "current_people": 12,
                    "total_footfall": 156,
                    "avg_dwell_time": 245.5,
                    "queue_length": 3
                },
                "cam_02": {
                    "current_people": 8,
                    "total_footfall": 89,
                    "avg_dwell_time": 180.2,
                    "queue_length": 0
                },
                "cam_03": {
                    "current_people": 5,
                    "total_footfall": 234,
                    "avg_dwell_time": 120.0,
                    "queue_length": 4
                },
                "cam_04": {
                    "current_people": 15,
                    "total_footfall": 312,
                    "avg_dwell_time": 300.5,
                    "queue_length": 0
                }
            }
        }
        await connection_manager.broadcast(metrics, "metrics")
        await asyncio.sleep(1)


async def broadcast_alerts():
    """Broadcast alerts to all connected clients."""
    alert_types = ["queue_warning", "loitering", "excessive_speed"]
    alert_id = 0

    while True:
        if alert_id % 10 == 0:
            alert = {
                "type": "alert",
                "timestamp": datetime.utcnow().isoformat(),
                "data": {
                    "id": f"alert_{alert_id}",
                    "camera_id": f"cam_{(alert_id % 4) + 1:02d}",
                    "alert_type": alert_types[alert_id % len(alert_types)],
                    "severity": "warning" if alert_id % 2 == 0 else "info",
                    "message": f"Test alert {alert_id}"
                }
            }
            await connection_manager.broadcast(alert, "alerts")

        alert_id += 1
        await asyncio.sleep(2)


