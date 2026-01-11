"""
Audience Research Agent.

Analyzes target audience demographics, psychographics, and behavior patterns.
"""

from typing import Dict, Any

from .base_agent import BaseResearchAgent
from ..models import ResearchType, ResearchInput


class AudienceAgent(BaseResearchAgent):
    """
    Research agent for audience analysis.

    Analyzes:
    - Demographics
    - Psychographics
    - Behavior patterns
    - Pain points and motivations
    - Customer personas
    """

    research_type = ResearchType.AUDIENCE
    agent_name = "Audience Research Agent"
    agent_description = "Researches target audience demographics, psychographics, and behavior"
    required_tools = ["google_search", "rag"]
    output_fields = [
        "demographics",
        "psychographics",
        "behavior_patterns",
        "pain_points",
        "personas",
    ]

    def get_research_prompt(self, input: ResearchInput) -> str:
        """Generate the audience research prompt."""
        context_str = ""
        if input.context:
            if "product_category" in input.context:
                context_str += f"Product Category: {input.context['product_category']}\n"
            if "region" in input.context:
                context_str += f"Geographic Focus: {input.context['region']}\n"
            if "existing_customers" in input.context:
                context_str += f"Existing Customer Info: {input.context['existing_customers']}\n"

        return f"""
You are a consumer insights researcher specializing in audience analysis and persona development.

Conduct comprehensive audience research for the following brand/product/topic.
{context_str}

Your analysis should cover:

1. **Demographics**: Age, gender, income, education, location, occupation, family status

2. **Psychographics**: Values, interests, lifestyle, attitudes, opinions, personality traits

3. **Behavior Patterns**: Purchase behavior, media consumption, online behavior, brand interactions

4. **Pain Points & Motivations**: What problems they face, what drives their decisions, purchase triggers

5. **Customer Personas**: 2-3 detailed personas representing key audience segments

Include specific data points and research sources where possible.
"""

    def get_output_schema(self) -> Dict[str, Any]:
        """Return the expected output schema."""
        return {
            "demographics": {
                "age_ranges": [
                    {"range": "18-24", "percentage": "X%", "characteristics": "Key traits"}
                ],
                "gender_distribution": {"male": "X%", "female": "X%", "other": "X%"},
                "income_levels": [
                    {"level": "Low/Middle/High", "range": "$X-$Y", "percentage": "X%"}
                ],
                "education": [
                    {"level": "High school/College/Graduate", "percentage": "X%"}
                ],
                "geography": {
                    "primary_regions": ["Region 1", "Region 2"],
                    "urban_rural_split": {"urban": "X%", "suburban": "X%", "rural": "X%"},
                },
                "occupation_types": ["Type 1", "Type 2"],
                "family_status": [
                    {"status": "Single/Married/Parents", "percentage": "X%"}
                ],
            },
            "psychographics": {
                "core_values": ["Value 1", "Value 2"],
                "interests": ["Interest 1", "Interest 2"],
                "lifestyle": {
                    "activities": ["Activity 1"],
                    "hobbies": ["Hobby 1"],
                    "media_preferences": ["Preference 1"],
                },
                "attitudes": {
                    "toward_brand_category": "Description",
                    "toward_advertising": "Description",
                    "toward_sustainability": "Description",
                },
                "personality_traits": ["Trait 1", "Trait 2"],
            },
            "behavior_patterns": {
                "purchase_behavior": {
                    "frequency": "How often they buy",
                    "average_spend": "$X",
                    "decision_timeline": "Quick/Moderate/Long",
                    "research_behavior": "How they research before buying",
                },
                "media_consumption": {
                    "social_platforms": ["Platform 1 - X hrs/day"],
                    "content_types": ["Type 1", "Type 2"],
                    "peak_usage_times": ["Time 1", "Time 2"],
                },
                "brand_interactions": {
                    "touchpoints": ["Touchpoint 1"],
                    "engagement_preferences": ["Preference 1"],
                    "loyalty_factors": ["Factor 1"],
                },
            },
            "pain_points": {
                "primary_challenges": [
                    {"challenge": "Description", "severity": "High/Medium/Low", "current_solutions": "How they cope"}
                ],
                "unmet_needs": ["Need 1", "Need 2"],
                "frustrations": ["Frustration 1", "Frustration 2"],
            },
            "motivations": {
                "purchase_triggers": ["Trigger 1", "Trigger 2"],
                "emotional_drivers": ["Driver 1", "Driver 2"],
                "rational_drivers": ["Driver 1", "Driver 2"],
                "aspirations": ["Aspiration 1"],
            },
            "personas": [
                {
                    "name": "Persona name",
                    "age": "Age",
                    "occupation": "Job",
                    "bio": "Brief background",
                    "goals": ["Goal 1"],
                    "frustrations": ["Frustration 1"],
                    "preferred_channels": ["Channel 1"],
                    "quote": "A quote that represents them",
                    "percentage_of_audience": "X%",
                }
            ],
            "summary": "Executive summary of audience research",
            "targeting_recommendations": {
                "primary_segment": "Description",
                "secondary_segments": ["Segment 1"],
                "messaging_approach": "How to communicate with this audience",
            },
        }

    def _generate_summary(self, analysis_data: Dict[str, Any]) -> str:
        """Generate a summary from audience analysis."""
        summary_parts = []

        demographics = analysis_data.get("demographics", {})
        if demographics.get("age_ranges"):
            primary_age = demographics["age_ranges"][0] if demographics["age_ranges"] else {}
            if primary_age:
                summary_parts.append(f"Primary age: {primary_age.get('range', 'N/A')}")

        personas = analysis_data.get("personas", [])
        if personas:
            summary_parts.append(f"{len(personas)} personas developed")

        pain_points = analysis_data.get("pain_points", {})
        challenges = pain_points.get("primary_challenges", [])
        if challenges:
            summary_parts.append(f"{len(challenges)} key pain points identified")

        return ". ".join(summary_parts) + "." if summary_parts else "Audience research completed"
