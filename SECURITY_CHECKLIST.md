# Security Checklist

Stop! Before committing code, run through this list:

## 🔍 Secrets Scan
- [ ] **Grep for Keys**: Run `grep -r "API_KEY" .` to ensure no hardcoded values.
- [ ] **Check Config**: Open `user_data/config.json`. Are keys empty or set to `""`?
- [ ] **Check Env**: Ensure `.env` is NOT in `git status`.

## 📦 Dependency Check
- [ ] Are we pulling trusted Docker images (`freqtradeorg/freqtrade:stable`)?
- [ ] Are there any new unknown massive files?

## 🛡️ Access Control
- [ ] Is the WebUI binding to `127.0.0.1` locally?
- [ ] Is password protection enabled for the WebUI?
