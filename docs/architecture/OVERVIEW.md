# Architecture Overview

## Monorepo Structure

```
Adiyogilanchain/
├── packages/           # Independent modules
│   ├── core/           # Platform Team - Config, utils
│   ├── langchain-*/    # AI/ML Team - LangChain integration
│   ├── api/            # Backend Team - REST endpoints
│   ├── ui/             # Frontend Team - React components
│   └── testing/        # QA Team - E2E & integration tests
├── apps/               # Deployable applications
│   ├── server/         # Backend entry point
│   └── web/            # Frontend entry point
└── docs/               # Documentation
```

## Package Dependencies

```
core
  ↑
langchain-client ← langchain-memory
  ↑                     ↑
langchain-chains ───────┘
  ↑
api ← ui
```

## Team Ownership

| Package | Team | Responsibility |
|---------|------|----------------|
| `core` | Platform | Config, types, utilities |
| `langchain-client` | AI/ML | Gemini model factory |
| `langchain-memory` | AI/ML | Session state management |
| `langchain-chains` | AI/ML | Conversation logic |
| `api` | Backend | REST endpoints |
| `ui` | Frontend | React components |
| `testing` | QA | E2E & integration tests |

## Data Flow

1. User sends message via UI
2. UI calls API `/chat/stream`
3. API uses `langchain-chains` to create conversation
4. Chain uses `langchain-client` to call Gemini
5. Memory stored via `langchain-memory`
6. Response streamed back to UI
