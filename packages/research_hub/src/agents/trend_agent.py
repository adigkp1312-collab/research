"""
Trend Analysis Agent.

Analyzes industry trends, viral content patterns, and emerging topics.
"""

from typing import Dict, Any

from .base_agent import BaseResearchAgent
from ..models import ResearchType, ResearchInput
from ..tools import YouTubeTool


class TrendAgent(BaseResearchAgent):
    """
    Research agent for trend analysis.

    Analyzes:
    - Industry trends
    - Viral content patterns
    - Emerging topics
    - Seasonal patterns
    - Technology and platform shifts
    """

    research_type = ResearchType.TREND
    agent_name = "Trend Analysis Agent"
    agent_description = "Identifies industry trends, viral patterns, and emerging topics"
    required_tools = ["google_search", "youtube"]
    output_fields = [
        "industry_trends",
        "viral_patterns",
        "emerging_topics",
        "seasonal_patterns",
        "technology_trends",
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.youtube_tool = YouTubeTool()

    def get_research_prompt(self, input: ResearchInput) -> str:
        """Generate the trend analysis prompt."""
        context_str = ""
        if input.context:
            if "industry" in input.context:
                context_str += f"Industry: {input.context['industry']}\n"
            if "timeframe" in input.context:
                context_str += f"Timeframe: {input.context['timeframe']}\n"
            if "region" in input.context:
                context_str += f"Region: {input.context['region']}\n"

        # Get YouTube trend data if available
        youtube_context = ""
        if self.youtube_tool.is_configured:
            trends = self.youtube_tool.analyze_video_trends(input.query, max_videos=15)
            if "error" not in trends:
                youtube_context = f"""
YouTube Trend Data:
- Videos Analyzed: {trends.get('videos_analyzed', 0)}
- Total Views: {trends.get('total_views', 0):,}
- Engagement Rate: {trends.get('engagement_rate', 0):.2%}
- Top Tags: {', '.join([t['tag'] for t in trends.get('top_tags', [])[:15]])}
"""

        return f"""
You are a trend analyst specializing in identifying patterns, emerging topics, and cultural shifts.

Conduct a comprehensive trend analysis for the following topic/industry.
{context_str}
{youtube_context}

Your analysis should cover:

1. **Industry Trends**: Macro trends shaping the industry, market shifts, consumer behavior changes

2. **Viral Patterns**: What makes content go viral in this space, successful formats, hooks that work

3. **Emerging Topics**: Rising topics, new conversations, what's gaining momentum

4. **Seasonal Patterns**: Timing considerations, peak periods, event-driven opportunities

5. **Technology & Platform Trends**: New platforms, features, tools changing the landscape

Focus on actionable insights and specific examples.
"""

    def get_output_schema(self) -> Dict[str, Any]:
        """Return the expected output schema."""
        return {
            "industry_trends": {
                "macro_trends": [
                    {
                        "trend": "Trend name",
                        "description": "What's happening",
                        "impact": "High/Medium/Low",
                        "timeframe": "Current/Emerging/Future",
                        "evidence": "Supporting data/examples",
                    }
                ],
                "consumer_behavior_shifts": [
                    {"shift": "Description", "driver": "What's causing it", "implications": "What it means"}
                ],
                "market_dynamics": ["Dynamic 1", "Dynamic 2"],
            },
            "viral_patterns": {
                "content_formats": [
                    {"format": "Format type", "virality_factor": "Why it works", "examples": ["Example 1"]}
                ],
                "emotional_triggers": ["Trigger 1", "Trigger 2"],
                "structural_elements": {
                    "hook_patterns": ["Pattern 1"],
                    "storytelling_structures": ["Structure 1"],
                    "engagement_mechanics": ["Mechanic 1"],
                },
                "success_factors": ["Factor 1", "Factor 2"],
            },
            "emerging_topics": [
                {
                    "topic": "Topic name",
                    "growth_rate": "Rapid/Steady/Early",
                    "related_keywords": ["Keyword 1"],
                    "opportunity_level": "High/Medium/Low",
                    "early_adopters": ["Who's already doing this"],
                }
            ],
            "seasonal_patterns": {
                "peak_periods": [
                    {"period": "Time period", "reason": "Why peak", "content_focus": "What to create"}
                ],
                "event_opportunities": [
                    {"event": "Event name", "date": "When", "relevance": "How to leverage"}
                ],
                "low_periods": ["Period 1 - strategy"],
                "content_calendar_recommendations": ["Recommendation 1"],
            },
            "technology_trends": {
                "platform_shifts": [
                    {"platform": "Name", "change": "What's changing", "adaptation_needed": "What to do"}
                ],
                "new_features": [
                    {"feature": "Name", "platform": "Where", "opportunity": "How to use"}
                ],
                "emerging_tools": ["Tool 1", "Tool 2"],
                "ai_impact": "How AI is affecting this space",
            },
            "content_trends": {
                "trending_formats": ["Format 1", "Format 2"],
                "aesthetic_trends": ["Aesthetic 1", "Aesthetic 2"],
                "audio_trends": ["Music/Sound trend 1"],
                "hashtag_trends": ["#trend1", "#trend2"],
            },
            "summary": "Executive summary of trend analysis",
            "recommendations": {
                "immediate_opportunities": ["Opportunity 1"],
                "trends_to_watch": ["Trend 1"],
                "risks_to_monitor": ["Risk 1"],
            },
        }

    def _generate_summary(self, analysis_data: Dict[str, Any]) -> str:
        """Generate a summary from trend analysis."""
        summary_parts = []

        industry = analysis_data.get("industry_trends", {})
        macro = industry.get("macro_trends", [])
        if macro:
            summary_parts.append(f"{len(macro)} macro trends identified")

        emerging = analysis_data.get("emerging_topics", [])
        if emerging:
            high_opp = [e for e in emerging if e.get("opportunity_level") == "High"]
            summary_parts.append(f"{len(high_opp)} high-opportunity emerging topics")

        viral = analysis_data.get("viral_patterns", {})
        formats = viral.get("content_formats", [])
        if formats:
            summary_parts.append(f"{len(formats)} viral content formats analyzed")

        return ". ".join(summary_parts) + "." if summary_parts else "Trend analysis completed"
