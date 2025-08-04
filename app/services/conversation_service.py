"""
Multi-Model Conversation Service
Uses both Anthropic (Claude) and GooseAI for optimal performance
"""

import uuid
from typing import Dict, Any
from datetime import datetime
import structlog

from app.services.multi_model_service import MultiModelService

logger = structlog.get_logger(__name__)


class ConversationService:
    """Service that uses multiple AI models for natural conversation"""
    
    def __init__(self):
        self.multi_model_service = MultiModelService()
        self.conversations: Dict[str, Dict[str, Any]] = {}
    
    async def start_conversation(self, project_idea: str) -> Dict[str, Any]:
        """Start a natural conversation about the project"""
        conversation_id = str(uuid.uuid4())
        
        # Create conversation
        conversation = {
            "id": conversation_id,
            "project_idea": project_idea,
            "messages": [],
            "started_at": datetime.utcnow().isoformat(),
            "last_activity": datetime.utcnow().isoformat(),
            "phase": "conversation"
        }
        
        # Let AI respond naturally to the project idea
        initial_response = await self.multi_model_service.generate_conversation_response(
            f"""You are a helpful AI assistant. A user wants to build: {project_idea}

Respond naturally and helpfully. Understand their project and be ready to help them with documentation when they ask for it."""
        )
        
        # Add messages
        conversation["messages"].extend([
            {"role": "user", "content": project_idea, "timestamp": datetime.utcnow().isoformat()},
            {"role": "assistant", "content": initial_response, "timestamp": datetime.utcnow().isoformat()}
        ])
        
        # Store conversation
        self.conversations[conversation_id] = conversation
        
        logger.info("Started conversation", conversation_id=conversation_id, project_idea=project_idea)
        
        return {
            "conversation_id": conversation_id,
            "response": initial_response,
            "phase": "conversation"
        }
    
    async def continue_conversation(self, conversation_id: str, user_message: str) -> Dict[str, Any]:
        """Continue natural conversation with Claude"""
        
        if conversation_id not in self.conversations:
            # Fallback: start new conversation
            return await self.start_conversation(user_message)
        
        conversation = self.conversations[conversation_id]
        
        # Add user message
        conversation["messages"].append({
            "role": "user", 
            "content": user_message, 
            "timestamp": datetime.utcnow().isoformat()
        })
        
        # Check if user wants documentation
        if self._should_generate_documentation(user_message):
            try:
                # Generate documentation
                documentation = await self.multi_model_service.generate_complete_project(
                    conversation["project_idea"],
                    conversation["messages"]
                )
                
                # Store documentation
                conversation["documentation"] = documentation
                conversation["phase"] = "documentation_generated"
                
                # Generate response about the documentation
                response = await self.multi_model_service.generate_conversation_response(
                    f"""Perfect! I've created documentation for your project: {documentation.get('project_name', 'Project')}

Your docs/ folder includes:
- Project overview
- Backend and frontend guides
- Setup instructions
- Implementation guide

The documentation is ready for download!"""
                )
            except Exception as e:
                logger.error(f"Error generating documentation: {e}")
                response = await self.multi_model_service.generate_conversation_response(
                    f"""I encountered an issue creating the documentation. Let me try again or you can ask me to generate it later."""
                )
        else:
            # Continue natural conversation
            context = self._build_context(conversation)
            
            response = await self.multi_model_service.generate_conversation_response(
                f"""You are a helpful AI assistant continuing a conversation about a project.

Project: {conversation['project_idea']}
Recent conversation: {context}
User's input: {user_message}

Respond naturally and helpfully. If they ask for documentation, solutions, or help with implementation, be ready to help."""
            )
        
        # Add assistant response
        conversation["messages"].append({
            "role": "assistant", 
            "content": response, 
            "timestamp": datetime.utcnow().isoformat()
        })
        
        # Update last activity
        conversation["last_activity"] = datetime.utcnow().isoformat()
        if "documentation" in conversation:
            conversation["phase"] = "documentation_generated"
        else:
            conversation["phase"] = "conversation"
        
        logger.info("Continued conversation", conversation_id=conversation_id, response_length=len(response))
        
        return {
            "conversation_id": conversation_id,
            "response": response,
            "phase": conversation["phase"]
        }
    
    def _should_generate_documentation(self, message: str) -> bool:
        """Check if user wants documentation"""
        keywords = [
            "generate docs", "create docs", "generate documentation", "create documentation",
            "docs ready", "documentation ready", "generate project docs", "create project docs",
            "ready for docs", "ready for documentation", "generate everything", "create everything",
            "docs folder", "documentation folder", "project docs", "project documentation",
            "generate project", "create project", "project ready", "docs please",
            "yes", "yes please", "sure", "okay", "go ahead", "generate", "create", "do it",
            "solution", "ideal solution", "best solution", "provide solution", "give me solution",
            "help me", "show me", "tell me", "what should", "how should", "recommend"
        ]
        return any(keyword in message.lower() for keyword in keywords)
    
    def _build_context(self, conversation: Dict[str, Any]) -> str:
        """Build conversation context"""
        recent_messages = conversation["messages"][-6:]  # Last 6 messages
        context_parts = []
        
        for msg in recent_messages:
            role = "User" if msg["role"] == "user" else "Assistant"
            content = msg["content"][:150] + "..." if len(msg["content"]) > 150 else msg["content"]
            context_parts.append(f"{role}: {content}")
        
        return " | ".join(context_parts)
    
    def get_conversation(self, conversation_id: str) -> Dict[str, Any]:
        """Get conversation by ID"""
        return self.conversations.get(conversation_id, {})
    
    def cleanup_expired_conversations(self, max_age_hours: int = 24):
        """Clean up old conversations"""
        cutoff = datetime.utcnow().timestamp() - (max_age_hours * 3600)
        
        expired = [
            conv_id for conv_id, conv in self.conversations.items()
            if datetime.fromisoformat(conv["last_activity"]).timestamp() < cutoff
        ]
        
        for conv_id in expired:
            del self.conversations[conv_id]
        
        if expired:
            logger.info(f"Cleaned up {len(expired)} expired conversations") 