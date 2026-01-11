"""
Google Search Grounding Tool for Research Hub.

Provides Google Search grounding capability using Vertex AI.
"""

import os
import json
from typing import Dict, Any, Optional, List
from datetime import datetime

import vertexai
from vertexai.generative_models import GenerativeModel, Tool
from vertexai.preview.generative_models import grounding

from ..config import GOOGLE_CLOUD_PROJECT, VERTEX_AI_LOCATION, DEFAULT_MODEL


class GoogleSearchTool:
    """
    Google Search grounding tool using Vertex AI.

    Enables real-time internet search capabilities for research agents.
    """

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

    @property
    def is_configured(self) -> bool:
        """Check if the tool is properly configured."""
        return bool(self.project_id)

    def _init_vertex_ai(self):
        """Initialize Vertex AI SDK."""
        if not self._initialized and self.project_id:
            vertexai.init(project=self.project_id, location=self.location)
            self._initialized = True

    def _get_model(self) -> GenerativeModel:
        """Get or create the GenerativeModel with Google Search tool."""
        if self._model is None:
            self._init_vertex_ai()

            google_search_tool = Tool.from_google_search_retrieval(
                grounding.GoogleSearchRetrieval()
            )

            self._model = GenerativeModel(
                self.model_name,
                tools=[google_search_tool],
            )

        return self._model

    def search(
        self,
        query: str,
        context: Optional[str] = None,
        output_schema: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Perform a search with Google Search grounding.

        Args:
            query: The search query
            context: Optional additional context for the search
            output_schema: Optional JSON schema for structured output

        Returns:
            Search results with sources
        """
        if not self.is_configured:
            return {"error": "Google Search tool not configured", "results": []}

        model = self._get_model()

        # Build prompt
        prompt = self._build_search_prompt(query, context, output_schema)

        try:
            response = model.generate_content(prompt)
            result = self._parse_response(response)

            # Extract grounding metadata for sources
            sources = self._extract_sources(response)

            return {
                "query": query,
                "results": result,
                "sources": sources,
                "searched_at": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            return {
                "query": query,
                "error": str(e),
                "results": {},
                "sources": [],
            }

    def research(
        self,
        query: str,
        research_prompt: str,
        output_schema: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Perform research with a custom prompt and expected output schema.

        Args:
            query: The subject to research
            research_prompt: Detailed prompt with instructions
            output_schema: Expected JSON output schema

        Returns:
            Structured research results
        """
        if not self.is_configured:
            return {"error": "Google Search tool not configured"}

        model = self._get_model()

        # Build the full prompt with schema
        schema_str = json.dumps(output_schema, indent=2)
        full_prompt = f"""
{research_prompt}

Subject: {query}

Return your findings as a JSON object with this exact structure:
{schema_str}

Only return the JSON object, no additional text or markdown code blocks.
Be thorough, accurate, and include real, verifiable information.
"""

        try:
            response = model.generate_content(full_prompt)
            result = self._parse_json_response(response.text)
            sources = self._extract_sources(response)

            return {
                "query": query,
                "analysis": result,
                "sources": sources,
                "searched_at": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            return {
                "query": query,
                "error": str(e),
                "analysis": {},
                "sources": [],
            }

    def _build_search_prompt(
        self,
        query: str,
        context: Optional[str],
        output_schema: Optional[Dict[str, Any]],
    ) -> str:
        """Build the search prompt."""
        prompt_parts = [f"Search for information about: {query}"]

        if context:
            prompt_parts.append(f"\nAdditional context: {context}")

        if output_schema:
            schema_str = json.dumps(output_schema, indent=2)
            prompt_parts.append(f"\nReturn results as JSON with this structure:\n{schema_str}")
        else:
            prompt_parts.append("\nProvide a comprehensive summary of the findings.")

        return "\n".join(prompt_parts)

    def _parse_response(self, response) -> Dict[str, Any]:
        """Parse the model response."""
        try:
            text = response.text
            return self._parse_json_response(text)
        except Exception:
            return {"raw_response": response.text if hasattr(response, 'text') else str(response)}

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
                # Return as raw text if not JSON
                return {"raw_response": response_text}

    def _extract_sources(self, response) -> List[Dict[str, str]]:
        """Extract sources from grounding metadata."""
        sources = []

        try:
            # Access grounding metadata from the response
            if hasattr(response, 'candidates') and response.candidates:
                candidate = response.candidates[0]
                if hasattr(candidate, 'grounding_metadata'):
                    metadata = candidate.grounding_metadata
                    if hasattr(metadata, 'grounding_chunks'):
                        for chunk in metadata.grounding_chunks:
                            if hasattr(chunk, 'web'):
                                sources.append({
                                    "url": chunk.web.uri if hasattr(chunk.web, 'uri') else "",
                                    "title": chunk.web.title if hasattr(chunk.web, 'title') else "",
                                    "source_type": "web",
                                })
        except Exception:
            # Grounding metadata extraction is best-effort
            pass

        return sources


# Factory function
def create_google_search_tool(
    model_name: str = None,
    project_id: str = None,
    location: str = None,
) -> GoogleSearchTool:
    """Create a Google Search tool instance."""
    return GoogleSearchTool(
        model_name=model_name,
        project_id=project_id,
        location=location,
    )
