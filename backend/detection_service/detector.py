import torch
import numpy as np
from typing import List, Dict, Optional, Tuple
import logging
import cv2
import sys
from pathlib import Path

try:
    from ultralytics import YOLO
    ULTRALYTICS_AVAILABLE = True
except ImportError:
    ULTRALYTICS_AVAILABLE = False

sys.path.append(str(Path(__file__).parent.parent))

from common.config import settings
from common.utils import get_logger
from common.models import Detection

logger = get_logger(__name__)


class YOLODetector:
    """YOLOv11 object detector with support for ONNX/TensorRT."""

    PERSON_CLASS_ID = 0
    RELEVANT_CLASSES = [0, 1, 2, 3, 5, 7]  # person, bicycle, car, motorcycle, bus, truck

    def __init__(
        self,
        model_name: str = "yolo11n",
        confidence: float = 0.5,
        device: str = "cuda" if torch.cuda.is_available() else "cpu"
    ):
        self.model_name = model_name
        self.confidence = confidence
        self.device = device
        self.model = None
        self.inference_count = 0
        self.total_inference_time = 0.0

        self._load_model()

    def _load_model(self):
        """Load YOLOv11 model."""
        if not ULTRALYTICS_AVAILABLE:
            logger.warning("Ultralytics not available, using mock detector")
            self.model = None
            return

        try:
            logger.info(f"Loading YOLOv11 model: {self.model_name} on {self.device}")

            model_path = Path(__file__).parent.parent.parent / "models" / f"{self.model_name}.pt"
            if model_path.exists():
                self.model = YOLO(str(model_path))
            else:
                logger.info(f"Model not found at {model_path}, using pretrained")
                self.model = YOLO(f"{self.model_name}.pt")

            if self.device == "cuda" and torch.cuda.is_available():
                self.model.to("cuda")

            logger.info(f"YOLOv11 model loaded successfully")

        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            raise

    def detect(self, frame: np.ndarray) -> List[Detection]:
        """Detect objects in a frame."""
        if self.model is None or not ULTRALYTICS_AVAILABLE:
            return []

        try:
            import time
            start_time = time.perf_counter()

            results = self.model(
                frame,
                conf=self.confidence,
                classes=self.RELEVANT_CLASSES,
                verbose=False,
                device=self.device
            )

            inference_time = time.perf_counter() - start_time
            self.inference_count += 1
            self.total_inference_time += inference_time

            detections = []
            if results and len(results) > 0:
                result = results[0]
                boxes = result.boxes

                for i in range(len(boxes)):
                    box = boxes[i]
                    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                    conf = float(box.conf[0])
                    cls = int(box.cls[0])
                    class_name = result.names[cls]

                    detection = Detection(
                        class_id=cls,
                        class_name=class_name,
                        confidence=conf,
                        bbox=[float(x1), float(y1), float(x2), float(y2)]
                    )
                    detections.append(detection)

            return detections

        except Exception as e:
            logger.error(f"Detection failed: {e}")
            return []

    def detect_batch(self, frames: List[np.ndarray]) -> List[List[Detection]]:
        """Detect objects in multiple frames."""
        if self.model is None or not ULTRALYTICS_AVAILABLE:
            return [[] for _ in frames]

        try:
            results = self.model(
                frames,
                conf=self.confidence,
                classes=self.RELEVANT_CLASSES,
                verbose=False,
                device=self.device
            )

            all_detections = []
            for result in results:
                detections = []
                boxes = result.boxes

                for i in range(len(boxes)):
                    box = boxes[i]
                    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                    conf = float(box.conf[0])
                    cls = int(box.cls[0])
                    class_name = result.names[cls]

                    detection = Detection(
                        class_id=cls,
                        class_name=class_name,
                        confidence=conf,
                        bbox=[float(x1), float(y1), float(x2), float(y2)]
                    )
                    detections.append(detection)

                all_detections.append(detections)

            return all_detections

        except Exception as e:
            logger.error(f"Batch detection failed: {e}")
            return [[] for _ in frames]

    def get_fps(self) -> float:
        """Get average inference FPS."""
        if self.inference_count == 0:
            return 0.0
        return self.inference_count / self.total_inference_time if self.total_inference_time > 0 else 0.0

    def get_stats(self) -> Dict:
        """Get detector statistics."""
        return {
            "model_name": self.model_name,
            "device": self.device,
            "inference_count": self.inference_count,
            "total_inference_time": self.total_inference_time,
            "avg_fps": self.get_fps(),
            "confidence_threshold": self.confidence
        }


class MockDetector:
    """Mock detector for testing without actual model."""

    def __init__(self, confidence: float = 0.5):
        self.confidence = confidence
        self.inference_count = 0

    def detect(self, frame: np.ndarray) -> List[Detection]:
        """Generate mock detections."""
        self.inference_count += 1

        height, width = frame.shape[:2]
        detections = []

        num_detections = np.random.randint(0, 4)
        for _ in range(num_detections):
            x1 = np.random.randint(0, width - 100)
            y1 = np.random.randint(0, height - 100)
            x2 = x1 + np.random.randint(50, 150)
            y2 = y1 + np.random.randint(100, 250)

            detections.append(Detection(
                class_id=0,
                class_name="person",
                confidence=np.random.uniform(0.5, 0.95),
                bbox=[float(x1), float(y1), float(x2), float(y2)]
            ))

        return detections

    def detect_batch(self, frames: List[np.ndarray]) -> List[List[Detection]]:
        """Generate mock detections for batch."""
        return [self.detect(frame) for frame in frames]

    def get_fps(self) -> float:
        return 30.0

    def get_stats(self) -> Dict:
        return {
            "model_name": "mock",
            "device": "mock",
            "inference_count": self.inference_count
        }


def create_detector(use_mock: bool = False) -> Tuple:
    """Factory function to create detector."""
    if use_mock:
        return MockDetector(settings.detection_confidence), "mock"

    detector = YOLODetector(
        model_name=settings.detection_model,
        confidence=settings.detection_confidence,
        device="cuda" if settings.use_cuda else "cpu"
    )
    return detector, settings.detection_model
