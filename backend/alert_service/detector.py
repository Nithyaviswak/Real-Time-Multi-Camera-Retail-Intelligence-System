import numpy as np
from typing import List, Dict, Optional
from collections import deque
from datetime import datetime, timedelta
import logging
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from common.utils import get_logger
from common.models import TrackedObject, Alert

logger = get_logger(__name__)


class AnomalyDetector:
    """Detect anomalies in customer behavior."""

    def __init__(
        self,
        loitering_threshold: float = 120.0,
        queue_threshold: int = 5,
        fall_threshold: float = 0.3,
        speed_threshold: float = 50.0
    ):
        self.loitering_threshold = loitering_threshold
        self.queue_threshold = queue_threshold
        self.fall_threshold = fall_threshold
        self.speed_threshold = speed_threshold

        self.person_positions: Dict[int, deque] = {}
        self.loitering_alerts: Dict[int, datetime] = {}
        self.alert_history: deque = deque(maxlen=100)

    def update(self, camera_id: str, tracks: List[TrackedObject], frame_time: float) -> List[Alert]:
        """Update and check for anomalies."""
        alerts = []

        for track in tracks:
            if track.class_name == "person":
                track_id = track.tracking_id
                x1, y1, x2, y2 = track.bbox
                center_x = (x1 + x2) / 2
                center_y = (y1 + y2) / 2
                width = x2 - x1
                height = y2 - y1
                aspect_ratio = height / width if width > 0 else 1.0

                if track_id not in self.person_positions:
                    self.person_positions[track_id] = deque(maxlen=30)

                self.person_positions[track_id].append({
                    'x': center_x,
                    'y': center_y,
                    'time': frame_time
                })

                if len(self.person_positions[track_id]) >= 10:
                    positions = list(self.person_positions[track_id])
                    time_diff = positions[-1]['time'] - positions[0]['time']

                    if time_diff > 0:
                        speed = self._calculate_speed(positions)
                        if speed > self.speed_threshold:
                            alerts.append(Alert(
                                id=f"speed_{camera_id}_{track_id}_{int(frame_time * 1000)}",
                                camera_id=camera_id,
                                alert_type="excessive_speed",
                                severity="warning",
                                message=f"Person moving too fast: {speed:.1f} px/s",
                                timestamp=datetime.utcnow(),
                                metadata={"track_id": track_id, "speed": speed}
                            ))

                if aspect_ratio < self.fall_threshold:
                    alerts.append(Alert(
                        id=f"fall_{camera_id}_{track_id}_{int(frame_time * 1000)}",
                        camera_id=camera_id,
                        alert_type="fall_detected",
                        severity="critical",
                        message=f"Possible fall detected",
                        timestamp=datetime.utcnow(),
                        metadata={"track_id": track_id, "aspect_ratio": aspect_ratio}
                    ))

                if self._is_loitering(track_id, frame_time):
                    if track_id not in self.loitering_alerts:
                        self.loitering_alerts[track_id] = datetime.utcnow()
                        alerts.append(Alert(
                            id=f"loiter_{camera_id}_{track_id}_{int(frame_time * 1000)}",
                            camera_id=camera_id,
                            alert_type="loitering",
                            severity="info",
                            message="Person loitering in area",
                            timestamp=datetime.utcnow(),
                            metadata={"track_id": track_id}
                        ))

        self._cleanup_old_positions(frame_time)

        for alert in alerts:
            self.alert_history.append(alert)

        return alerts

    def _calculate_speed(self, positions: List[Dict]) -> float:
        """Calculate average speed from positions."""
        if len(positions) < 2:
            return 0.0

        total_distance = 0.0
        total_time = 0.0

        for i in range(1, len(positions)):
            dx = positions[i]['x'] - positions[i-1]['x']
            dy = positions[i]['y'] - positions[i-1]['y']
            distance = np.sqrt(dx**2 + dy**2)
            time_diff = positions[i]['time'] - positions[i-1]['time']

            if time_diff > 0:
                total_distance += distance
                total_time += time_diff

        return total_distance / total_time if total_time > 0 else 0.0

    def _is_loitering(self, track_id: int, frame_time: float) -> bool:
        """Check if person is loitering."""
        if track_id not in self.person_positions:
            return False

        positions = self.person_positions[track_id]
        if len(positions) < 15:
            return False

        time_span = positions[-1]['time'] - positions[0]['time']
        return time_span > self.loitering_threshold

    def _cleanup_old_positions(self, current_time: float, max_age: float = 30.0):
        """Remove old position data."""
        to_remove = []
        for track_id, positions in self.person_positions.items():
            if positions:
                last_time = positions[-1]['time']
                if current_time - last_time > max_age:
                    to_remove.append(track_id)

        for track_id in to_remove:
            del self.person_positions[track_id]
            if track_id in self.loitering_alerts:
                del self.loitering_alerts[track_id]

    def get_alert_stats(self) -> Dict:
        """Get alert statistics."""
        alert_types = {}
        for alert in self.alert_history:
            alert_types[alert.alert_type] = alert_types.get(alert.alert_type, 0) + 1

        return {
            "total_alerts": len(self.alert_history),
            "alert_types": alert_types,
            "active_loitering": len(self.loitering_alerts)
        }


class QueueAlertMonitor:
    """Monitor queue lengths and generate alerts."""

    def __init__(self, warning_threshold: int = 3, critical_threshold: int = 5):
        self.warning_threshold = warning_threshold
        self.critical_threshold = critical_threshold

    def check_queue(self, camera_id: str, queue_length: int, frame_time: float) -> Optional[Alert]:
        """Check queue length and generate alerts."""
        if queue_length >= self.critical_threshold:
            return Alert(
                id=f"queue_crit_{camera_id}_{int(frame_time * 1000)}",
                camera_id=camera_id,
                alert_type="queue_overflow",
                severity="critical",
                message=f"Queue overflow: {queue_length} people waiting",
                timestamp=datetime.utcnow(),
                metadata={"queue_length": queue_length}
            )
        elif queue_length >= self.warning_threshold:
            return Alert(
                id=f"queue_warn_{camera_id}_{int(frame_time * 1000)}",
                camera_id=camera_id,
                alert_type="queue_warning",
                severity="warning",
                message=f"Queue building: {queue_length} people waiting",
                timestamp=datetime.utcnow(),
                metadata={"queue_length": queue_length}
            )

        return None
