# Project Configuration

## Active Project: project-9881b278-0a45-47c1-9ed

This project is now configured as the default for all operations.

## Quick Setup

```bash
# Set environment variables
export GOOGLE_CLOUD_PROJECT=project-9881b278-0a45-47c1-9ed
export VERTEX_AI_LOCATION=us-central1

# Or use the setup script
source setup_project.sh
```

## Available Models

Based on testing, this project has access to:
- `gemini-2.0-flash-exp` (Experimental)
- `gemini-2.0-flash` (Stable)

**Note:** Gemini 2.5 models are not available in this project.

## Current Configuration

- **Model:** `gemini-2.5-flash` (configured, but may not be available)
- **Location:** `us-central1`
- **Project ID:** `project-9881b278-0a45-47c1-9ed`

## Update Model if Needed

If `gemini-2.5-flash` is not available, update to use `gemini-2.0-flash`:

```python
# In packages/langchain_client/src/client.py
GEMINI_MODEL = "gemini-2.0-flash"  # Use available model
```

## Test the Setup

```bash
export GOOGLE_CLOUD_PROJECT=project-9881b278-0a45-47c1-9ed
export VERTEX_AI_LOCATION=us-central1
python3 test_local_setup.py
```

## Server

Start server with:
```bash
export GOOGLE_CLOUD_PROJECT=project-9881b278-0a45-47c1-9ed
export VERTEX_AI_LOCATION=us-central1
python3 apps/server/main.py
```
