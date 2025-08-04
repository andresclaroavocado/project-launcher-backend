"""
MCP (Model Context Protocol) API endpoints
Enables tool calling and action execution through GooseAI
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, List, Any, Optional
import structlog

from app.integrations.goose_ai_mcp_client import GooseAIMCPClient

logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/api/v1/mcp", tags=["mcp"])

# Global MCP client
_mcp_client: GooseAIMCPClient = None


async def get_mcp_client():
    """Get global MCP client"""
    global _mcp_client
    if _mcp_client is None:
        _mcp_client = GooseAIMCPClient()
    return _mcp_client


class ToolExecutionRequest(BaseModel):
    """Request model for tool execution"""
    tool_name: str
    parameters: Dict[str, Any]


class ToolExecutionResponse(BaseModel):
    """Response model for tool execution"""
    success: bool
    tool: str
    result: Dict[str, Any]
    message: str


@router.get("/status")
async def get_mcp_status():
    """Get MCP server status and available tools"""
    try:
        mcp_client = await get_mcp_client()
        status = await mcp_client.test_mcp_connection()
        
        return {
            "mcp_server": "GooseAI",
            "status": status,
            "capabilities": [
                "Tool calling",
                "Action execution",
                "Project generation",
                "Code generation",
                "Documentation creation",
                "Git operations",
                "Dependency management",
                "Project deployment"
            ]
        }
        
    except Exception as e:
        logger.error(f"Failed to get MCP status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tools")
async def get_available_tools():
    """Get list of available MCP tools"""
    try:
        mcp_client = await get_mcp_client()
        tools = await mcp_client.get_available_tools()
        
        return {
            "tools": tools,
            "total_tools": len(tools)
        }
        
    except Exception as e:
        logger.error(f"Failed to get available tools: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/execute", response_model=ToolExecutionResponse)
async def execute_tool(request: ToolExecutionRequest):
    """Execute a specific MCP tool"""
    try:
        logger.info(f"Executing MCP tool: {request.tool_name}", parameters=request.parameters)
        
        mcp_client = await get_mcp_client()
        result = await mcp_client.execute_tool(request.tool_name, request.parameters)
        
        return ToolExecutionResponse(
            success=result.get("success", False),
            tool=request.tool_name,
            result=result,
            message=result.get("message", "Tool executed")
        )
        
    except Exception as e:
        logger.error(f"Failed to execute tool {request.tool_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/create-project")
async def create_complete_project(project_request: Dict[str, Any]):
    """Create a complete project using MCP tools"""
    try:
        logger.info("Creating complete project using MCP", project_request=project_request)
        
        mcp_client = await get_mcp_client()
        
        # Step 1: Create project structure
        structure_result = await mcp_client.execute_tool("create_project_structure", {
            "project_name": project_request.get("project_name", "my-project"),
            "framework": project_request.get("framework", "react"),
            "backend": project_request.get("backend", "nodejs"),
            "database": project_request.get("database", "postgresql")
        })
        
        # Step 2: Generate key files
        files_to_generate = project_request.get("files", [])
        generated_files = []
        
        for file_spec in files_to_generate:
            file_result = await mcp_client.execute_tool("generate_code", {
                "file_type": file_spec.get("type"),
                "content": file_spec.get("content"),
                "framework": project_request.get("framework", "react")
            })
            generated_files.append(file_result)
        
        # Step 3: Create documentation
        doc_result = await mcp_client.execute_tool("create_documentation", {
            "doc_type": "readme",
            "project_info": f"Project: {project_request.get('project_name')}, Framework: {project_request.get('framework')}, Backend: {project_request.get('backend')}"
        })
        
        # Step 4: Initialize Git repository
        git_result = await mcp_client.execute_tool("execute_git_operations", {
            "operation": "init",
            "message": f"Initial commit for {project_request.get('project_name')}"
        })
        
        return {
            "success": True,
            "project_name": project_request.get("project_name"),
            "structure": structure_result,
            "files": generated_files,
            "documentation": doc_result,
            "git": git_result,
            "message": f"Complete project '{project_request.get('project_name')}' created successfully"
        }
        
    except Exception as e:
        logger.error(f"Failed to create complete project: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/deploy-project")
async def deploy_project(deploy_request: Dict[str, Any]):
    """Deploy project using MCP tools"""
    try:
        logger.info("Deploying project using MCP", deploy_request=deploy_request)
        
        mcp_client = await get_mcp_client()
        
        # Step 1: Install dependencies
        deps_result = await mcp_client.execute_tool("install_dependencies", {
            "package_manager": deploy_request.get("package_manager", "npm"),
            "dependencies": deploy_request.get("dependencies", [])
        })
        
        # Step 2: Deploy to platform
        deploy_result = await mcp_client.execute_tool("deploy_project", {
            "platform": deploy_request.get("platform", "vercel"),
            "project_path": deploy_request.get("project_path", ".")
        })
        
        return {
            "success": True,
            "dependencies": deps_result,
            "deployment": deploy_result,
            "message": f"Project deployed to {deploy_request.get('platform')} successfully"
        }
        
    except Exception as e:
        logger.error(f"Failed to deploy project: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def mcp_health_check():
    """Health check for MCP server"""
    try:
        mcp_client = await get_mcp_client()
        status = await mcp_client.test_mcp_connection()
        
        return {
            "mcp_server": "GooseAI",
            "status": "healthy" if status.get("status") == "available" else "unhealthy",
            "tools_available": status.get("tools_available", 0),
            "connection": status.get("status", "unknown")
        }
        
    except Exception as e:
        logger.error(f"MCP health check failed: {e}")
        return {
            "mcp_server": "GooseAI",
            "status": "unhealthy",
            "error": str(e)
        } 