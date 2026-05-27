import numpy as np
import cv2
from typing import List, Dict, Tuple, Optional
from collections import defaultdict
from datetime import datetime, timedelta
import logging
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from common.utils import get_logger, create_heatmap
from common.models import TrackedObject

logger = get_logger(__name__)


class HeatmapGenerator:
    """Generate heatmaps from tracked object positions."""

    def __init__(self, width: int, height: int, resolution: int = 10):
        self.width = width
        self.height = height
        self.resolution = resolution
        self.grid_width = width // resolution
        self.grid_height = height // resolution
        self.heatmap = np.zeros((self.grid_height, self.grid_width), dtype=np.float32)
        self.decay_rate = 0.95

    def add_points(self, points: List[Tuple[float, float]], weight: float = 1.0):
        """Add points to the heatmap."""
        for x, y in points:
            grid_x = min(int(x / self.resolution), self.grid_width - 1)
            grid_y = min(int(y / self.resolution), self.grid_height - 1)
            if 0 <= grid_x < self.grid_width and 0 <= grid_y < self.grid_height:
                self.heatmap[grid_y, grid_x] += weight

    def update(self, tracks: List[TrackedObject]):
        """Update heatmap with current track positions."""
        self.heatmap *= self.decay_rate

        for track in tracks:
            if track.class_name == "person":
                x1, y1, x2, y2 = track.bbox
                center_x = (x1 + x2) / 2
                center_y = (y1 + y2) / 2
                self.add_points([(center_x, center_y)], weight=1.0)

    def get_heatmap_image(self) -> np.ndarray:
        """Get heatmap as normalized image."""
        if self.heatmap.max() > 0:
            normalized = (self.heatmap / self.heatmap.max() * 255).astype(np.uint8)
        else:
            normalized = np.zeros_like(self.heatmap, dtype=np.uint8)

        heatmap_colored = cv2.applyColorMap(normalized, cv2.COLORMAP_JET)
        return heatmap_colored

    def get_grid_data(self) -> List[List[float]]:
        """Get heatmap data as 2D grid."""
        if self.heatmap.max() > 0:
            return (self.heatmap / self.heatmap.max()).tolist()
        return self.heatmap.tolist()

    def reset(self):
        """Reset the heatmap."""
        self.heatmap = np.zeros((self.grid_height, self.grid_width), dtype=np.float32)


class FootfallCounter:
    """Track footfall (entry/exit counting)."""

    def __init__(self, entrance_line_y: float = None, exit_line_y: float = None):
        self.entrance_line_y = entrance_line_y
        self.exit_line_y = exit_line_y

        self.total_footfall = 0
        self.current_count = 0

        self.seen_ids: Dict[int, str] = {}
        self.dwell_times: Dict[int, List[float]] = defaultdict(list)
        self.entry_times: Dict[int, datetime] = {}

    def update(self, tracks: List[TrackedObject], frame_time: float):
        """Update footfall with current tracks."""
        current_ids = set()

        for track in tracks:
            if track.class_name == "person":
                track_id = track.tracking_id
                current_ids.add(track_id)

                x1, y1, x2, y2 = track.bbox
                center_y = (y1 + y2) / 2

                if track_id not in self.seen_ids:
                    self.seen_ids[track_id] = "entered"
                    self.entry_times[track_id] = datetime.utcnow()
                    self.total_footfall += 1
                    self.current_count += 1
                else:
                    if track_id in self.entry_times:
                        dwell = (datetime.utcnow() - self.entry_times[track_id]).total_seconds()
                        self.dwell_times[track_id].append(dwell)

        for track_id in list(self.seen_ids.keys()):
            if track_id not in current_ids and track_id in self.entry_times:
                del self.entry_times[track_id]
                self.current_count = max(0, self.current_count - 1)

    def get_avg_dwell_time(self) -> float:
        """Calculate average dwell time in seconds."""
        if not self.dwell_times:
            return 0.0

        all_times = []
        for times in self.dwell_times.values():
            if times:
                all_times.append(sum(times) / len(times))

        return sum(all_times) / len(all_times) if all_times else 0.0

    def get_stats(self) -> Dict:
        """Get footfall statistics."""
        return {
            "total_footfall": self.total_footfall,
            "current_count": self.current_count,
            "avg_dwell_time": self.get_avg_dwell_time()
        }


class QueueDetector:
    """Detect and estimate queue lengths."""

    def __init__(
        self,
        queue_zone: List[Tuple[int, int]] = None,
        person_width: float = 60.0,
        spacing: float = 90.0
    ):
        self.queue_zone = queue_zone or [(0, 500), (200, 500), (200, 700), (0, 700)]
        self.person_width = person_width
        self.spacing = spacing
        self.queue_history: List[int] = []

    def estimate_queue_length(self, tracks: List[TrackedObject]) -> int:
        """Estimate queue length based on tracked persons in queue zone."""
        queue_count = 0

        for track in tracks:
            if track.class_name == "person":
                x1, y1, x2, y2 = track.bbox
                center_x = (x1 + x2) / 2
                center_y = (y1 + y2) / 2

                if self._is_in_zone(center_x, center_y):
                    queue_count += 1

        self.queue_history.append(queue_count)
        if len(self.queue_history) > 30:
            self.queue_history.pop(0)

        return queue_count

    def _is_in_zone(self, x: float, y: float) -> bool:
        """Check if point is in queue zone using ray casting."""
        n = len(self.queue_zone)
        inside = False

        p1x, p1y = self.queue_zone[0]
        for i in range(1, n + 1):
            p2x, p2y = self.queue_zone[i % n]
            if y > min(p1y, p2y):
                if y <= max(p1y, p2y):
                    if x <= max(p1x, p2x):
                        if p1y != p2y:
                            xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                        if p1x == p2x or x <= xinters:
                            inside = not inside
            p1x, p1y = p2x, p2y

        return inside

    def get_avg_queue_length(self) -> float:
        """Get average queue length over recent history."""
        return sum(self.queue_history) / len(self.queue_history) if self.queue_history else 0.0


class ShelfInteractionTracker:
    """Track shelf interactions."""

    def __init__(self, shelf_zones: Dict[str, List[Tuple[int, int]]] = None):
        self.shelf_zones = shelf_zones or {
            "shelf_1": [(50, 50), (200, 50), (200, 400), (50, 400)],
            "shelf_2": [(300, 50), (450, 50), (450, 400), (300, 400)],
            "shelf_3": [(500, 50), (650, 50), (650, 400), (500, 400)]
        }

        self.interactions: Dict[str, int] = {zone: 0 for zone in self.shelf_zones}
        self.active_interactions: Dict[int, str] = {}

    def update(self, tracks: List[TrackedObject]):
        """Update shelf interactions."""
        current_interactions = {}

        for track in tracks:
            if track.class_name == "person":
                x1, y1, x2, y2 = track.bbox
                center_x = (x1 + x2) / 2
                center_y = (y1 + y2) / 2

                for zone_name, zone_coords in self.shelf_zones.items():
                    if self._is_in_zone(center_x, center_y, zone_coords):
                        current_interactions[track.tracking_id] = zone_name

        for track_id, zone in current_interactions.items():
            if track_id not in self.active_interactions:
                self.interactions[zone] += 1

        self.active_interactions = current_interactions

    def _is_in_zone(self, x: float, y: float, zone: List[Tuple[int, int]]) -> bool:
        """Check if point is in zone."""
        n = len(zone)
        inside = False

        p1x, p1y = zone[0]
        for i in range(1, n + 1):
            p2x, p2y = zone[i % n]
            if y > min(p1y, p2y):
                if y <= max(p1y, p2y):
                    if x <= max(p1x, p2x):
                        if p1y != p2y:
                            xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                        if p1x == p2x or x <= xinters:
                            inside = not inside
            p1x, p1y = p2x, p2y

        return inside

    def get_interaction_counts(self) -> Dict[str, int]:
        """Get interaction counts by shelf."""
        return self.interactions.copy()



class AnalyticsEngine:
    """Main analytics engine combining all analytics."""

    def __init__(self, width: int = 1920, height: int = 1080):
        self.width = width
        self.height = height
        self.camera_id = None

        self.heatmap = HeatmapGenerator(width, height)
        self.footfall = FootfallCounter()
        self.queue_detector = QueueDetector()
        self.shelf_tracker = ShelfInteractionTracker()

    def update(self, camera_id: str, tracks: List[TrackedObject], frame_time: float):
        """Update all analytics with current tracks."""
        self.camera_id = camera_id
        self.heatmap.update(tracks)
        self.footfall.update(tracks, frame_time)
        self.queue_detector.estimate_queue_length(tracks)
        self.shelf_tracker.update(tracks)

    def get_metrics(self) -> Dict:
        """Get current analytics metrics."""
        return {
            "camera_id": self.camera_id,
            "timestamp": datetime.utcnow().isoformat(),
            "footfall": self.footfall.get_stats(),
            "queue_length": self.queue_detector.get_avg_queue_length(),
            "shelf_interactions": self.shelf_tracker.get_interaction_counts(),
            "heatmap_data": self.heatmap.get_grid_data()
        }

    def reset(self):
        """Reset all analytics."""
        self.heatmap.reset()
        self.footfall = FootfallCounter()
        self.queue_detector = QueueDetector()
        self.shelf_tracker = ShelfInteractionTracker()
