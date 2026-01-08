# LangChain Memory Package

**Team:** AI/ML

Session memory management for conversation context.

## Contents

- `buffer.py` - BufferWindowMemory wrapper for session state

## Usage

```python
from packages.langchain_memory.src import (
    get_session_memory,
    clear_session_memory,
    get_active_session_count,
)

# Get or create memory for a session
memory = get_session_memory("user-123", window_size=10)

# Use with LangChain chains
chain = ConversationChain(llm=model, memory=memory)

# Clear when done
clear_session_memory("user-123")

# Check active sessions
count = get_active_session_count()
```

## Memory Type

Uses `ConversationBufferWindowMemory`:
- Keeps last K messages (default: 10)
- Ideal for chat with limited context windows
- Memory persists in-memory (use Redis for production)

## Testing

```bash
cd packages/langchain-memory
pytest tests/
```
