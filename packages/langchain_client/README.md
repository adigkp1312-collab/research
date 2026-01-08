# LangChain Client Package

**Team:** AI/ML

Creates and configures LangChain chat models for Google Gemini.

## Contents

- `client.py` - Gemini model factory

## Usage

```python
from packages.langchain_client.src import create_chat_model, GEMINI_MODEL

# Create a chat model
model = create_chat_model(temperature=0.7, streaming=True)

# Use the model
response = await model.ainvoke("Hello, how are you?")
print(response.content)
```

## Configuration

Requires `GEMINI_API_KEY` environment variable from `packages/core`.

## Model

- **Model ID:** `gemini-2.0-flash-exp`
- **Name:** Gemini 3 Flash (Experimental)
- **Provider:** Google

## Testing

```bash
cd packages/langchain-client
pytest tests/
```

Note: Integration tests require `GEMINI_API_KEY` to be set.
