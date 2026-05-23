# Retail Intelligence System - Deployment Guide

## Prerequisites

### Hardware Requirements
- **Minimum**: 4-core CPU, 8GB RAM, 20GB storage
- **Recommended**: 8-core CPU, 16GB RAM, GPU (NVIDIA RTX 2060+), 50GB SSD
- **Edge**: NVIDIA Jetson Nano (for edge deployment)

### Software Requirements
- Docker 24.0+
- Docker Compose 2.20+
- NVIDIA Docker (for GPU support)
- 8GB+ free disk space

## Quick Start

### 1. Clone and Setup
```bash
git clone <repository-url>
cd retail-intelligence
```

### 2. Configure Environment
Edit `.env` file:
```env
# Database
POSTGRES_HOST=localhost
POSTGRES_PASSWORD=retail123

# ML Settings
DETECTION_MODEL=yolo11n
USE_CUDA=false  # Set to true if you have NVIDIA GPU
```

### 3. Start Services
```bash
# Start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f
```

### 4. Access Dashboard
- Frontend: http://localhost:3000
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## Docker Compose Services

| Service | Port | Description |
|---------|------|-------------|
| postgres | 5432 | PostgreSQL database |
| redis | 6379 | Redis cache |
| kafka | 9092 | Message streaming |
| stream-manager | 8002 | RTSP stream ingestion |
| detection-service | 8003 | YOLOv11 detection |
| tracking-service | 8004 | ByteTrack tracking |
| analytics-service | 8005 | Analytics engine |
| alert-service | 8006 | Anomaly detection |
| api-gateway | 8000, 8001 | REST + WebSocket |
| frontend | 3000 | React dashboard |

## Configuration

### Camera Configuration
Add RTSP streams in `.env`:
```env
RTSP_STREAMS=rtsp://user:pass@camera-ip:554/stream
```

Or configure multiple cameras:
```env
RTSP_STREAMS=rtsp://cam1,rtsp://cam2,rtsp://cam3,rtsp://cam4
```

### Model Configuration
```env
# Detection
DETECTION_MODEL=yolo11n  # Options: yolo11n, yolo11s, yolo11m
DETECTION_CONFIDENCE=0.5

# Tracking
TRACKING_IOU=0.3
```

### GPU Configuration
For GPU acceleration:
```env
USE_CUDA=true
```
Ensure NVIDIA Docker runtime is installed.

## Development Mode

### Backend Development
```bash
cd backend
pip install -r requirements.txt
python -m stream-manager.main
```

### Frontend Development
```bash
cd frontend/dashboard
npm install
npm run dev
```

## Production Deployment

### 1. Build Images
```bash
docker-compose build
```

### 2. Run Production Stack
```bash
docker-compose -f docker-compose.yml up -d
```

### 3. Health Checks
```bash
# Check all services
curl http://localhost:8000/health

# Check specific service
docker-compose exec api-gateway curl localhost:8000/health
```

### 4. View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f detection-service
```

## Testing

### Unit Tests
```bash
pytest backend/tests/unit/
```

### Integration Tests
```bash
pytest backend/tests/integration/
```

### E2E Tests
```bash
# Start test environment
docker-compose -f docker-compose.test.yml up -d

# Run tests
pytest backend/tests/e2e/
```

## Troubleshooting

### Common Issues

1. **Kafka not starting**
   ```bash
   # Check Kafka logs
   docker-compose logs kafka
   
   # Increase memory if needed
   ```

2. **Detection not working**
   ```bash
   # Check model download
   docker-compose logs detection-service
   
   # Verify GPU access
   nvidia-smi
   ```

3. **WebSocket connection failed**
   ```bash
   # Check API gateway
   curl http://localhost:8000/health
   
   # Check WebSocket port
   curl -i -N -H "Connection: Upgrade" -H "Upgrade: websocket" http://localhost:8001/ws/metrics
   ```

### Performance Tuning

1. **Increase detection workers**
   ```env
   DETECTION_WORKERS=4
   ```

2. **Optimize batch processing**
   ```env
   BATCH_SIZE=8
   ```

3. **Enable TensorRT**
   ```env
   USE_TENSORRT=true
   ```

## Monitoring

### Prometheus Metrics
Access metrics at: http://localhost:9090

### Grafana Dashboard
Access dashboards at: http://localhost:3001

## Security

### Production Checklist
- [ ] Change default passwords
- [ ] Enable SSL/TLS
- [ ] Configure firewall rules
- [ ] Set up authentication
- [ ] Enable audit logging

## Backup and Recovery

### Database Backup
```bash
docker-compose exec postgres pg_dump -U retail retail_intel > backup.sql
```

### Restore
```bash
docker-compose exec -T postgres psql -U retail retail_intel < backup.sql
```
