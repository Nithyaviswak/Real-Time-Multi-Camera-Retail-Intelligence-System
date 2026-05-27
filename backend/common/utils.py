import numpy as np
import cv2
from typing import List, Tuple, Optional
import logging
from datetime import datetime
import json
from pathlib import Path


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)


def calculate_iou(box1: List[float], box2: List[float]) -> float:
    """Calculate Intersection over Union between two boxes."""
    x1_min, y1_min, x1_max, y1_max = box1
    x2_min, y2_min, x2_max, y2_max = box2

    inter_x_min = max(x1_min, x2_min)
    inter_y_min = max(y1_min, y2_min)
    inter_x_max = min(x1_max, x2_max)
    inter_y_max = min(y1_max, y2_max)

    if inter_x_max < inter_x_min or inter_y_max < inter_y_min:
        return 0.0

    inter_area = (inter_x_max - inter_x_min) * (inter_y_max - inter_y_min)
    box1_area = (x1_max - x1_min) * (y1_max - y1_min)
    box2_area = (x2_max - x2_min) * (y2_max - y2_min)
    union_area = box1_area + box2_area - inter_area

    return inter_area / union_area if union_area > 0 else 0.0


def calculate_center(box: List[float]) -> Tuple[float, float]:
    """Calculate center point of a bounding box."""
    x1, y1, x2, y2 = box
    return ((x1 + x2) / 2, (y1 + y2) / 2)


def box_area(box: List[float]) -> float:
    """Calculate area of a bounding box."""
    x1, y1, x2, y2 = box
    return max(0, x2 - x1) * max(0, y2 - y1)


def normalize_bbox(box: List[float], width: int, height: int) -> List[float]:
    """Normalize bounding box to [0, 1] range."""
    x1, y1, x2, y2 = box
    return [x1 / width, y1 / height, x2 / width, y2 / height]


def denormalize_bbox(box: List[float], width: int, height: int) -> List[float]:
    """Denormalize bounding box from [0, 1] to pixel coordinates."""
    x1, y1, x2, y2 = box
    return [x1 * width, y1 * height, x2 * width, y2 * height]


def resize_frame(frame: np.ndarray, target_size: Tuple[int, int]) -> np.ndarray:
    """Resize frame to target size maintaining aspect ratio."""
    return cv2.resize(frame, target_size, interpolation=cv2.INTER_LINEAR)


def encode_frame_to_jpeg(frame: np.ndarray, quality: int = 85) -> bytes:
    """Encode frame to JPEG bytes."""
    encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), quality]
    _, buffer = cv2.imencode('.jpg', frame, encode_param)
    return buffer.tobytes()


def decode_jpeg_to_frame(data: bytes) -> np.ndarray:
    """Decode JPEG bytes to frame."""
    nparr = np.frombuffer(data, np.uint8)
    return cv2.imdecode(nparr, cv2.IMREAD_COLOR)


def draw_boxes(
    frame: np.ndarray,
    boxes: List[List[float]],
    labels: List[str],
    scores: Optional[List[float]] = None,
    color: Tuple[int, int, int] = (0, 255, 0),
    thickness: int = 2
) -> np.ndarray:
    """Draw bounding boxes on frame."""
    for i, box in enumerate(boxes):
        x1, y1, x2, y2 = map(int, box)
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, thickness)

        label = labels[i]
        if scores and i < len(scores):
            label += f" {scores[i]:.2f}"

        (label_w, label_h), _ = cv2.getTextSize(
            label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1
        )
        cv2.rectangle(
            frame, (x1, y1 - label_h - 10),
            (x1 + label_w, y1), color, -1
        )
        cv2.putText(
            frame, label, (x1, y1 - 5),
            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1
        )
    return frame


def calculate_optical_flow(
    prev_frame: np.ndarray,
    curr_frame: np.ndarray,
    points: np.ndarray
) -> np.ndarray:
    """Calculate optical flow for given points."""
    gray_prev = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
    gray_curr = cv2.cvtColor(curr_frame, cv2.COLOR_BGR2GRAY)

    if points is None or len(points) == 0:
        return np.array([])

    points = np.float32(points).reshape(-1, 1, 2)
    next_points, status, error = cv2.calcOpticalFlowPyrLK(
        gray_prev, gray_curr, points, None
    )

    return next_points


def create_heatmap(
    points: List[Tuple[float, float]],
    width: int,
    height: int,
    radius: int = 50,
    blur: int = 31
) -> np.ndarray:
    """Create heatmap from points using Gaussian blur."""
    heatmap = np.zeros((height, width), dtype=np.float32)

    for x, y in points:
        ix, iy = int(x), int(y)
        if 0 <= ix < width and 0 <= iy < height:
            cv2.circle(heatmap, (ix, iy), radius, 1, -1)

    if blur > 0:
        heatmap = cv2.GaussianBlur(heatmap, (blur, blur), 0)

    heatmap = (heatmap * 255 / heatmap.max()).astype(np.uint8) if heatmap.max() > 0 else heatmap.astype(np.uint8)
    return heatmap


def load_json(filepath: str) -> dict:
    """Load JSON file."""
    with open(filepath, 'r') as f:
        return json.load(f)


def save_json(data: dict, filepath: str) -> None:
    """Save data to JSON file."""
    Path(filepath).parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2, default=str)


def timestamp_ms() -> int:
    """Get current timestamp in milliseconds."""
    return int(datetime.utcnow().timestamp() * 1000)


def format_duration(seconds: float) -> str:
    """Format seconds to human-readable duration."""
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes}m {secs}s"
    else:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        return f"{hours}h {minutes}m"
