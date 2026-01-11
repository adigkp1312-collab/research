"""
Social Media Intelligence Agent.

Analyzes brand presence, engagement, influencers, and social trends.
"""

from typing import Dict, Any

from .base_agent import BaseResearchAgent
from ..models import ResearchType, ResearchInput


class SocialMediaAgent(BaseResearchAgent):
    """
    Research agent for social media intelligence.

    Analyzes:
    - Brand social presence
    - Engagement metrics and patterns
    - Influencer landscape
    - Content performance
    - Sentiment and trends
    """

    research_type = ResearchType.SOCIAL_MEDIA
    agent_name = "Social Media Intelligence Agent"
    agent_description = "Analyzes brand social presence, engagement, and influencer landscape"
    required_tools = ["google_search", "youtube"]
    output_fields = [
        "brand_presence",
        "engagement_analysis",
        "influencer_landscape",
        "content_performance",
        "sentiment_analysis",
    ]

    def get_research_prompt(self, input: ResearchInput) -> str:
        """Generate the social media intelligence prompt."""
        context_str = ""
        if input.context:
            if "platforms" in input.context:
                context_str += f"Platforms to Focus: {', '.join(input.context['platforms'])}\n"
            if "competitors" in input.context:
                context_str += f"Competitors to Include: {', '.join(input.context['competitors'])}\n"
            if "timeframe" in input.context:
                context_str += f"Timeframe: {input.context['timeframe']}\n"

        return f"""
You are a social media analyst specializing in brand intelligence and digital presence analysis.

Conduct a comprehensive social media analysis for the following brand/topic.
{context_str}

Your analysis should cover:

1. **Brand Presence**: Social media profiles, follower counts, posting frequency across platforms

2. **Engagement Analysis**: Engagement rates, best performing content, engagement patterns

3. **Influencer Landscape**: Relevant influencers in the space, partnership opportunities, micro vs macro influencers

4. **Content Performance**: Types of content that perform well, optimal posting times, content themes

5. **Sentiment Analysis**: Brand sentiment, common praise/complaints, sentiment trends

Include specific metrics and examples where possible.
"""

    def get_output_schema(self) -> Dict[str, Any]:
        """Return the expected output schema."""
        return {
            "brand_presence": {
                "platforms": [
                    {
                        "platform": "Instagram/TikTok/YouTube/etc",
                        "handle": "@handle",
                        "followers": "Count or estimate",
                        "posting_frequency": "Posts per week",
                        "profile_strength": "Strong/Medium/Weak",
                    }
                ],
                "total_reach": "Estimated total reach",
                "primary_platform": "Main platform focus",
                "growth_trend": "Growing/Stable/Declining",
            },
            "engagement_analysis": {
                "average_engagement_rate": "X%",
                "by_platform": [
                    {"platform": "Name", "engagement_rate": "X%", "benchmark": "Above/At/Below industry"}
                ],
                "best_performing_content": [
                    {"type": "Content type", "engagement": "Metrics", "example": "Description"}
                ],
                "engagement_patterns": {
                    "best_times": ["Time 1", "Time 2"],
                    "best_days": ["Day 1", "Day 2"],
                    "content_frequency_impact": "Description",
                },
            },
            "influencer_landscape": {
                "macro_influencers": [
                    {"name": "Name", "platform": "Platform", "followers": "Count", "relevance": "High/Medium/Low"}
                ],
                "micro_influencers": [
                    {"name": "Name", "platform": "Platform", "followers": "Count", "niche": "Niche area"}
                ],
                "partnership_opportunities": [
                    {"influencer": "Name", "fit_score": "High/Medium/Low", "reasoning": "Why good fit"}
                ],
                "influencer_trends": ["Trend 1", "Trend 2"],
            },
            "content_performance": {
                "top_content_types": [
                    {"type": "Type", "performance": "High/Medium/Low", "examples": ["Example 1"]}
                ],
                "content_themes": ["Theme 1", "Theme 2"],
                "hashtag_strategy": {
                    "branded_hashtags": ["#hashtag1"],
                    "trending_hashtags": ["#hashtag1"],
                    "niche_hashtags": ["#hashtag1"],
                },
                "content_recommendations": ["Recommendation 1"],
            },
            "sentiment_analysis": {
                "overall_sentiment": "Positive/Neutral/Negative",
                "sentiment_score": "X/10",
                "positive_themes": ["Theme 1", "Theme 2"],
                "negative_themes": ["Theme 1", "Theme 2"],
                "notable_mentions": [
                    {"source": "Source", "sentiment": "Positive/Negative", "summary": "What was said"}
                ],
                "reputation_risks": ["Risk 1"],
            },
            "summary": "Executive summary of social media intelligence",
            "recommendations": {
                "immediate_actions": ["Action 1"],
                "strategic_initiatives": ["Initiative 1"],
                "platform_priorities": ["Priority 1"],
            },
        }

    def _generate_summary(self, analysis_data: Dict[str, Any]) -> str:
        """Generate a summary from social analysis."""
        summary_parts = []

        presence = analysis_data.get("brand_presence", {})
        platforms = presence.get("platforms", [])
        if platforms:
            summary_parts.append(f"Presence on {len(platforms)} platforms")

        sentiment = analysis_data.get("sentiment_analysis", {})
        if sentiment.get("overall_sentiment"):
            summary_parts.append(f"Overall sentiment: {sentiment['overall_sentiment']}")

        influencers = analysis_data.get("influencer_landscape", {})
        macro = influencers.get("macro_influencers", [])
        micro = influencers.get("micro_influencers", [])
        total_influencers = len(macro) + len(micro)
        if total_influencers > 0:
            summary_parts.append(f"{total_influencers} relevant influencers identified")

        return ". ".join(summary_parts) + "." if summary_parts else "Social media analysis completed"
