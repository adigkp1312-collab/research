# Local Testing Guide

This guide helps you test the Vertex AI migration locally.

## Prerequisites

1. **Google Cloud Project**
   - Create or select a GCP project
   - Note your project ID

2. **Enable Vertex AI API**
   ```bash
   gcloud services enable aiplatform.googleapis.com
   ```

3. **Set up Authentication**
   ```bash
   # Option 1: Application Default Credentials (Recommended)
   gcloud auth application-default login
   
   # Option 2: Service Account (for production)
   # Create service account and download key
   export GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account-key.json
   ```

## Step 1: Install Dependencies

```bash
# Install all Python dependencies
pip install -r apps/server/requirements.txt

# Or install package by package
pip install -r packages/core/requirements.txt
pip install -r packages/langchain_client/requirements.txt
pip install -r packages/langchain_memory/requirements.txt
pip install -r packages/langchain_chains/requirements.txt
pip install -r packages/api/requirements.txt
```

## Step 2: Set Environment Variables

```bash
export GOOGLE_CLOUD_PROJECT=your-project-id
export VERTEX_AI_LOCATION=us-central1  # Optional, defaults to us-central1
```

## Step 3: Run Test Script

```bash
# Run the comprehensive test script
python test_local_setup.py
```

This will test:
- Environment configuration
- Package imports
- Vertex AI initialization
- Simple chat interaction
- Memory functionality
- Quick chat function

## Step 4: Test the API Server

```bash
# Start the server
python apps/server/main.py

# In another terminal, test the endpoints
curl http://localhost:8000/health

# Test chat endpoint
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello!", "session_id": "test-123"}'

# Test streaming endpoint
curl -X POST http://localhost:8000/chat/stream \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello!", "session_id": "test-123"}'
```

## Step 5: Test with Frontend

```bash
# Start backend (terminal 1)
export GOOGLE_CLOUD_PROJECT=your-project-id
python apps/server/main.py

# Start frontend (terminal 2)
cd packages/ui
npm install  # If not already done
npm run dev
```

Open http://localhost:5173 and test the chat interface.

## Troubleshooting

### "GOOGLE_CLOUD_PROJECT not found"
- Ensure environment variable is set: `echo $GOOGLE_CLOUD_PROJECT`
- Export it in your current shell session

### "Permission denied" or "Authentication failed"
- Run: `gcloud auth application-default login`
- Verify: `gcloud auth list`
- Check service account permissions if using service account

### "Vertex AI API not enabled"
```bash
gcloud services enable aiplatform.googleapis.com --project=your-project-id
```

### "Module not found" errors
- Ensure PYTHONPATH includes project root:
  ```bash
  export PYTHONPATH=/path/to/langchain-poc:$PYTHONPATH
  ```
- Or run from project root directory

### Import errors
- Verify all dependencies installed: `pip list | grep vertexai`
- Reinstall if needed: `pip install --upgrade google-cloud-aiplatform vertexai`

## Expected Output

When everything works, you should see:

```
✅ GOOGLE_CLOUD_PROJECT: your-project-id
✅ VERTEX_AI_LOCATION: us-central1
✅ Core package imports successful
✅ Vertex AI client imports successful
✅ Memory package imports successful
✅ Chains package imports successful
✅ Vertex AI initialized successfully
✅ Chat model created successfully
✅ Response received: Hello! How can I help you today?...
✅ Memory created
✅ Context saved
✅ Retrieved 2 messages
✅ Memory cleared
✅ Response: test successful...
```

## Next Steps

Once local testing passes:
1. Test with Docker: `docker-compose up`
2. Deploy to Cloud Run (see README.md)
3. Run integration tests
4. Update production environment variables
