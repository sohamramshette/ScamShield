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
        "ALLOWED_ORIGINS", "http://localhost:5173,http://localhost:8000,http://127.0.0.1:5173"
    )

    # DB
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://scamshield:scamshield_pass@localhost:5432/scamshield_db",
    )

    # AI Config
    AI_MODE: str = os.getenv("AI_MODE", "live")
    IBM_API_KEY: str = os.getenv("IBM_API_KEY", "")
    IBM_PROJECT_ID: str = os.getenv("IBM_PROJECT_ID", "")
    IBM_URL: str = os.getenv("IBM_URL", "https://us-south.ml.cloud.ibm.com")

    # Security
    JWT_SECRET: str = os.getenv("JWT_SECRET", "supersecretkey")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    JWT_EXPIRATION: int = int(os.getenv("JWT_EXPIRATION", "1440"))  # In minutes

    # Threat Intel APIs
    VT_ENABLED: bool = os.getenv("VT_ENABLED", "true").lower() == "true"
    VT_API_KEY: str = os.getenv("VT_API_KEY", "")
    VT_BASE_URL: str = os.getenv("VT_BASE_URL", "https://www.virustotal.com/api/v3")
    VT_TIMEOUT_MS: int = int(os.getenv("VT_TIMEOUT_MS", "5000"))
    VT_MAX_RETRIES: int = int(os.getenv("VT_MAX_RETRIES", "2"))
    GSB_ENABLED: bool = os.getenv("GSB_ENABLED", "true").lower() == "true"
    GSB_API_KEY: str = os.getenv("GSB_API_KEY", "")
    GSB_BASE_URL: str = os.getenv("GSB_BASE_URL", "https://safebrowsing.googleapis.com/v4/threatMatches:find")
    GSB_TIMEOUT_MS: int = int(os.getenv("GSB_TIMEOUT_MS", "5000"))
    GSB_MAX_RETRIES: int = int(os.getenv("GSB_MAX_RETRIES", "2"))
    WHOIS_ENABLED: bool = os.getenv("WHOIS_ENABLED", "true").lower() == "true"
    WHOIS_TIMEOUT_MS: int = int(os.getenv("WHOIS_TIMEOUT_MS", "5000"))
    WHOIS_MAX_RETRIES: int = int(os.getenv("WHOIS_MAX_RETRIES", "2"))
    
    SSL_ENABLED: bool = os.getenv("SSL_ENABLED", "true").lower() == "true"
    SSL_TIMEOUT_MS: int = int(os.getenv("SSL_TIMEOUT_MS", "5000"))
    SSL_MAX_RETRIES: int = int(os.getenv("SSL_MAX_RETRIES", "2"))
    
    URLSCAN_ENABLED: bool = os.getenv("URLSCAN_ENABLED", "true").lower() == "true"
    URLSCAN_API_KEY: str = os.getenv("URLSCAN_API_KEY", "")
    URLSCAN_BASE_URL: str = os.getenv("URLSCAN_BASE_URL", "https://urlscan.io/api/v1/search/")
    URLSCAN_TIMEOUT_MS: int = int(os.getenv("URLSCAN_TIMEOUT_MS", "5000"))
    URLSCAN_MAX_RETRIES: int = int(os.getenv("URLSCAN_MAX_RETRIES", "2"))
    
    PHISHTANK_ENABLED: bool = os.getenv("PHISHTANK_ENABLED", "true").lower() == "true"
    PHISHTANK_API: str = os.getenv("PHISHTANK_API", "https://checkurl.phishtank.com/checkurl/")
    PHISHTANK_TIMEOUT_MS: int = int(os.getenv("PHISHTANK_TIMEOUT_MS", "5000"))
    PHISHTANK_MAX_RETRIES: int = int(os.getenv("PHISHTANK_MAX_RETRIES", "2"))
    
    ABUSEIPDB_ENABLED: bool = os.getenv("ABUSEIPDB_ENABLED", "true").lower() == "true"
    ABUSEIPDB_API_KEY: str = os.getenv("ABUSEIPDB_API_KEY", "")
    ABUSEIPDB_BASE_URL: str = os.getenv("ABUSEIPDB_BASE_URL", "https://api.abuseipdb.com/api/v2/check")
    ABUSEIPDB_TIMEOUT_MS: int = int(os.getenv("ABUSEIPDB_TIMEOUT_MS", "5000"))
    ABUSEIPDB_MAX_RETRIES: int = int(os.getenv("ABUSEIPDB_MAX_RETRIES", "2"))

    # File storage
    REPORT_DIRECTORY: str = os.getenv("REPORT_DIRECTORY", "reports")

    class Config:
        env_file = ".env"


settings = Settings()
