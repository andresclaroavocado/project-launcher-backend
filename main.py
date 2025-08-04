"""
Multi-Model FastAPI backend for AI-powered project architect
"""

import os
import structlog
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from dotenv import load_dotenv

from app.api.conversation import router as conversation_router
from app.api.mcp import router as mcp_router
from app.services.multi_model_service import MultiModelService

# Load environment variables
load_dotenv()

# Configure logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger(__name__)

# Global services
multi_model_service: MultiModelService = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    global multi_model_service
    
    # Startup
    logger.info("Starting Multi-Model Project Architect")
    
    # Initialize multi-model service
    multi_model_service = MultiModelService()
    
    # Test all models
    try:
        model_status = await multi_model_service.test_all_models()
        logger.info("Multi-model service initialized", model_status=model_status)
    except Exception as e:
        logger.error("Failed to initialize multi-model service", error=str(e))
    
    yield
    
    # Shutdown
    logger.info("Shutting down Multi-Model Project Architect")


# Create FastAPI app
app = FastAPI(
    title="Project Architect API",
    description="AI-powered project architecture and generation",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000", 
        "http://127.0.0.1:3000",
        "https://project-launcher.vercel.app",
        "https://*.vercel.app",
        "https://*.vercel.com"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Trusted host middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["localhost", "127.0.0.1", "0.0.0.0", "*.vercel.app", "*.vercel.com"]
)

# Include routers
app.include_router(conversation_router)
app.include_router(mcp_router)


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    global multi_model_service
    
    try:
        import os
        
        # Check environment variables
        anthropic_key = os.getenv('ANTHROPIC_API_KEY')
        goose_key = os.getenv('GOOSE_AI_API_KEY')
        
        # Check service status
        service_status = "initialized" if multi_model_service else "not initialized"
        
        # Check API key status
        anthropic_status = "configured" if anthropic_key else "missing"
        goose_status = "configured" if goose_key else "missing"
        
        return {
            "status": "healthy",
            "service_status": service_status,
            "api_keys": {
                "anthropic": anthropic_status,
                "goose_ai": goose_status
            },
            "message": "API is ready" if (anthropic_key or goose_key) else "API keys needed"
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {"status": "unhealthy", "error": str(e)}


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Project Architect API",
        "version": "1.0.0",
        "status": "running"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 