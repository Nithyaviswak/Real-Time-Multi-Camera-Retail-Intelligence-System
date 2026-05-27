import asyncio
import logging
from datetime import datetime
import time
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from common.config import settings
from common.utils import get_logger
from tracking_service.tracker import MultiCameraTracker, ByteTracker
from common.models import Detection

logger = get_logger(__name__)


async def main():
    """Main entry point for tracking service."""
    logger.info("Starting Tracking Service")

    tracker = MultiCameraTracker(iou_threshold=settings.tracking_iou)

    logger.info("Tracking service initialized")

    camera_ids = ["cam_01", "cam_02", "cam_03", "cam_04"]

    logger.info("Tracking service started successfully")

    try:
        frame_time = time.time()
        for i in range(100):
            for camera_id in camera_ids:
                mock_detections = [
                    Detection(
                        class_id=0,
                        class_name="person",
                        confidence=0.85,
                        bbox=[100 + i * 2, 100 + i, 150 + i * 2, 300 + i]
                    )
                ]
                tracks = tracker.update(camera_id, mock_detections, frame_time)

            await asyncio.sleep(0.1)

        logger.info(f"Stats: {tracker.get_stats()}")

    except KeyboardInterrupt:
        logger.info("Shutting down tracking service")


if __name__ == "__main__":
    asyncio.run(main())
