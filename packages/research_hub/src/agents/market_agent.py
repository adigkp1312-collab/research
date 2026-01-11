"""
Market Analysis Agent.

Analyzes market size, trends, opportunities, and key players.
"""

from typing import Dict, Any

from .base_agent import BaseResearchAgent
from ..models import ResearchType, ResearchInput


class MarketAgent(BaseResearchAgent):
    """
    Research agent for market analysis.

    Analyzes:
    - Market size and growth
    - Industry trends
    - Key players and market share
    - Entry barriers
    - Opportunities and threats
    """

    research_type = ResearchType.MARKET
    agent_name = "Market Analysis Agent"
    agent_description = "Analyzes market size, trends, and opportunities"
    required_tools = ["google_search", "rag"]
    output_fields = [
        "market_overview",
        "market_size",
        "growth_trends",
        "key_players",
        "entry_barriers",
        "opportunities",
    ]

    def get_research_prompt(self, input: ResearchInput) -> str:
        """Generate the market analysis prompt."""
        context_str = ""
        if input.context:
            if "region" in input.context:
                context_str += f"Geographic Focus: {input.context['region']}\n"
            if "timeframe" in input.context:
                context_str += f"Timeframe: {input.context['timeframe']}\n"
            if "segment" in input.context:
                context_str += f"Market Segment: {input.context['segment']}\n"

        return f"""
You are a market research analyst specializing in industry analysis and market sizing.

Conduct a comprehensive market analysis for the following industry/market.
{context_str}

Your analysis should cover:

1. **Market Overview**: What is this market, who are the customers, what problems does it solve

2. **Market Size**: TAM (Total Addressable Market), SAM (Serviceable Addressable Market), SOM (Serviceable Obtainable Market) with dollar figures where available

3. **Growth Trends**: Historical growth, projected growth rates, factors driving growth

4. **Key Players**: Market leaders, their market share, recent moves/acquisitions

5. **Entry Barriers**: What makes it difficult to enter this market

6. **Opportunities & Threats**: Market gaps, emerging opportunities, potential threats

Include data sources and be specific with numbers where possible.
"""

    def get_output_schema(self) -> Dict[str, Any]:
        """Return the expected output schema."""
        return {
            "market_overview": {
                "definition": "What is this market",
                "customer_segments": ["Segment 1", "Segment 2"],
                "value_chain": "How value is created and delivered",
                "business_models": ["Model 1", "Model 2"],
            },
            "market_size": {
                "tam": {"value": "$X billion", "description": "Total addressable market"},
                "sam": {"value": "$X billion", "description": "Serviceable addressable market"},
                "som": {"value": "$X million", "description": "Serviceable obtainable market"},
                "year": "2024 or relevant year",
                "sources": ["Source 1"],
            },
            "growth_trends": {
                "historical_cagr": "X%",
                "projected_cagr": "X%",
                "projection_period": "2024-2030",
                "growth_drivers": ["Driver 1", "Driver 2"],
                "growth_inhibitors": ["Inhibitor 1"],
            },
            "key_players": [
                {
                    "name": "Company name",
                    "market_share": "X%",
                    "revenue": "$X",
                    "key_products": ["Product 1"],
                    "recent_news": "Notable recent development",
                }
            ],
            "entry_barriers": {
                "capital_requirements": "High/Medium/Low",
                "regulatory": ["Regulation 1"],
                "technology": ["Tech barrier"],
                "brand_loyalty": "Description",
                "economies_of_scale": "Description",
            },
            "opportunities": [
                {"opportunity": "Description", "potential_impact": "High/Medium/Low", "timeframe": "Short/Medium/Long term"}
            ],
            "threats": [
                {"threat": "Description", "likelihood": "High/Medium/Low", "impact": "High/Medium/Low"}
            ],
            "summary": "Executive summary of market analysis",
            "data_sources": ["Source 1", "Source 2"],
        }

    def _generate_summary(self, analysis_data: Dict[str, Any]) -> str:
        """Generate a summary from market analysis."""
        summary_parts = []

        market_size = analysis_data.get("market_size", {})
        if market_size.get("tam"):
            tam = market_size["tam"]
            if isinstance(tam, dict):
                summary_parts.append(f"TAM: {tam.get('value', 'N/A')}")

        growth = analysis_data.get("growth_trends", {})
        if growth.get("projected_cagr"):
            summary_parts.append(f"Projected CAGR: {growth['projected_cagr']}")

        players = analysis_data.get("key_players", [])
        if players:
            summary_parts.append(f"{len(players)} key players identified")

        opportunities = analysis_data.get("opportunities", [])
        if opportunities:
            summary_parts.append(f"{len(opportunities)} opportunities found")

        return ". ".join(summary_parts) + "." if summary_parts else "Market analysis completed"
