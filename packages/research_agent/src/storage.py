"""
Research Storage - Supabase CRUD Operations
============================================

Handles persistence of research data in Supabase project_research table.
"""

import os
import json
import uuid
from datetime import datetime
from urllib import request as url_request, error as url_error


SUPABASE_URL = os.environ.get('SUPABASE_URL', '')
SUPABASE_SERVICE_KEY = os.environ.get('SUPABASE_SERVICE_KEY', '')


def supabase_request(endpoint: str, method: str = 'GET', data: dict = None) -> dict:
    """
    Make request to Supabase REST API.
    
    Args:
        endpoint: API endpoint (e.g., 'project_research')
        method: HTTP method
        data: Request body for POST/PATCH
    
    Returns:
        Response data as dict or list
    """
    if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
        raise Exception("Supabase not configured")
    
    url = f"{SUPABASE_URL}/rest/v1/{endpoint}"
    headers = {
        'apikey': SUPABASE_SERVICE_KEY,
        'Authorization': f'Bearer {SUPABASE_SERVICE_KEY}',
        'Content-Type': 'application/json',
        'Prefer': 'return=representation'
    }
    
    body = json.dumps(data).encode('utf-8') if data else None
    req = url_request.Request(url, data=body, headers=headers, method=method)
    
    try:
        with url_request.urlopen(req, timeout=30) as resp:
            response_data = resp.read().decode('utf-8')
            if response_data:
                return json.loads(response_data)
            return {}
    except url_error.HTTPError as e:
        error_body = e.read().decode('utf-8')
        raise Exception(f"Supabase error {e.code}: {error_body}")


def create_research_entry(
    project_id: str, 
    user_id: str, 
    source_type: str, 
    source_input: str, 
    analysis_data: dict, 
    title: str
) -> dict:
    """
    Create research entry in Supabase.
    
    Args:
        project_id: UUID of the project
        user_id: UUID of the user
        source_type: 'url_research' or 'text_research'
        source_input: Original URL or text query
        analysis_data: Research results JSON
        title: Display title
    
    Returns:
        Created entry dict
    """
    research_id = str(uuid.uuid4())
    data = {
        'id': research_id,
        'project_id': project_id,
        'user_id': user_id,
        'source_type': source_type,
        'source_input': source_input,
        'analysis_data': analysis_data,
        'title': title,
        'created_at': datetime.utcnow().isoformat(),
        'updated_at': datetime.utcnow().isoformat()
    }
    
    result = supabase_request('project_research', 'POST', data)
    return result[0] if isinstance(result, list) else result


def get_research_by_id(research_id: str) -> dict:
    """Get research entry by ID."""
    result = supabase_request(f'project_research?id=eq.{research_id}&select=*')
    return result[0] if isinstance(result, list) and result else None


def list_research_by_project(project_id: str, limit: int = 50) -> list:
    """List all research entries for a project."""
    result = supabase_request(
        f'project_research?project_id=eq.{project_id}&select=*&order=created_at.desc&limit={limit}'
    )
    return result if isinstance(result, list) else []


def update_research_entry(research_id: str, user_id: str, updates: dict) -> dict:
    """
    Update research entry.
    
    Args:
        research_id: UUID of research entry
        user_id: UUID of user (for ownership check)
        updates: Fields to update
    
    Returns:
        Updated entry or None
    """
    updates['updated_at'] = datetime.utcnow().isoformat()
    result = supabase_request(
        f'project_research?id=eq.{research_id}&user_id=eq.{user_id}',
        'PATCH', updates
    )
    return result[0] if isinstance(result, list) and result else None


def delete_research_entry(research_id: str, user_id: str) -> bool:
    """Delete research entry."""
    try:
        supabase_request(
            f'project_research?id=eq.{research_id}&user_id=eq.{user_id}', 
            'DELETE'
        )
        return True
    except Exception:
        return False
