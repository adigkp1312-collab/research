# Core Package

**Team:** Platform

Shared configuration, types, and utilities used by all packages.

## Contents

- `config.py` - Environment variable configuration
- `types.py` - Shared type definitions

## Usage

```python
from packages.core.src import GEMINI_API_KEY, validate_config
from packages.core.src.types import ChatRequest, ChatResponse

# Validate configuration on startup
if not validate_config():
    print("Warning: Missing required configuration")
```

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `GEMINI_API_KEY` | Yes | Google Gemini API key |
| `LANGCHAIN_TRACING_V2` | No | Enable LangSmith tracing |
| `LANGCHAIN_API_KEY` | No | LangSmith API key |
| `LANGCHAIN_PROJECT` | No | LangSmith project name |
| `DEBUG` | No | Enable debug mode |
| `CORS_ORIGINS` | No | Comma-separated CORS origins |

## Testing

```bash
cd packages/core
pytest tests/
```
