#!/bin/bash
# Quick local test script

export GOOGLE_CLOUD_PROJECT=gen-lang-client-0097254519
export VERTEX_AI_LOCATION=us-central1

echo "🚀 Starting Local Test with Gemini 2.5 Flash"
echo "Project: $GOOGLE_CLOUD_PROJECT"
echo "Location: $VERTEX_AI_LOCATION"
echo ""

# Run comprehensive tests
python3 test_local_setup.py

echo ""
echo "=" * 60
echo "To start the server:"
echo "  python3 apps/server/main.py"
echo ""
echo "Then test with:"
echo "  curl http://localhost:8000/health"
echo "  curl -X POST http://localhost:8000/chat \\"
echo "    -H 'Content-Type: application/json' \\"
echo "    -d '{\"message\": \"Hello!\", \"session_id\": \"test-123\"}'"
echo "=" * 60
