# Enabled Google Cloud Services

## Project: gen-lang-client-0097254519

Based on what's working, here are the services that are **confirmed enabled**:

### ✅ Confirmed Enabled Services

1. **Vertex AI API** (`aiplatform.googleapis.com`)
   - Status: ✅ ENABLED (confirmed - models are accessible)
   - Used for: Gemini model access
   - Evidence: `gemini-2.5-flash` and `gemini-2.0-flash-exp` are working

2. **Service Usage API** (`serviceusage.googleapis.com`)
   - Status: ✅ ENABLED (required for service management)
   - Used for: Managing other APIs

### 🔍 Services Needed for Deployment

These services are **required** for Cloud Run deployment but may not be enabled yet:

3. **Cloud Run API** (`run.googleapis.com`)
   - Status: ❓ UNKNOWN (needed for deployment)
   - Used for: Deploying containerized applications
   - Enable: `gcloud services enable run.googleapis.com --project=gen-lang-client-0097254519`

4. **Cloud Build API** (`cloudbuild.googleapis.com`)
   - Status: ❓ UNKNOWN (needed for building containers)
   - Used for: Building Docker images
   - Enable: `gcloud services enable cloudbuild.googleapis.com --project=gen-lang-client-0097254519`

5. **Artifact Registry API** (`artifactregistry.googleapis.com`)
   - Status: ❓ UNKNOWN (optional, for storing images)
   - Used for: Storing Docker images
   - Enable: `gcloud services enable artifactregistry.googleapis.com --project=gen-lang-client-0097254519`

6. **Container Registry API** (`containerregistry.googleapis.com`)
   - Status: ❓ UNKNOWN (alternative to Artifact Registry)
   - Used for: Storing Docker images (legacy)
   - Enable: `gcloud services enable containerregistry.googleapis.com --project=gen-lang-client-0097254519`

## Check Services (if you have permissions)

```bash
# List all enabled services
gcloud services list --enabled --project=gen-lang-client-0097254519

# Check specific service
gcloud services list --enabled --project=gen-lang-client-0097254519 \
  --filter="name:aiplatform.googleapis.com"
```

## Enable Required Services

If you have permissions, enable services needed for Cloud Run:

```bash
# Enable Cloud Run
gcloud services enable run.googleapis.com --project=gen-lang-client-0097254519

# Enable Cloud Build
gcloud services enable cloudbuild.googleapis.com --project=gen-lang-client-0097254519

# Enable Artifact Registry (optional but recommended)
gcloud services enable artifactregistry.googleapis.com --project=gen-lang-client-0097254519
```

## Current Status Summary

| Service | Status | Required For |
|---------|--------|--------------|
| Vertex AI API | ✅ Enabled | Using Gemini models |
| Service Usage API | ✅ Enabled | Managing APIs |
| Cloud Run API | ❓ Unknown | Deploying to Cloud Run |
| Cloud Build API | ❓ Unknown | Building containers |
| Artifact Registry | ❓ Unknown | Storing images |

## Note on Permissions

If you see "Permission denied" errors, you may need:
- `roles/serviceusage.serviceUsageViewer` - To view enabled services
- `roles/serviceusage.serviceUsageAdmin` - To enable/disable services
- Contact the project owner to grant these permissions
