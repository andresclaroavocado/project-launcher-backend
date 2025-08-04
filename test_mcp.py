#!/usr/bin/env python3
"""
Test script for GooseAI MCP (Model Context Protocol) functionality
Demonstrates tool calling and project creation capabilities
"""

import asyncio
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from app.integrations.goose_ai_mcp_client import GooseAIMCPClient


async def test_mcp_connection():
    """Test MCP connection and tool availability"""
    print("🔍 Testing MCP Connection...")
    
    mcp_client = GooseAIMCPClient()
    status = await mcp_client.test_mcp_connection()
    
    print(f"Status: {status['status']}")
    print(f"Message: {status['message']}")
    print(f"Tools Available: {status['tools_available']}")
    
    if status['status'] == 'available':
        print("✅ MCP Connection Successful!")
        return True
    else:
        print("❌ MCP Connection Failed!")
        return False


async def test_available_tools():
    """Test getting available tools"""
    print("\n🛠️ Testing Available Tools...")
    
    mcp_client = GooseAIMCPClient()
    tools = await mcp_client.get_available_tools()
    
    print(f"Total Tools: {len(tools)}")
    for tool in tools:
        print(f"  - {tool['name']}: {tool['description']}")
    
    return tools


async def test_create_project_structure():
    """Test project structure creation"""
    print("\n🏗️ Testing Project Structure Creation...")
    
    mcp_client = GooseAIMCPClient()
    
    result = await mcp_client.execute_tool("create_project_structure", {
        "project_name": "test-react-app",
        "framework": "react",
        "backend": "nodejs",
        "database": "postgresql"
    })
    
    print(f"Success: {result['success']}")
    print(f"Message: {result['message']}")
    print(f"Project: {result['project_name']}")
    
    if result['success']:
        print("✅ Project Structure Created!")
        # Print first 200 characters of structure
        structure = result.get('structure', '')
        print(f"Structure Preview: {structure[:200]}...")
    
    return result


async def test_generate_code():
    """Test code generation"""
    print("\n💻 Testing Code Generation...")
    
    mcp_client = GooseAIMCPClient()
    
    result = await mcp_client.execute_tool("generate_code", {
        "file_type": "component",
        "content": "User authentication component with login form",
        "framework": "react"
    })
    
    print(f"Success: {result['success']}")
    print(f"File Type: {result['file_type']}")
    print(f"Framework: {result['framework']}")
    
    if result['success']:
        print("✅ Code Generated!")
        # Print first 200 characters of code
        code = result.get('code', '')
        print(f"Code Preview: {code[:200]}...")
    
    return result


async def test_create_documentation():
    """Test documentation creation"""
    print("\n📚 Testing Documentation Creation...")
    
    mcp_client = GooseAIMCPClient()
    
    result = await mcp_client.execute_tool("create_documentation", {
        "doc_type": "readme",
        "project_info": "React e-commerce app with Node.js backend and PostgreSQL database"
    })
    
    print(f"Success: {result['success']}")
    print(f"Doc Type: {result['doc_type']}")
    
    if result['success']:
        print("✅ Documentation Created!")
        # Print first 200 characters of documentation
        doc = result.get('documentation', '')
        print(f"Documentation Preview: {doc[:200]}...")
    
    return result


async def test_git_operations():
    """Test Git operations"""
    print("\n📝 Testing Git Operations...")
    
    mcp_client = GooseAIMCPClient()
    
    result = await mcp_client.execute_tool("execute_git_operations", {
        "operation": "init",
        "message": "Initial commit for test project"
    })
    
    print(f"Success: {result['success']}")
    print(f"Operation: {result['operation']}")
    print(f"Command: {result['command']}")
    print(f"Message: {result['message']}")
    
    if result['success']:
        print("✅ Git Operation Executed!")
    
    return result


async def test_complete_project_creation():
    """Test complete project creation workflow"""
    print("\n🚀 Testing Complete Project Creation...")
    
    mcp_client = GooseAIMCPClient()
    
    # Step 1: Create project structure
    print("Step 1: Creating project structure...")
    structure_result = await mcp_client.execute_tool("create_project_structure", {
        "project_name": "full-stack-app",
        "framework": "react",
        "backend": "nodejs",
        "database": "mongodb"
    })
    
    if not structure_result['success']:
        print("❌ Failed to create project structure")
        return False
    
    # Step 2: Generate main component
    print("Step 2: Generating main component...")
    code_result = await mcp_client.execute_tool("generate_code", {
        "file_type": "component",
        "content": "Main app component with routing and navigation",
        "framework": "react"
    })
    
    if not code_result['success']:
        print("❌ Failed to generate code")
        return False
    
    # Step 3: Create documentation
    print("Step 3: Creating documentation...")
    doc_result = await mcp_client.execute_tool("create_documentation", {
        "doc_type": "readme",
        "project_info": "Full-stack React app with Node.js backend and MongoDB"
    })
    
    if not doc_result['success']:
        print("❌ Failed to create documentation")
        return False
    
    # Step 4: Initialize Git
    print("Step 4: Initializing Git repository...")
    git_result = await mcp_client.execute_tool("execute_git_operations", {
        "operation": "init",
        "message": "Initial commit for full-stack app"
    })
    
    if not git_result['success']:
        print("❌ Failed to initialize Git")
        return False
    
    print("✅ Complete Project Creation Successful!")
    print(f"Project: {structure_result['project_name']}")
    print(f"Files Generated: 1 component + documentation")
    print(f"Git Repository: Initialized")
    
    return True


async def main():
    """Run all MCP tests"""
    print("🧪 GooseAI MCP Test Suite")
    print("=" * 50)
    
    # Check if API key is available
    api_key = os.getenv('GOOSE_AI_API_KEY')
    if not api_key:
        print("❌ GOOSE_AI_API_KEY not found in environment variables")
        print("Please set your GooseAI API key in the .env file")
        return
    
    print(f"✅ API Key found (length: {len(api_key)})")
    
    # Run tests
    tests = [
        ("MCP Connection", test_mcp_connection),
        ("Available Tools", test_available_tools),
        ("Project Structure", test_create_project_structure),
        ("Code Generation", test_generate_code),
        ("Documentation", test_create_documentation),
        ("Git Operations", test_git_operations),
        ("Complete Project", test_complete_project_creation)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            print(f"\n{'='*20} {test_name} {'='*20}")
            result = await test_func()
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
        print("🎉 All tests passed! MCP implementation is working correctly.")
    else:
        print("⚠️ Some tests failed. Check the output above for details.")


if __name__ == "__main__":
    asyncio.run(main()) 