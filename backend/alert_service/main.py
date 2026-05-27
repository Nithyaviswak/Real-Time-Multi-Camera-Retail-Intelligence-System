import asyncio
import logging
import sys
from pathlib import Path
import time

sys.path.append(str(Path(__file__).parent.parent))

from common.config import settings
from common.utils import get_logger
from alert_service.detector import AnomalyDetector, QueueAlertMonitor
from common.models import TrackedObject

logger = get_logger(__name__)


async def main():
    """Main entry point for alert service."""
    logger.info("Starting Alert Service")

    anomaly_detector = AnomalyDetector()
    queue_monitor = QueueAlertMonitor()

    logger.info("Alert service initialized")

    try:
        camera_ids = ["cam_01", "cam_02", "cam_03", "cam_04"]

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

                alerts = anomaly_detector.update(camera_id, mock_tracks, frame_time)

                queue_alert = queue_monitor.check_queue(camera_id, 4, frame_time)
                if queue_alert:
                    alerts.append(queue_alert)

            await asyncio.sleep(0.1)

        logger.info(f"Alert stats: {anomaly_detector.get_alert_stats()}")

    except KeyboardInterrupt:
        logger.info("Shutting down alert service")


if __name__ == "__main__":
    asyncio.run(main())
