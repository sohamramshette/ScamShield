# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-07-17

### Added
- **Authentication**: JWT-based authentication with Access and Refresh tokens.
- **Risk Engine**: Multi-indicator risk analysis for links, IPs, and structural patterns.
- **Website Scanner**: Deep URL scanning and validation.
- **QR Code Scanner**: QR code payload decoding and malicious link detection.
- **UPI Analyzer**: Validation of UPI formats and known fraudulent IDs.
- **Threat Intelligence**: Mock engine integration for VirusTotal-like reputation lookups.
- **AI Explanation**: Mock IBM WatsonX Granite integration explaining threats.
- **Reporting**: Automated PDF Generation containing risk analysis.
- **Security Hardening**: Integrated `slowapi` rate limiting, HSTS, CSP, and CORS restrictions.
- **Continuous Integration**: GitHub Actions configuration for automated linting and tests (PyTest, Ruff, Black, ESLint, Oxlint).

### Changed
- Refactored `passlib` out in favor of native `bcrypt` 5.0.0 for security compliance.
- Migrated legacy SQLAlchemy schema creation to formal `Alembic` database migrations.
- Frontend architecture modularized utilizing `React.lazy()` for performance-optimized chunking.

### Removed
- Unused frontend components and styling artifacts.
- Deprecated library integrations.
