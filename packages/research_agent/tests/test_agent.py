"""
Unit tests for Research Agent
"""

import pytest
from unittest.mock import patch, MagicMock


class TestDetectInputType:
    """Tests for detect_input_type function."""
    
    def test_detects_http_url(self):
        from research_agent.src.agent import detect_input_type
        assert detect_input_type("http://example.com") == "url"
    
    def test_detects_https_url(self):
        from research_agent.src.agent import detect_input_type
        assert detect_input_type("https://example.com/path") == "url"
    
    def test_detects_www_url(self):
        from research_agent.src.agent import detect_input_type
        assert detect_input_type("www.example.com") == "url"
    
    def test_detects_text_query(self):
        from research_agent.src.agent import detect_input_type
        assert detect_input_type("Nike Air Max shoes") == "text"
    
    def test_strips_whitespace(self):
        from research_agent.src.agent import detect_input_type
        assert detect_input_type("  https://example.com  ") == "url"


class TestGenerateTitle:
    """Tests for generate_title function."""
    
    def test_uses_product_name(self):
        from research_agent.src.agent import generate_title
        result = generate_title(
            "https://example.com",
            "url",
            {"product": {"name": "Nike Air Max"}}
        )
        assert result == "Research: Nike Air Max"
    
    def test_uses_company_name_as_fallback(self):
        from research_agent.src.agent import generate_title
        result = generate_title(
            "https://example.com",
            "url",
            {"company": {"name": "Nike Inc"}}
        )
        assert result == "Research: Nike Inc"
    
    def test_uses_domain_for_url(self):
        from research_agent.src.agent import generate_title
        result = generate_title(
            "https://www.nike.com/shoes",
            "url",
            {}
        )
        assert result == "Research: nike.com"
    
    def test_truncates_long_text(self):
        from research_agent.src.agent import generate_title
        long_text = "A" * 100
        result = generate_title(long_text, "text", {})
        assert len(result) <= 60
        assert result.endswith("...")


class TestParseJsonResponse:
    """Tests for parse_json_response function."""
    
    def test_parses_valid_json(self):
        from research_agent.src.search import parse_json_response
        result = parse_json_response('{"key": "value"}')
        assert result == {"key": "value"}
    
    def test_handles_markdown_json_block(self):
        from research_agent.src.search import parse_json_response
        result = parse_json_response('```json\n{"key": "value"}\n```')
        assert result == {"key": "value"}
    
    def test_handles_invalid_json(self):
        from research_agent.src.search import parse_json_response
        result = parse_json_response('not json')
        assert "error" in result


class TestResearchComprehensive:
    """Tests for research_comprehensive function."""
    
    @patch('research_agent.src.search.create_research_model')
    def test_calls_model_and_parses_response(self, mock_create_model):
        from research_agent.src.search import research_comprehensive
        
        mock_model = MagicMock()
        mock_response = MagicMock()
        mock_response.text = '{"product": {"name": "Test"}, "sources": []}'
        mock_model.generate_content.return_value = mock_response
        mock_create_model.return_value = mock_model
        
        result = research_comprehensive("test query", "text", ["product"])
        
        assert result["product"]["name"] == "Test"
        assert "generated_at" in result
        mock_model.generate_content.assert_called_once()


class TestStorage:
    """Tests for storage functions."""
    
    @patch('research_agent.src.storage.supabase_request')
    def test_create_research_entry(self, mock_request):
        from research_agent.src.storage import create_research_entry
        
        mock_request.return_value = [{"id": "test-uuid"}]
        
        result = create_research_entry(
            "project-123",
            "user-456",
            "text_research",
            "Nike shoes",
            {"product": {}},
            "Research: Nike"
        )
        
        assert result["id"] == "test-uuid"
        mock_request.assert_called_once()
    
    @patch('research_agent.src.storage.supabase_request')
    def test_get_research_by_id(self, mock_request):
        from research_agent.src.storage import get_research_by_id
        
        mock_request.return_value = [{"id": "test-uuid", "title": "Test"}]
        
        result = get_research_by_id("test-uuid")
        
        assert result["id"] == "test-uuid"
    
    @patch('research_agent.src.storage.supabase_request')
    def test_list_research_by_project(self, mock_request):
        from research_agent.src.storage import list_research_by_project
        
        mock_request.return_value = [
            {"id": "1", "title": "Research 1"},
            {"id": "2", "title": "Research 2"}
        ]
        
        result = list_research_by_project("project-123")
        
        assert len(result) == 2
