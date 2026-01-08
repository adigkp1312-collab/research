# Security: API Key Management

## Overview

This POC uses **Lambda environment variables** for secure API key management. Keys are never hardcoded in source code.

## ✅ Secure Practices

### Keys Never in Code
- ❌ No hardcoded API keys in source files
- ❌ No keys in git commits
- ❌ No keys in .env files (for production)
- ✅ Keys only in Lambda environment variables

### Lambda Environment Variables
```
Lambda Configuration
    ↓
Environment Variables
    ↓
GEMINI_API_KEY=your_key_here
    ↓
Code reads via: os.environ.get('GEMINI_API_KEY')
```

## 🔒 How It Works

### 1. Lambda Environment Setup
```bash
# Set in Lambda console or via CLI
aws lambda update-function-configuration \
  --function-name your-function \
  --environment Variables="{GEMINI_API_KEY=your_key}"
```

### 2. Code Reads from Environment
```python
# backend/src/config.py
api_key = os.environ.get("GEMINI_API_KEY", "")

# Lambda automatically injects environment variables
# No .env file needed in production
```

### 3. Validation
```python
if not api_key:
    raise ValueError("GEMINI_API_KEY not found in Lambda environment")
```

## 🚀 Production Recommendations

### Option 1: AWS Secrets Manager (Most Secure)

```python
# backend/src/config.py - Add this helper
import boto3
import json

def get_secret_from_aws_secrets_manager(secret_name: str) -> str:
    """Get secret from AWS Secrets Manager."""
    try:
        client = boto3.client('secretsmanager', region_name='us-east-1')
        response = client.get_secret_value(SecretId=secret_name)
        secret = json.loads(response['SecretString'])
        return secret.get('GEMINI_API_KEY', '')
    except Exception as e:
        print(f"Failed to get secret: {e}")
        return ""
```

**Create secret:**
```bash
aws secretsmanager create-secret \
  --name adiyogi/gemini-api-key \
  --secret-string '{"GEMINI_API_KEY":"your_key_here"}' \
  --region us-east-1
```

**Lambda IAM Permission:**
```json
{
  "Effect": "Allow",
  "Action": [
    "secretsmanager:GetSecretValue"
  ],
  "Resource": "arn:aws:secretsmanager:us-east-1:*:secret:adiyogi/gemini-api-key-*"
}
```

### Option 2: Environment Variables (Current)
- ✅ Simple
- ✅ Works out of the box
- ⚠️ Visible in Lambda console (requires proper access controls)

## 📋 Security Checklist

Before deploying:

- [ ] GEMINI_API_KEY set in Lambda environment (not in code)
- [ ] .env files gitignored (`.env` in `.gitignore`)
- [ ] No keys in commit history
- [ ] Lambda function has proper IAM permissions
- [ ] Secrets Manager used for production (recommended)
- [ ] Keys rotated regularly
- [ ] Access to Lambda console restricted

## 🔍 Verifying Security

### Check for Hardcoded Keys
```bash
# Search codebase for API keys
grep -r "AIzaSy" . --exclude-dir=node_modules --exclude-dir=venv
grep -r "sk-or-" . --exclude-dir=node_modules --exclude-dir=venv

# Should return no results
```

### Verify Environment Variable
```bash
# In Lambda test console
import os
print(os.environ.get('GEMINI_API_KEY', 'NOT_SET'))
# Should print your key (NOT_SET means not configured)
```

## 🚨 If Key is Compromised

1. **Rotate immediately:**
   ```bash
   # Get new key from Google AI Studio
   # Update in Lambda
   aws lambda update-function-configuration \
     --function-name your-function \
     --environment Variables="{GEMINI_API_KEY=new_key}"
   ```

2. **Revoke old key:**
   - Go to Google AI Studio
   - Delete/revoke the old key

3. **Audit access:**
   - Check Lambda logs for unauthorized access
   - Review Git history if key was accidentally committed
