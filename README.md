# ScamShield AI

A modern, production-ready, AI-powered cybersecurity platform that helps users detect scams before they become victims.

## Features (Phase 1)
- **Website Scanner**: Deep URL analysis, SSL checking, and Threat Intel integration (VirusTotal & Google Safe Browsing).
- **QR Scanner**: Decodes and analyzes malicious QR links.
- **UPI Analyzer**: Checks UPI IDs for known fraud records.
- **Threat Center Dashboard**: Visualizations of scan history, active alerts, and analytics.

## Tech Stack
- **Frontend**: React 19, TypeScript, Vite, TailwindCSS, Framer Motion
- **Backend**: FastAPI (Python 3.11), SQLAlchemy 2.0, PostgreSQL
- **AI Engine**: IBM WatsonX API (via `ai_service.py`)
- **Infrastructure**: Docker, Docker Compose, Nginx

## Local Setup & Deployment

1. **Clone and Configure**
   ```bash
   cp backend/.env.example backend/.env
   # Add your JWT_SECRET and AI API keys
   ```

2. **Run via Docker Compose (Recommended)**
   ```bash
   docker compose up --build -d
   ```
   - Frontend: `http://localhost:5173`
   - Backend API: `http://localhost:8000`
   - API Docs: `http://localhost:8000/docs`

3. **Run DB Migrations (Alembic)**
   ```bash
   docker compose exec backend alembic upgrade head
   ```

## Development Environment
- Code Formatting: `black`, `ruff` (Backend), `prettier`, `oxlint` (Frontend)
- Testing: `pytest` with `pytest-cov` (Backend)

Run tests locally:
```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt -r requirements-dev.txt
pytest --cov=app tests/
```

## Security Best Practices Built-In
- CSP & Security Headers Middleware
- Strict CORS rules
- `slowapi` Rate Limiting
- JWT tokens with Refresh flow
- Bcrypt password hashing
- Secure DB Connection Pooling
