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
│   ├── api/                # [Backend] FastAPI endpoints
│   ├── ui/                 # [Frontend] React components
│   └── testing/            # [QA] E2E & integration tests
├── apps/                   # Deployable applications
│   ├── server/             # Backend entry point
│   └── web/                # Frontend entry point
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

# Set API key
export GEMINI_API_KEY=your_key_here

# Install backend deps
pip install -r apps/server/requirements.txt

# Install frontend deps
cd packages/ui && npm install && cd ../..
```

### Run

```bash
# Start backend (from root)
PYTHONPATH=. uvicorn packages.api.src.app:app --reload --port 8000

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
| `packages/api` | Backend | - |
| `packages/ui` | Frontend | - |
| `packages/testing` | QA | - |
| `apps/*` | DevOps | - |

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

- [Architecture Overview](docs/architecture/OVERVIEW.md)
- [LLM Flow](docs/architecture/LLM_FLOW.md)
- [API Key Security](docs/security/API_KEYS.md)

## License

MIT
