# ADR-001: Lambda Environment Variables for API Keys

## Status
**Accepted**

## Date
2024-01-08

## Context
The application requires API keys (GEMINI_API_KEY, LANGCHAIN_API_KEY) to function. We need a secure, consistent method for providing these keys that:
1. Works in production (AWS Lambda)
2. Never exposes keys in source code
3. Provides a single source of truth

Alternative approaches considered:
- `.env` files with `load_dotenv()` - Lambda doesn't use .env files
- `export` commands in documentation - Suggests non-Lambda approach
- localStorage - Client-side, insecure
- Hardcoded keys - Security risk

## Decision
**All API keys MUST be provided via Lambda environment variables.**

### Implementation
```python
# packages/core/src/config.py
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '')
```

### Setting Keys
**Production (Lambda Console):**
1. Lambda → Configuration → Environment variables
2. Add: `GEMINI_API_KEY` = `your_key`

**Production (AWS CLI):**
```bash
aws lambda update-function-configuration \
  --function-name your-function \
  --environment Variables="{GEMINI_API_KEY=your_key}"
```

**Local Development (SAM):**
```bash
sam local start-api --env-vars env.json
```

### Prohibited Patterns
- ❌ `export GEMINI_API_KEY=...` in documentation
- ❌ `.env` file loading
- ❌ `load_dotenv()`
- ❌ Hardcoded keys
- ❌ localStorage/sessionStorage

## Consequences

### Positive
- Single method for all environments
- Keys never in source code
- Aligns with AWS best practices
- Easy rotation via Lambda Console

### Negative
- Local development requires SAM or env.json
- Slightly more setup for new developers

### Mitigations
- Provide SAM template for local development
- Document Lambda Console setup clearly
- Add env.json.example (gitignored values)

## Compliance
- [x] SPEC.md updated
- [x] CHECKLIST.md updated
- [x] README aligned with this decision
