# ScamShield AI - Project Structure (v1.0.0)

```
SafeGuard/
├── .github/                   # GitHub Actions workflows & templates
│   ├── ISSUE_TEMPLATE/        # Issue reporting templates
│   ├── workflows/             # CI and CodeQL workflows
│   ├── CODEOWNERS             # Repository maintainers
│   ├── dependabot.yml         # Automated dependency updates
│   └── PULL_REQUEST_TEMPLATE.md
├── backend/                   # Python FastAPI Backend
│   ├── alembic/               # Database migrations
│   ├── app/
│   │   ├── api/               # API endpoints (v1 routes)
│   │   ├── config/            # Environment settings
│   │   ├── core/              # Security and logging logic
│   │   ├── database/          # Session and DB pooling
│   │   ├── models/            # SQLAlchemy ORM models
│   │   ├── schemas/           # Pydantic validation models
│   │   └── services/          # Business logic (AI, Risk, Scanners)
│   ├── tests/                 # Pytest suite
│   ├── scripts/               # Utility scripts (e.g., generate_docs.py)
│   ├── Dockerfile             # Production container definition
│   └── pyproject.toml         # Python tool configurations (Ruff, Black)
├── frontend/                  # React + Vite SPA
│   ├── src/
│   │   ├── components/        # Reusable UI elements
│   │   ├── lib/               # Utility functions (e.g., Tailwind merge)
│   │   ├── pages/             # Route-level components (Scanners, Dashboard)
│   │   ├── App.tsx            # Main application router
│   │   └── index.css          # Global stylesheet
│   ├── Dockerfile             # Nginx static server definition
│   └── package.json           # Frontend dependencies and scripts
├── docs/                      # Generated documentation (OpenAPI, Security)
├── docker-compose.yml         # Multi-container orchestration
├── README.md                  # Project overview and setup guide
├── CHANGELOG.md               # Version history
├── CONTRIBUTING.md            # Guidelines for contributors
└── SECURITY.md                # Security and vulnerability reporting
```
