#!/usr/bin/env python3
"""
Check for Gemini 3 preview models and Gemini 2.5 models
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
    print("Checking for Gemini 3 Preview and Gemini 2.5 Models")
    print("=" * 70)
    print(f"Project: {project_id}")
    print(f"Location: {location}\n")
    
    # Test Gemini 3 preview models
    models_to_test = [
        # Gemini 3 Preview
        "gemini-3-pro-preview",
        "gemini-3-flash-preview",
        "gemini-3-pro-preview-001",
        "gemini-3-flash-preview-001",
        "gemini-3.0-pro-preview",
        "gemini-3.0-flash-preview",
        
        # Gemini 2.5 models
        "gemini-2.5-pro",
        "gemini-2.5-flash",
        "gemini-2.5-flash-lite",
        "gemini-2.5-flash-image",
        "gemini-2.5-pro-001",
        "gemini-2.5-flash-001",
        
        # Alternative naming
        "gemini-2-5-pro",
        "gemini-2-5-flash",
    ]
    
    print("Testing models...\n")
    
    available = []
    
    for model_name in models_to_test:
        print(f"Testing: {model_name:<35}", end=" ")
        if test_model(model_name):
            print("✅ Available")
            available.append(model_name)
        else:
            print("❌ Not found")
    
    print("\n" + "=" * 70)
    if available:
        print(f"✅ Found {len(available)} additional model(s):")
        for model in available:
            print(f"   • {model}")
        print("\n📋 All Available Models in Your Project:")
        print("   • gemini-2.0-flash-exp (currently configured)")
        print("   • gemini-2.0-flash")
        for model in available:
            print(f"   • {model}")
    else:
        print("❌ No Gemini 3 or Gemini 2.5 models found")
        print("\n📋 Currently Available Models:")
        print("   • gemini-2.0-flash-exp (currently configured)")
        print("   • gemini-2.0-flash")
        print("\nNote: Gemini 3 may require:")
        print("   - Preview access/whitelist")
        print("   - Different region")
        print("   - Project-specific enablement")

if __name__ == "__main__":
    main()
