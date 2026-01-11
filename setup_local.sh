#!/bin/bash
# Quick setup script for local testing

export GOOGLE_CLOUD_PROJECT=artful-striker-483214-b0
export VERTEX_AI_LOCATION=us-central1

echo "✅ Environment variables set:"
echo "   GOOGLE_CLOUD_PROJECT=$GOOGLE_CLOUD_PROJECT"
echo "   VERTEX_AI_LOCATION=$VERTEX_AI_LOCATION"
echo ""
echo "Next steps:"
echo "1. Authenticate: gcloud auth application-default login"
echo "2. Enable API: gcloud services enable aiplatform.googleapis.com --project=$GOOGLE_CLOUD_PROJECT"
echo "3. Run tests: python test_local_setup.py"
echo "4. Start server: python apps/server/main.py"
