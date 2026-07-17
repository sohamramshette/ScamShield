import logging
import sys

from app.config.settings import settings


def setup_logging():
    level_map = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL,
    }
    from pythonjsonlogger import jsonlogger

    log_level = level_map.get(settings.LOG_LEVEL.upper(), logging.INFO)

    logger = logging.getLogger()
    logger.setLevel(log_level)

    # Remove existing handlers
    if logger.hasHandlers():
        logger.handlers.clear()

    handler = logging.StreamHandler(sys.stdout)

    if settings.ENVIRONMENT == "production":
        formatter = jsonlogger.JsonFormatter(
            "%(asctime)s %(name)s %(levelname)s %(message)s"
        )
    else:
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )

    handler.setFormatter(formatter)
    logger.addHandler(handler)

    logger = logging.getLogger("scamshield")
    return logger


logger = setup_logging()


# Expose common log actions
def log_scan_started(scan_id: str, scan_type: str):
    logger.info(f"Scan Started | ID: {scan_id} | Type: {scan_type}")


def log_scan_completed(scan_id: str, scan_type: str, risk_score: int):
    logger.info(
        f"Scan Completed | ID: {scan_id} | Type: {scan_type} | Risk Score: {risk_score}"
    )


def log_threat_api_called(api_name: str, target: str):
    logger.info(f"Threat API Called | API: {api_name} | Target: {target}")


def log_ai_response(time_ms: int, status: str):
    logger.info(f"AI Response Time | Time: {time_ms}ms | Status: {status}")


def log_error(context: str, error_msg: str):
    logger.error(f"Error | Context: {context} | Details: {error_msg}")
