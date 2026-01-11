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

## Step 2: Configure Google Cloud Project

```bash
# Set up Application Default Credentials
gcloud auth application-default login

# Or set environment variables
export GOOGLE_CLOUD_PROJECT=your-project-id
export VERTEX_AI_LOCATION=us-central1

# Ensure Vertex AI API is enabled
gcloud services enable aiplatform.googleapis.com
```

---

## Step 3: Test Backend

```bash
# Set environment variables (if not already set)
export GOOGLE_CLOUD_PROJECT=your-project-id
export VERTEX_AI_LOCATION=us-central1

# Run directly with uvicorn
python apps/server/main.py
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

## Alternative: Docker Compose

For local development with Docker:

```bash
# Set environment variables
export GOOGLE_CLOUD_PROJECT=your-project-id
export VERTEX_AI_LOCATION=us-central1

# Start services
docker-compose up
```

---

## Troubleshooting

**Import errors?**
- Ensure PYTHONPATH includes project root
- Install dependencies: `pip install -r apps/server/requirements.txt`

**Module not found?**
- Check directory names use underscores (not hyphens)
- Run: `ls packages/` - should show `langchain_chains/` not `langchain-chains/`

**Vertex AI errors?**
- Verify GOOGLE_CLOUD_PROJECT is set correctly
- Ensure Vertex AI API is enabled in your GCP project
- Check Application Default Credentials are configured
- Verify service account has Vertex AI permissions

---

See [TESTING.md](TESTING.md) for detailed testing instructions.
