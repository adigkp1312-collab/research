#!/bin/bash
# Deploy Firestore Viewer to Cloud Run

set -e

# Configuration
PROJECT_ID="${GOOGLE_CLOUD_PROJECT:-project-9881b278-0a45-47c1-9ed}"
REGION="${REGION:-asia-south1}"
SERVICE_NAME="firestore-viewer"
IMAGE_NAME="gcr.io/${PROJECT_ID}/${SERVICE_NAME}"

echo "========================================"
echo "Deploying Firestore Viewer to Cloud Run"
echo "========================================"
echo "Project: ${PROJECT_ID}"
echo "Region: ${REGION}"
echo "Service: ${SERVICE_NAME}"
echo ""

# Build the Docker image
echo "Building Docker image..."
docker build -t ${IMAGE_NAME}:latest -f Dockerfile.viewer .

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
  --memory 1Gi \
  --cpu 1 \
  --allow-unauthenticated \
  --set-env-vars "GOOGLE_CLOUD_PROJECT=${PROJECT_ID}"

# Get the service URL
echo ""
echo "========================================"
echo "Deployment complete!"
echo "========================================"
SERVICE_URL=$(gcloud run services describe ${SERVICE_NAME} --region ${REGION} --format 'value(status.url)')
echo "Viewer URL: ${SERVICE_URL}"
echo ""
