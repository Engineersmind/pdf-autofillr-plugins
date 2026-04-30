# Security Policy

## Supported versions

| Version | Supported |
|---------|-----------|
| 0.1.x   | ✅        |

## Reporting a vulnerability

**GitHub Security Advisories (preferred):**
https://github.com/Engineersmind/pdf-autofillr-plugins/security/advisories/new

**Email:** Security@pdffillr.ai
Subject: `[SECURITY] <brief description>`

We respond within 48 hours and follow coordinated disclosure.

## Security best practices

```bash
cp .env.example .env && echo ".env" >> .gitignore
pip-audit
bandit -r packages/plugins/src/
```
