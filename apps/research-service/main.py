"""
Research Service - Cloud Run Flask App
=======================================

API wrapper for the research_agent package.
"""

import os
import time
from flask import Flask, request, jsonify
from flask_cors import CORS

from research_agent.src.agent import (
    detect_input_type,
    generate_title,
    research_product_company_market
)
from research_agent.src.search import research_comprehensive
from research_agent.src.storage import (
    create_research_entry,
    get_research_by_id,
    list_research_by_project,
    update_research_entry,
    delete_research_entry
)


app = Flask(__name__)
CORS(app)


@app.route('/')
def health():
    """Health check endpoint."""
    return jsonify({
        'status': 'ok',
        'service': 'research-service',
        'version': '1.0',
        'vertex_ai': bool(os.environ.get('GOOGLE_CLOUD_PROJECT')),
        'supabase': bool(os.environ.get('SUPABASE_URL')),
        'routes': [
            'POST /research',
            'GET /research/{project_id}',
            'GET /research/item/{research_id}',
            'PATCH /research/{research_id}',
            'DELETE /research/{research_id}'
        ]
    })


@app.route('/research', methods=['POST'])
def create_research():
    """Create new research from URL or text input."""
    try:
        body = request.get_json()
        
        project_id = body.get('project_id')
        user_id = body.get('user_id')
        input_value = body.get('input_value')
        
        if not project_id:
            return jsonify({'error': 'project_id is required'}), 400
        if not user_id:
            return jsonify({'error': 'user_id is required'}), 400
        if not input_value:
            return jsonify({'error': 'input_value is required'}), 400
        
        input_type = body.get('input_type') or detect_input_type(input_value)
        research_focus = body.get('research_focus', ['product', 'company', 'market'])
        
        start_time = time.time()
        
        # Perform research
        try:
            analysis_data = research_comprehensive(input_value, input_type, research_focus)
        except Exception as e:
            return jsonify({'error': 'Research failed', 'message': str(e)}), 500
        
        # Generate title and save
        source_type = 'url_research' if input_type == 'url' else 'text_research'
        title = generate_title(input_value, input_type, analysis_data)
        
        try:
            research_entry = create_research_entry(
                project_id, user_id, source_type, input_value, analysis_data, title
            )
        except Exception as e:
            return jsonify({
                'error': 'Failed to save research',
                'message': str(e),
                'analysis_data': analysis_data
            }), 500
        
        processing_time = round(time.time() - start_time, 2)
        
        return jsonify({
            'success': True,
            'research_id': research_entry.get('id'),
            'analysis_data': analysis_data,
            'sources_count': len(analysis_data.get('sources', [])),
            'processing_time': f'{processing_time}s',
            'metadata': {
                'input_type': input_type,
                'source_type': source_type,
                'research_focus': research_focus,
                'title': title
            }
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/research/<project_id>', methods=['GET'])
def list_research(project_id):
    """List all research for a project."""
    try:
        limit = request.args.get('limit', 50, type=int)
        research_items = list_research_by_project(project_id, limit)
        
        return jsonify({
            'success': True,
            'project_id': project_id,
            'count': len(research_items),
            'research': [
                {
                    'id': item.get('id'),
                    'source_type': item.get('source_type'),
                    'source_input': item.get('source_input'),
                    'title': item.get('title'),
                    'created_at': item.get('created_at'),
                    'updated_at': item.get('updated_at')
                }
                for item in research_items
            ]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/research/item/<research_id>', methods=['GET'])
def get_research(research_id):
    """Get single research item."""
    try:
        research = get_research_by_id(research_id)
        
        if not research:
            return jsonify({'error': 'Research not found'}), 404
        
        return jsonify({
            'success': True,
            'research': research
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/research/<research_id>', methods=['PATCH'])
def update_research(research_id):
    """Update research data."""
    try:
        body = request.get_json()
        user_id = body.get('user_id')
        
        if not user_id:
            return jsonify({'error': 'user_id is required'}), 400
        
        updates = {}
        if 'analysis_data' in body:
            updates['analysis_data'] = body['analysis_data']
        if 'title' in body:
            updates['title'] = body['title']
        
        if not updates:
            return jsonify({'error': 'No fields to update'}), 400
        
        updated = update_research_entry(research_id, user_id, updates)
        
        if not updated:
            return jsonify({'error': 'Research not found or update failed'}), 404
        
        return jsonify({
            'success': True,
            'research_id': research_id,
            'updated_at': updated.get('updated_at')
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/research/<research_id>', methods=['DELETE'])
def delete_research(research_id):
    """Delete research entry."""
    try:
        user_id = request.args.get('user_id')
        
        if not user_id:
            return jsonify({'error': 'user_id query parameter is required'}), 400
        
        success = delete_research_entry(research_id, user_id)
        
        if not success:
            return jsonify({'error': 'Research not found or delete failed'}), 404
        
        return jsonify({
            'success': True,
            'deleted': research_id
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=True)
