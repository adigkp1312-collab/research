# Claude Code Instructions

## Debugging Protocol - MUST FOLLOW

Before making ANY fix or deployment:

### 1. Reproduce Locally First
```bash
# Always test locally before assuming Cloud/production issues
python3 -m pytest  # or direct script test
```

### 2. Get Actual Error
- Ask user for exact error message
- Check logs: `gcloud logging read` or container logs
- If "silent fail" - add logging/print statements locally first
- Never guess at the cause

### 3. Confirm Root Cause
- Trace the code path manually
- Identify the exact line/function failing
- Explain to user: "The issue is X because Y"

### 4. Test Fix Locally
```bash
# Run the fix locally and confirm it works
python3 test_script.py
```

### 5. Only Then Deploy
- One deployment per confirmed fix
- Never deploy hoping it might work

## Common Mistakes to Avoid

- **Don't guess** - "This might be a container issue" without evidence
- **Don't stack fixes** - Fix one thing at a time
- **Don't deploy to debug** - Debug locally or ask for logs first
- **Don't assume** - Ask user what they actually see

## Cloud Run Debugging

If local works but Cloud Run doesn't:
1. Check Cloud Run logs first: `gcloud run services logs read SERVICE_NAME`
2. Check if it's a permissions/env issue
3. Check container startup: does the app even load?
4. Check request timeouts (default 300s)

## Streamlit Specific

- Button clicks cause page reruns
- Long-running tasks may timeout
- Check browser console for JS errors
- WebSocket connections can drop
