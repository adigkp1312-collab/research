#!/bin/bash
# Test script with your project ID

export GOOGLE_CLOUD_PROJECT=artful-striker-483214-b0
export VERTEX_AI_LOCATION=us-central1

echo "🚀 Testing with project: $GOOGLE_CLOUD_PROJECT"
echo ""

# Check if authenticated
if ! gcloud auth application-default print-access-token &>/dev/null; then
    echo "⚠️  Not authenticated. Running: gcloud auth application-default login"
    gcloud auth application-default login
fi

# Check if API is enabled
echo "Checking Vertex AI API..."
if gcloud services list --enabled --project=$GOOGLE_CLOUD_PROJECT --filter="name:aiplatform.googleapis.com" 2>&1 | grep -q "aiplatform"; then
    echo "✅ Vertex AI API is enabled"
else
    echo "⚠️  Vertex AI API not enabled. Enabling now..."
    gcloud services enable aiplatform.googleapis.com --project=$GOOGLE_CLOUD_PROJECT
fi

echo ""
echo "Running test script..."
python test_local_setup.py
