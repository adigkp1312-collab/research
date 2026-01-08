# Research Service API

Cloud Run service for internet research using Vertex AI with Google Search grounding.

## Base URL

**Production:** `https://research-service-1083011801594.asia-southeast1.run.app`

## Authentication

Currently unauthenticated. User validation is done via `user_id` in requests matching Supabase auth.

---

## Endpoints

### POST /research

Create new research from URL or text input.

**Request Body:**
```json
{
  "project_id": "uuid",
  "user_id": "uuid",
  "input_value": "https://example.com or text query",
  "input_type": "url | text",
  "research_focus": ["product", "company", "market"]
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `project_id` | UUID | ✅ | Project to attach research to |
| `user_id` | UUID | ✅ | User performing research |
| `input_value` | string | ✅ | URL or text query to research |
| `input_type` | string | ❌ | Auto-detected if not provided |
| `research_focus` | array | ❌ | Default: `["product", "company", "market"]` |

**Response (201):**
```json
{
  "success": true,
  "research_id": "uuid",
  "analysis_data": {
    "product": {
      "name": "Product Name",
      "description": "...",
      "features": ["..."],
      "pricing": "...",
      "usp": "...",
      "target_audience": "..."
    },
    "company": {
      "name": "Company Name",
      "about": "...",
      "founded": "...",
      "headquarters": "...",
      "mission": "...",
      "social_presence": {...}
    },
    "market": {
      "competitors": [...],
      "trends": [...],
      "audience_insights": "...",
      "market_size": "..."
    },
    "ad_recommendations": {
      "key_messages": [...],
      "emotional_hooks": [...],
      "visual_themes": [...],
      "cta_suggestions": [...]
    },
    "sources": [
      {"url": "...", "title": "..."}
    ],
    "generated_at": "2025-01-08T12:00:00Z"
  },
  "sources_count": 5,
  "processing_time": "3.2s",
  "metadata": {
    "input_type": "url",
    "source_type": "url_research",
    "research_focus": ["product", "company", "market"],
    "title": "Research: Example Product"
  }
}
```

---

### GET /research/{project_id}

List all research for a project.

**Query Parameters:**
| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `limit` | int | 50 | Max items to return |

**Response (200):**
```json
{
  "success": true,
  "project_id": "uuid",
  "count": 3,
  "research": [
    {
      "id": "uuid",
      "source_type": "url_research",
      "source_input": "https://...",
      "title": "Research: Product",
      "created_at": "2025-01-08T12:00:00Z",
      "updated_at": "2025-01-08T12:00:00Z"
    }
  ]
}
```

---

### GET /research/item/{research_id}

Get single research item with full data.

**Response (200):**
```json
{
  "success": true,
  "research": {
    "id": "uuid",
    "project_id": "uuid",
    "user_id": "uuid",
    "source_type": "url_research",
    "source_input": "https://...",
    "title": "Research: Product",
    "analysis_data": {...},
    "created_at": "2025-01-08T12:00:00Z",
    "updated_at": "2025-01-08T12:00:00Z"
  }
}
```

---

### PATCH /research/{research_id}

Update research data.

**Request Body:**
```json
{
  "user_id": "uuid",
  "analysis_data": {...},
  "title": "New Title"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `user_id` | UUID | ✅ | User making update |
| `analysis_data` | object | ❌ | Updated research data |
| `title` | string | ❌ | New title |

**Response (200):**
```json
{
  "success": true,
  "research_id": "uuid",
  "updated_at": "2025-01-08T12:30:00Z"
}
```

---

### DELETE /research/{research_id}

Delete research entry.

**Query Parameters:**
| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `user_id` | UUID | ✅ | User requesting deletion |

**Response (200):**
```json
{
  "success": true,
  "deleted": "uuid"
}
```

---

## Error Responses

```json
{
  "error": "Error message"
}
```

| Status | Description |
|--------|-------------|
| 400 | Bad request (missing required fields) |
| 404 | Research not found |
| 500 | Server error |

---

## Environment Variables

| Variable | Description |
|----------|-------------|
| `GOOGLE_CLOUD_PROJECT` | GCP project ID for Vertex AI |
| `VERTEX_AI_LOCATION` | Region (default: `us-central1`) |
| `SUPABASE_URL` | Supabase project URL |
| `SUPABASE_SERVICE_KEY` | Supabase service role key |

---

## Database Schema

Research is stored in Supabase table `project_research`:

```sql
create table project_research (
  id uuid primary key default gen_random_uuid(),
  project_id uuid references projects(id) on delete cascade,
  user_id uuid references auth.users not null,
  source_type text not null,  -- 'url_research' or 'text_research'
  source_input text not null,
  title text,
  analysis_data jsonb not null,
  created_at timestamptz default now(),
  updated_at timestamptz default now()
);
```

---

## Deployment

```bash
# From repo root
cd apps/research-service

# Deploy to Cloud Run
gcloud run deploy research-service \
  --source . \
  --region asia-southeast1 \
  --allow-unauthenticated \
  --set-env-vars GOOGLE_CLOUD_PROJECT=xxx,SUPABASE_URL=xxx,SUPABASE_SERVICE_KEY=xxx
```
