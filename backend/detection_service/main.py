import asyncio
import logging
from datetime import datetime
from typing import Dict
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from common.config import settings
from common.utils import get_logger
from detector import create_detector

logger = get_logger(__name__)


async def process_frame(camera_id: str, frame, detector):
    """Process a single frame with detection."""
    detections = detector.detect(frame)

    return {
        "camera_id": camera_id,
        "timestamp": datetime.utcnow().isoformat(),
        "detections": [
            {
                "class_id": d.class_id,
                "class_name": d.class_name,
                "confidence": d.confidence,
                "bbox": d.bbox
            }
            for d in detections
        ],
        "person_count": sum(1 for d in detections if d.class_name == "person")
    }


async def main():
    """Main entry point for detection service."""
    logger.info("Starting Detection Service")

    use_mock = not settings.use_cuda
    detector, model_name = create_detector(use_mock=use_mock)

    logger.info(f"Detector initialized: {model_name} (mock={use_mock})")

    logger.info("Detection service ready")
    logger.info(f"Stats: {detector.get_stats()}")

    await asyncio.sleep(1)

    logger.info("Detection service started successfully")

    try:
        while True:
            await asyncio.sleep(10)
            stats = detector.get_stats()
            logger.info(f"Stats: {stats}")

    except KeyboardInterrupt:
        logger.info("Shutting down detection service")


if __name__ == "__main__":
    asyncio.run(main())
