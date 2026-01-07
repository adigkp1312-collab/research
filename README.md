# LangChain Chat POC

A minimal proof-of-concept demonstrating LangChain + OpenRouter + Pinecone + LangSmith integration for the Adiyogi Arts platform.

## Purpose

This isolated repository validates the LangChain architecture before migrating the main Adiyogi Arts codebase. It demonstrates:

- **OpenRouter** integration for multi-model API access (Gemini, Claude, GPT-4)
- **LangChain** conversation chains with memory
- **LangSmith** for observability and debugging
- **Pinecone** vector store (prepared for RAG)
- **Streaming** responses for real-time chat

## Project Structure

```
langchain-poc/
├── frontend/                    # TypeScript/React POC
│   ├── src/
│   │   ├── langchain/          # LangChain configuration
│   │   │   ├── client.ts       # OpenRouter + LangChain setup
│   │   │   ├── chains/         # Chain implementations
│   │   │   └── memory/         # Memory management
│   │   └── App.tsx             # Simple chat UI
│   └── package.json
├── backend/                     # Python FastAPI POC
│   ├── src/
│   │   ├── langchain_client.py # OpenRouter + LangChain setup
│   │   ├── chains/             # Chain implementations
│   │   ├── memory/             # Memory management
│   │   └── main.py             # FastAPI app with streaming
│   ├── requirements.txt
│   └── tests/
├── .env.example                # Required API keys
└── docker-compose.yml          # Local development
```

## Prerequisites

- Node.js 18+
- Python 3.11+
- API Keys:
  - [OpenRouter](https://openrouter.ai/keys)
  - [LangSmith](https://smith.langchain.com)
  - [Pinecone](https://www.pinecone.io) (optional for POC)

## Quick Start

### 1. Clone and Setup

```bash
cd langchain-poc
cp .env.example .env
# Edit .env with your API keys
```

### 2. Start Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn src.main:app --reload --port 8000
```

### 3. Start Frontend

```bash
cd frontend
npm install
npm run dev
```

### 4. Access

- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- LangSmith Traces: https://smith.langchain.com

## Features

### Multi-Model Support via OpenRouter

Switch between models by changing the model ID:

```typescript
// Gemini Flash (fast, cheap)
createChatModel("google/gemini-flash-1.5");

// Claude Sonnet (creative)
createChatModel("anthropic/claude-3-sonnet-20240229");

// GPT-4 Turbo (structured output)
createChatModel("openai/gpt-4-turbo");
```

### Conversation Memory

The chat maintains context using LangChain's BufferWindowMemory:

```typescript
const memory = new BufferWindowMemory({
    k: 10,  // Keep last 10 messages
    returnMessages: true,
});
```

### Real-time Streaming

Responses stream token-by-token for better UX:

```python
@app.post("/chat/stream")
async def stream_chat(request: ChatRequest):
    # Returns StreamingResponse with real-time tokens
```

### LangSmith Observability

All LLM calls are automatically traced:

1. Set `LANGCHAIN_TRACING_V2=true` in `.env`
2. View traces at https://smith.langchain.com

## Validation Checklist

- [ ] OpenRouter connection works
- [ ] Model switching (Gemini ↔ Claude) works
- [ ] Conversation memory persists across turns
- [ ] Streaming responses work
- [ ] LangSmith traces are visible
- [ ] Error handling works gracefully

## Next Steps

After validating this POC:

1. Migrate conversation chain to main codebase
2. Add RAG with Pinecone for rules retrieval
3. Replace custom intelligence services
4. Add structured output parsing
