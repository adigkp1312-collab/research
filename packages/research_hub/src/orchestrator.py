"""
Research Orchestrator - Multi-agent coordination for research execution.

Coordinates parallel execution of specialized research agents.
"""

import asyncio
import time
from typing import Dict, Any, Optional, List
from datetime import datetime

from .config import (
    RESEARCH_TIMEOUT_SECONDS,
    MAX_CONCURRENT_AGENTS,
    ENABLE_AGENT_TRACING,
)
from .models import (
    ResearchType,
    ResearchResult,
    ResearchInput,
    ResearchEntry,
    ResearchStatus,
    InputType,
)
from .agents import (
    BaseResearchAgent,
    CompetitorAgent,
    MarketAgent,
    VideoAdAgent,
    SocialMediaAgent,
    AudienceAgent,
    TrendAgent,
)
from .storage import ResearchRepository


class ResearchOrchestrator:
    """
    Orchestrates multiple research agents.

    Features:
    - Parallel execution for independent research types
    - Graceful degradation on agent failures
    - Result aggregation and synthesis
    - Timeout handling
    - Optional storage persistence
    """

    def __init__(self, repository: Optional[ResearchRepository] = None):
        """
        Initialize the orchestrator.

        Args:
            repository: Optional repository for persisting results
        """
        self.repository = repository

        # Initialize all agents
        self.agents: Dict[ResearchType, BaseResearchAgent] = {
            ResearchType.COMPETITOR: CompetitorAgent(),
            ResearchType.MARKET: MarketAgent(),
            ResearchType.VIDEO_AD: VideoAdAgent(),
            ResearchType.SOCIAL_MEDIA: SocialMediaAgent(),
            ResearchType.AUDIENCE: AudienceAgent(),
            ResearchType.TREND: TrendAgent(),
        }

    def get_available_agents(self) -> List[Dict[str, Any]]:
        """Get information about all available agents."""
        return [agent.get_agent_info() for agent in self.agents.values()]

    def detect_input_type(self, query: str) -> InputType:
        """
        Auto-detect the input type from the query.

        Args:
            query: The input query string

        Returns:
            Detected InputType
        """
        query = query.strip().lower()

        # Check for URLs
        if query.startswith(('http://', 'https://', 'www.')):
            if 'youtube.com' in query or 'youtu.be' in query:
                return InputType.VIDEO_URL
            return InputType.URL

        # Check for topic patterns
        if any(word in query for word in ['trend', 'trends', 'market for', 'industry']):
            return InputType.TOPIC

        # Default to text/brand name
        # If it's a short phrase (likely a brand), use BRAND_NAME
        if len(query.split()) <= 3:
            return InputType.BRAND_NAME

        return InputType.TEXT

    async def execute_research(
        self,
        project_id: str,
        user_id: str,
        research_types: List[ResearchType],
        query: str,
        input_type: Optional[InputType] = None,
        context: Optional[Dict[str, Any]] = None,
        timeout_seconds: Optional[int] = None,
        save_results: bool = True,
    ) -> Dict[ResearchType, ResearchResult]:
        """
        Execute research across specified agent types.

        Args:
            project_id: Project UUID for storage
            user_id: User UUID for storage
            research_types: List of research types to execute
            query: The research query
            input_type: Optional input type (auto-detected if not provided)
            context: Optional additional context
            timeout_seconds: Optional timeout override
            save_results: Whether to save results to storage

        Returns:
            Dict mapping research_type to ResearchResult
        """
        timeout = timeout_seconds or RESEARCH_TIMEOUT_SECONDS

        # Auto-detect input type if not provided
        if input_type is None:
            input_type = self.detect_input_type(query)

        # Create input object
        input_data = ResearchInput(
            query=query,
            input_type=input_type,
            context=context,
        )

        # Execute research in parallel with concurrency limit
        results = await self._execute_parallel(
            research_types=research_types,
            input_data=input_data,
            timeout=timeout,
        )

        # Save results if repository is configured
        if save_results and self.repository and self.repository.is_configured:
            await self._save_results(
                project_id=project_id,
                user_id=user_id,
                input_data=input_data,
                results=results,
            )

        return results

    async def execute_single(
        self,
        research_type: ResearchType,
        query: str,
        input_type: Optional[InputType] = None,
        context: Optional[Dict[str, Any]] = None,
        timeout_seconds: Optional[int] = None,
    ) -> ResearchResult:
        """
        Execute a single research type.

        Args:
            research_type: The type of research to execute
            query: The research query
            input_type: Optional input type
            context: Optional additional context
            timeout_seconds: Optional timeout

        Returns:
            ResearchResult
        """
        timeout = timeout_seconds or RESEARCH_TIMEOUT_SECONDS

        if input_type is None:
            input_type = self.detect_input_type(query)

        input_data = ResearchInput(
            query=query,
            input_type=input_type,
            context=context,
        )

        agent = self.agents.get(research_type)
        if not agent:
            return self._create_error_result(
                research_type,
                f"Unknown research type: {research_type}"
            )

        try:
            result = await asyncio.wait_for(
                agent.research(input_data),
                timeout=timeout,
            )
            return result
        except asyncio.TimeoutError:
            return self._create_error_result(research_type, "Research timed out")
        except Exception as e:
            return self._create_error_result(research_type, str(e))

    async def _execute_parallel(
        self,
        research_types: List[ResearchType],
        input_data: ResearchInput,
        timeout: int,
    ) -> Dict[ResearchType, ResearchResult]:
        """
        Execute multiple research types in parallel with concurrency limit.
        """
        results: Dict[ResearchType, ResearchResult] = {}
        semaphore = asyncio.Semaphore(MAX_CONCURRENT_AGENTS)

        async def run_with_semaphore(research_type: ResearchType):
            async with semaphore:
                agent = self.agents.get(research_type)
                if not agent:
                    return research_type, self._create_error_result(
                        research_type,
                        f"Unknown research type: {research_type}"
                    )

                try:
                    result = await asyncio.wait_for(
                        agent.research(input_data),
                        timeout=timeout,
                    )
                    return research_type, result
                except asyncio.TimeoutError:
                    return research_type, self._create_error_result(
                        research_type,
                        "Research timed out"
                    )
                except Exception as e:
                    return research_type, self._create_error_result(
                        research_type,
                        str(e)
                    )

        # Create tasks for all research types
        tasks = [run_with_semaphore(rt) for rt in research_types]

        # Execute all tasks
        completed = await asyncio.gather(*tasks, return_exceptions=True)

        # Process results
        for item in completed:
            if isinstance(item, Exception):
                # This shouldn't happen due to our error handling, but just in case
                continue
            research_type, result = item
            results[research_type] = result

        return results

    async def _save_results(
        self,
        project_id: str,
        user_id: str,
        input_data: ResearchInput,
        results: Dict[ResearchType, ResearchResult],
    ):
        """Save research results to storage."""
        for research_type, result in results.items():
            try:
                title = self._generate_title(input_data.query, research_type, result)

                await self.repository.create(
                    project_id=project_id,
                    user_id=user_id,
                    research_type=research_type,
                    input=input_data,
                    result=result,
                    title=title,
                )
            except Exception as e:
                # Log error but don't fail the entire operation
                print(f"Failed to save {research_type.value} result: {e}")

    def _generate_title(
        self,
        query: str,
        research_type: ResearchType,
        result: ResearchResult,
    ) -> str:
        """Generate a title for the research entry."""
        type_labels = {
            ResearchType.COMPETITOR: "Competitor Analysis",
            ResearchType.MARKET: "Market Analysis",
            ResearchType.VIDEO_AD: "Video/Ad Analysis",
            ResearchType.SOCIAL_MEDIA: "Social Media Intel",
            ResearchType.AUDIENCE: "Audience Research",
            ResearchType.TREND: "Trend Analysis",
        }

        type_label = type_labels.get(research_type, "Research")

        # Try to extract a name from the analysis
        analysis = result.analysis_data
        name = None

        if "competitors" in analysis and analysis["competitors"]:
            first_comp = analysis["competitors"][0]
            if isinstance(first_comp, dict):
                name = first_comp.get("name")

        if not name and "market_overview" in analysis:
            overview = analysis["market_overview"]
            if isinstance(overview, dict):
                name = overview.get("definition", "")[:50]

        if not name:
            # Use the query, truncated
            name = query[:50] + "..." if len(query) > 50 else query

        return f"{type_label}: {name}"

    def _create_error_result(
        self,
        research_type: ResearchType,
        error_message: str,
    ) -> ResearchResult:
        """Create an error result for failed research."""
        return ResearchResult(
            research_type=research_type,
            analysis_data={"error": error_message},
            summary=f"Research failed: {error_message}",
            sources=[],
            confidence_score=0.0,
            tools_used=[],
            processing_time_ms=0,
            status=ResearchStatus.FAILED,
            error_message=error_message,
        )

    async def synthesize_results(
        self,
        results: Dict[ResearchType, ResearchResult],
    ) -> Dict[str, Any]:
        """
        Synthesize multiple research results into a combined summary.

        Args:
            results: Dict of research results

        Returns:
            Synthesized summary
        """
        synthesis = {
            "total_research_types": len(results),
            "successful": 0,
            "failed": 0,
            "total_sources": 0,
            "average_confidence": 0.0,
            "total_processing_time_ms": 0,
            "key_findings": [],
            "by_type": {},
        }

        confidence_sum = 0

        for research_type, result in results.items():
            if result.status == ResearchStatus.COMPLETED:
                synthesis["successful"] += 1
                confidence_sum += result.confidence_score
            else:
                synthesis["failed"] += 1

            synthesis["total_sources"] += len(result.sources)
            synthesis["total_processing_time_ms"] += result.processing_time_ms

            synthesis["by_type"][research_type.value] = {
                "status": result.status.value,
                "summary": result.summary,
                "confidence": result.confidence_score,
                "sources_count": len(result.sources),
            }

            # Extract key findings
            if result.summary and result.status == ResearchStatus.COMPLETED:
                synthesis["key_findings"].append({
                    "type": research_type.value,
                    "finding": result.summary,
                })

        if synthesis["successful"] > 0:
            synthesis["average_confidence"] = confidence_sum / synthesis["successful"]

        return synthesis


# Convenience function
async def run_research(
    query: str,
    research_types: List[ResearchType],
    project_id: str = "default",
    user_id: str = "default",
    context: Optional[Dict[str, Any]] = None,
) -> Dict[ResearchType, ResearchResult]:
    """
    Convenience function to run research.

    Args:
        query: Research query
        research_types: Types of research to run
        project_id: Project ID
        user_id: User ID
        context: Optional context

    Returns:
        Research results
    """
    orchestrator = ResearchOrchestrator()
    return await orchestrator.execute_research(
        project_id=project_id,
        user_id=user_id,
        research_types=research_types,
        query=query,
        context=context,
        save_results=False,  # Don't save by default in convenience function
    )
