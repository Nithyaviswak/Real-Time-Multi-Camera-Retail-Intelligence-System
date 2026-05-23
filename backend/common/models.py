from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class DetectionType(str, Enum):
    PERSON = "person"
    VEHICLE = "vehicle"
    SHOPPING_CART = "shopping_cart"
    CASH_REGISTER = "cash_register"


class Detection(BaseModel):
    class_id: int
    class_name: str
    confidence: float
    bbox: List[float] = Field(description="x1, y1, x2, y2")
    tracking_id: Optional[int] = None


class TrackedObject(BaseModel):
    tracking_id: int
    class_name: str
    bbox: List[float]
    confidence: float
    timestamp: Optional[datetime] = None
    embeddings: Optional[List[float]] = None


class FrameData(BaseModel):
    camera_id: str
    frame_id: int
    timestamp: datetime
    width: int
    height: int
    detections: List[Detection] = []


class MetricsUpdate(BaseModel):
    camera_id: str
    timestamp: datetime
    current_people: int
    total_footfall: int
    avg_dwell_time: float
    queue_length: int
    heatmap_data: Optional[Dict[str, Any]] = None
    alerts: List[str] = []


class Alert(BaseModel):
    id: str
    camera_id: str
    alert_type: str
    severity: str
    message: str
    timestamp: datetime
    metadata: Dict[str, Any] = {}


class HeatmapPoint(BaseModel):
    x: float
    y: float
    weight: float = 1.0


class ZoneConfig(BaseModel):
    zone_id: str
    zone_type: str
    coordinates: List[List[float]]


class CameraConfig(BaseModel):
    camera_id: str
    name: str
    rtsp_url: str
    zones: List[ZoneConfig] = []
    enabled: bool = True
