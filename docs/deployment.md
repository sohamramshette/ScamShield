# Deployment

## Local Development
Run `docker-compose up -d --build` from the root directory.

## Production
In production, you should use managed PostgreSQL, and set proper SSL/TLS for FastAPI (or sit behind a reverse proxy like NGINX).
