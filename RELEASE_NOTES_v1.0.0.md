# ScamShield AI - Release Notes v1.0.0

**Release Date**: July 17, 2026

We are incredibly proud to announce the general availability of ScamShield AI v1.0.0! This release marks our transition from MVP to a production-ready, enterprise-grade platform. 

## Features
- **Intelligent Threat Analytics**: Core engine analyzing Websites, QR codes, and UPI IDs for signs of phishing and fraud.
- **AI Explanations**: Seamless integration with IBM WatsonX Granite API to provide plain-english reasoning behind every threat score.
- **Mock Mode**: Fully operational deterministic fallback mode for testing without requiring AI API tokens.
- **Comprehensive Dashboard**: Beautiful, responsive, dark-mode interface built on React 19.
- **Exportable PDF Reports**: Enterprise-ready downloadable PDFs containing detailed indicator-level security breakdowns.
- **Identity & Access**: Secure JWT authentication featuring token refreshing and rate-limited endpoints.

## Security & Reliability
- Enforced Content Security Policy (CSP), HTTP Strict-Transport-Security (HSTS), and X-Frame-Options.
- Replaced unmaintained cryptography packages (`passlib`) with native `bcrypt 5.0.0`.
- Integrated `Alembic` database migrations for robust schema evolution.
- Enforced strict connection pooling on the PostgreSQL 15 database.

## Known Limitations
- *Upstream Dependency (`ecdsa 0.19.2`)*: Security audit flagged an upstream PySEC vulnerability in `ecdsa`. A patch from the upstream provider is pending; this does not currently affect our JWT implementation directly.
- Email and SMS analyzers are slated for Phase 2.

## Future Roadmap (Phase 2)
- Email (`.eml`) Static Analyzer
- SMS and WhatsApp Message Analyzer
- Community Threat Reporting & Shared Intel
- Browser Extension Support

Thank you for contributing to a safer digital world with ScamShield AI!
