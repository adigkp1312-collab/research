"""
Research Hub Service - FastAPI Application.

Unified research platform for branding and marketing intelligence.
"""

import os
import sys
from pathlib import Path
from typing import Optional, List
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Query, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Add project root to path for package imports
root = Path(__file__).parent.parent.parent
if str(root) not in sys.path:
    sys.path.insert(0, str(root))

from packages.research_hub.src.config import (
    validate_research_hub_config,
    get_config_summary,
    CORS_ORIGINS,
)
from packages.research_hub.src.models import (
    ResearchType,
    ResearchStatus,
    InputType,
    CreateResearchRequest,
    ResearchResponse,
    ListResearchRequest,
    BatchResearchRequest,
    ResearchSearchRequest,
    AgentInfo,
)
from packages.research_hub.src.orchestrator import ResearchOrchestrator
from packages.research_hub.src.storage import ResearchRepository


# =============================================================================
# APPLICATION SETUP
# =============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    config_status = validate_research_hub_config()
    print(f"Research Hub starting...")
    print(f"Configuration: {get_config_summary()}")

    if config_status["warnings"]:
        for warning in config_status["warnings"]:
            print(f"Warning: {warning}")

    if not config_status["ready"]:
        print(f"Missing required config: {config_status['missing']}")

    yield

    # Shutdown
    print("Research Hub shutting down...")


app = FastAPI(
    title="Research Hub API",
    description="Unified research platform for branding and marketing intelligence",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =============================================================================
# DEPENDENCIES
# =============================================================================

def get_orchestrator() -> ResearchOrchestrator:
    """Get research orchestrator with repository."""
    repository = ResearchRepository()
    return ResearchOrchestrator(repository=repository)


def get_repository() -> ResearchRepository:
    """Get research repository."""
    return ResearchRepository()


# =============================================================================
# HEALTH & STATUS ENDPOINTS
# =============================================================================

@app.get("/", tags=["Health"])
async def root():
    """Health check endpoint."""
    config_status = validate_research_hub_config()
    return {
        "status": "ok" if config_status["ready"] else "degraded",
        "service": "research-hub",
        "version": "1.0.0",
        "configured": config_status["configured"],
    }


@app.get("/health", tags=["Health"])
async def health():
    """Detailed health check."""
    config_status = validate_research_hub_config()
    return {
        "status": "healthy" if config_status["ready"] else "degraded",
        "service": "research-hub",
        "version": "1.0.0",
        "configuration": config_status,
        "summary": get_config_summary(),
    }


# =============================================================================
# AGENT ENDPOINTS
# =============================================================================

@app.get("/api/v1/research-hub/agents", tags=["Agents"])
async def list_agents():
    """List all available research agents and their capabilities."""
    orchestrator = get_orchestrator()
    agents = orchestrator.get_available_agents()
    return {
        "agents": agents,
        "count": len(agents),
    }


@app.get("/api/v1/research-hub/agents/{agent_type}", tags=["Agents"])
async def get_agent_info(agent_type: str):
    """Get detailed information about a specific agent."""
    try:
        research_type = ResearchType(agent_type)
    except ValueError:
        raise HTTPException(
            status_code=404,
            detail=f"Unknown agent type: {agent_type}"
        )

    orchestrator = get_orchestrator()
    agent = orchestrator.agents.get(research_type)

    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    return agent.get_agent_info()


# =============================================================================
# RESEARCH ENDPOINTS
# =============================================================================

@app.post("/api/v1/research-hub/research", tags=["Research"])
async def create_research(request: CreateResearchRequest):
    """
    Create new research.

    Executes research across specified types and returns results.
    For multiple research types, execution happens in parallel.
    """
    orchestrator = get_orchestrator()

    try:
        results = await orchestrator.execute_research(
            project_id=request.project_id,
            user_id="api-user",  # TODO: Get from auth
            research_types=request.research_types,
            query=request.input_value,
            input_type=request.input_type,
            context=request.context,
            save_results=True,
        )

        # Format response
        responses = []
        for research_type, result in results.items():
            responses.append({
                "research_type": research_type.value,
                "status": result.status.value,
                "summary": result.summary,
                "confidence_score": result.confidence_score,
                "sources_count": len(result.sources),
                "processing_time_ms": result.processing_time_ms,
                "tools_used": result.tools_used,
                "analysis_data": result.analysis_data,
            })

        # Get synthesis
        synthesis = await orchestrator.synthesize_results(results)

        return {
            "success": True,
            "query": request.input_value,
            "research_count": len(responses),
            "results": responses,
            "synthesis": synthesis,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/research-hub/research", tags=["Research"])
async def list_research(
    project_id: Optional[str] = Query(None),
    research_type: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    limit: int = Query(50, le=100),
    offset: int = Query(0),
):
    """List research entries with optional filters."""
    repo = get_repository()

    if not repo.is_configured:
        raise HTTPException(status_code=503, detail="Storage not configured")

    try:
        # Parse filters
        research_types = None
        if research_type:
            research_types = [ResearchType(research_type)]

        status_filter = None
        if status:
            status_filter = ResearchStatus(status)

        entries = await repo.list_by_project(
            project_id=project_id or "default",
            research_types=research_types,
            status=status_filter,
            limit=limit,
            offset=offset,
        )

        return {
            "success": True,
            "count": len(entries),
            "research": [e.to_dict() for e in entries],
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/research-hub/research/{research_id}", tags=["Research"])
async def get_research(research_id: str):
    """Get a single research entry by ID."""
    repo = get_repository()

    if not repo.is_configured:
        raise HTTPException(status_code=503, detail="Storage not configured")

    entry = await repo.get_by_id(research_id)

    if not entry:
        raise HTTPException(status_code=404, detail="Research not found")

    return {
        "success": True,
        "research": entry.to_dict(),
    }


@app.patch("/api/v1/research-hub/research/{research_id}", tags=["Research"])
async def update_research(
    research_id: str,
    updates: dict,
):
    """Update a research entry."""
    repo = get_repository()

    if not repo.is_configured:
        raise HTTPException(status_code=503, detail="Storage not configured")

    # Filter allowed updates
    allowed_fields = {"title", "tags", "is_pinned"}
    filtered_updates = {k: v for k, v in updates.items() if k in allowed_fields}

    if not filtered_updates:
        raise HTTPException(status_code=400, detail="No valid update fields provided")

    entry = await repo.update(
        research_id=research_id,
        user_id="api-user",  # TODO: Get from auth
        updates=filtered_updates,
    )

    if not entry:
        raise HTTPException(status_code=404, detail="Research not found or not authorized")

    return {
        "success": True,
        "research": entry.to_dict(),
    }


@app.delete("/api/v1/research-hub/research/{research_id}", tags=["Research"])
async def delete_research(research_id: str):
    """Delete a research entry."""
    repo = get_repository()

    if not repo.is_configured:
        raise HTTPException(status_code=503, detail="Storage not configured")

    success = await repo.delete(
        research_id=research_id,
        user_id="api-user",  # TODO: Get from auth
    )

    if not success:
        raise HTTPException(status_code=404, detail="Research not found or not authorized")

    return {"success": True, "deleted": research_id}


# =============================================================================
# PROJECT ENDPOINTS
# =============================================================================

@app.get("/api/v1/research-hub/projects/{project_id}/research", tags=["Projects"])
async def list_project_research(
    project_id: str,
    research_type: Optional[str] = Query(None),
    limit: int = Query(50, le=100),
    offset: int = Query(0),
):
    """List all research for a specific project."""
    repo = get_repository()

    if not repo.is_configured:
        raise HTTPException(status_code=503, detail="Storage not configured")

    research_types = None
    if research_type:
        research_types = [ResearchType(research_type)]

    entries = await repo.list_by_project(
        project_id=project_id,
        research_types=research_types,
        limit=limit,
        offset=offset,
    )

    return {
        "success": True,
        "project_id": project_id,
        "count": len(entries),
        "research": [e.to_dict() for e in entries],
    }


@app.get("/api/v1/research-hub/projects/{project_id}/research/summary", tags=["Projects"])
async def get_project_research_summary(project_id: str):
    """Get a summary of all research for a project."""
    repo = get_repository()

    if not repo.is_configured:
        raise HTTPException(status_code=503, detail="Storage not configured")

    summary = await repo.get_project_summary(project_id)

    return {
        "success": True,
        "summary": summary,
    }


# =============================================================================
# SEARCH ENDPOINTS
# =============================================================================

@app.post("/api/v1/research-hub/research/search", tags=["Search"])
async def search_research(request: ResearchSearchRequest):
    """Full-text search across research entries."""
    repo = get_repository()

    if not repo.is_configured:
        raise HTTPException(status_code=503, detail="Storage not configured")

    entries = await repo.search(
        query=request.query,
        project_id=request.project_id,
        research_types=request.research_types,
        limit=request.limit,
    )

    return {
        "success": True,
        "query": request.query,
        "count": len(entries),
        "results": [e.to_dict() for e in entries],
    }


# =============================================================================
# BATCH ENDPOINTS
# =============================================================================

@app.post("/api/v1/research-hub/research/batch", tags=["Batch"])
async def batch_research(
    request: BatchResearchRequest,
    background_tasks: BackgroundTasks,
):
    """
    Create multiple research requests.

    For large batches, consider running in background.
    """
    orchestrator = get_orchestrator()
    results = []

    for query_item in request.queries:
        input_value = query_item.get("input_value", "")
        research_types = query_item.get("research_types", [ResearchType.COMPETITOR])
        context = query_item.get("context")

        # Convert string types to enums
        if isinstance(research_types[0], str):
            research_types = [ResearchType(rt) for rt in research_types]

        try:
            result = await orchestrator.execute_research(
                project_id=request.project_id,
                user_id="api-user",
                research_types=research_types,
                query=input_value,
                context=context,
                save_results=True,
            )

            synthesis = await orchestrator.synthesize_results(result)
            results.append({
                "query": input_value,
                "success": True,
                "synthesis": synthesis,
            })

        except Exception as e:
            results.append({
                "query": input_value,
                "success": False,
                "error": str(e),
            })

    return {
        "success": True,
        "batch_size": len(request.queries),
        "completed": len([r for r in results if r["success"]]),
        "failed": len([r for r in results if not r["success"]]),
        "results": results,
    }


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=False,
    )
