# Firebase / Firestore Configuration

Configuration files for Google Cloud Firestore used by the Research Hub.

## Files

| File | Purpose |
|------|---------|
| `firestore.rules` | Security rules for access control |
| `firestore.indexes.json` | Composite indexes for query optimization |
| `firebase.json` | Firebase CLI configuration |

## Deploying

### Option 1: Using Firebase CLI

```bash
# Install Firebase CLI
npm install -g firebase-tools

# Login to Firebase
firebase login

# Set your project
firebase use your-project-id

# Deploy rules and indexes
cd firebase
firebase deploy --only firestore:rules,firestore:indexes
```

### Option 2: Using Google Cloud Console

1. Go to [Firestore Console](https://console.cloud.google.com/firestore)
2. Select your project
3. **Rules**: Go to Rules tab → Paste contents of `firestore.rules` → Publish
4. **Indexes**: Go to Indexes tab → Import from `firestore.indexes.json`

### Option 3: Using gcloud CLI

```bash
# Deploy indexes
gcloud firestore indexes composite create \
  --project=your-project-id \
  --collection-group=research_hub_entries \
  --field-config=field-path=project_id,order=ascending \
  --field-config=field-path=created_at,order=descending
```

## Indexes Explained

| Index | Purpose |
|-------|---------|
| `project_id + created_at` | List research by project (most common query) |
| `project_id + research_type + created_at` | Filter by research type within project |
| `project_id + status + created_at` | Filter by status within project |
| `user_id + created_at` | List user's research across all projects |
| `project_id + is_pinned + created_at` | Show pinned items first |
| `tags (array-contains)` | Search by tags |

## Security Rules Explained

### Access Control

| Action | Who Can Do It |
|--------|---------------|
| **Read** | Owner or project members |
| **Create** | Authenticated users (sets user_id to self) |
| **Update** | Owner only (cannot change ownership) |
| **Delete** | Owner only |

### Backend API Access

The backend API uses the **Firebase Admin SDK** which bypasses security rules. These rules are primarily for:

- Direct client-side access (web/mobile apps)
- Additional security layer
- Audit compliance

### Custom Claims (Optional)

For API keys or service accounts, you can add custom claims:

```javascript
// In your auth system
admin.auth().setCustomUserClaims(uid, { isServiceAccount: true });
```

Then in rules:
```
allow read: if request.auth.token.isServiceAccount == true;
```

## Testing Rules

Use the Firebase Emulator to test rules locally:

```bash
# Start emulator
firebase emulators:start --only firestore

# Run tests
npm test
```

## Field Exemptions

Large fields are exempted from indexing to save costs:

- `analysis_data` - Large JSON objects
- `agent_trace` - Debug traces
- `sources` - Array of source objects

These fields can still be read but cannot be used in queries.
