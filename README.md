# LangChain Chat POC

A minimal proof-of-concept demonstrating LangChain + Gemini 3 Flash with secure Lambda environment variable configuration.

## Purpose

This isolated repository validates the LangChain architecture before migrating the main Adiyogi Arts codebase. It demonstrates:

- **Direct Gemini 3 Flash** integration (no OpenRouter needed)
- **Secure key management** via Lambda environment variables
- **LangChain** conversation chains with memory
- **LangSmith** for observability (optional)
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
- Gemini API Key:
  - Get from: [Google AI Studio](https://aistudio.google.com/app/apikey)
  - Set via Lambda environment variables (see Setup section)

## Quick Start

### 1. Setup Environment Variables

**For Local Development:**
```bash
# Set environment variable (like Lambda does)
export GEMINI_API_KEY=your_key_here

# Or create .env file (gitignored)
echo "GEMINI_API_KEY=your_key_here" > .env
```

**For Lambda Deployment:**
Set `GEMINI_API_KEY` in Lambda environment variables (not in code).

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

### Gemini 3 Flash Only

This POC uses Gemini 3 Flash exclusively, configured via Lambda environment variables:

- **Model**: `gemini-2.0-flash-exp` (Gemini 3 Flash Experimental)
- **API**: Direct Google Gemini API (not OpenRouter)
- **Key Management**: Secure Lambda environment variables
- **No hardcoded keys**: Keys never in source code

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

- [ ] Gemini API key configured in Lambda environment
- [ ] Backend can read GEMINI_API_KEY from environment
- [ ] Conversation memory persists across turns
- [ ] Streaming responses work
- [ ] Error handling works gracefully
- [ ] LangSmith traces visible (if configured)

## Lambda Deployment

### Setting Environment Variables in Lambda

**Via AWS Console:**
1. Go to Lambda → Your Function → Configuration → Environment variables
2. Add: `GEMINI_API_KEY` = `your_key_here`
3. Save

**Via AWS CLI:**
```bash
aws lambda update-function-configuration \
  --function-name your-function-name \
  --environment Variables="{GEMINI_API_KEY=your_key_here}" \
  --region us-east-1
```

**Security Best Practice:**
For production, use AWS Secrets Manager instead of plain environment variables.

## Next Steps

After validating this POC:

1. Migrate conversation chain to main codebase
2. Add RAG for rules retrieval
3. Replace custom intelligence services
4. Add structured output parsing
