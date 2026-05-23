import asyncio
import cv2
import logging
import uuid
from datetime import datetime
from typing import Dict, Optional
import numpy as np
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent.parent))

from common.config import settings
from common.utils import get_logger, encode_frame_to_jpeg

logger = get_logger(__name__)


class StreamCapture:
    """RTSP stream capture with frame extraction."""

    def __init__(self, camera_id: str, rtsp_url: str):
        self.camera_id = camera_id
        self.rtsp_url = rtsp_url
        self.capture: Optional[cv2.VideoCapture] = None
        self.is_active = False
        self.frame_count = 0
        self.fps = 0.0
        self.width = 0
        self.height = 0

    def connect(self) -> bool:
        """Connect to RTSP stream."""
        self.capture = cv2.VideoCapture(self.rtsp_url)
        if not self.capture.isOpened():
            logger.error(f"Failed to open stream: {self.rtsp_url}")
            return False

        self.width = int(self.capture.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(self.capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.fps = self.capture.get(cv2.CAP_PROP_FPS)
        self.is_active = True
        logger.info(f"Connected to stream: {self.camera_id} ({self.width}x{self.height} @ {self.fps}fps)")
        return True

    def read_frame(self) -> Optional[Dict]:
        """Read a frame from the stream."""
        if not self.is_active or not self.capture:
            return None

        ret, frame = self.capture.read()
        if not ret:
            return None

        self.frame_count += 1

        return {
            "camera_id": self.camera_id,
            "frame_id": self.frame_count,
            "timestamp": datetime.utcnow(),
            "frame": frame,
            "width": self.width,
            "height": self.height
        }

    def release(self):
        """Release stream resources."""
        if self.capture:
            self.capture.release()
        self.is_active = False


class MockStreamCapture:
    """Mock stream capture for testing without actual RTSP streams."""

    def __init__(self, camera_id: str, width: int = 1920, height: int = 1080):
        self.camera_id = camera_id
        self.width = width
        self.height = height
        self.frame_count = 0
        self.fps = 25.0
        self.is_active = False

        self._background = None
        self._persons = []
        self._create_mock_scene()

    def _create_mock_scene(self):
        """Create a mock retail scene."""
        self._background = np.zeros((self.height, self.width, 3), dtype=np.uint8)
        self._background[:] = (200, 200, 200)

        cv2.rectangle(self._background, (50, 50), (200, 400), (180, 160, 140), -1)
        cv2.rectangle(self._background, (300, 50), (450, 400), (180, 160, 140), -1)
        cv2.rectangle(self._background, (500, 50), (650, 400), (180, 160, 140), -1)

        cv2.rectangle(self._background, (100, 500), (300, 600), (100, 100, 200), -1)

        cv2.putText(self._background, "ENTRANCE", (100, 480),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (50, 50, 50), 2)

    def connect(self) -> bool:
        """Simulate connection."""
        self.is_active = True
        logger.info(f"Mock stream connected: {self.camera_id} ({self.width}x{self.height} @ {self.fps}fps)")
        return True

    def read_frame(self) -> Optional[Dict]:
        """Generate a mock frame with moving persons."""
        if not self.is_active:
            return None

        self.frame_count += 1

        frame = self._background.copy()

        if self.frame_count % 150 < 75:
            x = 100 + (self.frame_count % 75) * 8
            y = 700 - (self.frame_count % 75) * 5
            cv2.circle(frame, (x, y), 30, (50, 100, 200), -1)
            cv2.rectangle(frame, (x-20, y+20), (x+20, y+80), (50, 100, 200), -1)

        for i in range(3):
            offset = (self.frame_count + i * 50) % 200
            x = 150 + i * 200 + offset // 2
            y = 200 + i * 50
            if x < 600:
                cv2.circle(frame, (x, y), 25, (80, 150, 80), -1)
                cv2.rectangle(frame, (x-15, y+20), (x+15, y+60), (80, 150, 80), -1)

        for i in range(2):
            offset = (self.frame_count + i * 80) % 180
            x = 400 + offset * 3
            y = 550 + i * 30
            if x < 750:
                cv2.circle(frame, (x, y), 28, (70, 130, 170), -1)
                cv2.rectangle(frame, (x-18, y+22), (x+18, y+75), (70, 130, 170), -1)

        cv2.putText(frame, f"Camera: {self.camera_id}", (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.putText(frame, f"Frame: {self.frame_count}", (20, 70),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

        return {
            "camera_id": self.camera_id,
            "frame_id": self.frame_count,
            "timestamp": datetime.utcnow(),
            "frame": frame,
            "width": self.width,
            "height": self.height
        }

    def release(self):
        """Release mock stream."""
        self.is_active = False


class StreamManager:
    """Manages multiple camera streams."""

    def __init__(self):
        self.streams: Dict[str, StreamCapture] = {}
        self.mock_streams: Dict[str, MockStreamCapture] = {}
        self._running = False

    def add_stream(self, camera_id: str, rtsp_url: str, use_mock: bool = False):
        """Add a stream to manage."""
        if use_mock:
            self.mock_streams[camera_id] = MockStreamCapture(camera_id)
        else:
            self.streams[camera_id] = StreamCapture(camera_id, rtsp_url)

    def connect_all(self) -> bool:
        """Connect to all streams."""
        all_connected = True

        for camera_id, stream in self.streams.items():
            if not stream.connect():
                logger.warning(f"Failed to connect {camera_id}, using mock")
                self.mock_streams[camera_id] = MockStreamCapture(camera_id)
                all_connected = False

        for mock_stream in self.mock_streams.values():
            mock_stream.connect()

        return len(self.streams) > 0 or len(self.mock_streams) > 0

    def read_all_frames(self) -> Dict[str, Dict]:
        """Read frames from all streams."""
        frames = {}

        for camera_id, stream in self.streams.items():
            frame_data = stream.read_frame()
            if frame_data:
                frames[camera_id] = frame_data

        for camera_id, mock_stream in self.mock_streams.items():
            frame_data = mock_stream.read_frame()
            if frame_data:
                frames[camera_id] = frame_data

        return frames

    def stop(self):
        """Stop all streams."""
        self._running = False
        for stream in self.streams.values():
            stream.release()
        for mock_stream in self.mock_streams.values():
            mock_stream.release()


async def main():
    """Main entry point for stream manager."""
    logger.info("Starting Stream Manager Service")

    manager = StreamManager()

    streams_config = [
        ("cam_01", "rtsp://demo:demo@ipvmdemo.dyndns.org:5541/onvif-media/media.httptest"),
        ("cam_02", "rtsp://demo:demo@ipvmdemo.dyndns.org:5541/onvif-media/media.httptest"),
    ]

    for camera_id, rtsp_url in streams_config:
        manager.add_stream(camera_id, rtsp_url, use_mock=True)

    if not manager.connect_all():
        logger.error("Failed to connect to any streams")
        return

    logger.info("Processing video streams...")

    try:
        while True:
            frames = manager.read_all_frames()
            if not frames:
                break

            for camera_id, frame_data in frames.items():
                frame = frame_data["frame"]
                jpeg_bytes = encode_frame_to_jpeg(frame, quality=70)
                logger.debug(f"Frame {frame_data['frame_id']} from {camera_id}: {len(jpeg_bytes)} bytes")

            await asyncio.sleep(0.04)

    except KeyboardInterrupt:
        logger.info("Shutting down...")
    finally:
        manager.stop()


if __name__ == "__main__":
    asyncio.run(main())
