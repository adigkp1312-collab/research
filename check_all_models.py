#!/usr/bin/env python3
"""
Comprehensive Vertex AI Model Checker

Tests a comprehensive list of Gemini models to find all available ones.
"""

import os
import sys
from pathlib import Path

# Add project root to path
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
        # Try a minimal generation to verify it works
        response = model.generate_content("test", generation_config={"max_output_tokens": 1})
        return True, None
    except Exception as e:
        error_msg = str(e)
        if "404" in error_msg or "not found" in error_msg.lower():
            return False, "not_found"
        elif "permission" in error_msg.lower() or "access" in error_msg.lower():
            return False, "permission"
        else:
            return False, "error"

def main():
    """Test comprehensive list of models."""
    project_id = os.environ.get('GOOGLE_CLOUD_PROJECT')
    location = os.environ.get('VERTEX_AI_LOCATION', 'us-central1')
    
    if not project_id:
        print("❌ GOOGLE_CLOUD_PROJECT not set")
        return
    
    print("=" * 70)
    print("Comprehensive Gemini Model Availability Check")
    print("=" * 70)
    print(f"Project: {project_id}")
    print(f"Location: {location}\n")
    
    # Comprehensive list of Gemini models to test
    models_to_test = [
        # Gemini 2.0 models
        "gemini-2.0-flash-exp",
        "gemini-2.0-flash-thinking-exp",
        "gemini-2.0-flash",
        "gemini-2.0-pro-exp",
        "gemini-2.0-pro",
        
        # Gemini 1.5 models
        "gemini-1.5-flash",
        "gemini-1.5-flash-001",
        "gemini-1.5-flash-002",
        "gemini-1.5-flash-8b",
        "gemini-1.5-pro",
        "gemini-1.5-pro-001",
        "gemini-1.5-pro-002",
        "gemini-1.5-pro-latest",
        "gemini-1.5-flash-latest",
        
        # Gemini 1.0 models
        "gemini-pro",
        "gemini-pro-v2",
        "gemini-pro-vision",
        
        # Alternative naming
        "gemini-pro-001",
        "gemini-pro-002",
    ]
    
    available = []
    not_found = []
    errors = []
    
    print("Testing models...\n")
    
    for model_name in models_to_test:
        print(f"Testing: {model_name:<35}", end=" ")
        is_available, error_type = test_model(model_name)
        
        if is_available:
            print("✅ Available")
            available.append(model_name)
        elif error_type == "not_found":
            print("❌ Not found")
            not_found.append(model_name)
        elif error_type == "permission":
            print("⚠️  Permission denied")
            errors.append((model_name, "permission"))
        else:
            print("⚠️  Error")
            errors.append((model_name, "error"))
    
    print("\n" + "=" * 70)
    print("Results Summary")
    print("=" * 70)
    
    if available:
        print(f"\n✅ Available Models ({len(available)}):")
        for model in available:
            print(f"   • {model}")
    
    if not_found:
        print(f"\n❌ Not Found ({len(not_found)}):")
        for model in not_found[:5]:  # Show first 5
            print(f"   • {model}")
        if len(not_found) > 5:
            print(f"   ... and {len(not_found) - 5} more")
    
    if errors:
        print(f"\n⚠️  Errors ({len(errors)}):")
        for model, error_type in errors:
            print(f"   • {model}: {error_type}")
    
    print("\n" + "=" * 70)
    print("Recommendation")
    print("=" * 70)
    
    if available:
        print(f"\nUse one of these available models:")
        for model in available:
            print(f"   • {model}")
        print(f"\nCurrently configured: gemini-2.0-flash-exp")
    else:
        print("\nNo models found. Check:")
        print("1. Vertex AI API is enabled")
        print("2. Billing is enabled")
        print("3. You have proper permissions")

if __name__ == "__main__":
    main()
