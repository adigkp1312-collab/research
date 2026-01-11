"""
Vertex AI Client - Gemini Model Factory

Creates Vertex AI GenerativeModel instances for Gemini.

Team: AI/ML
"""

from __future__ import annotations
from typing import Optional, Dict, Any

import vertexai
from vertexai.generative_models import GenerativeModel

# Import from core package
# PYTHONPATH is set by handler.py or main.py entry point
from packages.core.src import (
    GOOGLE_CLOUD_PROJECT,
    VERTEX_AI_LOCATION,
)

# Model Configuration
GEMINI_MODEL = "gemini-2.5-flash"  # Gemini 2.5 Flash - latest stable
MODEL_NAME = "Gemini 2.5 Flash"


def init_vertex_ai():
    """Initialize Vertex AI with project and location."""
    if GOOGLE_CLOUD_PROJECT:
        vertexai.init(project=GOOGLE_CLOUD_PROJECT, location=VERTEX_AI_LOCATION)
    else:
        raise ValueError(
            "GOOGLE_CLOUD_PROJECT not found in environment variables. "
            "Set it in Cloud Run environment variables or GCP project settings."
        )


def create_chat_model(
    temperature: float = 0.7,
    streaming: bool = True,
    max_tokens: Optional[int] = None,
    tools: Optional[list] = None,
) -> GenerativeModel:
    """
    Creates a Vertex AI GenerativeModel for Gemini.
    
    Args:
        temperature: Sampling temperature (0-2)
        streaming: Whether to stream responses (used by caller, not model config)
        max_tokens: Maximum tokens in response
        tools: Optional list of tools (e.g., Google Search grounding)
    
    Returns:
        A configured GenerativeModel instance
    
    Raises:
        ValueError: If GOOGLE_CLOUD_PROJECT is not set
    
    Example:
        >>> model = create_chat_model()
        >>> response = model.generate_content("Hello!")
    """
    if not GOOGLE_CLOUD_PROJECT:
        raise ValueError(
            "GOOGLE_CLOUD_PROJECT not found in environment variables. "
            "Set it in Cloud Run environment variables or GCP project settings."
        )
    
    # Initialize Vertex AI (only once, but safe to call multiple times)
    init_vertex_ai()
    
    # Build generation config dict
    from vertexai.generative_models import GenerationConfig
    generation_config = GenerationConfig(
        temperature=temperature,
        max_output_tokens=max_tokens,
    ) if max_tokens else GenerationConfig(temperature=temperature)
    
    # Create model with optional tools
    if tools:
        return GenerativeModel(
            GEMINI_MODEL,
            generation_config=generation_config,
            tools=tools
        )
    else:
        return GenerativeModel(
            GEMINI_MODEL,
            generation_config=generation_config
        )


def get_model_info() -> dict:
    """Get information about the current model."""
    return {
        "model": GEMINI_MODEL,
        "model_name": MODEL_NAME,
        "provider": "Google",
        "api_type": "Vertex AI (via GOOGLE_CLOUD_PROJECT)",
        "location": VERTEX_AI_LOCATION,
    }
