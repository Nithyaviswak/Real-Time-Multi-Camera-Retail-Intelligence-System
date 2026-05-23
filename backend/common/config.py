from pydantic_settings import BaseSettings
from typing import List, Optional
import os


class Settings(BaseSettings):
    # Database
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_user: str = "retail"
    postgres_password: str = "retail123"
    postgres_db: str = "retail_intel"

    # Redis
    redis_host: str = "localhost"
    redis_port: int = 6379

    # Kafka
    kafka_bootstrap_servers: str = "localhost:9092"

    # Service settings
    detection_workers: int = 2
    tracking_workers: int = 2
    max_queue_size: int = 100

    # ML Models
    detection_model: str = "yolo11n"
    detection_confidence: float = 0.5
    tracking_iou: float = 0.3
    use_tensorrt: bool = False
    use_cuda: bool = True

    # RTSP Streams
    rtsp_streams: str = ""

    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    ws_port: int = 8001

    # Frontend (not used by backend, but in .env)
    vite_api_url: Optional[str] = None
    vite_ws_url: Optional[str] = None

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
        "extra": "ignore"
    }

    @property
    def database_url(self) -> str:
        return f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"

    @property
    def sync_database_url(self) -> str:
        return f"postgresql://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"

    @property
    def kafka_servers(self) -> List[str]:
        return self.kafka_bootstrap_servers.split(",")

    @property
    def streams_list(self) -> List[str]:
        if not self.rtsp_streams:
            return []
        return [s.strip() for s in self.rtsp_streams.split(",") if s.strip()]


settings = Settings()
