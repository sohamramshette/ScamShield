# ScamShield AI - Deployment Guide

This guide covers everything required to successfully deploy ScamShield AI in a production environment using Docker, Render, or Railway.

---

## 1. Environment Variables

Both the frontend and backend require specific environment variables to function in production.

### Backend (`.env` or Cloud Secrets)
| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `ENVIRONMENT` | Must be set to `production` | Yes | `development` |
| `DATABASE_URL` | PostgreSQL connection string | Yes | `sqlite:///./sqlite.db` |
| `ALLOWED_ORIGINS` | Comma-separated list of allowed frontend URLs | Yes | `http://localhost:5173` |
| `JWT_SECRET` | Secure cryptographic key for auth | Yes | `supersecretkey` |
| `AI_MODE` | Set to `mock` or `watsonx` | No | `mock` |
| `IBM_API_KEY` | Required if `AI_MODE=watsonx` | No | - |

### Frontend (Build Time)
| Variable | Description | Required |
|----------|-------------|----------|
| `VITE_API_URL` | The public URL of the deployed backend API | Yes |

---

## 2. Docker Deployment Instructions (VPS / Self-Hosted)

If you are deploying to an AWS EC2 instance, DigitalOcean Droplet, or Linode:

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/ScamShield.git
   cd ScamShield
   ```
2. **Configure Environment:**
   Update the `docker-compose.yml` file or create a `.env` file to replace default development secrets.
3. **Start the Stack:**
   ```bash
   docker-compose up --build -d
   ```
4. **Reverse Proxy:**
   Set up Nginx or Traefik in front of ports `5173` and `8000` to handle SSL termination.

---

## 3. Render Deployment (PaaS)

ScamShield includes a `render.yaml` configuration file for zero-config deployments.

1. Create an account on [Render](https://render.com).
2. Go to your Dashboard and click **New -> Blueprint**.
3. Connect your GitHub repository.
4. Render will automatically read `render.yaml` and provision:
   - A PostgreSQL Database
   - A Backend Web Service (Docker)
   - A Frontend Web Service (Docker)
5. **Important:** After deployment, update the `ALLOWED_ORIGINS` in the backend service and the `VITE_API_URL` in the frontend service with the exact Render URLs generated.

---

## 4. Railway Deployment (PaaS)

1. Create an account on [Railway](https://railway.app).
2. Click **New Project** -> **Deploy from GitHub repo**.
3. Add a **PostgreSQL** plugin to the project.
4. Railway will automatically detect the Dockerfiles. Set the start commands:
   - Backend: `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - Frontend: Ensure port 80 is exposed for Nginx.
5. Link the `DATABASE_URL` from the PostgreSQL plugin to the backend service.

---

## 5. Health Check URLs

Once deployed, use these URLs to verify uptime:
- **Backend Health:** `https://your-backend-url.com/api/v1/health`
  - *Expected Response:* `{"status": "healthy", ...}`
- **Backend Docs:** `https://your-backend-url.com/docs`
- **Frontend Dashboard:** `https://your-frontend-url.com`

---

## 6. Deployment Checklist

- [ ] `ENVIRONMENT` set to `production`
- [ ] Production Database is provisioned and URL is linked
- [ ] `JWT_SECRET` generated securely (e.g., `openssl rand -hex 32`)
- [ ] Frontend `VITE_API_URL` points to Backend HTTPS URL
- [ ] Backend `ALLOWED_ORIGINS` contains Frontend HTTPS URL
- [ ] Health check endpoint returns `200 OK`

---

## 7. Troubleshooting Guide

**Issue: Frontend returns "Failed to fetch" or Network Error**
- **Cause:** CORS block or incorrect `VITE_API_URL`.
- **Fix:** Ensure `ALLOWED_ORIGINS` in the backend explicitly lists the frontend URL without a trailing slash. Ensure the frontend was rebuilt with the correct `VITE_API_URL`.

**Issue: Swagger UI (`/docs`) displays a blank page or unstyled text**
- **Cause:** Strict Content-Security-Policy (HSTS/CSP) blocking CDN assets.
- **Fix:** Ensure the `ENVIRONMENT` variable is properly configuring middleware, and that the server allows `cdn.jsdelivr.net`.

**Issue: Database Connection Refused**
- **Cause:** The backend is starting before PostgreSQL is ready, or the credentials are wrong.
- **Fix:** Check the `DATABASE_URL` environment variable. On Docker, ensure `depends_on: postgres` is properly honored.
