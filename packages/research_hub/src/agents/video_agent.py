"""
Video/Ad Analysis Agent.

Analyzes competitor videos, ad styles, messaging, and creative patterns.
"""

from typing import Dict, Any

from .base_agent import BaseResearchAgent
from ..models import ResearchType, ResearchInput
from ..tools import YouTubeTool


class VideoAdAgent(BaseResearchAgent):
    """
    Research agent for video and ad analysis.

    Analyzes:
    - Video styles and formats
    - Messaging themes and hooks
    - Call-to-action patterns
    - Engagement metrics
    - Creative recommendations
    """

    research_type = ResearchType.VIDEO_AD
    agent_name = "Video/Ad Analysis Agent"
    agent_description = "Analyzes competitor videos, ad styles, and messaging patterns"
    required_tools = ["google_search", "youtube"]
    output_fields = [
        "video_styles",
        "messaging_themes",
        "call_to_actions",
        "engagement_patterns",
        "creative_recommendations",
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.youtube_tool = YouTubeTool()

    def get_research_prompt(self, input: ResearchInput) -> str:
        """Generate the video/ad analysis prompt."""
        context_str = ""
        if input.context:
            if "platform" in input.context:
                context_str += f"Platform Focus: {input.context['platform']}\n"
            if "ad_type" in input.context:
                context_str += f"Ad Type: {input.context['ad_type']}\n"
            if "industry" in input.context:
                context_str += f"Industry: {input.context['industry']}\n"

        # Get YouTube data if available
        youtube_context = ""
        if self.youtube_tool.is_configured:
            trends = self.youtube_tool.analyze_video_trends(input.query, max_videos=10)
            if "error" not in trends:
                youtube_context = f"""
YouTube Research Data:
- Videos Analyzed: {trends.get('videos_analyzed', 0)}
- Average Views: {trends.get('average_views', 0):,}
- Engagement Rate: {trends.get('engagement_rate', 0):.2%}
- Top Tags: {', '.join([t['tag'] for t in trends.get('top_tags', [])[:10]])}
- Sample Titles: {'; '.join(trends.get('sample_titles', [])[:5])}
"""

        return f"""
You are a creative strategist specializing in video advertising and content analysis.

Analyze video content and advertising strategies for the following brand/topic.
{context_str}
{youtube_context}

Your analysis should cover:

1. **Video Styles**: Common formats, lengths, editing styles, visual aesthetics

2. **Messaging Themes**: Key messages, emotional appeals, value propositions

3. **Call-to-Actions**: CTA patterns, placement, effectiveness

4. **Engagement Patterns**: What drives views, likes, comments, shares

5. **Creative Recommendations**: Actionable insights for creating effective video content

Focus on patterns that drive engagement and conversion.
"""

    def get_output_schema(self) -> Dict[str, Any]:
        """Return the expected output schema."""
        return {
            "video_styles": {
                "formats": [
                    {"format": "Format name", "usage": "When/how used", "effectiveness": "High/Medium/Low"}
                ],
                "optimal_lengths": {
                    "short_form": "Under 60 seconds - use case",
                    "medium_form": "1-5 minutes - use case",
                    "long_form": "5+ minutes - use case",
                },
                "visual_aesthetics": ["Style 1", "Style 2"],
                "editing_patterns": ["Pattern 1", "Pattern 2"],
                "audio_elements": ["Music style", "Voice-over approach"],
            },
            "messaging_themes": {
                "primary_messages": ["Message 1", "Message 2"],
                "emotional_hooks": [
                    {"hook": "Description", "emotion": "Fear/Joy/Trust/etc", "effectiveness": "High/Medium/Low"}
                ],
                "value_propositions": ["VP 1", "VP 2"],
                "storytelling_approaches": ["Approach 1", "Approach 2"],
            },
            "call_to_actions": {
                "common_ctas": ["CTA 1", "CTA 2"],
                "placement_patterns": {
                    "beginning": "Description",
                    "middle": "Description",
                    "end": "Description",
                },
                "effective_ctas": [
                    {"cta": "Example", "context": "When used", "why_effective": "Reason"}
                ],
            },
            "engagement_patterns": {
                "high_engagement_factors": ["Factor 1", "Factor 2"],
                "optimal_posting": {
                    "times": ["Time 1", "Time 2"],
                    "frequency": "Recommendation",
                },
                "thumbnail_patterns": ["Pattern 1", "Pattern 2"],
                "title_patterns": ["Pattern 1", "Pattern 2"],
            },
            "creative_recommendations": {
                "for_awareness": ["Recommendation 1"],
                "for_consideration": ["Recommendation 1"],
                "for_conversion": ["Recommendation 1"],
                "quick_wins": ["Quick win 1", "Quick win 2"],
                "avoid": ["What to avoid 1"],
            },
            "summary": "Executive summary of video/ad analysis",
            "top_performing_examples": [
                {"title": "Video title", "url": "URL if available", "why_successful": "Reason"}
            ],
        }

    def _generate_summary(self, analysis_data: Dict[str, Any]) -> str:
        """Generate a summary from video analysis."""
        summary_parts = []

        styles = analysis_data.get("video_styles", {})
        if styles.get("formats"):
            summary_parts.append(f"{len(styles['formats'])} video formats analyzed")

        messaging = analysis_data.get("messaging_themes", {})
        if messaging.get("emotional_hooks"):
            summary_parts.append(f"{len(messaging['emotional_hooks'])} emotional hooks identified")

        recs = analysis_data.get("creative_recommendations", {})
        quick_wins = recs.get("quick_wins", [])
        if quick_wins:
            summary_parts.append(f"{len(quick_wins)} quick wins recommended")

        return ". ".join(summary_parts) + "." if summary_parts else "Video analysis completed"
