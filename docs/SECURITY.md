# Security Policy

## 🛡️ Core Principles
1.  **Least Privilege**: The bot runs with read-only API keys where possible (unless trading is enabled).
2.  **No Secrets in Code**: All sensitive credentials must be loaded via environment variables or a Git-ignored `config.json`.
3.  **Network Isolation**: The bot should run within a Docker network, exposing only necessary ports (e.g., for the WebUI).

## ⚠️ Critical Checks
Before deploying or pushing any changes, verify:
- [ ] No API keys in `config.json` (use environment variables or placeholders).
- [ ] Telegram tokens are not hardcoded.
- [ ] `.env` file is in `.gitignore`.
- [ ] SSH keys are not present in the build context.

## 🚨 Reporting Vulnerabilities
If you discover a security vulnerability within this project, please send an email to the maintainer rather than creating a public issue.
