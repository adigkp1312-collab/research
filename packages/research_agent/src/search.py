"""
Vertex AI Search with Google Search Grounding
==============================================

Uses Vertex AI's Gemini model with Google Search grounding
for real-time internet research.
"""

import os
import json
from datetime import datetime

import vertexai
from vertexai.generative_models import GenerativeModel, Tool
from vertexai.preview.generative_models import grounding


PROJECT_ID = os.environ.get('GOOGLE_CLOUD_PROJECT', '')
LOCATION = os.environ.get('VERTEX_AI_LOCATION', 'us-central1')


def init_vertex_ai():
    """Initialize Vertex AI with project and location."""
    if PROJECT_ID:
        vertexai.init(project=PROJECT_ID, location=LOCATION)


def create_research_model():
    """Create Gemini model with Google Search grounding."""
    init_vertex_ai()
    
    google_search_tool = Tool.from_google_search_retrieval(
        grounding.GoogleSearchRetrieval()
    )
    
    model = GenerativeModel(
        "gemini-1.5-flash-002",
        tools=[google_search_tool]
    )
    
    return model


def parse_json_response(response_text: str) -> dict:
    """Parse JSON from model response, handling markdown code blocks."""
    try:
        return json.loads(response_text)
    except json.JSONDecodeError:
        text = response_text.strip()
        if text.startswith("```json"):
            text = text[7:]
        elif text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        
        try:
            return json.loads(text.strip())
        except json.JSONDecodeError:
            return {"error": "Failed to parse response", "raw": response_text[:500]}


def build_research_prompt(query: str, input_type: str, research_focus: list) -> str:
    """Build the research prompt with requested focus areas."""
    focus_sections = []
    
    if "product" in research_focus:
        focus_sections.append('''
        "product": {
            "name": "Product name",
            "description": "What it does",
            "features": ["Feature 1", "Feature 2"],
            "pricing": "Pricing info",
            "usp": "Unique selling proposition",
            "target_audience": "Who it's for"
        }''')
    
    if "company" in research_focus:
        focus_sections.append('''
        "company": {
            "name": "Company name",
            "about": "What the company does",
            "founded": "Year",
            "headquarters": "Location",
            "mission": "Mission statement",
            "social_presence": {"instagram": "@handle", "youtube": "channel"}
        }''')
    
    if "market" in research_focus:
        focus_sections.append('''
        "market": {
            "competitors": [{"name": "Competitor", "positioning": "How positioned"}],
            "trends": ["Trend 1", "Trend 2"],
            "audience_insights": "Demographics and behavior",
            "market_size": "Market info"
        }''')
    
    sections_json = ",".join(focus_sections)
    
    return f"""
    Perform comprehensive research on the following:
    Input type: {input_type}
    Query: {query}
    
    Research this thoroughly using internet search and return a JSON object with this structure:
    {{
        "research_type": "product_research",
        "input": {{
            "type": "{input_type}",
            "value": "{query}"
        }},
        {sections_json},
        "ad_recommendations": {{
            "key_messages": ["Message 1", "Message 2"],
            "emotional_hooks": ["Hook 1", "Hook 2"],
            "visual_themes": ["Theme 1", "Theme 2"],
            "cta_suggestions": ["CTA 1", "CTA 2"]
        }},
        "sources": [
            {{"url": "https://...", "title": "Source title"}}
        ],
        "generated_at": "{datetime.utcnow().isoformat()}"
    }}
    
    Be thorough and accurate. Include real, verifiable information.
    Only return the JSON object, no other text or markdown.
    """


def research_comprehensive(query: str, input_type: str, research_focus: list) -> dict:
    """
    Perform comprehensive research using Vertex AI + Google Search.
    
    Args:
        query: URL or text to research
        input_type: "url" or "text"
        research_focus: List of areas to focus on ["product", "company", "market"]
    
    Returns:
        Dictionary with research results
    """
    model = create_research_model()
    prompt = build_research_prompt(query, input_type, research_focus)
    
    response = model.generate_content(prompt)
    result = parse_json_response(response.text)
    
    # Ensure required fields
    if "input" not in result:
        result["input"] = {"type": input_type, "value": query}
    if "generated_at" not in result:
        result["generated_at"] = datetime.utcnow().isoformat()
    if "sources" not in result:
        result["sources"] = []
    
    return result
