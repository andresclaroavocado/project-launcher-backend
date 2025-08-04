"""
Multi-Model Service for Documentation Generator
Orchestrates between Anthropic (Claude) and GooseAI for optimal performance
"""

import asyncio
from typing import Dict, List, Optional, Any
import structlog
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from app.integrations.anthropic_client import AnthropicClient
from app.integrations.goose_ai_client import GooseAIClient

logger = structlog.get_logger(__name__)


class MultiModelService:
    """Service that orchestrates multiple AI models for optimal performance"""
    
    def __init__(self):
        # Initialize both clients
        self.anthropic_client = AnthropicClient()
        self.goose_ai_client = GooseAIClient()
        
        # Model preferences and fallback strategy
        self.model_preferences = {
            "conversation": ["anthropic", "goose_ai"],
            "documentation": ["anthropic", "goose_ai"],
            "code": ["anthropic", "goose_ai"],
            "analysis": ["anthropic", "goose_ai"]
        }
        
        # Track model performance for optimization
        self.model_performance = {
            "anthropic": {"success": 0, "failure": 0, "avg_response_time": 0},
            "goose_ai": {"success": 0, "failure": 0, "avg_response_time": 0}
        }
        
        logger.info("MultiModelService initialized", 
                   anthropic_available=self.anthropic_client.client is not None,
                   goose_ai_available=self.goose_ai_client.available)
    
    async def generate_conversation_response(self, prompt: str, context: Dict[str, Any] = None) -> str:
        """Generate conversation response using the best available model"""
        
        # Try Anthropic first (preferred for conversation)
        if self.anthropic_client.client:
            try:
                start_time = asyncio.get_event_loop().time()
                response = await self.anthropic_client.generate_conversation_response(prompt, context)
                end_time = asyncio.get_event_loop().time()
                
                # Update performance metrics
                self._update_performance("anthropic", True, end_time - start_time)
                logger.info("Generated response with Anthropic", response_length=len(response))
                return response
                
            except Exception as e:
                logger.warning("Anthropic failed, trying GooseAI", error=str(e))
                self._update_performance("anthropic", False, 0)
        
        # Fallback to GooseAI
        if self.goose_ai_client.available:
            try:
                start_time = asyncio.get_event_loop().time()
                response = await self.goose_ai_client.generate_conversation_response(prompt, context)
                end_time = asyncio.get_event_loop().time()
                
                # Update performance metrics
                self._update_performance("goose_ai", True, end_time - start_time)
                logger.info("Generated response with GooseAI", response_length=len(response))
                return response
                
            except Exception as e:
                logger.error("GooseAI also failed", error=str(e))
                self._update_performance("goose_ai", False, 0)
        
        # If both fail, return a basic response
        return "I'm having trouble responding right now. Please try again."
    
    async def generate_complete_project(self, project_idea: str, conversation_history: List[Dict]) -> Dict[str, Any]:
        """Generate complete project documentation using the best available model"""
        
        # Try Anthropic first (preferred for documentation)
        if self.anthropic_client.client:
            try:
                start_time = asyncio.get_event_loop().time()
                response = await self.anthropic_client.generate_complete_project(project_idea, conversation_history)
                end_time = asyncio.get_event_loop().time()
                
                # Update performance metrics
                self._update_performance("anthropic", True, end_time - start_time)
                logger.info("Generated project with Anthropic", project_name=response.get("project_name"))
                return response
                
            except Exception as e:
                logger.warning("Anthropic failed for project generation, trying GooseAI", error=str(e))
                self._update_performance("anthropic", False, 0)
        
        # Fallback to GooseAI
        if self.goose_ai_client.available:
            try:
                start_time = asyncio.get_event_loop().time()
                response = await self.goose_ai_client.generate_complete_project(project_idea, conversation_history)
                end_time = asyncio.get_event_loop().time()
                
                # Update performance metrics
                self._update_performance("goose_ai", True, end_time - start_time)
                logger.info("Generated project with GooseAI", project_name=response.get("project_name"))
                return response
                
            except Exception as e:
                logger.error("GooseAI also failed for project generation", error=str(e))
                self._update_performance("goose_ai", False, 0)
        
        # If both fail, return a basic response
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
    
    async def test_all_models(self) -> Dict[str, Any]:
        """Test all available models and return status"""
        results = {}
        
        # Test Anthropic
        if self.anthropic_client.client:
            try:
                anthropic_status = await self.anthropic_client.test_api_key()
                results["anthropic"] = anthropic_status
            except Exception as e:
                results["anthropic"] = {"status": "error", "message": str(e)}
        else:
            results["anthropic"] = {"status": "missing", "message": "No API key configured"}
        
        # Test GooseAI
        if self.goose_ai_client.available:
            try:
                goose_ai_status = await self.goose_ai_client.test_api_key()
                results["goose_ai"] = goose_ai_status
            except Exception as e:
                results["goose_ai"] = {"status": "error", "message": str(e)}
        else:
            results["goose_ai"] = {"status": "missing", "message": "No API key configured"}
        
        # Get available models from GooseAI
        if self.goose_ai_client.available:
            try:
                available_models = await self.goose_ai_client.get_available_models()
                results["goose_ai"]["available_models"] = available_models
            except Exception as e:
                results["goose_ai"]["available_models"] = []
        
        return results
    
    def _update_performance(self, model: str, success: bool, response_time: float):
        """Update performance metrics for a model"""
        if model not in self.model_performance:
            return
        
        if success:
            self.model_performance[model]["success"] += 1
            # Update average response time
            current_avg = self.model_performance[model]["avg_response_time"]
            success_count = self.model_performance[model]["success"]
            self.model_performance[model]["avg_response_time"] = (
                (current_avg * (success_count - 1) + response_time) / success_count
            )
        else:
            self.model_performance[model]["failure"] += 1
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics for all models"""
        stats = {}
        
        for model, metrics in self.model_performance.items():
            total_requests = metrics["success"] + metrics["failure"]
            success_rate = (metrics["success"] / total_requests * 100) if total_requests > 0 else 0
            
            stats[model] = {
                "total_requests": total_requests,
                "success_rate": round(success_rate, 2),
                "avg_response_time": round(metrics["avg_response_time"], 3),
                "success_count": metrics["success"],
                "failure_count": metrics["failure"]
            }
        
        return stats
    
    async def get_available_models(self) -> Dict[str, List[str]]:
        """Get available models from all providers"""
        models = {}
        
        # Anthropic models (hardcoded since we know what's available)
        models["anthropic"] = ["claude-3-5-sonnet-20241022"]
        
        # GooseAI models
        if self.goose_ai_client.available:
            try:
                goose_models = await self.goose_ai_client.get_available_models()
                models["goose_ai"] = goose_models
            except Exception as e:
                logger.error("Failed to get GooseAI models", error=str(e))
                models["goose_ai"] = []
        else:
            models["goose_ai"] = []
        
        return models
    
    def get_model_recommendations(self) -> Dict[str, str]:
        """Get model recommendations based on performance"""
        recommendations = {}
        
        for task_type in ["conversation", "documentation", "code", "analysis"]:
            # Simple recommendation logic based on success rates
            anthropic_success_rate = self.model_performance["anthropic"]["success"] / max(
                self.model_performance["anthropic"]["success"] + self.model_performance["anthropic"]["failure"], 1
            )
            goose_ai_success_rate = self.model_performance["goose_ai"]["success"] / max(
                self.model_performance["goose_ai"]["success"] + self.model_performance["goose_ai"]["failure"], 1
            )
            
            if anthropic_success_rate >= goose_ai_success_rate:
                recommendations[task_type] = "anthropic"
            else:
                recommendations[task_type] = "goose_ai"
        
        return recommendations 