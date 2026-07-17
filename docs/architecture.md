# Architecture Overview

ScamShield AI consists of a React/Vite Frontend, a FastAPI Backend, and a PostgreSQL database.

## MVP Phase
This document covers the Phase 1 MVP architecture.

- **Frontend**: Vite, React, Tailwind, Shadcn.
- **Backend**: FastAPI
  - Authentication
  - Risk Engine (Scores 0-100)
  - Threat Intelligence Aggregation
  - AI Explanation via WatsonX (Mocked initially)
- **Database**: PostgreSQL
