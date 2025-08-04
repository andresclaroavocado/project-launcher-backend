"""
Multi-Model API endpoints for conversation and model management
"""

from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import structlog
import zipfile
import os
import tempfile
import json

from app.services.conversation_service import ConversationService
from app.services.multi_model_service import MultiModelService

logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/api/v1", tags=["conversation"])


class ProjectIdeaRequest(BaseModel):
    """Request model for project idea"""
    project_idea: str


class ContinueConversationRequest(BaseModel):
    """Request model for continuing conversation"""
    conversation_id: str
    message: str


class ConversationResponse(BaseModel):
    """Response model for conversation"""
    conversation_id: str
    response: str
    phase: str
    download_url: str
    filename: str


# Global services
_conversation_service: ConversationService = None
_multi_model_service: MultiModelService = None


async def get_services():
    """Get global services"""
    global _conversation_service, _multi_model_service
    
    if _conversation_service is None:
        _multi_model_service = MultiModelService()
        _conversation_service = ConversationService()
    
    return _conversation_service, _multi_model_service


@router.post("/conversation/start", response_model=ConversationResponse)
async def start_conversation(request: ProjectIdeaRequest):
    """Start a new project conversation"""
    try:
        logger.info(f"Starting conversation for project idea: {request.project_idea}")
        
        conversation_service, _ = await get_services()
        
        result = await conversation_service.start_conversation(request.project_idea)
        
        # Create downloadable response
        response_content = result.get("response", "")
        conversation_id = result.get("conversation_id", "")
        
        # Create response with download info
        response_data = {
            "conversation_id": conversation_id,
            "response": response_content,
            "phase": result.get("phase", "project_idea"),
            "download_url": f"/api/v1/conversation/{conversation_id}/response/download",
            "filename": f"claude-response-{conversation_id}.txt"
        }
        
        logger.info(f"Conversation started successfully", 
                   conversation_id=conversation_id,
                   response_length=len(response_content))
        
        return ConversationResponse(**response_data)
        
    except Exception as e:
        logger.error(f"Error starting conversation: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        conversation_service, multi_model_service = await get_services()
        
        # Test all models
        model_status = await multi_model_service.test_all_models()
        
        # Get performance stats
        performance_stats = multi_model_service.get_performance_stats()
        
        return {
            "status": "healthy",
            "models": model_status,
            "performance": performance_stats,
            "message": "Multi-model service is running"
        }
        
    except Exception as e:
        logger.error(f"Health check failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/models/status")
async def get_model_status():
    """Get status of all available models"""
    try:
        _, multi_model_service = await get_services()
        return await multi_model_service.test_all_models()
    except Exception as e:
        logger.error(f"Error getting model status: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/models/available")
async def get_available_models():
    """Get list of available models from all providers"""
    try:
        _, multi_model_service = await get_services()
        return await multi_model_service.get_available_models()
    except Exception as e:
        logger.error(f"Error getting available models: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/models/performance")
async def get_model_performance():
    """Get performance statistics for all models"""
    try:
        _, multi_model_service = await get_services()
        return multi_model_service.get_performance_stats()
    except Exception as e:
        logger.error(f"Error getting model performance: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/models/recommendations")
async def get_model_recommendations():
    """Get model recommendations based on performance"""
    try:
        _, multi_model_service = await get_services()
        return multi_model_service.get_model_recommendations()
    except Exception as e:
        logger.error(f"Error getting model recommendations: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/conversation/continue", response_model=ConversationResponse)
async def continue_conversation(request: ContinueConversationRequest):
    """Continue an existing conversation"""
    try:
        logger.info(f"Continuing conversation {request.conversation_id} with message: {request.message}")
        
        conversation_service, _ = await get_services()
        
        result = await conversation_service.continue_conversation(
            request.conversation_id, 
            request.message
        )
        
        # Create downloadable response
        response_content = result.get("response", "")
        conversation_id = result.get("conversation_id", "")
        
        # Create response with download info
        response_data = {
            "conversation_id": conversation_id,
            "response": response_content,
            "phase": result.get("phase", "requirements_gathering"),
            "download_url": f"/api/v1/conversation/{conversation_id}/response/download",
            "filename": f"claude-response-{conversation_id}.txt"
        }
        
        logger.info(f"Conversation continued successfully", 
                   conversation_id=request.conversation_id,
                   response_length=len(response_content))
        
        return ConversationResponse(**response_data)
        
    except Exception as e:
        logger.error(f"Error continuing conversation: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/conversation/{conversation_id}/download")
async def download_complete_project(conversation_id: str):
    """Download the complete project as a ZIP file"""
    
    try:
        conversation_service, _ = await get_services()
        
        conversation = conversation_service.get_conversation(conversation_id)
        
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        if "complete_project" not in conversation:
            raise HTTPException(status_code=404, detail="Complete project not generated yet. Please generate the complete project first.")
        
        complete_project = conversation["complete_project"]
        project_name = complete_project.get("project_name", "project").lower().replace(" ", "-")
        
        # Create temporary ZIP file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.zip') as tmp_file:
            with zipfile.ZipFile(tmp_file.name, 'w', zipfile.ZIP_DEFLATED) as zipf:
                
                # Add project metadata
                metadata = {
                    "project_name": complete_project.get("project_name", "Project"),
                    "description": complete_project.get("description", ""),
                    "generated_at": conversation.get("last_activity", ""),
                    "conversation_id": conversation_id
                }
                zipf.writestr("project-metadata.json", json.dumps(metadata, indent=2))
                
                # Add file structure
                file_structure = complete_project.get("file_structure", {})
                
                # Add backend files
                for file_config in file_structure.get("backend", []):
                    file_path = file_config.get("path", "")
                    content = file_config.get("content", "")
                    zipf.writestr(file_path, content)
                
                # Add frontend files
                for file_config in file_structure.get("frontend", []):
                    file_path = file_config.get("path", "")
                    content = file_config.get("content", "")
                    zipf.writestr(file_path, content)
                
                # Add documentation files
                docs_structure = file_structure.get("docs", {})
                for category, files in docs_structure.items():
                    for filename, file_data in files.items():
                        if isinstance(file_data, dict):
                            content = file_data.get("content", "")
                            file_path = f"docs/{category}/{filename}"
                            zipf.writestr(file_path, content)
                
                # Add configuration files
                for file_config in file_structure.get("config", []):
                    file_path = file_config.get("path", "")
                    content = file_config.get("content", "")
                    zipf.writestr(file_path, content)
                
                # Add dependencies
                dependencies = complete_project.get("dependencies", {})
                if dependencies:
                    zipf.writestr("dependencies.json", json.dumps(dependencies, indent=2))
                
                # Add GitHub issues
                github_issues = complete_project.get("github_issues", [])
                if github_issues:
                    zipf.writestr("github-issues.json", json.dumps(github_issues, indent=2))
                
                # Add README
                readme_content = f"""# {complete_project.get("project_name", "Project")}

{complete_project.get("description", "Project description")}

## Project Structure

This project was generated using the Project Architect AI system.

### Components
- Backend: {len(file_structure.get("backend", []))} files
- Frontend: {len(file_structure.get("frontend", []))} files
- Documentation: {len(docs_structure.get("architecture", {})) + len(docs_structure.get("technical", {})) + len(docs_structure.get("business", {}))} files

### Getting Started

1. Install dependencies
2. Configure environment variables
3. Run the application

See the documentation in the `docs/` folder for detailed instructions.

Generated on: {conversation.get("last_activity", "")}
"""
                zipf.writestr("README.md", readme_content)
            
            # Return the ZIP file
            return FileResponse(
                path=tmp_file.name,
                filename=f"{project_name}-complete-project.zip",
                media_type="application/zip"
            )
    
    except Exception as e:
        logger.error(f"Error creating download: {e}")
        raise HTTPException(status_code=500, detail=str(e)) 


@router.get("/conversation/{conversation_id}/response/download")
async def download_claude_response(conversation_id: str):
    """Download the latest Claude response as a text file"""
    
    try:
        conversation_service, _ = await get_services()
        
        conversation = conversation_service.get_conversation(conversation_id)
        
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        # Get the latest assistant response
        messages = conversation.get("messages", [])
        assistant_messages = [msg for msg in messages if msg.get("role") == "assistant"]
        
        if not assistant_messages:
            raise HTTPException(status_code=404, detail="No Claude responses found")
        
        # Get the latest response
        latest_response = assistant_messages[-1].get("content", "")
        
        # Create response content with metadata
        response_content = f"""Claude Response - Project Architect

Project: {conversation.get('project_idea', 'Unknown Project')}
Conversation ID: {conversation_id}
Generated: {assistant_messages[-1].get('timestamp', 'Unknown')}

{'='*50}

{latest_response}

{'='*50}

Generated by Claude AI via Project Architect API
"""
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.txt', mode='w', encoding='utf-8') as tmp_file:
            tmp_file.write(response_content)
            tmp_file_path = tmp_file.name
        
        # Return the file
        return FileResponse(
            path=tmp_file_path,
            filename=f"claude-response-{conversation_id}.txt",
            media_type="text/plain"
        )
    
    except Exception as e:
        logger.error(f"Error downloading Claude response: {e}")
        raise HTTPException(status_code=500, detail=str(e)) 