"""
Base Research Agent - Abstract base class for all research agents.

Provides common functionality for Vertex AI integration and research execution.
"""

import os
import json
import time
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from datetime import datetime

import vertexai
from vertexai.generative_models import GenerativeModel, Tool
from vertexai.preview.generative_models import grounding

from ..config import (
    GOOGLE_CLOUD_PROJECT,
    VERTEX_AI_LOCATION,
    DEFAULT_MODEL,
    ENABLE_AGENT_TRACING,
)
from ..models import (
    ResearchType,
    ResearchResult,
    ResearchInput,
    ResearchSource,
    ResearchStatus,
)
from ..tools import GoogleSearchTool, RAGTool


class BaseResearchAgent(ABC):
    """
    Abstract base class for research agents.

    Each specialized agent inherits from this and implements:
    - get_research_prompt(): Returns the research prompt template
    - get_output_schema(): Returns the expected output schema
    - parse_analysis(): Parses the model response into structured data
    """

    # Subclasses must define these
    research_type: ResearchType
    agent_name: str
    agent_description: str
    required_tools: List[str] = ["google_search"]
    output_fields: List[str] = []

    def __init__(
        self,
        model_name: str = None,
        project_id: str = None,
        location: str = None,
    ):
        self.model_name = model_name or DEFAULT_MODEL
        self.project_id = project_id or GOOGLE_CLOUD_PROJECT
        self.location = location or VERTEX_AI_LOCATION
        self._model: Optional[GenerativeModel] = None
        self._initialized = False

        # Initialize tools
        self.google_search = GoogleSearchTool(
            model_name=self.model_name,
            project_id=self.project_id,
            location=self.location,
        )
        self.rag_tool = RAGTool()

    @property
    def is_configured(self) -> bool:
        """Check if the agent is properly configured."""
        return bool(self.project_id)

    def _init_vertex_ai(self):
        """Initialize Vertex AI SDK."""
        if not self._initialized and self.project_id:
            vertexai.init(project=self.project_id, location=self.location)
            self._initialized = True

    def _get_model(self) -> GenerativeModel:
        """Get or create the GenerativeModel with required tools."""
        if self._model is None:
            self._init_vertex_ai()

            tools = []

            # Add Google Search if required
            if "google_search" in self.required_tools:
                google_search_tool = Tool.from_google_search_retrieval(
                    grounding.GoogleSearchRetrieval()
                )
                tools.append(google_search_tool)

            self._model = GenerativeModel(
                self.model_name,
                tools=tools if tools else None,
            )

        return self._model

    @abstractmethod
    def get_research_prompt(self, input: ResearchInput) -> str:
        """
        Generate the research prompt for this agent type.

        Args:
            input: Research input with query and context

        Returns:
            Formatted prompt string
        """
        pass

    @abstractmethod
    def get_output_schema(self) -> Dict[str, Any]:
        """
        Return the expected output schema for this agent.

        Returns:
            JSON schema as dictionary
        """
        pass

    def parse_analysis(self, response_text: str) -> Dict[str, Any]:
        """
        Parse the model response into structured data.

        Override in subclass for custom parsing.

        Args:
            response_text: Raw model response text

        Returns:
            Parsed analysis data
        """
        return self._parse_json_response(response_text)

    def _parse_json_response(self, response_text: str) -> Dict[str, Any]:
        """Parse JSON from model response, handling markdown code blocks."""
        try:
            return json.loads(response_text)
        except json.JSONDecodeError:
            text = response_text.strip()

            # Remove markdown code blocks
            if text.startswith("```json"):
                text = text[7:]
            elif text.startswith("```"):
                text = text[3:]
            if text.endswith("```"):
                text = text[:-3]

            try:
                return json.loads(text.strip())
            except json.JSONDecodeError:
                return {"raw_response": response_text, "parse_error": True}

    def _extract_sources(self, response) -> List[ResearchSource]:
        """Extract sources from grounding metadata."""
        sources = []

        try:
            if hasattr(response, 'candidates') and response.candidates:
                candidate = response.candidates[0]
                if hasattr(candidate, 'grounding_metadata'):
                    metadata = candidate.grounding_metadata
                    if hasattr(metadata, 'grounding_chunks'):
                        for chunk in metadata.grounding_chunks:
                            if hasattr(chunk, 'web'):
                                sources.append(ResearchSource(
                                    url=chunk.web.uri if hasattr(chunk.web, 'uri') else "",
                                    title=chunk.web.title if hasattr(chunk.web, 'title') else "",
                                    source_type="web",
                                ))
        except Exception:
            pass

        return sources

    def _build_full_prompt(self, input: ResearchInput) -> str:
        """Build the complete prompt with schema and RAG context."""
        base_prompt = self.get_research_prompt(input)
        schema = self.get_output_schema()
        schema_str = json.dumps(schema, indent=2)

        # Add RAG context if available
        rag_context = ""
        if "rag" in self.required_tools and self.rag_tool.is_configured:
            rag_context = self.rag_tool.get_context(input.query, max_length=2000)
            if rag_context:
                rag_context = f"\n{rag_context}\n---\n"

        # Build full prompt
        prompt = f"""
{rag_context}
{base_prompt}

Subject/Query: {input.query}
{"Context: " + json.dumps(input.context) if input.context else ""}

IMPORTANT: Return your analysis as a valid JSON object with exactly this structure:
{schema_str}

Requirements:
- Be thorough and accurate
- Include real, verifiable information from your search
- Only return the JSON object, no additional text or markdown code blocks
- If you cannot find information for a field, use null or an empty array
"""

        return prompt

    def _calculate_confidence(self, analysis_data: Dict[str, Any]) -> float:
        """
        Calculate confidence score based on data completeness.

        Args:
            analysis_data: Parsed analysis data

        Returns:
            Confidence score between 0 and 1
        """
        if "parse_error" in analysis_data:
            return 0.0

        schema = self.get_output_schema()
        if not schema:
            return 0.5

        total_fields = len(schema)
        filled_fields = 0

        for key in schema:
            value = analysis_data.get(key)
            if value is not None:
                if isinstance(value, (list, dict)):
                    if len(value) > 0:
                        filled_fields += 1
                elif isinstance(value, str):
                    if value.strip():
                        filled_fields += 1
                else:
                    filled_fields += 1

        return filled_fields / total_fields if total_fields > 0 else 0.0

    async def research(self, input: ResearchInput) -> ResearchResult:
        """
        Execute research for this agent type.

        Args:
            input: Research input with query and context

        Returns:
            ResearchResult with analysis data and metadata
        """
        start_time = time.time()
        agent_trace = {"steps": []} if ENABLE_AGENT_TRACING else None

        if not self.is_configured:
            return ResearchResult(
                research_type=self.research_type,
                analysis_data={"error": "Agent not configured"},
                summary="Research failed: Agent not properly configured",
                sources=[],
                confidence_score=0.0,
                tools_used=[],
                processing_time_ms=0,
                status=ResearchStatus.FAILED,
                error_message="GOOGLE_CLOUD_PROJECT not set",
            )

        try:
            # Build prompt
            prompt = self._build_full_prompt(input)

            if agent_trace:
                agent_trace["steps"].append({
                    "step": "build_prompt",
                    "timestamp": datetime.utcnow().isoformat(),
                    "prompt_length": len(prompt),
                })

            # Get model and generate
            model = self._get_model()
            response = model.generate_content(prompt)

            if agent_trace:
                agent_trace["steps"].append({
                    "step": "model_generate",
                    "timestamp": datetime.utcnow().isoformat(),
                    "response_length": len(response.text) if response.text else 0,
                })

            # Parse response
            analysis_data = self.parse_analysis(response.text)

            # Extract sources
            sources = self._extract_sources(response)

            # Add any sources from the analysis data
            if "sources" in analysis_data and isinstance(analysis_data["sources"], list):
                for src in analysis_data["sources"]:
                    if isinstance(src, dict) and "url" in src:
                        sources.append(ResearchSource(
                            url=src.get("url", ""),
                            title=src.get("title", ""),
                            source_type="web",
                        ))

            # Calculate confidence
            confidence = self._calculate_confidence(analysis_data)

            # Generate summary
            summary = analysis_data.get("summary", "")
            if not summary:
                summary = self._generate_summary(analysis_data)

            processing_time = int((time.time() - start_time) * 1000)

            if agent_trace:
                agent_trace["steps"].append({
                    "step": "complete",
                    "timestamp": datetime.utcnow().isoformat(),
                    "processing_time_ms": processing_time,
                })

            return ResearchResult(
                research_type=self.research_type,
                analysis_data=analysis_data,
                summary=summary,
                sources=sources,
                confidence_score=confidence,
                tools_used=self.required_tools,
                processing_time_ms=processing_time,
                status=ResearchStatus.COMPLETED,
                agent_trace=agent_trace,
            )

        except Exception as e:
            processing_time = int((time.time() - start_time) * 1000)

            return ResearchResult(
                research_type=self.research_type,
                analysis_data={"error": str(e)},
                summary=f"Research failed: {str(e)}",
                sources=[],
                confidence_score=0.0,
                tools_used=self.required_tools,
                processing_time_ms=processing_time,
                status=ResearchStatus.FAILED,
                error_message=str(e),
                agent_trace=agent_trace,
            )

    def _generate_summary(self, analysis_data: Dict[str, Any]) -> str:
        """
        Generate a summary from analysis data.

        Override in subclass for custom summary generation.
        """
        # Default implementation - extract key points
        summary_parts = []

        for key in self.output_fields[:3]:  # Top 3 fields
            value = analysis_data.get(key)
            if value:
                if isinstance(value, str):
                    summary_parts.append(f"{key}: {value[:100]}")
                elif isinstance(value, list) and len(value) > 0:
                    summary_parts.append(f"{key}: {len(value)} items found")

        return "; ".join(summary_parts) if summary_parts else "Analysis completed"

    def get_agent_info(self) -> Dict[str, Any]:
        """Get information about this agent."""
        return {
            "type": self.research_type.value,
            "name": self.agent_name,
            "description": self.agent_description,
            "tools": self.required_tools,
            "output_fields": self.output_fields,
            "configured": self.is_configured,
        }
