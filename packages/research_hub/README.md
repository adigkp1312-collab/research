# Research Hub

**Team: AI/ML**

Unified research platform for branding and marketing intelligence using Vertex AI Agent Garden tools.

## Overview

Research Hub provides a multi-agent research system that consolidates all research types in one place:

- **Competitor Analysis** - Analyze competitor landscape, positioning, and strategies
- **Market Analysis** - Market size, trends, opportunities, and key players
- **Video/Ad Analysis** - Video styles, messaging, CTAs, and engagement patterns
- **Social Media Intelligence** - Brand presence, engagement, and influencer landscape
- **Audience Research** - Demographics, psychographics, and behavior patterns
- **Trend Analysis** - Industry trends, viral patterns, and emerging topics

## Architecture

```
┌──────────────────────────┐
│   Research Orchestrator  │
│   (Multi-Agent Coord)    │
└────────────┬─────────────┘
             │
┌────────────┼────────────┐
│     │      │      │     │
▼     ▼      ▼      ▼     ▼
[6 Specialized Research Agents]
             │
┌────────────┴────────────┐
│  Vertex AI Agent Garden │
│  - Google Search        │
│  - RAG Engine           │
│  - YouTube Data API     │
└─────────────────────────┘
```

## Installation

```bash
pip install -r requirements.txt
```

## Environment Variables

```bash
# Required
GOOGLE_CLOUD_PROJECT=your-project-id

# Optional
VERTEX_AI_LOCATION=us-central1
YOUTUBE_API_KEY=your-youtube-key
VERTEX_AI_DATASTORE_ID=your-datastore-id
RESEARCH_HUB_MODEL=gemini-2.0-flash-001
RESEARCH_TIMEOUT_SECONDS=60
MAX_CONCURRENT_AGENTS=3
FIRESTORE_COLLECTION=research_hub_entries
```

## Storage

Uses **Google Cloud Firestore** for data persistence. No additional setup required - Firestore is automatically available when you have a GCP project.

Firestore collection: `research_hub_entries`

## Usage

### Programmatic Usage

```python
import asyncio
from packages.research_hub.src.orchestrator import ResearchOrchestrator
from packages.research_hub.src.models import ResearchType

async def main():
    orchestrator = ResearchOrchestrator()

    results = await orchestrator.execute_research(
        project_id="my-project",
        user_id="user-123",
        research_types=[
            ResearchType.COMPETITOR,
            ResearchType.MARKET,
        ],
        query="Nike athletic shoes",
        context={"industry": "footwear", "region": "north_america"},
    )

    for research_type, result in results.items():
        print(f"{research_type.value}: {result.summary}")

asyncio.run(main())
```

### API Usage

Start the service:

```bash
cd apps/research-hub-service
python main.py
```

Create research:

```bash
curl -X POST http://localhost:8080/api/v1/research-hub/research \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": "my-project",
    "research_types": ["competitor", "market"],
    "input_value": "Nike athletic shoes",
    "context": {"industry": "footwear"}
  }'
```

List agents:

```bash
curl http://localhost:8080/api/v1/research-hub/agents
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/research-hub/research` | POST | Create new research |
| `/api/v1/research-hub/research` | GET | List research entries |
| `/api/v1/research-hub/research/{id}` | GET | Get single entry |
| `/api/v1/research-hub/research/{id}` | PATCH | Update entry |
| `/api/v1/research-hub/research/{id}` | DELETE | Delete entry |
| `/api/v1/research-hub/projects/{id}/research` | GET | List project research |
| `/api/v1/research-hub/projects/{id}/research/summary` | GET | Get project summary |
| `/api/v1/research-hub/research/search` | POST | Full-text search |
| `/api/v1/research-hub/research/batch` | POST | Batch research |
| `/api/v1/research-hub/agents` | GET | List available agents |

## Package Structure

```
research_hub/
├── src/
│   ├── orchestrator.py      # Multi-agent coordinator
│   ├── config.py            # Configuration
│   ├── agents/              # Specialized agents
│   │   ├── base_agent.py
│   │   ├── competitor_agent.py
│   │   ├── market_agent.py
│   │   ├── video_agent.py
│   │   ├── social_agent.py
│   │   ├── audience_agent.py
│   │   └── trend_agent.py
│   ├── tools/               # Agent Garden tools
│   │   ├── google_search.py
│   │   ├── youtube_tool.py
│   │   └── rag_tool.py
│   ├── models/              # Data models
│   │   └── research_types.py
│   └── storage/             # Persistence
│       ├── supabase_client.py
│       └── research_repo.py
├── tests/
├── requirements.txt
└── README.md
```

## Testing

```bash
cd packages/research_hub
pytest tests/ -v
```

## Deployment

### Cloud Run

```bash
cd /path/to/langchain-poc
gcloud run deploy research-hub \
  --source apps/research-hub-service \
  --region us-central1 \
  --set-env-vars GOOGLE_CLOUD_PROJECT=your-project
```

### Docker

```bash
docker build -t research-hub -f apps/research-hub-service/Dockerfile .
docker run -p 8080:8080 -e GOOGLE_CLOUD_PROJECT=your-project research-hub
```
