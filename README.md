# Retail Intelligence System

Production-grade real-time computer vision system for retail analytics.

## Features

- **Customer Detection**: YOLOv11-based object detection
- **Multi-Camera Tracking**: ByteTrack for multi-object tracking
- **Footfall Analytics**: Entry/exit counting
- **Heatmap Generation**: Zone-based heatmaps
- **Queue Detection**: Real-time queue monitoring
- **Shelf Interaction**: Product interaction tracking
- **Dwell Time**: Customer dwell time estimation
- **Anomaly Detection**: Loitering, fall detection, alerts
- **Real-time Dashboard**: WebSocket-based live updates

## Quick Start

```bash
# Install dependencies
pip install -r backend/stream-manager/requirements.txt

# Run demo
python scripts/demo.py --duration 30
```

## Docker Deployment

```bash
docker-compose up -d
```

Access dashboard at http://localhost:3000

## Documentation

- [Architecture](docs/ARCHITECTURE.md)
- [Deployment Guide](docs/DEPLOYMENT.md)
- [Benchmark Report](docs/BENCHMARK.md)

## Requirements

- Python 3.11+
- 8GB RAM minimum
- CUDA-capable GPU (optional)
