import os
import sys

# Fix for pyzbar on Windows with Python 3.8+
if os.name == 'nt':
    try:
        pyzbar_path = os.path.join(os.path.dirname(sys.executable), "Lib", "site-packages", "pyzbar")
        os.add_dll_directory(pyzbar_path)
    except Exception:
        pass

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from starlette.middleware.base import BaseHTTPMiddleware

from app.config.settings import settings
from app.core.rate_limiter import limiter

# Define tags for OpenAPI documentation
tags_metadata = [
    {"name": "Health", "description": "System health and status checks"},
    {"name": "Authentication", "description": "User login and registration"},
    {"name": "Website Scanner", "description": "Website risk analysis"},
    {"name": "QR Scanner", "description": "QR code risk analysis"},
    {"name": "UPI Scanner", "description": "UPI ID risk analysis"},
    {"name": "History", "description": "Scan history retrieval"},
    {"name": "Reports", "description": "Report generation and download"},
]

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Backend API for the ScamShield AI Cyber Threat Analysis Platform.",
    version=settings.VERSION,
    openapi_tags=tags_metadata,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


# Security Headers Middleware
class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; img-src 'self' data: https://fastapi.tiangolo.com;"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=()"
        return response


app.add_middleware(SecurityHeadersMiddleware)

# CORS middleware for frontend access
origins = [origin.strip() for origin in settings.ALLOWED_ORIGINS.split(",")]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": {"code": f"HTTP_{exc.status_code}", "message": exc.detail},
        },
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Invalid request parameters",
                "details": exc.errors(),
            },
        },
    )


# Centralized Exception Handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    import logging

    logging.error(f"Unhandled Exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred.",
            },
        },
    )


@app.get("/")
def root():
    return {"message": "Welcome to ScamShield AI API"}


from app.api.v1 import auth, health, history, scanners, dashboard, email, message, apk

# Removed Base.metadata.create_all(bind=engine) - using Alembic now.

app.include_router(health.router, prefix="/api/v1")
app.include_router(auth.router, prefix="/api/v1/auth")
app.include_router(scanners.router, prefix="/api/v1/scanners")
app.include_router(history.router, prefix="/api/v1/history")
app.include_router(dashboard.router, prefix="/api/v1/dashboard")
app.include_router(email.router, prefix="/api/v1/email")
app.include_router(message.router, prefix="/api/v1/message")
app.include_router(apk.router, prefix="/api/v1/apk")
