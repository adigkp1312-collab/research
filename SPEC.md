# Project Specification

**Version:** 1.0  
**Last Updated:** 2024-01-08  
**Status:** Active

This document is the **single source of truth** for project requirements. AI agents and developers MUST read this before making changes.

---

## Core Requirements

### 1. Configuration Management

| Requirement | Description |
|-------------|-------------|
| **MUST** | Use Cloud Run environment variables for configuration |
| **MUST** | Read config via `os.environ.get('KEY_NAME')` |
| **MUST** | Use Google Cloud Project ID for Vertex AI authentication |
| **MUST NOT** | Use `export` commands in documentation |
| **MUST NOT** | Use `.env` files (even for local development) |
| **MUST NOT** | Hardcode any configuration in source code |
| **MUST NOT** | Use localStorage/sessionStorage for sensitive data |

**Rationale:** Cloud Run injects environment variables automatically. Using `os.environ.get()` works identically in Cloud Run and local development. Vertex AI uses Application Default Credentials (ADC) or service accounts for authentication.

### 2. Local Development

| Requirement | Description |
|-------------|-------------|
| **MUST** | Use direct uvicorn or Cloud Run emulator for local testing |
| **MUST** | Use Application Default Credentials (ADC) for GCP authentication |
| **MUST** | Set `GOOGLE_CLOUD_PROJECT` environment variable |
| **MUST NOT** | Suggest `export` commands for setting keys in documentation |

### 3. Configuration Pattern

```python
# CORRECT - Cloud Run compatible
GOOGLE_CLOUD_PROJECT = os.environ.get('GOOGLE_CLOUD_PROJECT', '')
VERTEX_AI_LOCATION = os.environ.get('VERTEX_AI_LOCATION', 'us-central1')

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
| `GOOGLE_CLOUD_PROJECT` | Yes | Cloud Run / GCP | Google Cloud Project ID |
| `VERTEX_AI_LOCATION` | No | Cloud Run / GCP | Vertex AI region (default: `us-central1`) |
| `LANGCHAIN_API_KEY` | No | Cloud Run / GCP | LangSmith API key (optional) |
| `LANGCHAIN_TRACING_V2` | No | Cloud Run / GCP | Enable tracing (`true`/`false`) |
| `LANGCHAIN_PROJECT` | No | Cloud Run / GCP | LangSmith project name |

---

## Compliance Checklist

Before any change, verify:

- [ ] Read this SPEC.md
- [ ] Checked relevant ADRs in `docs/adr/`
- [ ] No prohibited patterns introduced
- [ ] Cloud Run environment variables used (not export/dotenv)
- [ ] GOOGLE_CLOUD_PROJECT configured
- [ ] Tests added for new functionality
- [ ] Documentation updated

---

## References

- ADRs: `docs/adr/`
- Checklist: `CHECKLIST.md`
- AI Rules: `.cursor/rules.md`
