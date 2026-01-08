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

## Local Development

```bash
# Set environment variable
export GEMINI_API_KEY=your_key_here

# Or use .env file (gitignored)
echo "GEMINI_API_KEY=your_key" > .env
```

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
