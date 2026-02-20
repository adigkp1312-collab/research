#!/bin/bash

# Configuration
SERVICE_NAME="meta-ads-ui"
REGION="europe-west1"
PROJECT_ID="project-9881b278-0a45-47c1-9ed" # Extracted from src/config.py
IMAGE_NAME="gcr.io/$PROJECT_ID/$SERVICE_NAME"

echo "🚀 Starting deployment for $SERVICE_NAME..."

# Build the container image using Cloud Build
echo "🏗️ Building container image..."
gcloud builds submit --tag "$IMAGE_NAME" --project "$PROJECT_ID"

# Deploy to Cloud Run
echo "🌍 Deploying to Cloud Run..."
gcloud run deploy "$SERVICE_NAME" \
    --image "$IMAGE_NAME" \
    --platform managed \
    --region "$REGION" \
    --allow-unauthenticated \
    --project "$PROJECT_ID" \
    --memory 2Gi \
    --cpu 2 \
    --set-env-vars "GCS_BUCKET=metaadsscrapper,GCS_PROJECT=$PROJECT_ID,SUPABASE_URL=https://zlhxxqkbtadbihyrmyvp.supabase.co,SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InpsaHh4cWtidGFkYmloeXJteXZwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjU1MDkwNTIsImV4cCI6MjA4MTA4NTA1Mn0.K_PLMzd6QYuzefcQsBtnREJiPuc1rDdzcJuwCD76zM4"

echo "✅ Deployment complete!"
gcloud run services describe "$SERVICE_NAME" --platform managed --region "$REGION" --project "$PROJECT_ID" --format 'value(status.url)'
