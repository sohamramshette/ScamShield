# ScamShield AI - API Documentation

## OpenAPI / Swagger
The OpenAPI specification is available at `docs/openapi.json`. 
When running the backend, you can access the interactive Swagger UI at:
- http://localhost:8000/docs
- http://localhost:8000/redoc

## Postman Collection
To generate a Postman collection:
1. Open Postman.
2. Click **Import**.
3. Select `docs/openapi.json`.
4. Postman will automatically generate a full collection with all endpoints, request bodies, and responses.

## Key Endpoints

### Authentication
- `POST /api/v1/auth/register`: Register a new user (Body: `{ "email": "...", "password": "..." }`)
- `POST /api/v1/auth/login`: Login (Form Data: `username`, `password`) - Returns `access_token` and `refresh_token`
- `POST /api/v1/auth/refresh`: Refresh token (Body: `{ "refresh_token": "..." }`)

### Health
- `GET /api/v1/health`: Get system health status

### Scanners
- `POST /api/v1/scanners/website`: Scan a URL
- `POST /api/v1/scanners/qr`: Scan a QR code content
- `POST /api/v1/scanners/upi`: Scan a UPI ID

### History
- `GET /api/v1/history/scans`: Get scan history (requires authentication)
