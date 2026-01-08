# Adiyogi LangChain

Modular LangChain + Gemini 3 Flash integration for Adiyogi Arts.

## Structure

```
Adiyogilanchain/
├── packages/               # Independent modules
│   ├── core/               # [Platform] Config, types, utils
│   ├── langchain-client/   # [AI/ML] Gemini model factory
│   ├── langchain-memory/   # [AI/ML] Session memory
│   ├── langchain-chains/   # [AI/ML] Conversation chains
│   ├── research_agent/     # [AI/ML] Internet research with Vertex AI
│   ├── api/                # [Backend] FastAPI endpoints
│   ├── ui/                 # [Frontend] React components
│   └── testing/            # [QA] E2E & integration tests
├── apps/                   # Deployable applications
│   ├── server/             # Backend entry point (Lambda)
│   ├── web/                # Frontend entry point
│   └── research-service/   # Research API (Cloud Run)
├── docs/                   # Documentation
└── scripts/                # Development scripts
```

## Quick Start

### Prerequisites
- Python 3.11+
- Node.js 20+
- Gemini API Key ([Get one here](https://aistudio.google.com/app/apikey))

### Setup

```bash
# Clone
git clone https://github.com/adigkp1312-collab/Adiyogilanchain.git
cd Adiyogilanchain

# Install backend deps
pip install -r apps/server/requirements.txt

# Install frontend deps
cd packages/ui && npm install && cd ../..
```

### Configure API Key (Lambda Environment Variables)

**Production (Lambda Console):**
1. Lambda → Configuration → Environment variables
2. Add: `GEMINI_API_KEY` = `your_key`

**Production (AWS CLI):**
```bash
aws lambda update-function-configuration \
  --function-name your-function \
  --environment Variables="{GEMINI_API_KEY=your_key}"
```

**Local Development (SAM):**
```bash
# Create env.json (gitignored)
echo '{"Function": {"GEMINI_API_KEY": "your_key"}}' > env.json

# Start local Lambda
sam local start-api --env-vars env.json
```

See [ADR-001](docs/adr/001-lambda-environment-variables.md) for details.

### Run (Local with SAM)

```bash
# Start backend with SAM
sam local start-api --env-vars env.json --port 8000

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
