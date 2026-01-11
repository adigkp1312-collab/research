#!/usr/bin/env python3
"""
List Available Vertex AI Models

Lists all available Gemini models in your GCP project.

Usage:
    export GOOGLE_CLOUD_PROJECT=your-project-id
    export VERTEX_AI_LOCATION=us-central1
    python3 list_vertex_models.py
"""

import os
import sys
from pathlib import Path

# Add project root to path
root = Path(__file__).parent
if str(root) not in sys.path:
    sys.path.insert(0, str(root))

def list_models_via_api():
    """List models using Vertex AI API."""
    try:
        import vertexai
        from vertexai.generative_models import GenerativeModel
        
        project_id = os.environ.get('GOOGLE_CLOUD_PROJECT')
        location = os.environ.get('VERTEX_AI_LOCATION', 'us-central1')
        
        if not project_id:
            print("❌ GOOGLE_CLOUD_PROJECT not set")
            return False
        
        print(f"Initializing Vertex AI for project: {project_id}")
        print(f"Location: {location}\n")
        
        vertexai.init(project=project_id, location=location)
        
        # Try to list available models by testing common model names
        print("=" * 60)
        print("Testing Common Gemini Model Names")
        print("=" * 60)
        
        model_names = [
            "gemini-1.5-flash",
            "gemini-1.5-flash-001",
            "gemini-1.5-flash-002",
            "gemini-1.5-pro",
            "gemini-1.5-pro-001",
            "gemini-1.5-pro-002",
            "gemini-pro",
            "gemini-pro-v2",
            "gemini-2.0-flash-exp",
            "gemini-2.0-flash-thinking-exp",
        ]
        
        available_models = []
        
        for model_name in model_names:
            try:
                print(f"Testing: {model_name}...", end=" ")
                model = GenerativeModel(model_name)
                # Try a simple generation to verify it works
                response = model.generate_content("test", generation_config={"max_output_tokens": 1})
                print("✅ Available")
                available_models.append(model_name)
            except Exception as e:
                error_msg = str(e)
                if "404" in error_msg or "not found" in error_msg.lower():
                    print("❌ Not found")
                elif "permission" in error_msg.lower() or "access" in error_msg.lower():
                    print("⚠️  Permission denied")
                else:
                    print(f"⚠️  Error: {error_msg[:50]}")
        
        print("\n" + "=" * 60)
        print("Summary")
        print("=" * 60)
        
        if available_models:
            print(f"✅ Found {len(available_models)} available model(s):")
            for model in available_models:
                print(f"   - {model}")
        else:
            print("❌ No models found. Possible issues:")
            print("   1. Vertex AI API not enabled")
            print("   2. Project doesn't have access to Gemini models")
            print("   3. Billing not enabled")
            print("   4. Wrong location/region")
        
        return len(available_models) > 0
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Install: pip install google-cloud-aiplatform vertexai")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def list_models_via_gcloud():
    """List models using gcloud CLI."""
    print("\n" + "=" * 60)
    print("Alternative: List Models via gcloud CLI")
    print("=" * 60)
    
    project_id = os.environ.get('GOOGLE_CLOUD_PROJECT')
    location = os.environ.get('VERTEX_AI_LOCATION', 'us-central1')
    
    if not project_id:
        print("❌ GOOGLE_CLOUD_PROJECT not set")
        return
    
    print(f"\nRun this command to list models:")
    print(f"gcloud ai models list --region={location} --project={project_id}")
    print(f"\nOr check available publishers:")
    print(f"gcloud ai models list --region={location} --project={project_id} --filter='displayName:gemini*'")


def main():
    """Main function."""
    print("=" * 60)
    print("Vertex AI Model Availability Checker")
    print("=" * 60)
    print()
    
    project_id = os.environ.get('GOOGLE_CLOUD_PROJECT')
    location = os.environ.get('VERTEX_AI_LOCATION', 'us-central1')
    
    if not project_id:
        print("❌ GOOGLE_CLOUD_PROJECT environment variable not set")
        print("   Set it with: export GOOGLE_CLOUD_PROJECT=your-project-id")
        return
    
    print(f"Project: {project_id}")
    print(f"Location: {location}\n")
    
    # Try API method
    success = list_models_via_api()
    
    # Show gcloud alternative
    list_models_via_gcloud()
    
    if not success:
        print("\n" + "=" * 60)
        print("Troubleshooting")
        print("=" * 60)
        print("1. Enable Vertex AI API:")
        print(f"   gcloud services enable aiplatform.googleapis.com --project={project_id}")
        print("\n2. Check API status:")
        print(f"   gcloud services list --enabled --project={project_id} | grep aiplatform")
        print("\n3. Verify billing is enabled for the project")
        print("\n4. Check your IAM permissions")


if __name__ == "__main__":
    main()
