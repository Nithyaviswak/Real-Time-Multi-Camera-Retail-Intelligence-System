import time
import numpy as np
import cv2
import sys
from pathlib import Path
import json
from datetime import datetime

# Add backend to path
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from detection_service.detector import YOLODetector, MockDetector
from tracking_service.tracker import MultiCameraTracker
from analytics_service.analytics import AnalyticsEngine
from common.models import Detection

def create_test_frame(width=1920, height=1080):
    """Create a test frame with random content."""
    frame = np.random.randint(0, 255, (height, width, 3), dtype=np.uint8)
    cv2.rectangle(frame, (100, 100), (300, 400), (200, 150, 100), -1)
    cv2.rectangle(frame, (500, 200), (700, 500), (100, 200, 150), -1)
    cv2.rectangle(frame, (900, 150), (1100, 450), (150, 100, 200), -1)
    return frame

def benchmark_detection(detector, num_frames=100):
    """Benchmark detection performance."""
    print(f"\n{'='*50}")
    print("DETECTION BENCHMARK")
    print(f"{'='*50}")

    times = []

    for i in range(num_frames):
        frame = create_test_frame()

        start = time.perf_counter()
        detections = detector.detect(frame)
        elapsed = time.perf_counter() - start

        times.append(elapsed * 1000)

        if i % 20 == 0:
            print(f"Frame {i}: {elapsed*1000:.2f}ms, {len(detections)} detections")

    times = np.array(times)

    print(f"\n--- Detection Results ---")
    print(f"Frames processed: {num_frames}")
    print(f"Average time: {times.mean():.2f}ms")
    print(f"Median time: {np.median(times):.2f}ms")
    print(f"Min time: {times.min():.2f}ms")
    print(f"Max time: {times.max():.2f}ms")
    print(f"Std dev: {times.std():.2f}ms")
    print(f"FPS: {1000/times.mean():.1f}")

    return {
        "avg_ms": times.mean(),
        "median_ms": np.median(times),
        "fps": 1000/times.mean()
    }

def benchmark_tracking(tracker, num_frames=100):
    """Benchmark tracking performance."""
    print(f"\n{'='*50}")
    print("TRACKING BENCHMARK")
    print(f"{'='*50}")

    times = []
    camera_id = "test_cam"

    for i in range(num_frames):
        mock_detections = [
            Detection(
                class_id=0,
                class_name="person",
                confidence=0.85,
                bbox=[100 + i * 2 + j * 50, 100 + j * 30,
                      150 + i * 2 + j * 50, 300 + j * 30]
            )
            for j in range(3)
        ]

        start = time.perf_counter()
        tracks = tracker.update(camera_id, mock_detections, time.time())
        elapsed = time.perf_counter() - start

        times.append(elapsed * 1000)

    times = np.array(times)

    print(f"\n--- Tracking Results ---")
    print(f"Frames processed: {num_frames}")
    print(f"Average time: {times.mean():.2f}ms")
    print(f"Median time: {np.median(times):.2f}ms")
    print(f"FPS: {1000/times.mean():.1f}")
    print(f"Final tracks: {tracker.get_stats()}")

    return {
        "avg_ms": times.mean(),
        "fps": 1000/times.mean()
    }

def benchmark_analytics(analytics, num_frames=100):
    """Benchmark analytics performance."""
    print(f"\n{'='*50}")
    print("ANALYTICS BENCHMARK")
    print(f"{'='*50}")

    times = []
    camera_id = "test_cam"

    for i in range(num_frames):
        from common.models import TrackedObject

        mock_tracks = [
            TrackedObject(
                tracking_id=j,
                class_name="person",
                bbox=[100 + i * 2 + j * 50, 100 + j * 30,
                      150 + i * 2 + j * 50, 300 + j * 30],
                confidence=0.85,
                timestamp=None
            )
            for j in range(3)
        ]

        start = time.perf_counter()
        analytics.update(camera_id, mock_tracks, time.time())
        elapsed = time.perf_counter() - start

        times.append(elapsed * 1000)

    times = np.array(times)

    print(f"\n--- Analytics Results ---")
    print(f"Frames processed: {num_frames}")
    print(f"Average time: {times.mean():.2f}ms")
    print(f"Median time: {np.median(times):.2f}ms")
    print(f"FPS: {1000/times.mean():.1f}")
    print(f"Final metrics: {analytics.get_metrics()}")

    return {
        "avg_ms": times.mean(),
        "fps": 1000/times.mean()
    }

def benchmark_pipeline(num_frames=100):
    """Benchmark full pipeline."""
    print(f"\n{'='*50}")
    print("FULL PIPELINE BENCHMARK")
    print(f"{'='*50}")

    detector = MockDetector(confidence=0.5)
    tracker = MultiCameraTracker(iou_threshold=0.3)
    analytics = AnalyticsEngine(width=1920, height=1080)

    total_times = []

    for i in range(num_frames):
        frame = create_test_frame()

        start = time.perf_counter()

        detections = detector.detect(frame)
        tracks = tracker.update("test_cam", detections, time.time())
        analytics.update("test_cam", tracks, time.time())

        elapsed = time.perf_counter() - start
        total_times.append(elapsed * 1000)

        if i % 20 == 0:
            print(f"Frame {i}: {elapsed*1000:.2f}ms")

    total_times = np.array(total_times)

    print(f"\n--- Pipeline Results ---")
    print(f"Frames processed: {num_frames}")
    print(f"Average time: {total_times.mean():.2f}ms")
    print(f"Median time: {np.median(total_times):.2f}ms")
    print(f"Min time: {total_times.min():.2f}ms")
    print(f"Max time: {total_times.max():.2f}ms")
    print(f"FPS: {1000/total_times.mean():.1f}")

    return {
        "avg_ms": total_times.mean(),
        "fps": 1000/total_times.mean()
    }

def main():
    """Run all benchmarks."""
    print("="*50)
    print("RETAIL INTELLIGENCE BENCHMARK")
    print("="*50)
    print(f"Started at: {datetime.now()}")

    results = {}

    print("\n--- Running Detector Benchmark ---")
    detector = MockDetector()
    results["detection"] = benchmark_detection(detector, num_frames=100)

    print("\n--- Running Tracker Benchmark ---")
    tracker = MultiCameraTracker()
    results["tracking"] = benchmark_tracking(tracker, num_frames=100)

    print("\n--- Running Analytics Benchmark ---")
    analytics = AnalyticsEngine()
    results["analytics"] = benchmark_analytics(analytics, num_frames=100)

    print("\n--- Running Pipeline Benchmark ---")
    results["pipeline"] = benchmark_pipeline(num_frames=100)

    print("\n" + "="*50)
    print("SUMMARY")
    print("="*50)
    print(f"Detection: {results['detection']['avg_ms']:.2f}ms ({results['detection']['fps']:.1f} FPS)")
    print(f"Tracking:  {results['tracking']['avg_ms']:.2f}ms ({results['tracking']['fps']:.1f} FPS)")
    print(f"Analytics: {results['analytics']['avg_ms']:.2f}ms ({results['analytics']['fps']:.1f} FPS)")
    print(f"Pipeline:  {results['pipeline']['avg_ms']:.2f}ms ({results['pipeline']['fps']:.1f} FPS)")

    output_file = Path(__file__).parent / "benchmark_results.json"
    with open(output_file, 'w') as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "results": results
        }, f, indent=2)

    print(f"\nResults saved to: {output_file}")
    print(f"Completed at: {datetime.now()}")

if __name__ == "__main__":
    main()
