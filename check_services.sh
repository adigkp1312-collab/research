#!/bin/bash
# Check enabled GCP services

PROJECT_ID=project-9881b278-0a45-47c1-9ed

echo "=" * 70
echo "Enabled Google Cloud Services for Project: $PROJECT_ID"
echo "=" * 70
echo ""

echo "🔍 Checking all enabled services..."
gcloud services list --enabled --project=$PROJECT_ID --format="table(serviceName,title)" 2>&1 | head -50

echo ""
echo "=" * 70
echo "Key Services for This Project"
echo "=" * 70

# Check specific services we need
echo ""
echo "Checking Vertex AI..."
if gcloud services list --enabled --project=$PROJECT_ID --filter="name:aiplatform.googleapis.com" 2>&1 | grep -q "aiplatform"; then
    echo "✅ Vertex AI API (aiplatform.googleapis.com) - ENABLED"
else
    echo "❌ Vertex AI API (aiplatform.googleapis.com) - NOT ENABLED"
fi

echo ""
echo "Checking Cloud Run..."
if gcloud services list --enabled --project=$PROJECT_ID --filter="name:run.googleapis.com" 2>&1 | grep -q "run"; then
    echo "✅ Cloud Run API (run.googleapis.com) - ENABLED"
else
    echo "❌ Cloud Run API (run.googleapis.com) - NOT ENABLED"
fi

echo ""
echo "Checking Cloud Build..."
if gcloud services list --enabled --project=$PROJECT_ID --filter="name:cloudbuild.googleapis.com" 2>&1 | grep -q "cloudbuild"; then
    echo "✅ Cloud Build API (cloudbuild.googleapis.com) - ENABLED"
else
    echo "❌ Cloud Build API (cloudbuild.googleapis.com) - NOT ENABLED"
fi

echo ""
echo "Checking Artifact Registry..."
if gcloud services list --enabled --project=$PROJECT_ID --filter="name:artifactregistry.googleapis.com" 2>&1 | grep -q "artifactregistry"; then
    echo "✅ Artifact Registry API (artifactregistry.googleapis.com) - ENABLED"
else
    echo "❌ Artifact Registry API (artifactregistry.googleapis.com) - NOT ENABLED"
fi

echo ""
echo "=" * 70
echo "To enable missing services, run:"
echo "  gcloud services enable <service-name> --project=$PROJECT_ID"
echo "=" * 70
