#!/usr/bin/env python3
"""
Check for Gemini 3 models specifically
"""

import os
import sys
from pathlib import Path

root = Path(__file__).parent
if str(root) not in sys.path:
    sys.path.insert(0, str(root))

def test_model(model_name):
    """Test if a model is available."""
    try:
        import vertexai
        from vertexai.generative_models import GenerativeModel
        
        project_id = os.environ.get('GOOGLE_CLOUD_PROJECT')
        location = os.environ.get('VERTEX_AI_LOCATION', 'us-central1')
        
        vertexai.init(project=project_id, location=location)
        model = GenerativeModel(model_name)
        response = model.generate_content("test", generation_config={"max_output_tokens": 1})
        return True
    except Exception as e:
        return False

def main():
    project_id = os.environ.get('GOOGLE_CLOUD_PROJECT')
    location = os.environ.get('VERTEX_AI_LOCATION', 'us-central1')
    
    print("=" * 70)
    print("Checking for Gemini 3 Models")
    print("=" * 70)
    print(f"Project: {project_id}")
    print(f"Location: {location}\n")
    
    # Test Gemini 3 model names
    gemini3_models = [
        "gemini-3-flash",
        "gemini-3-flash-exp",
        "gemini-3-flash-001",
        "gemini-3-flash-002",
        "gemini-3-pro",
        "gemini-3-pro-exp",
        "gemini-3-pro-001",
        "gemini-3",
        "gemini-3.0-flash",
        "gemini-3.0-flash-exp",
        "gemini-3.0-pro",
        "gemini-3.0-pro-exp",
    ]
    
    print("Testing Gemini 3 model names...\n")
    
    available = []
    
    for model_name in gemini3_models:
        print(f"Testing: {model_name:<30}", end=" ")
        if test_model(model_name):
            print("✅ Available")
            available.append(model_name)
        else:
            print("❌ Not found")
    
    print("\n" + "=" * 70)
    if available:
        print(f"✅ Found {len(available)} Gemini 3 model(s):")
        for model in available:
            print(f"   • {model}")
    else:
        print("❌ No Gemini 3 models found")
        print("\nNote: Gemini 3 may not be available yet, or may have")
        print("different naming. The available models are:")
        print("   • gemini-2.0-flash-exp")
        print("   • gemini-2.0-flash")

if __name__ == "__main__":
    main()
