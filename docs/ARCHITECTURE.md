# Retail Intelligence System - Architecture

## System Overview

The Retail Intelligence System is a real-time computer vision platform designed for retail analytics. It processes multiple camera streams simultaneously to detect customers, track their movements, and generate actionable insights.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         RETAIL INTELLIGENCE SYSTEM                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌──────────────┐   ┌──────────────┐   ┌──────────────┐   ┌─────────────┐ │
│  │   Camera 1  │   │   Camera 2   │   │   Camera N   │   │ Mock Stream │ │
│  │   (RTSP)    │   │   (RTSP)    │   │   (RTSP)    │   │   (Test)    │ │
│  └──────┬───────┘   └──────┬───────┘   └──────┬───────┘   └──────┬──────┘ │
│         │                  │                  │                  │        │
│         └──────────────────┼──────────────────┼──────────────────┘        │
│                             ▼                                              │
│                   ┌──────────────────┐                                      │
│                   │  Stream Manager │                                       │
│                   └────────┬─────────┘                                      │
│                            │                                                │
│         ┌──────────────────┼──────────────────┐                            │
│         ▼                  ▼                  ▼                            │
│  ┌─────────────┐   ┌─────────────┐   ┌─────────────┐                     │
│  │ Detection   │   │ Detection   │   │ Detection   │  (YOLOv11/RT-DETR)  │
│  │ Worker 1   │   │ Worker 2   │   │ Worker N    │                     │
│  └──────┬──────┘   └──────┬──────┘   └──────┬──────┘                     │
│         │                   │                  │                              │
│         └───────────────────┼──────────────────┘                             │
│                            ▼                                                │
│                   ┌──────────────┐                                          │
│                   │   Tracking   │  (ByteTrack)                             │
│                   │   Service    │                                          │
│                   └──────┬───────┘                                         │
│                          │                                                  │
│    ┌─────────────────────┼─────────────────────┐                           │
│    ▼                     ▼                     ▼                            │
│ ┌──────────┐       ┌──────────┐         ┌──────────┐                     │
│ │Analytics │       │  Alerts   │         │  Re-ID   │                     │
│ │ Service  │       │ Service   │         │ Service  │                     │
│ └────┬─────┘       └─────┬─────┘         └────┬─────┘                   │
│      │                    │                    │                            │
│      └────────────────────┼────────────────────┘                            │
│                           ▼                                                 │
│                   ┌──────────────┐                                          │
│                   │    Kafka     │                                          │
│                   └──────┬───────┘                                          │
│                          │                                                  │
│         ┌────────────────┼────────────────┐                                │
│         ▼                ▼                ▼                                │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                      │
│  │ PostgreSQL  │  │   Redis     │  │  WebSocket  │                      │
│  │ (Analytics) │  │ (Cache/Sub) │  │  (Live UI)  │                      │
│  └─────────────┘  └─────────────┘  └─────────────┘                      │
│                                                                           │
│  ┌──────────────────────────────────────────────────────┐                 │
│  │                    React Dashboard                    │                 │
│  │  (Live metrics, heatmaps, alerts, camera views)     │                 │
│  └──────────────────────────────────────────────────────┘                 │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Component Description

### 1. Stream Manager
- **Purpose**: Manages RTSP/IP camera streams
- **Technology**: FastAPI + OpenCV
- **Responsibilities**:
  - Frame extraction from video streams
  - Frame preprocessing and batching
  - Distribution to detection workers

### 2. Detection Service
- **Purpose**: Object detection using deep learning
- **Technology**: YOLOv11 (ultralytics)
- **Supported Models**:
  - YOLOv11n (nano - fastest)
  - YOLOv11s (small)
  - YOLOv11m (medium)
  - RT-DETR (optional)
- **Optimizations**:
  - ONNX export for inference
  - TensorRT acceleration (optional)
  - Batch processing

### 3. Tracking Service
- **Purpose**: Multi-object tracking across frames
- **Technology**: ByteTrack algorithm
- **Features**:
  - Real-time tracking
  - ID management
  - IoU-based matching
  - ReID embeddings (future)

### 4. Analytics Service
- **Purpose**: Business intelligence generation
- **Features**:
  - Footfall counting
  - Dwell time estimation
  - Heatmap generation
  - Queue detection
  - Shelf interaction tracking

### 5. Alert Service
- **Purpose**: Anomaly detection and alerting
- **Features**:
  - Loitering detection
  - Fall detection
  - Queue overflow alerts
  - Excessive speed alerts

### 6. API Gateway
- **Purpose**: REST API and WebSocket server
- **Technology**: FastAPI
- **Endpoints**:
  - `/api/cameras` - Camera management
  - `/api/metrics` - Real-time metrics
  - `/api/analytics` - Historical analytics
  - `/api/alerts` - Alert management
  - `/ws/metrics` - WebSocket for live data
  - `/ws/alerts` - WebSocket for alerts

### 7. Frontend Dashboard
- **Purpose**: Real-time visualization
- **Technology**: React + Vite + Recharts
- **Features**:
  - Live metrics display
  - Heatmap visualization
  - Alert notifications
  - Camera selection

## Data Flow

1. **Stream Ingestion**: RTSP frames → Stream Manager
2. **Detection**: Frames → YOLOv11 → Bounding Boxes
3. **Tracking**: Bounding Boxes → ByteTrack → Tracked Objects
4. **Analytics**: Tracked Objects → Analytics Engine → Metrics
5. **Alerts**: Tracked Objects → Anomaly Detector → Alerts
6. **Storage**: Metrics → PostgreSQL, Cache → Redis
7. **Streaming**: Kafka → WebSocket → Frontend

## Technology Stack

| Component | Technology |
|-----------|------------|
| ML Models | YOLOv11, ByteTrack |
| Backend | Python 3.11, FastAPI |
| Streaming | Kafka, Redis Streams |
| Database | PostgreSQL |
| Cache | Redis |
| Frontend | React 18, TypeScript |
| Visualization | Recharts |
| Deployment | Docker, Docker Compose |

## Performance Targets

| Metric | Target |
|--------|--------|
| FPS per stream | 25+ FPS |
| End-to-end latency | <100ms |
| Concurrent cameras | 4+ |
| Detection mAP | >0.5 |
| Tracking accuracy | >0.8 |

## Scaling Considerations

- Horizontal scaling via Kubernetes
- Load balancing via Kafka consumer groups
- Edge deployment on Jetson Nano
- Cloud deployment on GPU instances
