# Project Specification

**Version:** 1.0  
**Last Updated:** 2024-01-08  
**Status:** Active

This document is the **single source of truth** for project requirements. AI agents and developers MUST read this before making changes.

---

## Core Requirements

### 1. API Key Management

| Requirement | Description |
|-------------|-------------|
| **MUST** | Use Lambda environment variables for all API keys |
| **MUST** | Read keys via `os.environ.get('KEY_NAME')` |
| **MUST NOT** | Use `export` commands in documentation |
| **MUST NOT** | Use `.env` files (even for local development) |
| **MUST NOT** | Hardcode any keys in source code |
| **MUST NOT** | Use localStorage/sessionStorage for sensitive data |

**Rationale:** Lambda injects environment variables automatically. Using `os.environ.get()` works identically in Lambda and local SAM testing.

### 2. Local Development

| Requirement | Description |
|-------------|-------------|
| **MUST** | Use AWS SAM for local Lambda testing |
| **MUST** | Use `env.json` for local environment variables (gitignored) |
| **MUST NOT** | Suggest `export` commands for setting keys |

### 3. Configuration Pattern

```python
# CORRECT - Lambda-compatible
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '')

# WRONG - Do not use
load_dotenv()  # No .env files
os.environ['KEY'] = 'hardcoded'  # No hardcoding
```

---

## Prohibited Patterns

### Code

```python
# ❌ PROHIBITED
localStorage.setItem('api_key', key)
sessionStorage.setItem('data', value)
API_KEY = "sk-hardcoded-key"
load_dotenv()
export GEMINI_API_KEY=xxx  # In documentation

# ✅ REQUIRED
os.environ.get('GEMINI_API_KEY', '')
```

### Documentation

```markdown
# ❌ PROHIBITED
export GEMINI_API_KEY=your_key
echo "KEY=value" >> ~/.zshrc
Create a .env file with...

# ✅ REQUIRED
Set GEMINI_API_KEY in Lambda environment variables
Use SAM local with env.json for testing
```

---

## Package Ownership

| Package | Team | Approval Required From |
|---------|------|----------------------|
| `packages/core` | Platform | Platform Lead |
| `packages/langchain-*` | AI/ML | AI/ML Lead |
| `packages/api` | Backend | Backend Lead |
| `packages/ui` | Frontend | Frontend Lead |
| `packages/testing` | QA | QA Lead |
| `apps/*` | DevOps | DevOps Lead |

---

## Environment Variables

| Variable | Required | Source | Description |
|----------|----------|--------|-------------|
| `GEMINI_API_KEY` | Yes | Lambda Console | Google Gemini API key |
| `LANGCHAIN_API_KEY` | No | Lambda Console | LangSmith API key |
| `LANGCHAIN_TRACING_V2` | No | Lambda Console | Enable tracing (`true`/`false`) |
| `LANGCHAIN_PROJECT` | No | Lambda Console | LangSmith project name |

---

## Compliance Checklist

Before any change, verify:

- [ ] Read this SPEC.md
- [ ] Checked relevant ADRs in `docs/adr/`
- [ ] No prohibited patterns introduced
- [ ] Lambda environment variables used (not export/dotenv)
- [ ] Tests added for new functionality
- [ ] Documentation updated

---

## References

- ADRs: `docs/adr/`
- Checklist: `CHECKLIST.md`
- AI Rules: `.cursor/rules.md`
