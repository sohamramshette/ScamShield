import os

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # App
    PROJECT_NAME: str = "ScamShield AI"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = os.getenv(
        "ENVIRONMENT", "development"
    )  # development, testing, production
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    # Security / CORS
    ALLOWED_ORIGINS: str = os.getenv(
        "ALLOWED_ORIGINS", "http://localhost:5173,http://localhost:8000"
    )

    # DB
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://scamshield:scamshield_pass@localhost:5432/scamshield_db",
    )

    # AI Config
    AI_MODE: str = os.getenv("AI_MODE", "mock")
    IBM_API_KEY: str = os.getenv("IBM_API_KEY", "")
    IBM_PROJECT_ID: str = os.getenv("IBM_PROJECT_ID", "")
    IBM_URL: str = os.getenv("IBM_URL", "https://us-south.ml.cloud.ibm.com")

    # Security
    JWT_SECRET: str = os.getenv("JWT_SECRET", "supersecretkey")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    JWT_EXPIRATION: int = int(os.getenv("JWT_EXPIRATION", "1440"))  # In minutes

    # Threat Intel APIs
    VIRUSTOTAL_API_KEY: str = os.getenv("VIRUSTOTAL_API_KEY", "")
    GOOGLE_SAFE_BROWSING_KEY: str = os.getenv("GOOGLE_SAFE_BROWSING_KEY", "")
    PHISHTANK_API: str = os.getenv("PHISHTANK_API", "")
    WHOIS_PROVIDER: str = os.getenv("WHOIS_PROVIDER", "")

    # File storage
    REPORT_DIRECTORY: str = os.getenv("REPORT_DIRECTORY", "reports")

    class Config:
        env_file = ".env"


settings = Settings()
