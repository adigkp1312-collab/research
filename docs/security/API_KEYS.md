# API Key Security

## Overview

This project uses secure environment variable management for API keys.

## Required Keys

| Key | Required | Source |
|-----|----------|--------|
| `GEMINI_API_KEY` | Yes | [Google AI Studio](https://aistudio.google.com/app/apikey) |
| `LANGCHAIN_API_KEY` | No | [LangSmith](https://smith.langchain.com) |

## Security Best Practices

### DO
- ✅ Set keys via environment variables
- ✅ Use Lambda environment variables in production
- ✅ Use AWS Secrets Manager for sensitive keys
- ✅ Rotate keys regularly

### DON'T
- ❌ Commit keys to git
- ❌ Hardcode keys in source code
- ❌ Log keys in application logs
- ❌ Share keys via chat/email

## Setting Keys (Lambda Environment Variables ONLY)

Per [ADR-001](../adr/001-lambda-environment-variables.md), all API keys must be set via Lambda environment variables.

### Production (Lambda Console)

1. Go to Lambda → Your Function → Configuration → Environment variables
2. Add: `GEMINI_API_KEY` = `your_key`
3. Save

### Production (AWS CLI)

```bash
aws lambda update-function-configuration \
  --function-name your-function \
  --environment Variables="{GEMINI_API_KEY=your_key}" \
  --region us-east-1
```

### Local Development (SAM)

```bash
# Create env.json (gitignored - never commit!)
echo '{"Function": {"GEMINI_API_KEY": "your_key"}}' > env.json

# Run with SAM
sam local start-api --env-vars env.json
```

## Prohibited Patterns

- ❌ `export GEMINI_API_KEY=...` - Not Lambda-compatible
- ❌ `.env` files with `load_dotenv()` - Lambda doesn't use .env
- ❌ Hardcoded keys - Security risk
- ❌ localStorage - Client-side, insecure

## Lambda Deployment

```bash
aws lambda update-function-configuration \
  --function-name your-function \
  --environment Variables="{GEMINI_API_KEY=your_key}" \
  --region us-east-1
```

## How Keys Are Read

```python
# packages/core/src/config.py
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '')
```

Keys are read at module load time from environment variables.
Never stored in code or config files.
