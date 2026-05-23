#!/usr/bin/env python3
"""
Demo script for Retail Intelligence System.
Runs a simple demo without requiring actual RTSP streams.
"""

import asyncio
import time
import sys
import cv2
import numpy as np
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))

import cv2
import numpy as np

from detection_service.detector import MockDetector
from tracking_service.tracker import MultiCameraTracker
from analytics_service.analytics import AnalyticsEngine
from alert_service.detector import AnomalyDetector
from common.models import Detection, TrackedObject
from common.utils import draw_boxes


def create_demo_frame(frame_num, width=1280, height=720):
    """Create a demo retail scene frame."""
    frame = np.ones((height, width, 3), dtype=np.uint8) * 200

    cv2.rectangle(frame, (50, 50), (300, 250), (180, 160, 140), -1)
    cv2.rectangle(frame, (350, 50), (600, 250), (180, 160, 140), -1)
    cv2.rectangle(frame, (650, 50), (900, 250), (180, 160, 140), -1)

    cv2.rectangle(frame, (100, 450), (250, 550), (100, 100, 200), -1)
    cv2.putText(frame, "CHECKOUT", (110, 440), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (50, 50, 50), 2)

    cv2.rectangle(frame, (950, 100), (1200, 650), (50, 50, 50), 3)
    cv2.putText(frame, "ENTRANCE", (1000, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (50, 50, 50), 2)

    num_people = (frame_num // 30) % 4 + 2
    for i in range(num_people):
        x = 200 + (i * 150) + (frame_num % 50)
        y = 300 + (i * 80) % 200

        if x < 900:
            cv2.circle(frame, (x, y), 25, (50, 100, 200), -1)
            cv2.rectangle(frame, (x-15, y+20), (x+15, y+70), (50, 100, 200), -1)

    for i in range(2):
        x = 150 + (frame_num % 100) * 3
        y = 500 + i * 40
        if x < 220:
            cv2.circle(frame, (x, y), 20, (70, 130, 170), -1)
            cv2.rectangle(frame, (x-12, y+15), (x+12, y+55), (70, 130, 170), -1)

    cv2.putText(frame, f"Frame: {frame_num}", (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
    cv2.putText(frame, f"Demo Mode", (width-180, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (100, 100, 100), 2)

    return frame


async def run_demo(duration_seconds=30):
    """Run the demo."""
    print("=" * 60)
    print("RETAIL INTELLIGENCE SYSTEM - DEMO")
    print("=" * 60)

    detector = MockDetector(confidence=0.5)
    tracker = MultiCameraTracker(iou_threshold=0.3)
    analytics = {f"cam_{i:02d}": AnalyticsEngine() for i in range(1, 5)}
    anomaly_detector = AnomalyDetector()

    camera_ids = list(analytics.keys())

    print("\nInitializing components...")
    print(f"- Detector: Mock Detector")
    print(f"- Trackers: {len(camera_ids)} cameras")
    print(f"- Analytics: {len(analytics)} engines")
    print(f"- Anomaly Detector: Enabled")
    print(f"\nRunning demo for {duration_seconds} seconds...")

    frame_num = 0
    start_time = time.time()

    try:
        while time.time() - start_time < duration_seconds:
            frame = create_demo_frame(frame_num)

            all_tracks = []
            for camera_id in camera_ids:
                detections = detector.detect(frame)
                tracks = tracker.update(camera_id, detections, time.time())
                analytics[camera_id].update(camera_id, tracks, time.time())
                all_tracks.extend(tracks)

            alerts = anomaly_detector.update("cam_01", all_tracks, time.time())

            if frame_num % 30 == 0:
                print(f"\n--- Frame {frame_num} ---")
                for camera_id in camera_ids:
                    metrics = analytics[camera_id].get_metrics()
                    print(f"{camera_id}: {metrics['footfall']['current_count']} people, "
                          f"footfall: {metrics['footfall']['total_footfall']}, "
                          f"queue: {metrics['queue_length']}")

                if alerts:
                    print("Alerts:")
                    for alert in alerts[-3:]:
                        print(f"  - {alert.alert_type}: {alert.message}")

            frame_num += 1
            await asyncio.sleep(0.04)

    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user")

    print("\n" + "=" * 60)
    print("DEMO COMPLETE")
    print("=" * 60)

    print("\nFinal Statistics:")
    print(f"- Total frames processed: {frame_num}")
    print(f"- Duration: {time.time() - start_time:.1f} seconds")

    for camera_id in camera_ids:
        metrics = analytics[camera_id].get_metrics()
        print(f"\n{camera_id}:")
        print(f"  Total footfall: {metrics['footfall']['total_footfall']}")
        print(f"  Peak people: {metrics['footfall']['current_count']}")
        print(f"  Avg dwell time: {metrics['footfall']['avg_dwell_time']:.1f}s")

    print(f"\nAlert stats: {anomaly_detector.get_alert_stats()}")


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Retail Intelligence Demo")
    parser.add_argument("--duration", type=int, default=30, help="Demo duration in seconds")
    args = parser.parse_args()

    asyncio.run(run_demo(args.duration))


if __name__ == "__main__":
    main()
