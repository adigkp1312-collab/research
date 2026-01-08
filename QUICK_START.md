# Quick Start - Testing Guide

## ✅ Setup Complete!

All code is ready. Follow these steps to test:

---

## Step 1: Install Dependencies

```bash
cd /Users/guptaaditya/Applications/langchain-poc

# Install Python dependencies
pip install -r apps/server/requirements.txt

# Install SAM CLI (if not installed)
brew install aws-sam-cli

# Install frontend dependencies
cd packages/ui && npm install && cd ../..
```

---

## Step 2: Configure API Key

```bash
# Copy example
cp env.json.example env.json

# Edit env.json and add your GEMINI_API_KEY
# File format:
{
  "LangChainAPI": {
    "GEMINI_API_KEY": "your_actual_key_here"
  }
}
```

---

## Step 3: Test Backend

```bash
# Build SAM application
sam build

# Start local API (Lambda simulation)
sam local start-api --env-vars env.json --port 8000
```

**Test endpoints:**
```bash
# Health check
curl http://localhost:8000/health

# Chat (streaming)
curl -X POST http://localhost:8000/chat/stream \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello!", "session_id": "test-123"}'
```

---

## Step 4: Test Frontend

```bash
# In another terminal
cd packages/ui
npm run dev
```

Open: http://localhost:5173

---

## Alternative: Direct uvicorn (without SAM)

If SAM isn't installed yet:

```bash
# Set PYTHONPATH
export PYTHONPATH=/Users/guptaaditya/Applications/langchain-poc

# Set API key
export GEMINI_API_KEY=your_key_here

# Run directly
python3 apps/server/main.py
```

---

## Troubleshooting

**Import errors?**
- Ensure PYTHONPATH includes project root
- Install dependencies: `pip install -r apps/server/requirements.txt`

**Module not found?**
- Check directory names use underscores (not hyphens)
- Run: `ls packages/` - should show `langchain_chains/` not `langchain-chains/`

**API key errors?**
- Verify env.json format matches example
- Check env.json has `LangChainAPI` key (not `Parameters`)

---

See [TESTING.md](TESTING.md) for detailed testing instructions.
