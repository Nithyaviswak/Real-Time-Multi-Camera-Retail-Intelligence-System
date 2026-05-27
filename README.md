<p align="center">
  <img src="docs/banner.png" alt="Retail Intelligence System Banner" width="100%"/>
</p>

<h1 align="center">🎯 Real-Time Multi-Camera Retail Intelligence System</h1>

<p align="center">
  <strong>Production-grade computer vision pipeline for real-time retail analytics — built with YOLOv11, ByteTrack, Kafka, and React</strong>
</p>

<p align="center">
  <a href="#-features"><img src="https://img.shields.io/badge/Features-12+-blue?style=for-the-badge" alt="Features"/></a>
  <a href="#-tech-stack"><img src="https://img.shields.io/badge/Python-3.11-green?style=for-the-badge&logo=python" alt="Python"/></a>
  <a href="#-tech-stack"><img src="https://img.shields.io/badge/FastAPI-0.109-teal?style=for-the-badge&logo=fastapi" alt="FastAPI"/></a>
  <a href="#-tech-stack"><img src="https://img.shields.io/badge/React-18-61DAFB?style=for-the-badge&logo=react" alt="React"/></a>
  <a href="#-quick-start"><img src="https://img.shields.io/badge/Docker-Ready-2496ED?style=for-the-badge&logo=docker" alt="Docker"/></a>
</p>

<p align="center">
  <a href="#-quick-start">Quick Start</a> •
  <a href="#-architecture">Architecture</a> •
  <a href="#-services">Services</a> •
  <a href="#-benchmarks">Benchmarks</a> •
  <a href="docs/DEPLOYMENT.md">Deployment Guide</a>
</p>

---

## 📋 Overview

A **microservices-based** computer vision system that processes multiple RTSP camera streams in real-time to deliver actionable retail analytics. The system detects and tracks customers, generates heatmaps, counts footfall, monitors queues, and flags anomalies — all streamed live to a React dashboard via WebSocket.

```
RTSP Cameras → Stream Manager → YOLOv11 Detection → ByteTrack Tracking
     ↓                                                       ↓
 Frame Extraction                              Analytics + Anomaly Detection
                                                       ↓
                                    Kafka → WebSocket → React Dashboard
```

---

## ✨ Features

<table>
<tr>
<td width="50%">

### 🔍 Computer Vision
- **YOLOv11 Object Detection** — nano/small/medium model variants
- **ByteTrack MOT** — real-time multi-object tracking with IoU matching
- **TensorRT / ONNX** acceleration support
- **Batch inference** for multi-camera throughput

</td>
<td width="50%">

### 📊 Analytics Engine
- **Footfall Counting** — entry/exit counting with 95%+ accuracy
- **Dwell Time Estimation** — per-customer time-in-store tracking
- **Heatmap Generation** — zone-based spatial density maps
- **Queue Detection** — real-time queue length monitoring

</td>
</tr>
<tr>
<td width="50%">

### 🚨 Alert System
- **Loitering Detection** — extended dwell in restricted zones
- **Fall Detection** — aspect ratio anomaly detection
- **Queue Overflow Alerts** — configurable threshold warnings
- **Speed Anomalies** — unusual movement pattern detection

</td>
<td width="50%">

### 🖥️ Dashboard & API
- **React Dashboard** — live metrics, charts, camera views
- **WebSocket Streaming** — sub-second real-time updates
- **REST API** — full camera, metrics, and alert management
- **Multi-Camera Views** — per-camera analytics drilldown

</td>
</tr>
</table>

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    RETAIL INTELLIGENCE SYSTEM                           │
│                                                                         │
│   ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────┐         │
│   │ Camera 1 │  │ Camera 2 │  │ Camera N │  │ Mock Stream  │         │
│   │  (RTSP)  │  │  (RTSP)  │  │  (RTSP)  │  │   (Demo)     │         │
│   └────┬─────┘  └────┬─────┘  └────┬─────┘  └──────┬───────┘         │
│        └──────────────┼─────────────┼───────────────┘                  │
│                       ▼                                                 │
│              ┌─────────────────┐                                        │
│              │  Stream Manager │  :8002                                 │
│              └────────┬────────┘                                        │
│                       │                                                  │
│        ┌──────────────┼──────────────┐                                  │
│        ▼              ▼              ▼                                  │
│   ┌──────────┐  ┌──────────┐  ┌──────────┐                            │
│   │Detection │  │Detection │  │Detection │  YOLOv11 :8003             │
│   │Worker 1  │  │Worker 2  │  │Worker N  │                            │
│   └────┬─────┘  └────┬─────┘  └────┬─────┘                            │
│        └──────────────┼──────────────┘                                  │
│                       ▼                                                  │
│              ┌─────────────────┐                                        │
│              │ Tracking Service│  ByteTrack :8004                      │
│              └────────┬────────┘                                        │
│                       │                                                  │
│        ┌──────────────┼──────────────┐                                  │
│        ▼              ▼              ▼                                  │
│   ┌──────────┐  ┌──────────┐  ┌──────────┐                            │
│   │Analytics │  │  Alert   │  │  Kafka   │                            │
│   │ :8005    │  │  :8006   │  │ Streams  │                            │
│   └────┬─────┘  └────┬─────┘  └────┬─────┘                            │
│        └──────────────┼──────────────┘                                  │
│                       ▼                                                  │
│   ┌──────────┐  ┌──────────┐  ┌──────────────────────────┐            │
│   │PostgreSQL│  │  Redis   │  │     API Gateway :8000    │            │
│   │(Storage) │  │ (Cache)  │  │  REST + WebSocket + Docs │            │
│   └──────────┘  └──────────┘  └────────────┬─────────────┘            │
│                                             ▼                           │
│                              ┌──────────────────────────┐              │
│                              │   React Dashboard :3000  │              │
│                              │ Metrics • Heatmaps • Alerts│             │
│                              └──────────────────────────┘              │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 🛠️ Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **ML / Detection** | YOLOv11 (Ultralytics), PyTorch | Real-time object detection |
| **Tracking** | ByteTrack | Multi-object tracking with IoU matching |
| **Backend** | Python 3.11, FastAPI, Uvicorn | Async microservices |
| **Messaging** | Apache Kafka, Redis Pub/Sub | Event streaming & caching |
| **Database** | PostgreSQL 15 | Analytics persistence |
| **Cache** | Redis 7 | Real-time state & pub/sub |
| **Frontend** | React 18, TypeScript, Vite | Live dashboard |
| **Charts** | Recharts | Data visualization |
| **Deployment** | Docker, Docker Compose | Container orchestration |

---

## 🚀 Quick Start

### Prerequisites

- **Docker** 24.0+ & **Docker Compose** 2.20+
- 8 GB RAM minimum (16 GB recommended)
- NVIDIA GPU + NVIDIA Docker *(optional, for CUDA acceleration)*

### 1. Clone the Repository

```bash
git clone https://github.com/Nithyaviswak/Real-Time-Multi-Camera-Retail-Intelligence-System.git
cd Real-Time-Multi-Camera-Retail-Intelligence-System
```

### 2. Configure Environment

```bash
# The .env file is pre-configured with defaults
# Edit if needed:
nano .env
```

Key settings in `.env`:

```env
DETECTION_MODEL=yolo11n       # Options: yolo11n, yolo11s, yolo11m
DETECTION_CONFIDENCE=0.5      # Detection confidence threshold
USE_CUDA=true                 # Set false if no NVIDIA GPU
TRACKING_IOU=0.3              # Tracking IoU threshold
RTSP_STREAMS=rtsp://...       # Comma-separated RTSP URLs
```

### 3. Launch All Services

```bash
docker compose up -d
```

### 4. Access the System

| Interface | URL |
|-----------|-----|
| 🖥️ **Dashboard** | [http://localhost:3000](http://localhost:3000) |
| 📡 **REST API** | [http://localhost:8000](http://localhost:8000) |
| 📖 **API Docs** (Swagger) | [http://localhost:8000/docs](http://localhost:8000/docs) |
| ❤️ **Health Check** | [http://localhost:8000/health](http://localhost:8000/health) |

### 5. Run the Demo (No Cameras Required)

```bash
pip install -r backend/detection_service/requirements.txt
python scripts/demo.py --duration 30
```

---

## 🧩 Services

<details>
<summary><b>📷 Stream Manager</b> — Port 8002</summary>

Manages RTSP/IP camera connections with automatic reconnection and mock stream fallback for testing.

- Frame extraction from multiple video streams
- Automatic fallback to mock streams if RTSP fails
- Configurable resolution and frame rate
- JPEG encoding for efficient transport

</details>

<details>
<summary><b>🔍 Detection Service</b> — Port 8003</summary>

YOLOv11-powered object detection with GPU/CPU support.

- Model variants: `yolo11n` (2.6 MB), `yolo11s` (9.4 MB), `yolo11m` (20 MB)
- Batch inference for multi-stream processing
- Configurable confidence thresholds
- Automatic CPU fallback with mock detector for testing

</details>

<details>
<summary><b>🏃 Tracking Service</b> — Port 8004</summary>

ByteTrack multi-object tracker with per-camera tracking state.

- IoU-based detection-to-track association
- Two-stage matching (high + low confidence)
- Automatic track lifecycle management
- Per-camera independent tracking

</details>

<details>
<summary><b>📈 Analytics Service</b> — Port 8005</summary>

Real-time business intelligence from tracked objects.

- **Footfall Counter** — entry/exit counting per person
- **Heatmap Generator** — spatial density with decay
- **Queue Detector** — polygon-based queue zone monitoring
- **Shelf Interaction Tracker** — product engagement tracking

</details>

<details>
<summary><b>🚨 Alert Service</b> — Port 8006</summary>

Anomaly detection and real-time alerting.

- **Loitering** — extended dwell in configured zones (>120s default)
- **Fall Detection** — bounding box aspect ratio anomalies
- **Speed Alerts** — excessive movement speed detection
- **Queue Overflow** — configurable queue length thresholds

</details>

<details>
<summary><b>🌐 API Gateway</b> — Port 8000</summary>

FastAPI REST + WebSocket gateway.

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/cameras` | GET | List all cameras |
| `/api/metrics` | GET | Current metrics for all cameras |
| `/api/metrics/{id}` | GET | Metrics for specific camera |
| `/api/analytics/footfall` | GET | Footfall analytics |
| `/api/analytics/heatmap` | GET | Heatmap data |
| `/api/alerts` | GET | Recent alerts |
| `/ws/metrics` | WS | Real-time metrics stream |
| `/ws/alerts` | WS | Real-time alert stream |

</details>

---

## 📊 Benchmarks

### Inference Performance (RTX 3070)

| Model | FPS (FP32) | FPS (FP16) | Latency | mAP@0.5 |
|-------|-----------|-----------|---------|---------|
| YOLOv11n | 120 | 180 | 8 ms | 0.52 |
| YOLOv11s | 65 | 95 | 15 ms | 0.61 |
| YOLOv11m | 36 | 52 | 28 ms | 0.68 |

### End-to-End Pipeline

| Stage | Latency |
|-------|---------|
| Frame Capture | 5–10 ms |
| Detection (YOLOv11n) | 8–10 ms |
| Tracking (ByteTrack) | 1–2 ms |
| Analytics | 0.5–1 ms |
| **Total** | **~16–26 ms** |

### Multi-Camera Scaling

| Cameras | FPS/Camera | CPU Load | GPU Load |
|---------|-----------|----------|----------|
| 1 | 30 | 25% | 40% |
| 4 | 28 | 50% | 75% |
| 8 | 20 | 75% | 90% |

### Analytics Accuracy

| Metric | Accuracy |
|--------|----------|
| Footfall Counting | 95.2% |
| Queue Detection | 94.3% |
| Tracking MOTA | 0.82 |
| Tracking IDF1 | 0.78 |

> 📄 Full benchmark report: [docs/BENCHMARK.md](docs/BENCHMARK.md)

---

## 📁 Project Structure

```
├── backend/
│   ├── common/                 # Shared config, models, utilities
│   │   ├── config.py           # Centralized settings (pydantic-settings)
│   │   ├── models.py           # Data models (Detection, TrackedObject, Alert)
│   │   └── utils.py            # IoU, heatmap, frame encoding helpers
│   ├── stream_manager/         # RTSP stream ingestion service
│   ├── detection_service/      # YOLOv11 object detection
│   ├── tracking_service/       # ByteTrack multi-object tracker
│   ├── analytics_service/      # Footfall, heatmaps, queues, shelves
│   ├── alert_service/          # Anomaly detection & alerting
│   └── api_gateway/            # FastAPI REST + WebSocket gateway
├── frontend/
│   ├── Dockerfile              # Multi-stage build (Node → Nginx)
│   └── dashboard/              # React + TypeScript + Vite app
│       ├── src/
│       │   ├── App.tsx         # Main dashboard component
│       │   ├── main.tsx        # Entry point
│       │   └── index.css       # Global styles
│       ├── package.json
│       └── vite.config.ts
├── scripts/
│   ├── demo.py                 # Standalone demo (no cameras needed)
│   ├── benchmark.py            # Performance benchmarking
│   └── setup.sh                # Environment setup script
├── docs/
│   ├── ARCHITECTURE.md         # System architecture deep-dive
│   ├── DEPLOYMENT.md           # Deployment & operations guide
│   └── BENCHMARK.md            # Full benchmark report
├── docker-compose.yml          # Complete service orchestration
├── .env                        # Environment configuration
└── .gitignore
```

---

## ⚙️ Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DETECTION_MODEL` | `yolo11n` | YOLO model variant |
| `DETECTION_CONFIDENCE` | `0.5` | Min detection confidence |
| `USE_CUDA` | `true` | Enable GPU acceleration |
| `TRACKING_IOU` | `0.3` | Tracking IoU threshold |
| `RTSP_STREAMS` | — | Comma-separated RTSP URLs |
| `POSTGRES_PASSWORD` | `retail123` | Database password |
| `REDIS_HOST` | `localhost` | Redis hostname |
| `KAFKA_BOOTSTRAP_SERVERS` | `localhost:9092` | Kafka brokers |

### Camera Configuration

```env
# Single camera
RTSP_STREAMS=rtsp://user:pass@192.168.1.100:554/stream

# Multiple cameras
RTSP_STREAMS=rtsp://cam1:554/stream,rtsp://cam2:554/stream,rtsp://cam3:554/stream
```

---

## 🔧 Development

### Backend (Local)

```bash
cd backend
pip install -r detection_service/requirements.txt
python -m detection_service.main
```

### Frontend (Local)

```bash
cd frontend/dashboard
npm install
npm run dev
```

### Full Stack (Docker)

```bash
docker compose up -d          # Start all services
docker compose logs -f        # Stream all logs
docker compose ps             # Check service status
docker compose down           # Stop everything
```

---

## 📖 Documentation

| Document | Description |
|----------|-------------|
| [Architecture](docs/ARCHITECTURE.md) | System design, data flow, component details |
| [Deployment Guide](docs/DEPLOYMENT.md) | Docker setup, GPU config, production checklist |
| [Benchmark Report](docs/BENCHMARK.md) | Performance metrics, scaling analysis |

---

## 🗺️ Roadmap

- [ ] Re-identification (Re-ID) for cross-camera person matching
- [ ] TensorRT INT8 quantization for edge deployment
- [ ] Kubernetes Helm chart for cloud scaling
- [ ] Grafana + Prometheus observability stack
- [ ] NVIDIA Jetson Nano edge deployment profile
- [ ] Age/gender demographic analytics
- [ ] Product shelf planogram compliance detection

---

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

---

<p align="center">
  Built with ❤️ using YOLOv11 • ByteTrack • FastAPI • React • Kafka • Docker
</p>
