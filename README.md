# Adiyogi Research

Modular LangChain + Gemini 3 Flash integration for Adiyogi Arts.

## Structure

```
research/
├── packages/               # Python libraries
│   ├── core/               # Config, types, utils
│   ├── knowledge_base/     # Knowledge base logic
│   ├── research_agent/     # AI research agent (Vertex AI + Grounding)
│   ├── langchain-client/   # Gemini model factory
│   ├── langchain-memory/   # Session memory
│   ├── langchain-chains/   # Conversation chains
│   ├── api/                # FastAPI endpoints
│   ├── ui/                 # React components
│   └── testing/            # E2E & integration tests
│
├── apps/                   # Deployable applications
│   ├── server/             # Backend entry point (Lambda)
│   ├── web/                # Frontend entry point
│   ├── research-service/   # Research API (Cloud Run)
│   └── research-hub-service/ # Research Hub API
│
├── experiments/            # Research experiments & POCs
│   └── meta-ads-scraper/   # Meta Ad Library scraper (Playwright + GCS)
│
├── notebooks/              # Jupyter notebooks for exploration
├── datasets/               # Sample data & GCS references
├── tools/                  # Standalone CLI utilities
├── docs/                   # Documentation
├── scripts/                # Development scripts
└── firebase/               # Firebase configs
```

## Quick Start

### Prerequisites
- Python 3.11+
- Node.js 20+
- Google Cloud Project with Vertex AI API enabled
- GCP Service Account with Vertex AI permissions

### Setup

```bash
# Clone
git clone https://github.com/adigkp1312-collab/research.git
cd research

# Install backend deps
pip install -r apps/server/requirements.txt

# Install frontend deps
cd packages/ui && npm install && cd ../..
```

### Configure Google Cloud Project

**Production (Cloud Run):**
1. Create a Google Cloud Project
2. Enable Vertex AI API
3. Set up Application Default Credentials or Service Account
4. Deploy with environment variables:
   - `GOOGLE_CLOUD_PROJECT` = `your-project-id`
   - `VERTEX_AI_LOCATION` = `us-central1` (or your preferred region)

**Local Development:**
```bash
# Set up Application Default Credentials
gcloud auth application-default login

# Or set environment variables
export GOOGLE_CLOUD_PROJECT=your-project-id
export VERTEX_AI_LOCATION=us-central1

# Run locally
python apps/server/main.py
```

See deployment instructions below for Cloud Run setup.

### Run (Local Development)

```bash
# Set environment variables
export GOOGLE_CLOUD_PROJECT=your-project-id
export VERTEX_AI_LOCATION=us-central1

# Start backend
python apps/server/main.py

# Start frontend (new terminal)
cd packages/ui && npm run dev
```

Access:
- Frontend: http://localhost:5173
- Backend: http://localhost:8000
- API Docs: http://localhost:8000/docs

## Team Ownership

| Package | Team | Contact |
|---------|------|---------|
| `packages/core` | Platform | - |
| `packages/langchain-*` | AI/ML | - |
| `packages/research_agent` | AI/ML | - |
| `packages/api` | Backend | - |
| `packages/ui` | Frontend | - |
| `packages/testing` | QA | - |
| `apps/*` | DevOps | - |

## Deployment

### Main API (Cloud Run)

Deploy the main API to Cloud Run:

```bash
cd apps/server
gcloud run deploy langchain-api \
  --source . \
  --region us-central1 \
  --set-env-vars GOOGLE_CLOUD_PROJECT=your-project-id,VERTEX_AI_LOCATION=us-central1 \
  --allow-unauthenticated
```

## Research Service (Cloud Run)

Internet research agent using Vertex AI + Google Search grounding.

**Deployed:** `https://research-service-1083011801594.asia-southeast1.run.app`

### Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/research` | Create research from URL or text |
| GET | `/research/{project_id}` | List all research for project |
| GET | `/research/item/{id}` | Get single research item |
| PATCH | `/research/{id}` | Update research |
| DELETE | `/research/{id}` | Delete research |

### Deploy

```bash
cd apps/research-service
gcloud run deploy research-service \
  --source . \
  --region asia-southeast1 \
  --set-env-vars GOOGLE_CLOUD_PROJECT=your-project,SUPABASE_URL=xxx,SUPABASE_SERVICE_KEY=xxx
```

See [Research Agent README](packages/research_agent/README.md) for package details.

## Testing

```bash
# Run all tests
./scripts/test-all.sh

# Run specific package tests
cd packages/api && pytest tests/

# Run E2E tests
cd packages/testing && npm run test:e2e
```

## Documentation

- [Project Specification](SPEC.md) - Requirements and rules
- [Pre-Commit Checklist](CHECKLIST.md) - Verification before commit
- [Architecture Overview](docs/architecture/OVERVIEW.md)
- [LLM Flow](docs/architecture/LLM_FLOW.md)
- [API Key Security](docs/security/API_KEYS.md)
- [Research Agent](packages/research_agent/README.md) - Internet research
- [Research Service API](docs/api/RESEARCH_SERVICE.md) - Cloud Run API docs
- [ADRs](docs/adr/README.md) - Architecture decisions

## License

MIT
