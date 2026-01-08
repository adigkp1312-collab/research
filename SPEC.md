# Project Specification

**Project:** Adiyogi LangChain  
**Last Updated:** 2024-01-08  
**Status:** Active

---

## 1. Core Requirements

### 1.1 API Key Management

| Requirement | Status |
|-------------|--------|
| All API keys MUST be read from Lambda environment variables | MANDATORY |
| Keys are accessed via `os.environ.get('KEY_NAME')` | MANDATORY |
| No alternative key sources (localStorage, .env files, hardcoded) | MANDATORY |

**Implementation:**
```python
# CORRECT - Lambda environment variables
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '')

# WRONG - Do NOT use these patterns
# localStorage.getItem('key')  ❌
# load_dotenv()  ❌
# API_KEY = "hardcoded"  ❌
```

### 1.2 Data Persistence

| Requirement | Status |
|-------------|--------|
| NO localStorage or sessionStorage | MANDATORY |
| NO client-side data persistence | MANDATORY |
| All data via Supabase or backend APIs | MANDATORY |

### 1.3 Documentation

| Requirement | Status |
|-------------|--------|
| No `export KEY=value` commands in README | MANDATORY |
| Document Lambda environment variable setup only | MANDATORY |
| Reference AWS Console or AWS CLI for key setup | MANDATORY |

---

## 2. Prohibited Patterns

**DO NOT USE:**

| Pattern | Reason |
|---------|--------|
| `export GEMINI_API_KEY=...` in docs | Suggests non-Lambda approach |
| `localStorage.setItem()` | Client-side persistence banned |
| `sessionStorage` | Client-side persistence banned |
| `.env` file loading | Lambda doesn't use .env files |
| `load_dotenv()` | Lambda doesn't use .env files |
| Hardcoded API keys | Security risk |

---

## 3. Team Ownership

| Package | Team | Responsibility |
|---------|------|----------------|
| `packages/core` | Platform | Config, types, utilities |
| `packages/langchain-client` | AI/ML | Gemini model factory |
| `packages/langchain-memory` | AI/ML | Session memory |
| `packages/langchain-chains` | AI/ML | Conversation chains |
| `packages/api` | Backend | REST endpoints |
| `packages/ui` | Frontend | React components |
| `packages/testing` | QA | E2E + integration tests |

---

## 4. Environment Variables

### Required

| Variable | Description | Set Via |
|----------|-------------|---------|
| `GEMINI_API_KEY` | Google Gemini API key | Lambda Console |

### Optional

| Variable | Description | Default |
|----------|-------------|---------|
| `LANGCHAIN_TRACING_V2` | Enable LangSmith | `false` |
| `LANGCHAIN_API_KEY` | LangSmith API key | - |
| `LANGCHAIN_PROJECT` | LangSmith project | `adiyogi-poc` |

---

## 5. Compliance Checklist

Before any commit, verify:

- [ ] No prohibited patterns used
- [ ] API keys only from Lambda environment variables
- [ ] No localStorage/sessionStorage usage
- [ ] No hardcoded secrets
- [ ] Documentation aligned with Lambda-only approach
- [ ] ADR created for new architectural decisions

---

## 6. References

- [ADR-001: Lambda Environment Variables](docs/adr/001-lambda-environment-variables.md)
- [Security: API Keys](docs/security/API_KEYS.md)
