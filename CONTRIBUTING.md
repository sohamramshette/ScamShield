# Contributing to ScamShield AI

First off, thank you for considering contributing to ScamShield AI! It's people like you that make ScamShield AI such a great tool for the community.

## Development Workflow
We use a standard GitHub flow:
1. Fork the repo and create your branch from `main`.
2. If you've added code that should be tested, add tests.
3. If you've changed APIs, update the documentation.
4. Ensure the test suite passes.
5. Make sure your code lints.
6. Issue that pull request!

## Local Setup

### Backend
We use Python 3.11 with FastAPI.
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
pip install -r requirements.txt -r requirements-dev.txt
```
To run linters:
```bash
ruff check .
black .
isort .
pytest
```

### Frontend
We use React 19 + Vite.
```bash
cd frontend
npm install
npm run dev
```
To run linters:
```bash
npm run lint
npx prettier --write .
```

## Pull Request Guidelines
- PRs should be atomic and solve a single issue.
- Please use our PR template (`.github/PULL_REQUEST_TEMPLATE.md`).
- Ensure all CI tests pass.
