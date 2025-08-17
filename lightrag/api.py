"""
LightRAG REST API Server
"""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Depends, Security
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse
import uvicorn

from .config import settings
from .core import get_service
from .init import run_initialization
from .routes import router as api_router

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Security
security = HTTPBearer(auto_error=False)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    logger.info("Starting LightRAG API server...")
    
    # Initialize database
    try:
        run_initialization()
    except Exception as e:
        logger.warning(f"Database initialization warning: {e}")
        # Continue anyway, database might already be initialized
    
    # Initialize LightRAG service
    service = get_service()
    logger.info("LightRAG service initialized")
    
    yield
    
    # Cleanup
    logger.info("Shutting down LightRAG API server...")
    service.close()


# Create FastAPI application
app = FastAPI(
    title="LightRAG API",
    description="Graph-enhanced retrieval system for hybrid RAG applications",
    version="0.1.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def verify_api_key(credentials: HTTPAuthorizationCredentials = Security(security)) -> bool:
    """Verify API key for authentication"""
    if not settings.api_key:
        # No API key configured, allow all requests
        return True
    
    if not credentials:
        raise HTTPException(
            status_code=401,
            detail="API key required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if credentials.credentials != settings.api_key:
        raise HTTPException(
            status_code=403,
            detail="Invalid API key",
        )
    
    return True


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "LightRAG API",
        "version": "0.1.0",
        "status": "operational",
        "storage_type": settings.storage_type
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        service = get_service()
        stats = await service.get_graph_stats()
        
        return {
            "status": "healthy",
            "service": "LightRAG",
            "storage_type": settings.storage_type,
            "stats": stats.get("stats", {})
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "error": str(e)
            }
        )


# Include API routes
app.include_router(
    api_router,
    prefix="/api",
    dependencies=[Depends(verify_api_key)]
)


# Exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions"""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc) if settings.log_level == "DEBUG" else None
        }
    )


def main():
    """Run the API server"""
    uvicorn.run(
        "lightrag.api:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.log_level == "DEBUG",
        log_level=settings.log_level.lower()
    )


if __name__ == "__main__":
    main()