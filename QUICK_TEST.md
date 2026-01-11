# Quick Local Test Guide

## Fast Setup (3 Steps)

### 1. Set Environment Variables
```bash
export GOOGLE_CLOUD_PROJECT=your-project-id
export VERTEX_AI_LOCATION=us-central1
```

### 2. Authenticate with GCP
```bash
gcloud auth application-default login
```

### 3. Run Test Script
```bash
python test_local_setup.py
```

## If Tests Pass

Start the server:
```bash
python apps/server/main.py
```

Then test in another terminal:
```bash
# Health check
curl http://localhost:8000/health

# Chat test
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello!", "session_id": "test-123"}'
```

## Common Issues

**"GOOGLE_CLOUD_PROJECT not found"**
- Make sure you exported it: `export GOOGLE_CLOUD_PROJECT=your-id`
- Check: `echo $GOOGLE_CLOUD_PROJECT`

**"Permission denied"**
- Run: `gcloud auth application-default login`
- Enable API: `gcloud services enable aiplatform.googleapis.com`

**"Module not found"**
- Install deps: `pip install -r apps/server/requirements.txt`
- Check PYTHONPATH: `export PYTHONPATH=$(pwd)`

See [TEST_LOCAL.md](TEST_LOCAL.md) for detailed troubleshooting.
