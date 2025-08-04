#!/usr/bin/env python3
"""
Test script to verify the client initialization fix
"""

import os
import asyncio
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_goose_ai_client():
    """Test GooseAI client initialization"""
    print("🧪 Testing GooseAI Client Initialization...")
    
    try:
        from app.integrations.goose_ai_client import GooseAIClient
        
        client = GooseAIClient()
        print(f"✅ GooseAI Client Status: {'Available' if client.available else 'Not Available'}")
        print(f"✅ Client Object: {'Initialized' if client.client else 'Not Initialized'}")
        
        if client.available:
            print("✅ GooseAI client initialized successfully!")
            return True
        else:
            print("⚠️ GooseAI client not available (missing API key)")
            return False
            
    except Exception as e:
        print(f"❌ GooseAI Client Error: {e}")
        return False

def test_anthropic_client():
    """Test Anthropic client initialization"""
    print("\n🧪 Testing Anthropic Client Initialization...")
    
    try:
        from app.integrations.anthropic_client import AnthropicClient
        
        client = AnthropicClient()
        print(f"✅ Anthropic Client Status: {'Available' if client.client else 'Not Available'}")
        
        if client.client:
            print("✅ Anthropic client initialized successfully!")
            return True
        else:
            print("⚠️ Anthropic client not available (missing API key)")
            return False
            
    except Exception as e:
        print(f"❌ Anthropic Client Error: {e}")
        return False

def test_multi_model_service():
    """Test MultiModelService initialization"""
    print("\n🧪 Testing MultiModelService Initialization...")
    
    try:
        from app.services.multi_model_service import MultiModelService
        
        service = MultiModelService()
        print(f"✅ MultiModelService Status: Initialized")
        print(f"✅ Anthropic Available: {service.anthropic_client.client is not None}")
        print(f"✅ GooseAI Available: {service.goose_ai_client.available}")
        
        print("✅ MultiModelService initialized successfully!")
        return True
        
    except Exception as e:
        print(f"❌ MultiModelService Error: {e}")
        return False

async def test_conversation_service():
    """Test ConversationService initialization"""
    print("\n🧪 Testing ConversationService Initialization...")
    
    try:
        from app.services.conversation_service import ConversationService
        
        service = ConversationService()
        print(f"✅ ConversationService Status: Initialized")
        print(f"✅ MultiModelService Available: {service.multi_model_service is not None}")
        
        print("✅ ConversationService initialized successfully!")
        return True
        
    except Exception as e:
        print(f"❌ ConversationService Error: {e}")
        return False

async def main():
    """Run all tests"""
    print("🔧 Client Initialization Test Suite")
    print("=" * 50)
    
    # Check environment variables
    anthropic_key = os.getenv('ANTHROPIC_API_KEY')
    goose_key = os.getenv('GOOSE_AI_API_KEY')
    
    print(f"Environment Variables:")
    print(f"  ANTHROPIC_API_KEY: {'Set' if anthropic_key else 'Missing'}")
    print(f"  GOOSE_AI_API_KEY: {'Set' if goose_key else 'Missing'}")
    print()
    
    # Run tests
    tests = [
        ("GooseAI Client", test_goose_ai_client),
        ("Anthropic Client", test_anthropic_client),
        ("MultiModelService", test_multi_model_service),
        ("ConversationService", test_conversation_service)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            print(f"{'='*20} {test_name} {'='*20}")
            if asyncio.iscoroutinefunction(test_func):
                result = await test_func()
            else:
                result = test_func()
            results[test_name] = "✅ PASSED" if result else "❌ FAILED"
        except Exception as e:
            print(f"❌ Error in {test_name}: {str(e)}")
            results[test_name] = "❌ ERROR"
    
    # Print summary
    print(f"\n{'='*50}")
    print("📊 Test Results Summary")
    print("=" * 50)
    
    for test_name, result in results.items():
        print(f"{test_name}: {result}")
    
    passed = sum(1 for result in results.values() if "✅" in result)
    total = len(results)
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Client initialization is working correctly.")
    else:
        print("⚠️ Some tests failed. Check the output above for details.")

if __name__ == "__main__":
    asyncio.run(main()) 