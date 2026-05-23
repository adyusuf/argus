from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Argus"
    debug: bool = False
    secret_key: str = "change-me-in-production"

    database_url: str = "postgresql+asyncpg://argus:argus_dev@db:5432/argus"
    redis_url: str = "redis://redis:6379/0"

    ai_provider: str = "mock"
    aws_access_key_id: str = ""
    aws_secret_access_key: str = ""
    aws_region: str = "ap-southeast-2"

    rtsp_simulator_url: str = "rtsp://rtsp-simulator:8554"

    frame_interval_seconds: int = 10
    max_concurrent_streams: int = 50

    model_config = {"env_file": ".env"}


settings = Settings()
