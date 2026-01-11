#!/bin/bash
# Deploy Research Hub API to Cloud Run

set -e

# Configuration
PROJECT_ID="${GOOGLE_CLOUD_PROJECT:-artful-striker-483214-b0}"
REGION="${REGION:-asia-south1}"
SERVICE_NAME="research-hub-api"
IMAGE_NAME="gcr.io/${PROJECT_ID}/${SERVICE_NAME}"

echo "========================================"
echo "Deploying Research Hub API to Cloud Run"
echo "========================================"
echo "Project: ${PROJECT_ID}"
echo "Region: ${REGION}"
echo "Service: ${SERVICE_NAME}"
echo ""

# Set the project
gcloud config set project ${PROJECT_ID}

# Enable required APIs
echo "Enabling required APIs..."
gcloud services enable run.googleapis.com containerregistry.googleapis.com cloudbuild.googleapis.com

# Build the Docker image
echo ""
echo "Building Docker image..."
docker build -t ${IMAGE_NAME}:latest .

# Push to Container Registry
echo ""
echo "Pushing to Container Registry..."
docker push ${IMAGE_NAME}:latest

# Deploy to Cloud Run
echo ""
echo "Deploying to Cloud Run..."
gcloud run deploy ${SERVICE_NAME} \
  --image ${IMAGE_NAME}:latest \
  --region ${REGION} \
  --platform managed \
  --memory 2Gi \
  --cpu 2 \
  --timeout 300 \
  --concurrency 10 \
  --min-instances 0 \
  --max-instances 3 \
  --allow-unauthenticated \
  --set-env-vars "HEADLESS=1,GOOGLE_CLOUD_PROJECT=${PROJECT_ID}"

# Get the service URL
echo ""
echo "========================================"
echo "Deployment complete!"
echo "========================================"
SERVICE_URL=$(gcloud run services describe ${SERVICE_NAME} --region ${REGION} --format 'value(status.url)')
echo "API URL: ${SERVICE_URL}"
echo ""
echo "Test with:"
echo "  curl ${SERVICE_URL}/health"
echo ""
echo "Search for ads:"
echo "  curl -X POST ${SERVICE_URL}/api/search -H 'Content-Type: application/json' -d '{\"query\": \"Nike\", \"country\": \"IN\"}'"
