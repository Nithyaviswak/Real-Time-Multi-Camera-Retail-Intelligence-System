import numpy as np
from typing import List, Dict, Optional, Tuple
import logging
import sys
from pathlib import Path
from dataclasses import dataclass, field

sys.path.append(str(Path(__file__).parent.parent))

from common.utils import get_logger, calculate_iou
from common.models import Detection, TrackedObject

logger = get_logger(__name__)


@dataclass
class Track:
    """Single object track."""
    track_id: int
    class_name: str
    bbox: List[float]
    confidence: float
    timestamp: float
    hits: int = 0
    age: int = 0
    time_since_update: int = 0
    embeddings: List[float] = field(default_factory=list)

    def to_tracked_object(self) -> TrackedObject:
        """Convert to TrackedObject."""
        return TrackedObject(
            tracking_id=self.track_id,
            class_name=self.class_name,
            bbox=self.bbox,
            confidence=self.confidence,
            timestamp=None,
            embeddings=self.embeddings
        )


class ByteTracker:
    """ByteTrack-inspired multi-object tracker."""

    def __init__(
        self,
        track_thresh: float = 0.5,
        track_buffer: int = 30,
        match_thresh: float = 0.8,
        frame_rate: float = 25.0
    ):
        self.track_thresh = track_thresh
        self.track_buffer = track_buffer
        self.match_thresh = match_thresh
        self.frame_rate = frame_rate

        self.tracks: Dict[int, Track] = {}
        self.track_id_count = 0
        self.frame_count = 0

        self.max_time_lost = int(self.track_buffer * self.frame_rate / 30.0)

    def update(self, detections: List[Detection], frame_time: float) -> List[TrackedObject]:
        """Update tracks with new detections."""
        self.frame_count += 1

        if not detections:
            self._mark_lost_tracks()
            return self._get_active_tracks()

        detections_high = [d for d in detections if d.confidence >= self.track_thresh]
        detections_low = [d for d in detections if d.confidence < self.track_thresh]

        remaining = self._match_detections(detections_high, frame_time)

        if remaining:
            low_matches = self._match_detections(detections_low, frame_time, use_remaining=True)

        return self._get_active_tracks()

    def _match_detections(
        self,
        detections: List[Detection],
        frame_time: float,
        use_remaining: bool = False
    ) -> List:
        """Match detections to tracks using IoU."""
        if not self.tracks:
            for det in detections:
                self._create_track(det, frame_time)
            return []

        active_tracks = [t for t in self.tracks.values() if t.time_since_update == 0]
        if not active_tracks:
            for det in detections:
                self._create_track(det, frame_time)
            return []

        iou_matrix = np.zeros((len(active_tracks), len(detections)))
        for i, track in enumerate(active_tracks):
            for j, det in enumerate(detections):
                iou_matrix[i, j] = calculate_iou(track.bbox, det.bbox)

        matched_indices = []
        for i in range(iou_matrix.shape[0]):
            if i in [m[0] for m in matched_indices]:
                continue
            for j in range(iou_matrix.shape[1]):
                if j in [m[1] for m in matched_indices]:
                    continue
                if iou_matrix[i, j] >= self.match_thresh:
                    matched_indices.append((i, j))
                    break

        unmatched_tracks = set(range(len(active_tracks))) - set(m[0] for m in matched_indices)
        unmatched_detections = set(range(len(detections))) - set(m[1] for m in matched_indices)

        for track_idx, det_idx in matched_indices:
            track = active_tracks[track_idx]
            det = detections[det_idx]
            self._update_track(track, det, frame_time)

        for track_idx in sorted(unmatched_tracks, reverse=True):
            self.tracks[active_tracks[track_idx].track_id].time_since_update += 1

        for det_idx in unmatched_detections:
            self._create_track(detections[det_idx], frame_time)

        return list(unmatched_detections)

    def _create_track(self, detection: Detection, frame_time: float):
        """Create a new track."""
        self.track_id_count += 1
        track = Track(
            track_id=self.track_id_count,
            class_name=detection.class_name,
            bbox=detection.bbox,
            confidence=detection.confidence,
            timestamp=frame_time,
            hits=1,
            age=0,
            time_since_update=0
        )
        self.tracks[track.track_id] = track

    def _update_track(self, track: Track, detection: Detection, frame_time: float):
        """Update an existing track."""
        track.bbox = detection.bbox
        track.confidence = detection.confidence
        track.timestamp = frame_time
        track.hits += 1
        track.age += 1
        track.time_since_update = 0

    def _mark_lost_tracks(self):
        """Mark tracks as lost."""
        for track in self.tracks.values():
            track.time_since_update += 1

    def _get_active_tracks(self) -> List[TrackedObject]:
        """Get all active tracks."""
        active = []
        to_remove = []

        for track_id, track in self.tracks.items():
            if track.time_since_update <= self.max_time_lost:
                active.append(track.to_tracked_object())
            else:
                to_remove.append(track_id)

        for track_id in to_remove:
            del self.tracks[track_id]

        return active

    def get_tracks_by_class(self, class_name: str) -> List[TrackedObject]:
        """Get tracks filtered by class name."""
        return [
            t.to_tracked_object()
            for t in self.tracks.values()
            if t.class_name == class_name and t.time_since_update == 0
        ]

    def get_stats(self) -> Dict:
        """Get tracker statistics."""
        return {
            "active_tracks": len([t for t in self.tracks.values() if t.time_since_update == 0]),
            "total_tracks": len(self.tracks),
            "next_track_id": self.track_id_count,
            "frame_count": self.frame_count
        }


class MultiCameraTracker:
    """Manager for tracking across multiple cameras."""

    def __init__(self, iou_threshold: float = 0.3):
        self.iou_threshold = iou_threshold
        self.trackers: Dict[str, ByteTracker] = {}

    def get_tracker(self, camera_id: str) -> ByteTracker:
        """Get or create tracker for a camera."""
        if camera_id not in self.trackers:
            self.trackers[camera_id] = ByteTracker(
                track_thresh=0.5,
                track_buffer=30,
                match_thresh=self.iou_threshold,
                frame_rate=25.0
            )
        return self.trackers[camera_id]

    def update(self, camera_id: str, detections: List[Detection], frame_time: float) -> List[TrackedObject]:
        """Update tracking for a specific camera."""
        tracker = self.get_tracker(camera_id)
        return tracker.update(detections, frame_time)

    def get_all_active(self) -> Dict[str, List[TrackedObject]]:
        """Get active tracks from all cameras."""
        return {
            camera_id: tracker.get_tracks_by_class("person")
            for camera_id, tracker in self.trackers.items()
        }

    def get_stats(self) -> Dict:
        """Get statistics for all trackers."""
        return {
            camera_id: tracker.get_stats()
            for camera_id, tracker in self.trackers.items()
        }
