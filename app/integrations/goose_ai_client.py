"""
GooseAI Client Integration for Documentation Generator
Provides access to multiple AI models through GooseAI's unified API
"""

import os
import json
import requests
from typing import Dict, List, Optional, Any
import structlog
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables from .env file
load_dotenv()

logger = structlog.get_logger(__name__)


class GooseAIClient:
    """GooseAI client for accessing multiple AI models"""
    
    def __init__(self):
        # Load API key from environment variable
        self.api_key = os.getenv('GOOSE_AI_API_KEY')
        self.base_url = "https://api.goose.ai/v1"
        self.available = bool(self.api_key)
        
        # Configure OpenAI client for GooseAI
        if self.available:
            try:
                self.client = OpenAI(
                    api_key=self.api_key,
                    base_url=self.base_url,
                    http_client=None  # Let OpenAI create its own client without proxies
                )
                logger.info("GooseAI client initialized successfully", api_key_length=len(self.api_key) if self.api_key else 0)
            except Exception as e:
                logger.error(f"Failed to initialize GooseAI client: {e}")
                self.client = None
                self.available = False
        else:
            self.client = None
            logger.warning("GooseAI client not available - missing API key")
    
    def _get_available_models(self) -> List[str]:
        """Get list of available models from GooseAI using direct API call"""
        try:
            if not self.available or not self.api_key:
                return []
            
            # Use direct HTTP request to get engines (GooseAI's term for models)
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            response = requests.get(f"{self.base_url}/engines", headers=headers)
            
            if response.status_code == 200:
                engines_data = response.json()
                engines = engines_data.get("data", [])
                return [engine.get("id") for engine in engines if engine.get("id")]
            else:
                logger.error(f"Failed to get engines: {response.status_code} - {response.text}")
                return []
                
        except Exception as e:
            logger.error("Failed to get available models", error=str(e))
            return []
    
    def _select_best_model(self, task_type: str = "conversation") -> str:
        """Select the best model for the given task"""
        available_models = self._get_available_models()
        
        # Model selection logic based on task type
        model_preferences = {
            "conversation": ["gpt-j-6b", "gpt-neo-20b", "gpt-neo-125m"],
            "documentation": ["gpt-j-6b", "gpt-neo-20b", "gpt-neo-125m"],
            "code": ["gpt-j-6b", "gpt-neo-20b", "gpt-neo-125m"],
            "analysis": ["gpt-j-6b", "gpt-neo-20b", "gpt-neo-125m"]
        }
        
        preferred_models = model_preferences.get(task_type, ["gpt-j-6b"])
        
        # Find the first available preferred model
        for model in preferred_models:
            if model in available_models:
                return model
        
        # Fallback to first available model
        return available_models[0] if available_models else "gpt-j-6b"
    
    async def generate_conversation_response(self, prompt: str, context: Dict[str, Any] = None) -> str:
        """Generate a natural conversation response using GooseAI"""
        
        if not self.available or not self.client:
            raise Exception("GooseAI not available - missing API key")
        
        try:
            # Select appropriate model for conversation
            model = self._select_best_model("conversation")
            
            # Build the full prompt with context
            full_prompt = prompt
            if context and context.get("conversation_history"):
                history = context["conversation_history"]
                full_prompt = f"Context: {json.dumps(history, indent=2)}\n\nUser: {prompt}\n\nAssistant:"
            
            # Generate response using GooseAI's completion API
            response = self.client.completions.create(
                model=model,
                prompt=full_prompt,
                max_tokens=512,
                temperature=0.7
            )
            return response.choices[0].text.strip()
                
        except Exception as e:
            logger.error("GooseAI generation failed", error=str(e))
            return "I'm having trouble responding right now. Please try again."
    
    async def generate_complete_project(self, project_idea: str, conversation_history: List[Dict]) -> Dict[str, Any]:
        """Generate complete project documentation using GooseAI"""
        
        if not self.available or not self.client:
            raise Exception("GooseAI not available - missing API key")
        
        try:
            # Select appropriate model for documentation
            model = self._select_best_model("documentation")
            
            # Build context from conversation history
            context = self._build_context(conversation_history)
            
            prompt = f"""You are creating documentation for a project. A user wants to build: {project_idea}. Based on the conversation history, create documentation that reflects what the user has shared.

Requirements:
- Use ALL information from the conversation
- Match the user's description and requirements
- Include their technology choices and features
- Be practical and actionable

Documentation to Create:
- Project overview (based on their description)
- Setup guide (using their technology choices)
- Implementation guide (based on their requirements)

Conversation Context:
{context}

Use This Information

Please provide the documentation in this JSON format:
{{
    "project_name": "Project name based on user description",
    "overview": "Project overview based on user's description",
    "setup_guide": "Setup guide using their technology choices",
    "implementation_guide": "Implementation guide based on their requirements",
    "backend": "Backend file contents using their tech choices",
    "frontend": "Frontend file contents using their tech choices",
    "config": "Configuration file contents",
    "dependencies": "Dependencies based on conversation info",
    "github_issues": "GitHub issues based on conversation info"
}}

Use ALL the information from the conversation to create relevant documentation. Make sure the documentation reflects what the user actually described about their project."""

            # Generate response using GooseAI's completion API
            response = self.client.completions.create(
                model=model,
                prompt=prompt,
                max_tokens=4000,
                temperature=0.3
            )
            response_text = response.choices[0].text.strip()
            
            # Parse the response
            return self._parse_response(response_text)
            
        except Exception as e:
            logger.error("Failed to generate complete project with GooseAI", error=str(e))
            return {
                "project_name": "Project",
                "overview": "Documentation generation failed. Please try again.",
                "setup_guide": "",
                "implementation_guide": "",
                "backend": "",
                "frontend": "",
                "config": "",
                "dependencies": [],
                "github_issues": []
            }
    
    def _build_context(self, conversation_history: List[Dict]) -> str:
        """Build context string from conversation history"""
        if not conversation_history:
            return "No previous conversation."
        
        context_parts = []
        for i, message in enumerate(conversation_history[-10:], 1):  # Last 10 messages
            role = message.get("role", "user")
            content = message.get("content", "")
            context_parts.append(f"{i}. {role.title()}: {content}")
        
        return "\n".join(context_parts)
    
    def _parse_response(self, response_text: str) -> Dict[str, Any]:
        """Parse GooseAI response into structured format"""
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
            logger.info("Successfully parsed GooseAI response", 
                       project_name=result.get("project_name"))
            return result
            
        except json.JSONDecodeError as e:
            logger.warning("Failed to parse GooseAI response as JSON", 
                          error=str(e), response=response_text[:200])
            
            # Fallback: return structured response
            return {
                "project_name": "project",
                "overview": response_text,
                "setup_guide": "",
                "implementation_guide": "",
                "backend": "",
                "frontend": "",
                "config": "",
                "dependencies": [],
                "github_issues": []
            }
    
    async def test_api_key(self) -> Dict[str, Any]:
        """Test GooseAI API key and connection"""
        if not self.available or not self.api_key:
            return {"status": "missing", "message": "No API key configured"}
        
        try:
            # Test by listing engines using direct API call
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            response = requests.get(f"{self.base_url}/engines", headers=headers)
            
            if response.status_code == 200:
                engines_data = response.json()
                engines = engines_data.get("data", [])
                engine_count = len(engines)
                
                logger.info("GooseAI API key test successful", engine_count=engine_count)
                return {
                    "status": "valid",
                    "message": f"Connected successfully. {engine_count} engines available.",
                    "engines": [engine.get("id") for engine in engines if engine.get("id")]
                }
            else:
                logger.error(f"GooseAI API test failed: {response.status_code} - {response.text}")
                return {
                    "status": "invalid",
                    "message": f"Connection failed: {response.status_code} - {response.text}"
                }
            
        except Exception as e:
            logger.error("GooseAI API key test failed", error=str(e))
            return {
                "status": "invalid",
                "message": f"Connection failed: {str(e)}"
            }
    
    async def get_available_models(self) -> List[str]:
        """Get list of available models"""
        return self._get_available_models()
    
    async def is_available(self) -> bool:
        """Check if GooseAI is available"""
        return self.available 