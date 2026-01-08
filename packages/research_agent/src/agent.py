"""
Research Agent - Main Entry Point
==================================

Orchestrates research queries and handles input processing.
"""

from urllib.parse import urlparse

from .search import research_comprehensive
from .storage import (
    create_research_entry,
    get_research_by_id,
    list_research_by_project,
    update_research_entry,
    delete_research_entry
)


def detect_input_type(input_value: str) -> str:
    """
    Detect if input is URL or text.
    
    Args:
        input_value: User input string
    
    Returns:
        "url" or "text"
    """
    input_value = input_value.strip()
    
    if input_value.startswith(('http://', 'https://', 'www.')):
        return "url"
    
    try:
        parsed = urlparse(input_value)
        if parsed.scheme in ('http', 'https') and parsed.netloc:
            return "url"
    except Exception:
        pass
    
    return "text"


def generate_title(input_value: str, input_type: str, analysis_data: dict) -> str:
    """
    Generate a display title for the research entry.
    
    Args:
        input_value: Original input
        input_type: "url" or "text"
        analysis_data: Research results
    
    Returns:
        Display title string
    """
    product_name = analysis_data.get('product', {}).get('name')
    company_name = analysis_data.get('company', {}).get('name')
    
    if product_name and product_name not in ('Unknown', 'Parse error'):
        return f"Research: {product_name}"
    if company_name and company_name not in ('Unknown', 'Parse error'):
        return f"Research: {company_name}"
    
    if input_type == "url":
        try:
            parsed = urlparse(input_value)
            domain = parsed.netloc.replace('www.', '')
            return f"Research: {domain}"
        except Exception:
            pass
    
    if len(input_value) > 50:
        return f"Research: {input_value[:47]}..."
    return f"Research: {input_value}"


def research_product_company_market(
    input_value: str,
    project_id: str,
    user_id: str,
    input_type: str = None,
    research_focus: list = None
) -> dict:
    """
    Main entry point for research.
    
    Performs research and saves to Supabase.
    
    Args:
        input_value: URL or text query
        project_id: UUID of project
        user_id: UUID of user
        input_type: Optional, auto-detected if not provided
        research_focus: List of areas ["product", "company", "market"]
    
    Returns:
        Dict with research results and metadata
    """
    if input_type is None:
        input_type = detect_input_type(input_value)
    
    if research_focus is None:
        research_focus = ['product', 'company', 'market']
    
    # Perform research
    analysis_data = research_comprehensive(input_value, input_type, research_focus)
    
    # Generate title and determine source type
    source_type = 'url_research' if input_type == 'url' else 'text_research'
    title = generate_title(input_value, input_type, analysis_data)
    
    # Save to Supabase
    research_entry = create_research_entry(
        project_id=project_id,
        user_id=user_id,
        source_type=source_type,
        source_input=input_value,
        analysis_data=analysis_data,
        title=title
    )
    
    return {
        'success': True,
        'research_id': research_entry.get('id'),
        'analysis_data': analysis_data,
        'sources_count': len(analysis_data.get('sources', [])),
        'metadata': {
            'input_type': input_type,
            'source_type': source_type,
            'research_focus': research_focus,
            'title': title
        }
    }
