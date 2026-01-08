# Testing Guide

## Prerequisites Check

Run this to check your environment:

```bash
# Check Python version (need 3.11+)
python3 --version

# Check SAM CLI
sam --version

# Check Node.js (for frontend)
node --version
```

## Installation

### 1. Install SAM CLI

**macOS:**
```bash
brew install aws-sam-cli
```

**Linux/Windows:**
See: https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/install-sam-cli.html

### 2. Install Python Dependencies

```bash
cd /Users/guptaaditya/Applications/langchain-poc
pip install -r apps/server/requirements.txt
```

### 3. Setup Environment Variables

```bash
# Copy example file
cp env.json.example env.json

# Edit env.json and add your GEMINI_API_KEY
# env.json is gitignored, so your keys won't be committed
```

**env.json format:**
```json
{
  "LangChainAPI": {
    "GEMINI_API_KEY": "your_actual_key_here",
    "LANGCHAIN_TRACING_V2": "false",
    "LANGCHAIN_API_KEY": "",
    "LANGCHAIN_PROJECT": "adiyogi-poc"
  }
}
```

## Testing Backend (SAM Local)

### Start API

```bash
cd /Users/guptaaditya/Applications/langchain-poc

# Build the application
sam build

# Start local API (runs on port 8000)
sam local start-api --env-vars env.json --port 8000
```

### Test Endpoints

**In another terminal:**

```bash
# Health check
curl http://localhost:8000/health

# Chat endpoint (non-streaming)
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello!", "session_id": "test-123"}'

# Chat endpoint (streaming)
curl -X POST http://localhost:8000/chat/stream \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello!", "session_id": "test-123"}'
```

## Testing Frontend

```bash
cd packages/ui

# Install dependencies
npm install

# Start dev server
npm run dev
```

Access at: http://localhost:5173

## Running Tests

### Backend Tests

```bash
# Set PYTHONPATH
export PYTHONPATH=/Users/guptaaditya/Applications/langchain-poc

# Run all tests
./scripts/test-all.sh

# Or test individual packages
cd packages/core && pytest tests/
cd packages/api && pytest tests/
```

### Frontend Tests

```bash
cd packages/ui
npm test
```

## Troubleshooting

### "SAM CLI not found"
Install SAM CLI:
```bash
brew install aws-sam-cli
```

### "Module not found: packages.*"
Ensure PYTHONPATH is set:
```bash
export PYTHONPATH=/Users/guptaaditya/Applications/langchain-poc
```

### "GEMINI_API_KEY not found"
Check env.json exists and has correct format:
```bash
cat env.json
# Should show your key under LangChainAPI
```

### Import Errors
The handler.py sets PYTHONPATH automatically for Lambda. For local testing with uvicorn directly:
```bash
PYTHONPATH=. uvicorn packages.api.src.app:app --reload
```

## Quick Start

```bash
# 1. Setup
cp env.json.example env.json
# Edit env.json with your key

# 2. Build
sam build

# 3. Start backend
sam local start-api --env-vars env.json --port 8000

# 4. In another terminal, start frontend
cd packages/ui && npm run dev

# 5. Test
curl http://localhost:8000/health
```
