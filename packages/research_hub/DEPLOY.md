# Research Hub - Cloud Deployment Setup

## One-Time Setup (GCP Console)

### Step 1: Create New GCP Project

1. Go to [GCP Console](https://console.cloud.google.com)
2. Click project dropdown → "New Project"
3. Name: `research-hub-prod` (or your choice)
4. Click "Create"
5. Select the new project

### Step 2: Enable Billing

1. Go to Billing → Link a billing account to the project

### Step 3: Enable Required APIs

Run in Cloud Shell or terminal:
```bash
gcloud config set project YOUR_PROJECT_ID

gcloud services enable \
  cloudbuild.googleapis.com \
  run.googleapis.com \
  artifactregistry.googleapis.com \
  firestore.googleapis.com
```

### Step 4: Create Artifact Registry Repository

```bash
gcloud artifacts repositories create research-hub \
  --repository-format=docker \
  --location=asia-south1 \
  --description="Research Hub Docker images"
```

### Step 5: Create Firestore Database

1. Go to [Firestore](https://console.cloud.google.com/firestore)
2. Click "Create Database"
3. Select "Native mode"
4. Location: `asia-south1`
5. Click "Create"

### Step 6: Grant Cloud Build Permissions

```bash
# Get project number
PROJECT_NUMBER=$(gcloud projects describe $(gcloud config get-value project) --format='value(projectNumber)')

# Grant Cloud Run Admin to Cloud Build
gcloud projects add-iam-policy-binding $(gcloud config get-value project) \
  --member="serviceAccount:${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com" \
  --role="roles/run.admin"

# Grant Service Account User
gcloud projects add-iam-policy-binding $(gcloud config get-value project) \
  --member="serviceAccount:${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com" \
  --role="roles/iam.serviceAccountUser"
```

### Step 7: Connect GitHub to Cloud Build

1. Go to [Cloud Build Triggers](https://console.cloud.google.com/cloud-build/triggers)
2. Click "Connect Repository"
3. Select "GitHub (Cloud Build GitHub App)"
4. Authenticate with GitHub
5. Select your repository: `langchain-poc` (or the repo containing this code)
6. Click "Connect"

### Step 8: Create Build Trigger

1. Click "Create Trigger"
2. Configure:
   - **Name**: `deploy-research-hub`
   - **Event**: Push to a branch
   - **Branch**: `^main$` (or your branch)
   - **Configuration**: Cloud Build configuration file
   - **Location**: `packages/research_hub/cloudbuild.yaml`
3. Click "Create"

---

## How It Works

After setup, every push to `main` branch will:

1. Trigger Cloud Build
2. Build Docker image with Playwright/Chromium
3. Push to Artifact Registry
4. Deploy to Cloud Run
5. Your API is live!

---

## API Endpoints

Once deployed, you'll get a URL like:
`https://research-hub-api-xxxxx-el.a.run.app`

**Endpoints:**
- `GET /health` - Health check
- `POST /api/search` - Search Meta Ad Library
- `POST /api/download` - Download a video
- `GET /api/videos` - List downloaded videos

**Example:**
```bash
curl -X POST https://YOUR_URL/api/search \
  -H "Content-Type: application/json" \
  -d '{"query": "Nike", "country": "IN", "media_type": "video"}'
```

---

## Costs (Approximate)

- **Cloud Run**: ~$0 when idle (scales to zero)
- **Artifact Registry**: ~$0.10/GB/month
- **Firestore**: Free tier covers light usage
- **Cloud Build**: 120 free build-minutes/day

Total: Nearly free for light usage.

---

## Troubleshooting

**Build fails?**
- Check Cloud Build logs in GCP Console
- Ensure all APIs are enabled
- Verify permissions are set

**Deployment fails?**
- Check Cloud Run logs
- Verify Firestore is created
- Check memory/CPU limits

**Scraping returns 0 results?**
- Meta may be blocking - try different queries
- Check browser automation logs
