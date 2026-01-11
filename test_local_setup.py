#!/usr/bin/env python3
"""
Local Setup Test Script

Tests the Vertex AI implementation locally.
Run this to verify your GCP setup is correct.

Usage:
    export GOOGLE_CLOUD_PROJECT=your-project-id
    export VERTEX_AI_LOCATION=us-central1
    python test_local_setup.py
"""

import os
import sys
from pathlib import Path

# Add project root to path
root = Path(__file__).parent
if str(root) not in sys.path:
    sys.path.insert(0, str(root))

def test_environment():
    """Test environment variables."""
    print("=" * 60)
    print("Testing Environment Configuration")
    print("=" * 60)
    
    project_id = os.environ.get('GOOGLE_CLOUD_PROJECT')
    location = os.environ.get('VERTEX_AI_LOCATION', 'us-central1')
    
    if not project_id:
        print("❌ GOOGLE_CLOUD_PROJECT not set")
        print("   Set it with: export GOOGLE_CLOUD_PROJECT=your-project-id")
        return False
    
    print(f"✅ GOOGLE_CLOUD_PROJECT: {project_id}")
    print(f"✅ VERTEX_AI_LOCATION: {location}")
    return True


def test_imports():
    """Test package imports."""
    print("\n" + "=" * 60)
    print("Testing Package Imports")
    print("=" * 60)
    
    try:
        from packages.core.src import GOOGLE_CLOUD_PROJECT, VERTEX_AI_LOCATION
        print("✅ Core package imports successful")
        
        from packages.langchain_client.src import create_chat_model, init_vertex_ai
        print("✅ Vertex AI client imports successful")
        
        from packages.langchain_memory.src import get_session_memory
        print("✅ Memory package imports successful")
        
        from packages.langchain_chains.src import quick_chat, stream_chat
        print("✅ Chains package imports successful")
        
        return True
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False


def test_vertex_ai_init():
    """Test Vertex AI initialization."""
    print("\n" + "=" * 60)
    print("Testing Vertex AI Initialization")
    print("=" * 60)
    
    try:
        from packages.langchain_client.src import init_vertex_ai, create_chat_model
        
        print("Initializing Vertex AI...")
        init_vertex_ai()
        print("✅ Vertex AI initialized successfully")
        
        print("Creating chat model...")
        model = create_chat_model(temperature=0.7, streaming=False)
        print("✅ Chat model created successfully")
        
        return True, model
    except Exception as e:
        print(f"❌ Vertex AI initialization failed: {e}")
        print("\nTroubleshooting:")
        print("1. Ensure GOOGLE_CLOUD_PROJECT is set correctly")
        print("2. Run: gcloud auth application-default login")
        print("3. Ensure Vertex AI API is enabled:")
        print("   gcloud services enable aiplatform.googleapis.com")
        return False, None


def test_simple_chat(model):
    """Test a simple chat interaction."""
    print("\n" + "=" * 60)
    print("Testing Simple Chat")
    print("=" * 60)
    
    if not model:
        print("⚠️  Skipping chat test (model not available)")
        return False
    
    try:
        print("Sending test message: 'Hello, say hi back!'")
        response = model.generate_content("Hello, say hi back!")
        
        if hasattr(response, 'text'):
            print(f"✅ Response received: {response.text[:100]}...")
            return True
        else:
            print(f"⚠️  Response format unexpected: {response}")
            return False
    except Exception as e:
        print(f"❌ Chat test failed: {e}")
        return False


def test_memory():
    """Test memory functionality."""
    print("\n" + "=" * 60)
    print("Testing Memory Functionality")
    print("=" * 60)
    
    try:
        from packages.langchain_memory.src import get_session_memory, clear_session_memory
        
        memory = get_session_memory("test-session-123")
        print("✅ Memory created")
        
        memory.save_context({"input": "Hello"}, {"output": "Hi there!"})
        print("✅ Context saved")
        
        messages = memory.get_messages()
        print(f"✅ Retrieved {len(messages)} messages")
        
        clear_session_memory("test-session-123")
        print("✅ Memory cleared")
        
        return True
    except Exception as e:
        print(f"❌ Memory test failed: {e}")
        return False


def test_quick_chat():
    """Test quick_chat function."""
    print("\n" + "=" * 60)
    print("Testing quick_chat Function")
    print("=" * 60)
    
    try:
        import asyncio
        from packages.langchain_chains.src import quick_chat
        
        async def run_test():
            response = await quick_chat(
                session_id="test-session",
                message="Say 'test successful' if you can read this."
            )
            print(f"✅ Response: {response[:100]}...")
            return True
        
        result = asyncio.run(run_test())
        return result
    except Exception as e:
        print(f"❌ quick_chat test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("Local Setup Test - Vertex AI Migration")
    print("=" * 60)
    print("\nThis script tests the Vertex AI implementation locally.")
    print("Make sure you have:")
    print("1. GOOGLE_CLOUD_PROJECT environment variable set")
    print("2. GCP Application Default Credentials configured")
    print("3. Vertex AI API enabled in your project\n")
    
    results = []
    
    # Test 1: Environment
    results.append(("Environment", test_environment()))
    if not results[-1][1]:
        print("\n❌ Environment setup failed. Please fix and try again.")
        return
    
    # Test 2: Imports
    results.append(("Imports", test_imports()))
    if not results[-1][1]:
        print("\n❌ Import test failed. Check dependencies.")
        return
    
    # Test 3: Vertex AI Init
    init_success, model = test_vertex_ai_init()
    results.append(("Vertex AI Init", init_success))
    
    # Test 4: Simple Chat (if init succeeded)
    if init_success:
        results.append(("Simple Chat", test_simple_chat(model)))
    
    # Test 5: Memory
    results.append(("Memory", test_memory()))
    
    # Test 6: Quick Chat (if init succeeded)
    if init_success:
        results.append(("Quick Chat", test_quick_chat()))
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Your setup is ready.")
    else:
        print("\n⚠️  Some tests failed. Please review the errors above.")


if __name__ == "__main__":
    main()
