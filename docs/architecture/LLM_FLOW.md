# LLM Flow Architecture

## Request Flow

```
┌─────────┐     ┌─────────┐     ┌──────────────┐     ┌────────────┐
│   UI    │────▶│   API   │────▶│ langchain-   │────▶│  Gemini    │
│         │     │         │     │ chains       │     │  API       │
└─────────┘     └─────────┘     └──────────────┘     └────────────┘
                     │                  │
                     │                  ▼
                     │          ┌──────────────┐
                     │          │ langchain-   │
                     │          │ memory       │
                     │          └──────────────┘
                     │                  │
                     ▼                  ▼
              ┌─────────────────────────────────┐
              │           core                   │
              │  (config, types, utils)          │
              └─────────────────────────────────┘
```

## Components

### 1. UI (packages/ui)
- React frontend
- Handles user input
- Displays streaming responses
- Manages session state

### 2. API (packages/api)
- FastAPI REST endpoints
- Request validation
- Streaming responses
- CORS handling

### 3. LangChain Chains (packages/langchain-chains)
- ConversationChain with memory
- System prompts
- Streaming callbacks

### 4. LangChain Client (packages/langchain-client)
- Gemini model factory
- API key management
- LangSmith tracing

### 5. LangChain Memory (packages/langchain-memory)
- BufferWindowMemory
- Session management
- Context persistence

### 6. Core (packages/core)
- Environment configuration
- Shared types
- Utilities

## Streaming Flow

1. Client sends POST to `/chat/stream`
2. API creates `AsyncIteratorCallbackHandler`
3. Chain invokes Gemini with callback
4. Callback yields tokens as they arrive
5. API returns `StreamingResponse`
6. Client reads tokens in real-time
