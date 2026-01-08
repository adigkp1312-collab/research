# ADR-001: Lambda Environment Variables for API Keys

**Date:** 2024-01-08  
**Status:** Accepted

## Context

We need a secure, consistent way to manage API keys (GEMINI_API_KEY, LANGCHAIN_API_KEY) across:
- Local development
- Lambda deployment
- CI/CD pipelines

Options considered:
1. `.env` files with `python-dotenv`
2. `export` commands in shell
3. Lambda environment variables with SAM local
4. AWS Secrets Manager

## Decision

**Use Lambda environment variables exclusively.**

- Production: Set via Lambda Console or AWS CLI
- Local development: Use AWS SAM with `env.json` (gitignored)
- Code: Read via `os.environ.get('KEY_NAME', '')`

**Prohibited:**
- `.env` files
- `export` commands in documentation
- `python-dotenv` library
- Hardcoded keys

## Consequences

### Positive

- Single code path for all environments
- No risk of committing `.env` files
- Lambda-native approach
- SAM local provides identical behavior to production
- Clear security boundary

### Negative

- Requires SAM CLI installation for local dev
- Slightly more setup than simple `export`
- Team must learn SAM basics

### Neutral

- `os.environ.get()` works identically everywhere
- No code changes needed between local and production

## Compliance

- [x] SPEC.md updated with requirement
- [x] Prohibited patterns documented
- [ ] SAM template created
- [ ] env.json.example created
- [ ] README updated to remove `export` suggestions
- [ ] Team notified

## Implementation

### Code Pattern

```python
# packages/core/src/config.py
import os

GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '')
```

### Local Development

```bash
# env.json (gitignored)
{
  "Parameters": {
    "GEMINI_API_KEY": "your_key_here"
  }
}

# Run
sam local start-api --env-vars env.json
```

### Production

```bash
aws lambda update-function-configuration \
  --function-name adiyogi-langchain \
  --environment Variables="{GEMINI_API_KEY=your_key}"
```
