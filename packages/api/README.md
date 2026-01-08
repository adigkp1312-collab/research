# API Package

**Team:** Backend

FastAPI REST API for the LangChain chat service.

## Contents

- `app.py` - Application factory
- `routes/` - Modular route definitions
  - `health.py` - Health check endpoints
  - `chat.py` - Chat endpoints
  - `models.py` - Model information endpoints
- `middleware/` - Custom middleware
  - `cors.py` - CORS configuration

## Endpoints

### Health
- `GET /` - Health check
- `GET /health` - Health check (alias)

### Chat
- `POST /chat` - Non-streaming chat
- `POST /chat/stream` - Streaming chat
- `DELETE /chat/session/{session_id}` - Clear session

### Models
- `GET /models` - Model information
- `GET /models/current` - Current model

## Usage

```python
from packages.api.src import create_app

app = create_app()

# Or use the default instance
from packages.api.src import app
```

## Running

```bash
cd packages/api
uvicorn src.app:app --reload --port 8000
```

## Testing

```bash
cd packages/api
pytest tests/
```
