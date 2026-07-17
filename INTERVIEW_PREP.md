# ScamShield AI - Interview Preparation Guide

Use this guide to prepare for technical interviews when discussing ScamShield AI.

## 🎤 The Elevator Pitch
"ScamShield AI is a full-stack cybersecurity SaaS platform I built to proactively detect phishing, malicious QR codes, and fraudulent UPI handles. I architected it using React, FastAPI, and PostgreSQL, and integrated IBM WatsonX to provide AI-driven threat explanations. The entire system is containerized with Docker and hardened with enterprise security best practices like strict CORS, CSP headers, and JWT auth."

---

## 🏗️ Architecture Explanation

**Question:** "Walk me through the architecture of ScamShield."
**Answer:**
"I designed ScamShield using a decoupled microservices approach. 
1. The **Frontend** is a Vite/React SPA. I chose Vite for its rapid HMR and build speeds.
2. The **Backend** is FastAPI (Python 3.11). I chose FastAPI for its asynchronous capabilities, which are crucial when reaching out to multiple external APIs concurrently (like IBM WatsonX and VirusTotal).
3. The **Database** is PostgreSQL, managed via SQLAlchemy ORM and Alembic for migrations, ensuring schema integrity.
4. **Deployment:** The stack is containerized using Docker Compose, allowing parity between my local development and production environments."

---

## 🛡️ Security Questions

**Question:** "How did you secure the application?"
**Answer:**
"Security was implemented at multiple layers:
- **Authentication:** Stateless JWT tokens with Argon2 hashing.
- **API Protection:** I implemented rate limiting using `slowapi` to prevent brute-force attacks.
- **Middleware:** Custom middleware injects security headers like `Content-Security-Policy`, `X-Frame-Options`, and `X-Content-Type-Options`.
- **Infrastructure:** Docker environment variables isolate secrets, ensuring no hardcoded keys in the repository."

---

## 🤖 AI Integration Questions

**Question:** "Why IBM WatsonX, and how did you integrate it?"
**Answer:**
"I chose IBM WatsonX for its enterprise-grade models (Granite) and strict data privacy guarantees, which are vital in cybersecurity. Instead of relying on heavy abstractions like LangChain, I wrote a direct, asynchronous integration to the WatsonX REST API using `httpx`. This reduced bloat, improved latency, and gave me fine-grained control over the prompt engineering required for threat analysis."

---

## 🚧 Challenges Faced

**Question:** "What was the hardest technical challenge you faced?"
**Answer:**
"One major challenge was ensuring the frontend could securely communicate with the backend across environments (local vs Docker vs Production). I had issues where Docker runtime variables weren't available during the Vite build phase. I resolved this by passing `VITE_API_URL` as a Docker `ARG` during the build stage, and carefully configuring CORS and HSTS headers on the backend so that Swagger UI and the Frontend could successfully interact without being blocked by browser security policies."
