"""
LLM Orchestrator Service for Web-Based Project Architect
Coordinates multiple LLM providers including Anthropic API and GooseAI
"""

import asyncio
from typing import Dict, List, Optional, Any
import json
import structlog
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from app.core.config import settings, LLM_PROVIDERS
from app.integrations.anthropic_client import AnthropicClient
from app.integrations.goose_ai import GooseAIIntegration

logger = structlog.get_logger(__name__)


class LLMOrchestrator:
    """Orchestrates multiple LLM providers for enhanced project creation"""
    
    def __init__(self):
        try:
            self.goose_ai = GooseAIIntegration()
        except Exception as e:
            logger.warning(f"Failed to initialize GooseAI: {e}")
            self.goose_ai = None
            
        # Create our own AnthropicClient instance
        self.anthropic_client = AnthropicClient()
        self.active_providers = self._get_active_providers()
        
    def _get_active_providers(self) -> Dict[str, bool]:
        """Get list of active LLM providers"""
        return {
            "goose_ai": LLM_PROVIDERS["goose_ai"]["enabled"] and self.goose_ai is not None,
            "anthropic": True,  # Always try Anthropic client if available
        }
    
    async def initialize(self):
        """Initialize all LLM providers"""
        logger.info("Initializing LLM Orchestrator")
        
        # Initialize GooseAI
        if self.active_providers["goose_ai"]:
            try:
                # GooseAI doesn't need explicit initialization
                logger.info("GooseAI initialized successfully")
            except Exception as e:
                logger.error("Failed to initialize GooseAI", error=str(e))
                self.active_providers["goose_ai"] = False
        
        logger.info("LLM Orchestrator initialized", active_providers=self.active_providers)
    
    async def generate_response(self, prompt: str, provider: str = "auto", context: Dict[str, Any] = None) -> str:
        """Generate response using specified or best available provider"""
        
        if provider == "auto":
            # Use the default provider from settings, fallback to best available
            try:
                provider = settings.DEFAULT_LLM_PROVIDER
                if not self.active_providers.get(provider, False):
                    provider = self._select_best_provider(context)
            except:
                provider = self._select_best_provider(context)
        
        if not self.active_providers.get(provider, False):
            raise ValueError(f"Provider {provider} is not available")
        
        try:
            if provider == "anthropic":
                return await self._generate_with_anthropic(prompt, context)
            elif provider == "goose_ai":
                return await self._generate_with_goose_ai(prompt, context)
            else:
                raise ValueError(f"Unknown provider: {provider}")
                
        except Exception as e:
            logger.error(f"Error generating response with {provider}", error=str(e))
            # Fallback to another provider
            return await self._fallback_response(prompt, provider, context)
    
    def _select_best_provider(self, context: Dict[str, Any] = None) -> str:
        """Select the best provider based on context and availability"""
        
        # Priority order based on capabilities
        priority_order = ["anthropic", "goose_ai"]
        
        for provider in priority_order:
            if self.active_providers.get(provider, False):
                return provider
        
        raise ValueError("No LLM providers are available")
    

    
    async def _generate_with_anthropic(self, prompt: str, context: Dict[str, Any] = None) -> str:
        """Generate response using Anthropic API client"""
        
        try:
            if not self.anthropic_client.client:
                raise Exception("Anthropic client not available")
            
            # Use the Anthropic client to generate conversation response
            response = await self.anthropic_client.generate_conversation_response(
                prompt=prompt,
                context=context
            )
            
            return response
                
        except Exception as e:
            logger.error("Anthropic generation failed", error=str(e))
            raise
    
    async def _generate_with_goose_ai(self, prompt: str, context: Dict[str, Any] = None) -> str:
        """Generate response using GooseAI"""
        
        try:
            if self.goose_ai is None:
                raise Exception("GooseAI not available")
                
            response = await self.goose_ai.generate_response(prompt, context)
            return str(response)
        except Exception as e:
            logger.error("GooseAI generation failed", error=str(e))
            raise
    

    async def _fallback_response(self, prompt: str, failed_provider: str, context: Dict[str, Any] = None) -> str:
        """Generate fallback response using another provider"""
        
        fallback_providers = ["goose_ai"]
        
        # Safely remove the failed provider from the list
        if failed_provider in fallback_providers:
            fallback_providers.remove(failed_provider)
        
        for provider in fallback_providers:
            if self.active_providers.get(provider, False):
                try:
                    logger.info(f"Trying fallback provider: {provider}")
                    return await self.generate_response(prompt, provider, context)
                except Exception as e:
                    logger.error(f"Fallback provider {provider} also failed", error=str(e))
                    continue
        
        # If all providers fail, return a basic response
        return "I'm having trouble generating a response right now. Please try again later."
    
    async def generate_architecture(self, project_idea: str, conversation_history: List[Dict]) -> Dict[str, Any]:
        """Generate comprehensive architecture using Anthropic API"""
        
        if not self.active_providers["anthropic"]:
            raise ValueError("Anthropic API is not available for architecture generation")
        
        try:
            # Use Anthropic API for architecture generation
            architecture = await self.anthropic_client.create_project_with_claude(
                project_idea=project_idea,
                conversation_history=conversation_history
            )
            
            # Generate architecture diagram
            if "architecture" in architecture:
                diagram = await self.anthropic_client.generate_architecture_diagram(
                    architecture["architecture"]
                )
                architecture["architecture_diagram"] = diagram
            
            return architecture
            
        except Exception as e:
            logger.error("Failed to generate architecture with Claude CLI", error=str(e))
            raise
    
    async def generate_documentation(self, project_spec: Dict[str, Any], doc_type: str) -> str:
        """Generate documentation using Anthropic API"""
        
        if not self.active_providers["anthropic"]:
            raise ValueError("Anthropic API is not available for documentation generation")
        
        try:
            return await self.anthropic_client.generate_documentation(project_spec, doc_type)
        except Exception as e:
            logger.error(f"Failed to generate {doc_type} documentation", error=str(e))
            raise
    
    async def create_repository_structure(self, project_spec: Dict[str, Any]) -> Dict[str, Any]:
        """Create repository structure using Anthropic API"""
        
        if not self.active_providers["anthropic"]:
            raise ValueError("Anthropic API is not available for repository structure creation")
        
        try:
            return await self.anthropic_client.create_repository_structure(project_spec)
        except Exception as e:
            logger.error("Failed to create repository structure", error=str(e))
            raise
    
    async def generate_complete_project(self, project_idea: str, conversation_history: List[Dict], libraries: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate complete project with all files, repositories, and documentation"""
        
        if not self.active_providers["anthropic"]:
            raise ValueError("Anthropic API is not available for complete project generation")
        
        try:
            return await self.anthropic_client.generate_complete_project(
                project_idea=project_idea,
                conversation_history=conversation_history,
                libraries=libraries
            )
        except Exception as e:
            logger.error("Failed to generate complete project", error=str(e))
            raise
    
    async def multi_llm_conversation(self, messages: List[Dict], providers: List[str] = None) -> List[Dict]:
        """Conduct a conversation using multiple LLM providers"""
        
        if not providers:
            providers = [p for p, active in self.active_providers.items() if active]
        
        conversation_results = []
        
        for provider in providers:
            if not self.active_providers.get(provider, False):
                continue
            
            try:
                # Combine all messages into a single prompt
                combined_prompt = self._combine_messages(messages)
                
                response = await self.generate_response(
                    prompt=combined_prompt,
                    provider=provider,
                    context={"conversation_history": messages}
                )
                
                conversation_results.append({
                    "provider": provider,
                    "response": response,
                    "status": "success"
                })
                
            except Exception as e:
                logger.error(f"Provider {provider} failed in multi-LLM conversation", error=str(e))
                conversation_results.append({
                    "provider": provider,
                    "response": None,
                    "status": "failed",
                    "error": str(e)
                })
        
        return conversation_results
    
    def _combine_messages(self, messages: List[Dict]) -> str:
        """Combine conversation messages into a single prompt"""
        
        combined = []
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            combined.append(f"{role.title()}: {content}")
        
        return "\n\n".join(combined)
    
    async def get_provider_status(self) -> Dict[str, Any]:
        """Get status of all LLM providers"""
        
        status = {}
        
        for provider, active in self.active_providers.items():
            status[provider] = {
                "active": active,
                "config": LLM_PROVIDERS.get(provider, {})
            }
        
        return status
    
    async def cleanup(self):
        """Clean up resources"""
        
        try:
            # Clean up any resources if needed
            logger.info("LLM Orchestrator cleanup completed")
        except Exception as e:
            logger.error("Error during LLM Orchestrator cleanup", error=str(e)) 