# Security Policy

## Supported Versions

| Package | Version | Supported |
|---------|---------|-----------|
| pdf-autofillr-plugins | 0.2.0 | ✅ |
| Any previous version | < latest | ❌ |

---

## Reporting a Vulnerability

**Do NOT open a public GitHub issue for security vulnerabilities.**
Public issues expose users to 0-days before a fix is available.

### Preferred — GitHub Security Advisories (private)
https://github.com/Engineersmind/pdf-autofillr-plugins/security/advisories/new

GitHub keeps this completely private until a fix is released.

### Alternative — Email
**security@engineersmind.com**
Subject: `[SECURITY] <brief description>`

---

## Response Timeline

| Severity | First Response | Patch Target |
|----------|---------------|--------------|
| Critical | 24 hours | 7 days |
| High | 48 hours | 14 days |
| Medium / Low | 5 business days | Next release |

We follow coordinated disclosure — we'll work with you on timing before anything is made public.

---

## Scope

Areas most relevant for security research in this codebase:

- **Plugin discovery** — `PluginRegistry` loads arbitrary Python files from user-supplied paths; path traversal and code injection are in scope
- **Module import chain** — lazy imports could be abused if a malicious package shadows a module name
- **File path handling** — `--path` arguments in discovery accept user-supplied directories
- **JSON parsing** — `safe_json_loads` handles untrusted input
- **`@requires` decorator** — declares pip dependencies that are installed at plugin load time
- **Docker image** — any vulnerabilities in the base image or installed packages

---

## Security Best Practices (for contributors)

```bash
# Never commit .env — always use .env.example
cp plugins/.env.example .env
echo ".env" >> .gitignore

# Scan dependencies for known CVEs
pip-audit

# Static analysis
bandit -r plugins/src/
```

- Never log API keys or raw user input in plugin code
- Always validate user-supplied file paths before passing to `discover_plugins()`
- `.env` files are in `.gitignore` and must never be committed
- Plugin authors should document any external network calls or file system access in their plugin's docstring

---

## After Reporting

Once a vulnerability is confirmed:

1. We open a private GitHub Security Advisory
2. We develop and test a fix on a private branch
3. We coordinate a disclosure date with the reporter
4. We release the patch and publish the advisory simultaneously
5. Reporter is credited in the advisory (unless they prefer anonymity)
