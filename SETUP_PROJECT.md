# Setup for Project: project-9881b278-0a45-47c1-9ed

## Quick Setup Steps

### 1. Set Environment Variables

```bash
export GOOGLE_CLOUD_PROJECT=project-9881b278-0a45-47c1-9ed
export VERTEX_AI_LOCATION=us-central1
```

Or use the setup script:
```bash
source setup_local.sh
```

### 2. Authenticate with GCP

```bash
# Authenticate with Application Default Credentials
gcloud auth application-default login

# Make sure you're using the correct account
gcloud auth list

# If needed, set the account
gcloud config set account your-email@example.com
```

### 3. Set the Project

```bash
gcloud config set project project-9881b278-0a45-47c1-9ed
```

### 4. Enable Vertex AI API

```bash
gcloud services enable aiplatform.googleapis.com --project=project-9881b278-0a45-47c1-9ed
```

**Note:** You need to have the "Service Usage Admin" or "Project Editor" role on the project to enable APIs.

### 5. Verify Access

```bash
# Check if you can access the project
gcloud projects describe project-9881b278-0a45-47c1-9ed

# Check if Vertex AI API is enabled
gcloud services list --enabled --project=project-9881b278-0a45-47c1-9ed | grep aiplatform
```

### 6. Run Tests

```bash
# Make sure environment variables are set
export GOOGLE_CLOUD_PROJECT=project-9881b278-0a45-47c1-9ed
export VERTEX_AI_LOCATION=us-central1

# Run the test script
python test_local_setup.py
```

## If You Get Permission Errors

If you see "Permission denied" errors:

1. **Check Project Access**
   - Ensure you have access to the project `project-9881b278-0a45-47c1-9ed`
   - Contact the project owner to grant you access

2. **Required Roles**
   - `roles/aiplatform.user` - To use Vertex AI
   - `roles/serviceusage.serviceUsageAdmin` - To enable APIs
   - Or `roles/editor` - For full project access

3. **Request Access**
   ```bash
   # Check your current permissions
   gcloud projects get-iam-policy project-9881b278-0a45-47c1-9ed
   ```

## Alternative: Use Service Account

If you have a service account key:

```bash
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account-key.json
export GOOGLE_CLOUD_PROJECT=project-9881b278-0a45-47c1-9ed
export VERTEX_AI_LOCATION=us-central1

python test_local_setup.py
```

## Quick Test Command

Once everything is set up:

```bash
./test_with_project.sh
```

This script will:
- Set environment variables
- Check authentication
- Enable Vertex AI API if needed
- Run the test script
