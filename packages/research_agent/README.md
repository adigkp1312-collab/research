# Research Agent

Internet research capabilities using Vertex AI with Google Search grounding.

## Purpose

Researches products, companies, and markets to provide structured insights for ad/video creation.

## Features

- URL or text input
- Google Search grounding via Vertex AI
- Structured JSON output (product, company, market, ad recommendations)
- Supabase storage for persistence

## Usage

```python
from research_agent.src.agent import research_product_company_market

result = await research_product_company_market(
    query="Nike Air Max",
    input_type="text",
    research_focus=["product", "company", "market"]
)
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/research` | POST | Create new research |
| `/research/{project_id}` | GET | List research by project |
| `/research/item/{id}` | GET | Get single research |
| `/research/{id}` | PATCH | Update research |
| `/research/{id}` | DELETE | Delete research |

## Environment Variables

```bash
GOOGLE_CLOUD_PROJECT=your-project-id
VERTEX_AI_LOCATION=us-central1
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_SERVICE_KEY=xxx
```
