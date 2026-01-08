# LangChain Chains Package

**Team:** AI/ML

Conversation chain implementations for different use cases.

## Contents

- `director.py` - Director conversation chain for video production
- `prompts.py` - System prompt definitions

## Chains

### Director Chain
Video production assistant with memory:

```python
from packages.langchain_chains.src import create_director_chain, stream_chat

# Create chain
chain = create_director_chain("session-123")
result = await chain.ainvoke({"input": "Help me brainstorm a video"})

# Or use streaming
async for token in stream_chat("session-123", "Hello"):
    print(token, end="")
```

## Prompts

Available system prompts:
- `director` - Video production assistant
- `assistant` - General assistant
- `brainstorm` - Creative brainstorming

```python
from packages.langchain_chains.src import PROMPTS
from packages.langchain_chains.src.prompts import get_prompt

prompt = get_prompt("director")
```

## Testing

```bash
cd packages/langchain-chains
pytest tests/
```

Note: Integration tests require `GEMINI_API_KEY` to be set.
