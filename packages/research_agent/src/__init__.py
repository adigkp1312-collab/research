"""Research Agent Package - Vertex AI + Google Search grounding for research."""

from .agent import research_product_company_market, detect_input_type
from .storage import (
    create_research_entry,
    get_research_by_id,
    list_research_by_project,
    update_research_entry,
    delete_research_entry
)
from .search import create_research_model, parse_json_response

__all__ = [
    "research_product_company_market",
    "detect_input_type",
    "create_research_entry",
    "get_research_by_id", 
    "list_research_by_project",
    "update_research_entry",
    "delete_research_entry",
    "create_research_model",
    "parse_json_response"
]
