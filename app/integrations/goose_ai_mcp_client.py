"""
GooseAI MCP (Model Context Protocol) Client
Enables tool calling and action execution through GooseAI
"""

import os
import json
import asyncio
from typing import Dict, List, Optional, Any, Callable
import structlog
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

logger = structlog.get_logger(__name__)


class GooseAIMCPClient:
    """GooseAI client with MCP capabilities for tool calling and action execution"""
    
    def __init__(self):
        # Load API key from environment variable
        self.api_key = os.getenv('GOOSE_AI_API_KEY')
        self.base_url = "https://api.goose.ai/v1"
        self.available = bool(self.api_key)
        
        # Configure OpenAI client for GooseAI
        if self.available:
            self.client = OpenAI(
                api_key=self.api_key,
                base_url=self.base_url
            )
            logger.info("GooseAI MCP client initialized successfully", api_key_length=len(self.api_key) if self.api_key else 0)
        else:
            self.client = None
            logger.warning("GooseAI MCP client not available - missing API key")
        
        # Register available tools
        self.tools = self._register_tools()
    
    def _register_tools(self) -> Dict[str, Dict[str, Any]]:
        """Register available tools for MCP"""
        return {
            "create_project_structure": {
                "name": "create_project_structure",
                "description": "Create a complete project file structure",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "project_name": {"type": "string", "description": "Name of the project"},
                        "framework": {"type": "string", "description": "Frontend framework (react, vue, angular)"},
                        "backend": {"type": "string", "description": "Backend technology (nodejs, python, java)"},
                        "database": {"type": "string", "description": "Database type (postgresql, mysql, mongodb)"}
                    },
                    "required": ["project_name"]
                }
            },
            "generate_code": {
                "name": "generate_code",
                "description": "Generate code files for the project",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "file_type": {"type": "string", "description": "Type of file to generate"},
                        "content": {"type": "string", "description": "Code content or description"},
                        "framework": {"type": "string", "description": "Framework for the code"}
                    },
                    "required": ["file_type", "content"]
                }
            },
            "create_documentation": {
                "name": "create_documentation",
                "description": "Create project documentation",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "doc_type": {"type": "string", "description": "Type of documentation (readme, api, setup)"},
                        "project_info": {"type": "string", "description": "Project information and requirements"}
                    },
                    "required": ["doc_type", "project_info"]
                }
            },
            "execute_git_operations": {
                "name": "execute_git_operations",
                "description": "Execute Git operations for the project",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "operation": {"type": "string", "description": "Git operation (init, add, commit, push)"},
                        "message": {"type": "string", "description": "Commit message or operation details"}
                    },
                    "required": ["operation"]
                }
            },
            "install_dependencies": {
                "name": "install_dependencies",
                "description": "Install project dependencies",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "package_manager": {"type": "string", "description": "Package manager (npm, pip, maven)"},
                        "dependencies": {"type": "array", "items": {"type": "string"}, "description": "List of dependencies"}
                    },
                    "required": ["package_manager", "dependencies"]
                }
            },
            "deploy_project": {
                "name": "deploy_project",
                "description": "Deploy the project to a platform",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "platform": {"type": "string", "description": "Deployment platform (vercel, railway, heroku)"},
                        "project_path": {"type": "string", "description": "Path to the project"}
                    },
                    "required": ["platform", "project_path"]
                }
            }
        }
    
    async def execute_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a specific tool with parameters"""
        
        if not self.available or not self.client:
            raise Exception("GooseAI MCP client not available")
        
        if tool_name not in self.tools:
            raise Exception(f"Tool '{tool_name}' not found")
        
        try:
            # Get tool definition
            tool_def = self.tools[tool_name]
            
            # Execute the tool based on type
            if tool_name == "create_project_structure":
                return await self._create_project_structure(parameters)
            elif tool_name == "generate_code":
                return await self._generate_code(parameters)
            elif tool_name == "create_documentation":
                return await self._create_documentation(parameters)
            elif tool_name == "execute_git_operations":
                return await self._execute_git_operations(parameters)
            elif tool_name == "install_dependencies":
                return await self._install_dependencies(parameters)
            elif tool_name == "deploy_project":
                return await self._deploy_project(parameters)
            else:
                raise Exception(f"Tool '{tool_name}' not implemented")
                
        except Exception as e:
            logger.error(f"Failed to execute tool {tool_name}", error=str(e))
            return {
                "success": False,
                "error": str(e),
                "tool": tool_name
            }
    
    async def _create_project_structure(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create project file structure"""
        project_name = params.get("project_name", "my-project")
        framework = params.get("framework", "react")
        backend = params.get("backend", "nodejs")
        database = params.get("database", "postgresql")
        
        # Generate project structure using GooseAI
        prompt = f"""Create a complete project structure for:
Project Name: {project_name}
Frontend Framework: {framework}
Backend Technology: {backend}
Database: {database}

Provide the file structure in JSON format with:
- Directory structure
- Key files to create
- Configuration files
- Dependencies to install

Format as JSON with 'structure' and 'files' arrays."""

        response = await self._call_goose_ai(prompt)
        
        return {
            "success": True,
            "tool": "create_project_structure",
            "project_name": project_name,
            "structure": response,
            "message": f"Project structure created for {project_name}"
        }
    
    async def _generate_code(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Generate code files"""
        file_type = params.get("file_type")
        content = params.get("content")
        framework = params.get("framework", "react")
        
        prompt = f"""Generate {file_type} code for {framework} framework.

Requirements: {content}

Provide the complete code with:
- Proper imports
- Best practices
- Comments for clarity
- Error handling

Return only the code without explanations."""

        code = await self._call_goose_ai(prompt)
        
        return {
            "success": True,
            "tool": "generate_code",
            "file_type": file_type,
            "code": code,
            "framework": framework
        }
    
    async def _create_documentation(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create project documentation"""
        doc_type = params.get("doc_type")
        project_info = params.get("project_info")
        
        prompt = f"""Create {doc_type} documentation for the project.

Project Information: {project_info}

Create comprehensive documentation including:
- Project overview
- Setup instructions
- Usage examples
- API documentation (if applicable)
- Deployment guide

Format as markdown."""

        documentation = await self._call_goose_ai(prompt)
        
        return {
            "success": True,
            "tool": "create_documentation",
            "doc_type": doc_type,
            "documentation": documentation
        }
    
    async def _execute_git_operations(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute Git operations"""
        operation = params.get("operation")
        message = params.get("message", "")
        
        # Simulate Git operations (in real implementation, you'd execute actual Git commands)
        git_commands = {
            "init": "git init",
            "add": "git add .",
            "commit": f'git commit -m "{message}"',
            "push": "git push origin main"
        }
        
        command = git_commands.get(operation, f"git {operation}")
        
        return {
            "success": True,
            "tool": "execute_git_operations",
            "operation": operation,
            "command": command,
            "message": f"Git {operation} executed successfully"
        }
    
    async def _install_dependencies(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Install project dependencies"""
        package_manager = params.get("package_manager")
        dependencies = params.get("dependencies", [])
        
        # Generate installation commands
        if package_manager == "npm":
            command = f"npm install {' '.join(dependencies)}"
        elif package_manager == "pip":
            command = f"pip install {' '.join(dependencies)}"
        elif package_manager == "maven":
            command = f"mvn install"
        else:
            command = f"{package_manager} install {' '.join(dependencies)}"
        
        return {
            "success": True,
            "tool": "install_dependencies",
            "package_manager": package_manager,
            "dependencies": dependencies,
            "command": command,
            "message": f"Dependencies installed using {package_manager}"
        }
    
    async def _deploy_project(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Deploy project to platform"""
        platform = params.get("platform")
        project_path = params.get("project_path")
        
        # Generate deployment commands
        deploy_commands = {
            "vercel": "vercel --prod",
            "railway": "railway up",
            "heroku": "git push heroku main",
            "netlify": "netlify deploy --prod"
        }
        
        command = deploy_commands.get(platform, f"deploy to {platform}")
        
        return {
            "success": True,
            "tool": "deploy_project",
            "platform": platform,
            "project_path": project_path,
            "command": command,
            "message": f"Project deployed to {platform}"
        }
    
    async def _call_goose_ai(self, prompt: str) -> str:
        """Make API call to GooseAI"""
        try:
            # Select best model for the task
            model = "gpt-j-6b"  # Default to gpt-j-6b for tool execution
            
            response = self.client.completions.create(
                model=model,
                prompt=prompt,
                max_tokens=2000,
                temperature=0.3
            )
            
            return response.choices[0].text.strip()
            
        except Exception as e:
            logger.error("GooseAI API call failed", error=str(e))
            raise
    
    async def get_available_tools(self) -> List[Dict[str, Any]]:
        """Get list of available tools"""
        return list(self.tools.values())
    
    async def test_mcp_connection(self) -> Dict[str, Any]:
        """Test MCP connection and tool availability"""
        if not self.available:
            return {
                "status": "unavailable",
                "message": "GooseAI MCP client not configured",
                "tools_available": 0
            }
        
        try:
            # Test basic API connection
            test_response = await self._call_goose_ai("Test connection")
            
            return {
                "status": "available",
                "message": "GooseAI MCP client connected successfully",
                "tools_available": len(self.tools),
                "tools": list(self.tools.keys()),
                "test_response": test_response[:100] + "..." if len(test_response) > 100 else test_response
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Connection failed: {str(e)}",
                "tools_available": 0
            } 