import asyncio
import logging
import sys
from pathlib import Path
import time

sys.path.append(str(Path(__file__).parent.parent))

from common.config import settings
from common.utils import get_logger
from analytics import AnalyticsEngine
from common.models import TrackedObject

logger = get_logger(__name__)


async def main():
    """Main entry point for analytics service."""
    logger.info("Starting Analytics Service")

    analytics = AnalyticsEngine(width=1920, height=1080)

    camera_ids = ["cam_01", "cam_02", "cam_03", "cam_04"]
    analytics_engines = {cam: AnalyticsEngine(width=1920, height=1080) for cam in camera_ids}

    logger.info("Analytics service initialized")

    try:
        frame_time = time.time()
        for i in range(100):
            for camera_id in camera_ids:
                mock_tracks = [
                    TrackedObject(
                        tracking_id=i + j,
                        class_name="person",
                        bbox=[100 + i * 2 + j * 50, 100 + j * 30, 150 + i * 2 + j * 50, 300 + j * 30],
                        confidence=0.85,
                        timestamp=None
                    )
                    for j in range(3)
                ]

                analytics_engines[camera_id].update(camera_id, mock_tracks, frame_time)
                metrics = analytics_engines[camera_id].get_metrics()

            await asyncio.sleep(0.1)

        for camera_id, engine in analytics_engines.items():
            logger.info(f"{camera_id}: {engine.get_metrics()}")

    except KeyboardInterrupt:
        logger.info("Shutting down analytics service")


if __name__ == "__main__":
    asyncio.run(main())
