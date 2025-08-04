"""
Anthropic Client Integration for Web-Based Project Architect
Uses the Anthropic Python client for direct API access
"""

import os
import json
from typing import Dict, List, Optional, Any
import structlog
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from app.core.config import settings

logger = structlog.get_logger(__name__)


class AnthropicClient:
    """Direct Anthropic API client for project creation"""
    
    def __init__(self):
        # Load API key from environment variable
        self.api_key = os.getenv('ANTHROPIC_API_KEY')
        print(f"AnthropicClient init - API key found: {bool(self.api_key)}, length: {len(self.api_key) if self.api_key else 0}")
        logger.info(f"AnthropicClient init - API key found: {bool(self.api_key)}, length: {len(self.api_key) if self.api_key else 0}")
        
        # Initialize client
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize the Anthropic client with API key"""
        if not self.api_key or self.api_key == "your-claude-api-key-here":
            logger.warning("ANTHROPIC_API_KEY not found or set to placeholder value")
            self.client = None
            return
        
        try:
            import anthropic
            # Initialize client with explicit API key from environment
            self.client = anthropic.Anthropic(api_key=self.api_key)
            logger.info("Anthropic client initialized successfully", api_key_length=len(self.api_key))
        except ImportError:
            logger.error("Anthropic package not installed. Run: pip install anthropic")
            self.client = None
        except Exception as e:
            logger.error(f"Failed to initialize Anthropic client: {e}")
            self.client = None
    
    async def generate_conversation_response(self, prompt: str, context: Dict[str, Any] = None) -> str:
        """Generate a natural conversation response from Claude"""
        
        try:
            # Simple, natural prompt to Claude
            message = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=512,
                temperature=0.7,
                messages=[{"role": "user", "content": prompt}]
            )
            
            response_text = message.content[0].text
            logger.info("Generated conversation response", length=len(response_text))
            
            return response_text
            
        except Exception as e:
            logger.error(f"Error generating conversation response: {e}")
            return "I'm having trouble responding right now. Please try again."
    
    async def test_api_key(self) -> bool:
        """Test if the API key is working"""
        if not self.client:
            return False
        
        try:
            # Make a simple test call
            message = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=10,
                messages=[
                    {
                        "role": "user", 
                        "content": "Hello"
                    }
                ]
            )
            return True
        except Exception as e:
            logger.error(f"API key test failed: {e}")
            return False

    async def create_project_with_claude(self, project_idea: str, conversation_history: List[Dict]) -> Dict[str, Any]:
        """Create a project using Claude API with conversation context"""
        
        if not self.client:
            return {"error": "Anthropic client not available"}
        
        try:
            # Prepare conversation data
            conversation_data = {
                "project_idea": project_idea,
                "conversation_history": conversation_history,
                "instructions": self._get_project_creation_instructions()
            }
            
            # Create the prompt
            prompt = f"""
            You are an expert software architect helping create a new project. 
            
            Project Idea: {conversation_data['project_idea']}
            
            Conversation History: {json.dumps(conversation_data['conversation_history'], indent=2)}
            
            Instructions: {conversation_data['instructions']}
            
            Please provide your response in JSON format with the following structure:
            {{
                "project_name": "suggested-project-name",
                "description": "comprehensive project description",
                "architecture": {{
                    "backend": {{
                        "framework": "recommended framework",
                        "database": "database choice",
                        "api": "API design approach",
                        "security": "security considerations"
                    }},
                    "frontend": {{
                        "framework": "frontend framework",
                        "ui_library": "UI component library",
                        "state_management": "state management solution"
                    }},
                    "devops": {{
                        "deployment": "deployment strategy",
                        "ci_cd": "CI/CD approach",
                        "monitoring": "monitoring and logging"
                    }}
                }},
                "documentation": {{
                    "architecture_docs": ["list of architecture documents to create"],
                    "technical_docs": ["list of technical documents"],
                    "business_docs": ["list of business documents"]
                }},
                "repositories": [
                    {{
                        "name": "repository-name",
                        "description": "repository description",
                        "type": "backend|frontend|docs|infrastructure"
                    }}
                ],
                "next_steps": ["list of immediate next steps"],
                "estimated_timeline": "estimated development timeline"
            }}
            """
            
            # Get response from Claude
            message = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=4000,
                temperature=0.7,
                messages=[{"role": "user", "content": prompt}]
            )
            
            response_text = message.content[0].text
            
            # Parse the response
            return self._parse_claude_response(response_text)
            
        except Exception as e:
            logger.error(f"Error creating project with Claude: {e}")
            return {"error": str(e)}
    
    def _get_project_creation_instructions(self) -> str:
        """Get instructions for Claude project creation"""
        return """
        You are an expert software architect helping someone create a new project. 
        
        Your task is to:
        1. Analyze the project idea and conversation history
        2. Generate a comprehensive project architecture
        3. Create detailed documentation
        4. Provide repository structure recommendations
        
        Be specific and provide actionable recommendations.
        """
    
    def _parse_claude_response(self, response_text: str) -> Dict[str, Any]:
        """Parse Claude's response and extract structured data"""
        
        try:
            # Try to extract JSON from the response
            # Claude might wrap JSON in markdown code blocks
            if "```json" in response_text:
                start = response_text.find("```json") + 7
                end = response_text.find("```", start)
                json_str = response_text[start:end].strip()
            elif "```" in response_text:
                start = response_text.find("```") + 3
                end = response_text.find("```", start)
                json_str = response_text[start:end].strip()
            else:
                # Try to find JSON in the response
                json_str = response_text
            
            # Parse JSON
            result = json.loads(json_str)
            logger.info("Successfully parsed Claude response", 
                       project_name=result.get("project_name"))
            return result
            
        except json.JSONDecodeError as e:
            logger.warning("Failed to parse Claude response as JSON", 
                          error=str(e), response=response_text[:200])
            
            # Fallback: return structured response
            return {
                "project_name": "project",
                "description": response_text,
                "architecture": {},
                "documentation": {},
                "repositories": [],
                "next_steps": [],
                "estimated_timeline": "3-4 weeks",
                "raw_response": response_text
            }
    
    async def generate_architecture_diagram(self, architecture_spec: Dict[str, Any]) -> str:
        """Generate architecture diagram using Claude"""
        
        if not self.client:
            return ""
        
        diagram_prompt = f"""
        Create a Mermaid.js architecture diagram for this project:
        
        {json.dumps(architecture_spec, indent=2)}
        
        Please provide only the Mermaid.js code without any markdown formatting.
        """
        
        try:
            message = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=2000,
                temperature=0.3,
                messages=[{"role": "user", "content": diagram_prompt}]
            )
            
            diagram_code = message.content[0].text.strip()
            
            # Clean up any markdown formatting
            if "```mermaid" in diagram_code:
                start = diagram_code.find("```mermaid") + 10
                end = diagram_code.find("```", start)
                diagram_code = diagram_code[start:end].strip()
            
            logger.info("Generated architecture diagram", length=len(diagram_code))
            return diagram_code
            
        except Exception as e:
            logger.error(f"Error generating architecture diagram: {e}")
            return ""
    
    async def generate_documentation(self, project_spec: Dict[str, Any], doc_type: str) -> str:
        """Generate specific documentation using Claude"""
        
        if not self.client:
            return ""
        
        doc_prompts = {
            "architecture": """
            Create a comprehensive architecture document for this project.
            Include system overview, component diagrams, technology choices, and deployment strategy.
            """,
            "api_spec": """
            Create a detailed API specification document.
            Include endpoints, request/response formats, authentication, and examples.
            """,
            "deployment": """
            Create a deployment guide with step-by-step instructions.
            Include environment setup, configuration, and deployment procedures.
            """,
            "marketing": """
            Create a marketing strategy document.
            Include target audience, value proposition, go-to-market strategy, and business model.
            """
        }
        
        prompt = f"""
        {doc_prompts.get(doc_type, "Create a comprehensive document for this project.")}
        
        Project specification:
        {json.dumps(project_spec, indent=2)}
        
        Please provide the document in Markdown format.
        """
        
        try:
            message = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=4000,
                temperature=0.7,
                messages=[{"role": "user", "content": prompt}]
            )
            
            document = message.content[0].text.strip()
            logger.info(f"Generated {doc_type} documentation", length=len(document))
            return document
            
        except Exception as e:
            logger.error(f"Error generating {doc_type} documentation: {e}")
            return ""

    async def generate_complete_project(self, project_idea: str, conversation_history: List[Dict], libraries: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate comprehensive technical documentation and project structure"""
        
        try:
            # Build conversation context
            conversation_context = self._build_conversation_context(conversation_history)
            
            # Create comprehensive documentation prompt
            prompt = f"""
            You are creating documentation for a project. A user wants to build: {project_idea}
            
            Based on the conversation history, create documentation that reflects what the user has shared.
            
            **Requirements:**
            1. Use all the information from the conversation
            2. Create documentation that matches what the user described
            3. Include any technology choices they mentioned
            4. Cover the features and functionality they discussed
            5. Make it practical and ready to use
            
            **Documentation to Create:**
            - Project overview (based on their description)
            - Setup guide (using their technology choices)
            - Implementation guide (based on their requirements)
            
            **File Structure to Generate:**
            ```
            docs/
            ├── overview.md
            ├── setup.md
            └── implementation.md
            ```
            
            **Conversation Context (Use This Information):**
            {conversation_context}
            
            Generate a JSON response with this structure:
            {{
                "project_name": "Project Name based on conversation",
                "description": "Project description based on what user shared",
                "file_structure": {{
                    "docs": {{
                        "overview.md": {{
                            "content": "Project overview based on user's description"
                        }},
                        "setup.md": {{
                            "content": "Setup instructions using technology choices mentioned"
                        }},
                        "implementation.md": {{
                            "content": "Implementation guide based on user's requirements"
                        }}
                    }},
                    "backend": [
                        {{
                            "path": "backend/main.py",
                            "content": "Backend starter using technology choices mentioned"
                        }},
                        {{
                            "path": "backend/requirements.txt",
                            "content": "Dependencies based on technology stack mentioned"
                        }}
                    ],
                    "frontend": [
                        {{
                            "path": "frontend/package.json",
                            "content": "Frontend dependencies based on choices mentioned"
                        }},
                        {{
                            "path": "frontend/src/App.js",
                            "content": "Frontend starter based on technology mentioned"
                        }}
                    ],
                    "config": [
                        {{
                            "path": "README.md",
                            "content": "Project overview and setup based on conversation"
                        }}
                    ]
                }},
                "dependencies": {{
                    "backend": ["dependencies based on technology mentioned"],
                    "frontend": ["dependencies based on technology mentioned"]
                }},
                "github_issues": [
                    {{
                        "title": "Project setup and implementation",
                        "description": "Implementation tasks based on user's requirements",
                        "labels": ["documentation", "setup", "implementation"]
                    }}
                ]
            }}
            
            Use ALL the information from the conversation to create relevant documentation. Make sure the documentation reflects what the user actually described about their project."""
            
            # Get comprehensive response from Claude
            message = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=8000,
                temperature=0.7,
                messages=[{"role": "user", "content": prompt}]
            )
            
            response_text = message.content[0].text
            
            # Parse the comprehensive response
            return self._parse_complete_project_response(response_text)
            
        except Exception as e:
            logger.error(f"Error generating complete project: {e}")
            return {"error": str(e)}
    
    def _get_complete_project_instructions(self) -> str:
        """Get instructions for complete project generation"""
        return """
        You are an expert software architect creating a complete project structure.
        
        Your task is to:
        1. Analyze the project idea and conversation history
        2. Define all necessary libraries and dependencies
        3. Generate complete file structures for all components
        4. Create proper poetry/pip configurations
        5. Generate comprehensive documentation
        6. Create GitHub repository structures
        7. Generate initial GitHub issues
        8. Create claude.md guides for project development
        
        Be comprehensive and provide complete, working code for all files.
        Include all necessary imports, configurations, and dependencies.
        """
    
    def _parse_complete_project_response(self, response_text: str) -> Dict[str, Any]:
        """Parse Claude's complete project response"""
        
        try:
            # Try to extract JSON from the response
            if "```json" in response_text:
                start = response_text.find("```json") + 7
                end = response_text.find("```", start)
                json_str = response_text[start:end].strip()
            elif "```" in response_text:
                start = response_text.find("```") + 3
                end = response_text.find("```", start)
                json_str = response_text[start:end].strip()
            else:
                json_str = response_text
            
            # Parse JSON
            result = json.loads(json_str)
            logger.info("Successfully parsed complete project response", 
                       project_name=result.get("project_name"))
            return result
            
        except json.JSONDecodeError as e:
            logger.warning("Failed to parse complete project response as JSON", 
                          error=str(e), response=response_text[:200])
            
            # Fallback: return structured response
            return {
                "project_name": "project",
                "description": response_text,
                "file_structure": {},
                "repositories": [],
                "dependencies": {},
                "github_issues": [],
                "claude_guide": {},
                "deployment": {},
                "raw_response": response_text
            }


# Global instance
anthropic_client = AnthropicClient() 