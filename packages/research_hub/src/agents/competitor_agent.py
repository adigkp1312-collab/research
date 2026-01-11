"""
Competitor Research Agent.

Analyzes competitor landscape, positioning, strengths, and strategies.
"""

from typing import Dict, Any

from .base_agent import BaseResearchAgent
from ..models import ResearchType, ResearchInput


class CompetitorAgent(BaseResearchAgent):
    """
    Research agent for competitor analysis.

    Analyzes:
    - Direct and indirect competitors
    - Market positioning
    - Strengths and weaknesses
    - Pricing strategies
    - Marketing channels and messaging
    """

    research_type = ResearchType.COMPETITOR
    agent_name = "Competitor Research Agent"
    agent_description = "Analyzes competitor landscape, positioning, and strategies"
    required_tools = ["google_search", "rag"]
    output_fields = [
        "competitors",
        "positioning_analysis",
        "strengths_weaknesses",
        "pricing_analysis",
        "marketing_channels",
        "key_differentiators",
    ]

    def get_research_prompt(self, input: ResearchInput) -> str:
        """Generate the competitor research prompt."""
        context_str = ""
        if input.context:
            if "industry" in input.context:
                context_str += f"Industry: {input.context['industry']}\n"
            if "region" in input.context:
                context_str += f"Region: {input.context['region']}\n"
            if "target_audience" in input.context:
                context_str += f"Target Audience: {input.context['target_audience']}\n"

        return f"""
You are a competitive intelligence analyst specializing in market research.

Conduct a comprehensive competitor analysis for the following brand/product/company.
{context_str}

Your analysis should cover:

1. **Competitor Identification**: Find direct competitors (same product/service) and indirect competitors (alternative solutions)

2. **Positioning Analysis**: How each competitor positions themselves in the market

3. **Strengths & Weaknesses**: SWOT-style analysis for each major competitor

4. **Pricing Strategy**: Pricing models, tiers, and value propositions

5. **Marketing Channels**: Where competitors advertise and promote (social media, search, TV, influencers, etc.)

6. **Key Differentiators**: What makes each competitor unique

Be thorough and include specific examples where possible.
"""

    def get_output_schema(self) -> Dict[str, Any]:
        """Return the expected output schema."""
        return {
            "competitors": [
                {
                    "name": "Competitor name",
                    "type": "direct or indirect",
                    "description": "Brief description",
                    "website": "URL if known",
                    "market_share": "Estimated market share or position",
                }
            ],
            "positioning_analysis": {
                "market_segments": ["Segment 1", "Segment 2"],
                "positioning_map": [
                    {"competitor": "Name", "position": "Premium/Budget/Mid-tier", "focus": "Key focus area"}
                ],
                "gaps": ["Identified market gaps"],
            },
            "strengths_weaknesses": [
                {
                    "competitor": "Name",
                    "strengths": ["Strength 1", "Strength 2"],
                    "weaknesses": ["Weakness 1", "Weakness 2"],
                }
            ],
            "pricing_analysis": {
                "pricing_models": ["Model 1", "Model 2"],
                "price_ranges": [
                    {"competitor": "Name", "low": "Price", "high": "Price", "model": "Subscription/One-time/etc"}
                ],
                "value_propositions": ["VP 1", "VP 2"],
            },
            "marketing_channels": {
                "primary_channels": ["Channel 1", "Channel 2"],
                "by_competitor": [
                    {"competitor": "Name", "channels": ["Channel 1"], "notable_campaigns": "Description"}
                ],
            },
            "key_differentiators": [
                {"competitor": "Name", "differentiators": ["Differentiator 1", "Differentiator 2"]}
            ],
            "summary": "Executive summary of competitive landscape",
            "recommendations": ["Strategic recommendation 1", "Recommendation 2"],
        }

    def _generate_summary(self, analysis_data: Dict[str, Any]) -> str:
        """Generate a summary from competitor analysis."""
        competitors = analysis_data.get("competitors", [])
        competitor_count = len(competitors) if isinstance(competitors, list) else 0

        summary_parts = [f"Identified {competitor_count} competitors"]

        if "positioning_analysis" in analysis_data:
            gaps = analysis_data["positioning_analysis"].get("gaps", [])
            if gaps:
                summary_parts.append(f"{len(gaps)} market gaps identified")

        if "recommendations" in analysis_data:
            recs = analysis_data["recommendations"]
            if recs:
                summary_parts.append(f"{len(recs)} strategic recommendations")

        return ". ".join(summary_parts) + "."
