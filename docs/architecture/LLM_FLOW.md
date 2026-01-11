# LLM Flow Architecture

## Request Flow

```
┌─────────┐     ┌─────────┐     ┌──────────────┐     ┌────────────┐
│   UI    │────▶│   API   │────▶│ conversation │────▶│  Vertex   │
│         │     │         │     │ chains        │     │  AI       │
└─────────┘     └─────────┘     └──────────────┘     └────────────┘
                     │                  │
                     │                  ▼
                     │          ┌──────────────┐
                     │          │ conversation │
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

### 3. Conversation Chains (packages/langchain-chains)
- Direct Vertex AI integration
- System prompts
- Streaming support

### 4. Vertex AI Client (packages/langchain-client)
- Vertex AI GenerativeModel factory
- GCP project configuration
- Model initialization

### 5. Conversation Memory (packages/langchain-memory)
- Custom in-memory storage
- Session management
- Context windowing

### 6. Core (packages/core)
- Environment configuration
- Shared types
- Utilities

## Streaming Flow

1. Client sends POST to `/chat/stream`
2. API calls `stream_chat()` function
3. Function builds conversation prompt with history
4. Vertex AI `generate_content()` called with `stream=True`
5. Tokens yielded as they arrive from Vertex AI
6. API returns `StreamingResponse`
7. Client reads tokens in real-time
