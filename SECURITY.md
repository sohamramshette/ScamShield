# Security Policy

## Supported Versions

Currently, only the latest release is actively supported for security updates.

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability

If you discover a security vulnerability within ScamShield AI, please send an e-mail to the maintainers rather than creating a public issue. We will review the vulnerability and respond within 48 hours.

All security vulnerabilities will be promptly addressed. We adhere to responsible disclosure policies and ask that you give us a reasonable amount of time to push a patch before publicizing the vulnerability.

### Security Guarantees
- **No plaintext passwords**: ScamShield strictly uses `bcrypt` hashing with salt.
- **JWT Protection**: Access tokens are kept short-lived (30 minutes) and require a secure refresh token to re-issue.
- **CORS Restricted**: The API explicitly blocks wildcard (`*`) access in production.
- **Rate Limited**: Brute-forcing endpoints such as login/register are throttled by `slowapi`.
