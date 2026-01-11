"""
Ads Research Agent.

Analyzes competitor ads from Meta (Facebook/Instagram) Ad Library.
"""

from typing import Dict, Any, List

from .base_agent import BaseResearchAgent
from ..models import ResearchType, ResearchInput, ResearchResult, ResearchStatus, ResearchSource
from ..tools import MetaAdsLibraryTool
import time


class AdsResearchAgent(BaseResearchAgent):
    """
    Research agent for analyzing competitor ads.

    Uses Meta Ad Library API to analyze:
    - Competitor ad creatives and messaging
    - Ad spend patterns (where available)
    - Platform distribution
    - Targeting strategies
    - Creative recommendations
    """

    research_type = ResearchType.VIDEO_AD  # Extends video/ad analysis
    agent_name = "Ads Research Agent"
    agent_description = "Analyzes competitor ads from Meta Ad Library (Facebook/Instagram)"
    required_tools = ["google_search", "meta_ads"]
    output_fields = [
        "competitor_ads",
        "creative_analysis",
        "messaging_themes",
        "platform_distribution",
        "targeting_insights",
        "recommendations",
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.meta_ads_tool = MetaAdsLibraryTool()

    def get_research_prompt(self, input: ResearchInput) -> str:
        """Generate the ads research prompt."""
        context_str = ""
        if input.context:
            if "platforms" in input.context:
                context_str += f"Platforms: {', '.join(input.context['platforms'])}\n"
            if "countries" in input.context:
                context_str += f"Countries: {', '.join(input.context['countries'])}\n"
            if "industry" in input.context:
                context_str += f"Industry: {input.context['industry']}\n"

        # Get Meta Ads data if available
        meta_ads_context = ""
        if self.meta_ads_tool.is_configured:
            countries = input.context.get("countries", ["US"]) if input.context else ["US"]
            ads_data = self.meta_ads_tool.analyze_ad_creative(
                search_terms=input.query,
                countries=countries,
            )
            if "error" not in ads_data:
                meta_ads_context = f"""
Meta Ad Library Data:
- Ads Analyzed: {ads_data.get('ads_analyzed', 0)}
- Platform Distribution: {ads_data.get('platform_distribution', {})}
- Sample Headlines: {ads_data.get('creative_patterns', {}).get('headline_styles', [])[:5]}
- Sample CTAs: {ads_data.get('creative_patterns', {}).get('cta_patterns', [])[:5]}
"""

        return f"""
You are an advertising strategist specializing in digital ad analysis and competitive intelligence.

Analyze advertising strategies for the following brand/competitor.
{context_str}
{meta_ads_context}

Your analysis should cover:

1. **Competitor Ads Overview**: Number of active ads, platforms used, ad formats

2. **Creative Analysis**: Visual styles, video vs static, carousel usage, branding elements

3. **Messaging Themes**: Key messages, value propositions, emotional appeals, CTAs

4. **Platform Distribution**: Where they advertise (Facebook, Instagram, etc.) and why

5. **Targeting Insights**: Inferred audience targeting from ad content and placements

6. **Recommendations**: Actionable insights for creating competitive ad campaigns

Focus on patterns and strategies that can inform ad creative development.
"""

    def get_output_schema(self) -> Dict[str, Any]:
        """Return the expected output schema."""
        return {
            "competitor_ads": {
                "total_ads_found": 0,
                "active_ads": 0,
                "platforms": {"facebook": 0, "instagram": 0},
                "ad_formats": ["Image", "Video", "Carousel"],
                "average_ad_age_days": 0,
            },
            "creative_analysis": {
                "visual_styles": ["Style 1", "Style 2"],
                "dominant_colors": ["Color 1", "Color 2"],
                "video_vs_static_ratio": "60% video, 40% static",
                "branding_elements": ["Logo placement", "Brand colors"],
                "creative_quality": "High/Medium/Low",
            },
            "messaging_themes": {
                "primary_messages": ["Message 1", "Message 2"],
                "value_propositions": ["VP 1", "VP 2"],
                "emotional_appeals": ["Appeal 1", "Appeal 2"],
                "call_to_actions": ["CTA 1", "CTA 2"],
                "tone_of_voice": "Professional/Casual/Urgent/etc",
            },
            "platform_distribution": {
                "facebook": {"percentage": 0, "ad_types": ["Feed", "Stories"]},
                "instagram": {"percentage": 0, "ad_types": ["Feed", "Reels"]},
                "audience_network": {"percentage": 0},
                "messenger": {"percentage": 0},
            },
            "targeting_insights": {
                "inferred_demographics": {
                    "age_range": "25-44",
                    "gender": "All",
                    "interests": ["Interest 1", "Interest 2"],
                },
                "geographic_focus": ["Country 1", "Country 2"],
                "behavioral_targeting": ["Behavior 1"],
            },
            "ad_examples": [
                {
                    "headline": "Example headline",
                    "body": "Example body copy",
                    "cta": "Shop Now",
                    "platform": "instagram",
                    "snapshot_url": "URL if available",
                }
            ],
            "recommendations": {
                "creative_opportunities": ["Opportunity 1"],
                "messaging_gaps": ["Gap 1"],
                "platform_strategy": "Recommendation",
                "quick_wins": ["Win 1", "Win 2"],
            },
            "summary": "Executive summary of ads analysis",
        }

    async def research(self, input: ResearchInput) -> ResearchResult:
        """
        Execute ads research combining Meta Ad Library and AI analysis.
        """
        start_time = time.time()
        sources: List[ResearchSource] = []

        # Get countries from context
        countries = ["US"]
        if input.context and "countries" in input.context:
            countries = input.context["countries"]

        # Fetch data from Meta Ad Library
        meta_data = {}
        if self.meta_ads_tool.is_configured:
            # Get competitor ads
            competitor_data = self.meta_ads_tool.search_competitor_ads(
                competitor_name=input.query,
                countries=countries,
            )

            # Get creative analysis
            creative_data = self.meta_ads_tool.analyze_ad_creative(
                search_terms=input.query,
                countries=countries,
            )

            if "error" not in competitor_data:
                meta_data["competitor"] = competitor_data
                # Add sources
                for sample in competitor_data.get("ad_samples", [])[:5]:
                    if sample.get("snapshot_url"):
                        sources.append(ResearchSource(
                            url=sample["snapshot_url"],
                            title=f"Ad by {sample.get('page_name', 'Unknown')}",
                            source_type="meta_ads",
                        ))

            if "error" not in creative_data:
                meta_data["creative"] = creative_data

        # Now use the base agent to get AI analysis
        # This combines Meta data with Google Search grounding
        result = await super().research(input)

        # Merge Meta data into the analysis
        if meta_data:
            result.analysis_data["meta_ads_data"] = meta_data

            # Update sources
            result.sources.extend(sources)

            # Update summary with Meta data
            if "competitor" in meta_data:
                comp = meta_data["competitor"]
                result.summary = f"Found {comp.get('total_ads_found', 0)} ads, " \
                                f"{comp.get('active_ads', 0)} active. " + result.summary

        processing_time = int((time.time() - start_time) * 1000)
        result.processing_time_ms = processing_time

        return result

    def _generate_summary(self, analysis_data: Dict[str, Any]) -> str:
        """Generate a summary from ads analysis."""
        summary_parts = []

        meta = analysis_data.get("meta_ads_data", {})
        if meta:
            comp = meta.get("competitor", {})
            if comp:
                summary_parts.append(f"{comp.get('total_ads_found', 0)} ads found")
                summary_parts.append(f"{comp.get('active_ads', 0)} active")

        messaging = analysis_data.get("messaging_themes", {})
        if messaging.get("primary_messages"):
            summary_parts.append(f"{len(messaging['primary_messages'])} messaging themes")

        recs = analysis_data.get("recommendations", {})
        if recs.get("quick_wins"):
            summary_parts.append(f"{len(recs['quick_wins'])} quick wins identified")

        return ". ".join(summary_parts) + "." if summary_parts else "Ads analysis completed"
