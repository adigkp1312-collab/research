"""
Data models and types for the Research Hub.

Defines all enums, dataclasses, and Pydantic models used across the package.
"""

from enum import Enum
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field
from datetime import datetime
from pydantic import BaseModel, Field
import uuid


class ResearchType(str, Enum):
    """Types of research supported by the hub."""
    COMPETITOR = "competitor"
    MARKET = "market"
    VIDEO_AD = "video_ad"
    SOCIAL_MEDIA = "social_media"
    AUDIENCE = "audience"
    TREND = "trend"


class ResearchStatus(str, Enum):
    """Status of a research entry."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class InputType(str, Enum):
    """Types of input for research."""
    URL = "url"
    TEXT = "text"
    BRAND_NAME = "brand_name"
    TOPIC = "topic"
    VIDEO_URL = "video_url"


@dataclass
class ResearchSource:
    """A source used in research."""
    url: str
    title: str
    source_type: str  # 'web', 'youtube', 'social', 'rag'
    retrieved_at: datetime = field(default_factory=datetime.utcnow)
    relevance_score: Optional[float] = None
    snippet: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "url": self.url,
            "title": self.title,
            "source_type": self.source_type,
            "retrieved_at": self.retrieved_at.isoformat(),
            "relevance_score": self.relevance_score,
            "snippet": self.snippet,
        }


@dataclass
class ResearchInput:
    """Input for a research request."""
    query: str
    input_type: InputType
    context: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "query": self.query,
            "input_type": self.input_type.value if isinstance(self.input_type, InputType) else self.input_type,
            "context": self.context,
        }


@dataclass
class ResearchResult:
    """Result from a research agent."""
    research_type: ResearchType
    analysis_data: Dict[str, Any]
    summary: str
    sources: List[ResearchSource]
    confidence_score: float
    tools_used: List[str]
    processing_time_ms: int
    status: ResearchStatus = ResearchStatus.COMPLETED
    agent_trace: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "research_type": self.research_type.value,
            "analysis_data": self.analysis_data,
            "summary": self.summary,
            "sources": [s.to_dict() for s in self.sources],
            "confidence_score": self.confidence_score,
            "tools_used": self.tools_used,
            "processing_time_ms": self.processing_time_ms,
            "status": self.status.value,
            "agent_trace": self.agent_trace,
            "error_message": self.error_message,
        }


@dataclass
class ResearchEntry:
    """A complete research entry for storage."""
    id: str
    project_id: str
    user_id: str
    research_type: ResearchType
    input: ResearchInput
    result: ResearchResult
    title: str
    status: ResearchStatus = ResearchStatus.COMPLETED
    tags: List[str] = field(default_factory=list)
    is_pinned: bool = False
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    @classmethod
    def create(
        cls,
        project_id: str,
        user_id: str,
        research_type: ResearchType,
        input: ResearchInput,
        result: ResearchResult,
        title: str,
        tags: List[str] = None,
    ) -> "ResearchEntry":
        """Factory method to create a new research entry."""
        return cls(
            id=str(uuid.uuid4()),
            project_id=project_id,
            user_id=user_id,
            research_type=research_type,
            input=input,
            result=result,
            title=title,
            status=result.status,
            tags=tags or [],
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for Supabase storage."""
        return {
            "id": self.id,
            "project_id": self.project_id,
            "user_id": self.user_id,
            "research_type": self.research_type.value,
            "input_query": self.input.query,
            "input_type": self.input.input_type.value if isinstance(self.input.input_type, InputType) else self.input.input_type,
            "input_context": self.input.context,
            "analysis_data": self.result.analysis_data,
            "summary": self.result.summary,
            "confidence_score": self.result.confidence_score,
            "sources": [s.to_dict() for s in self.result.sources],
            "tools_used": self.result.tools_used,
            "agent_trace": self.result.agent_trace,
            "processing_time_ms": self.result.processing_time_ms,
            "title": self.title,
            "tags": self.tags,
            "is_pinned": self.is_pinned,
            "status": self.status.value,
            "error_message": self.result.error_message,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ResearchEntry":
        """Create a ResearchEntry from a dictionary."""
        sources = [
            ResearchSource(
                url=s["url"],
                title=s["title"],
                source_type=s["source_type"],
                retrieved_at=datetime.fromisoformat(s["retrieved_at"]) if s.get("retrieved_at") else datetime.utcnow(),
                relevance_score=s.get("relevance_score"),
                snippet=s.get("snippet"),
            )
            for s in (data.get("sources") or [])
        ]

        result = ResearchResult(
            research_type=ResearchType(data["research_type"]),
            analysis_data=data.get("analysis_data", {}),
            summary=data.get("summary", ""),
            sources=sources,
            confidence_score=data.get("confidence_score", 0.0),
            tools_used=data.get("tools_used", []),
            processing_time_ms=data.get("processing_time_ms", 0),
            status=ResearchStatus(data.get("status", "completed")),
            agent_trace=data.get("agent_trace"),
            error_message=data.get("error_message"),
        )

        input_data = ResearchInput(
            query=data.get("input_query", ""),
            input_type=InputType(data.get("input_type", "text")),
            context=data.get("input_context"),
        )

        return cls(
            id=data["id"],
            project_id=data["project_id"],
            user_id=data["user_id"],
            research_type=ResearchType(data["research_type"]),
            input=input_data,
            result=result,
            title=data.get("title", ""),
            status=ResearchStatus(data.get("status", "completed")),
            tags=data.get("tags", []),
            is_pinned=data.get("is_pinned", False),
            created_at=datetime.fromisoformat(data["created_at"]) if data.get("created_at") else datetime.utcnow(),
            updated_at=datetime.fromisoformat(data["updated_at"]) if data.get("updated_at") else datetime.utcnow(),
        )


# =============================================================================
# PYDANTIC MODELS FOR API
# =============================================================================

class CreateResearchRequest(BaseModel):
    """Request to create new research."""
    project_id: str = Field(..., description="Project UUID")
    research_types: List[ResearchType] = Field(
        ...,
        description="Types of research to perform"
    )
    input_value: str = Field(..., description="URL, text, or query")
    input_type: Optional[InputType] = Field(
        None,
        description="Auto-detected if not provided"
    )
    context: Optional[Dict[str, Any]] = Field(
        None,
        description="Additional context for research"
    )
    tags: Optional[List[str]] = Field(default=[], description="Tags for organization")

    class Config:
        json_schema_extra = {
            "example": {
                "project_id": "123e4567-e89b-12d3-a456-426614174000",
                "research_types": ["competitor", "market"],
                "input_value": "Nike athletic shoes",
                "input_type": "brand_name",
                "context": {"industry": "footwear", "region": "north_america"},
                "tags": ["q1-2025", "competitor-analysis"]
            }
        }


class ResearchResponse(BaseModel):
    """Response for a single research entry."""
    success: bool
    research_id: str
    research_type: ResearchType
    status: ResearchStatus
    title: str
    summary: str
    analysis_data: Dict[str, Any]
    sources_count: int
    confidence_score: float
    processing_time_ms: int
    tools_used: List[str]
    created_at: str


class ListResearchRequest(BaseModel):
    """Request to list research with filters."""
    project_id: Optional[str] = None
    research_types: Optional[List[ResearchType]] = None
    tags: Optional[List[str]] = None
    status: Optional[ResearchStatus] = None
    date_from: Optional[str] = None
    date_to: Optional[str] = None
    search_query: Optional[str] = None
    limit: int = Field(default=50, le=100)
    offset: int = 0
    sort_by: str = "created_at"
    sort_order: str = "desc"


class BatchResearchRequest(BaseModel):
    """Request for batch research."""
    project_id: str
    queries: List[Dict[str, Any]]  # List of {input_value, research_types, context}
    parallel: bool = True


class ResearchSearchRequest(BaseModel):
    """Full-text search request."""
    query: str
    project_id: Optional[str] = None
    research_types: Optional[List[ResearchType]] = None
    limit: int = 20


class AgentInfo(BaseModel):
    """Information about a research agent."""
    type: str
    name: str
    description: str
    tools: List[str]
    output_fields: List[str]
