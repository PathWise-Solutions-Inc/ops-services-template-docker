"""
Pydantic models for API requests and responses
"""

from typing import Optional, List, Dict, Any, Literal
from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID


# Request Models

class DocumentInsertRequest(BaseModel):
    """Request model for document insertion"""
    content: str = Field(..., description="Document content to insert")
    filename: Optional[str] = Field(None, description="Optional filename")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Optional metadata")
    
    class Config:
        json_schema_extra = {
            "example": {
                "content": "This is a sample document about machine learning...",
                "filename": "ml_basics.txt",
                "metadata": {"category": "education", "author": "John Doe"}
            }
        }


class BatchInsertRequest(BaseModel):
    """Request model for batch document insertion"""
    documents: List[DocumentInsertRequest] = Field(..., description="List of documents to insert")
    
    class Config:
        json_schema_extra = {
            "example": {
                "documents": [
                    {
                        "content": "Document 1 content...",
                        "filename": "doc1.txt"
                    },
                    {
                        "content": "Document 2 content...",
                        "filename": "doc2.txt"
                    }
                ]
            }
        }


class QueryRequest(BaseModel):
    """Request model for RAG queries"""
    query: str = Field(..., description="Query text")
    mode: Literal["naive", "local", "global", "hybrid"] = Field(
        default="hybrid",
        description="Query mode: naive (keyword), local (entity-based), global (graph-based), or hybrid"
    )
    top_k: int = Field(default=5, ge=1, le=50, description="Number of results to return")
    filters: Optional[Dict[str, Any]] = Field(None, description="Optional filters")
    
    class Config:
        json_schema_extra = {
            "example": {
                "query": "What are the key concepts in machine learning?",
                "mode": "hybrid",
                "top_k": 5
            }
        }


class DocumentDeleteRequest(BaseModel):
    """Request model for document deletion"""
    document_id: str = Field(..., description="Document ID to delete")
    
    class Config:
        json_schema_extra = {
            "example": {
                "document_id": "550e8400-e29b-41d4-a716-446655440000"
            }
        }


# Response Models

class DocumentResponse(BaseModel):
    """Response model for document operations"""
    success: bool
    message: Optional[str] = None
    document_id: Optional[str] = None
    content_length: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    

class BatchInsertResponse(BaseModel):
    """Response model for batch insertion"""
    success: bool
    total: int
    successful: int
    failed: int
    results: List[DocumentResponse]
    

class QueryResponse(BaseModel):
    """Response model for queries"""
    success: bool
    query: str
    mode: str
    response: Optional[str] = None
    sources: Optional[List[Dict[str, Any]]] = None
    entities: Optional[List[Dict[str, Any]]] = None
    relationships: Optional[List[Dict[str, Any]]] = None
    error: Optional[str] = None
    processing_time: Optional[float] = None
    

class GraphStatsResponse(BaseModel):
    """Response model for graph statistics"""
    success: bool
    stats: Dict[str, Any]
    storage_type: str
    last_updated: Optional[datetime] = None
    

class HealthResponse(BaseModel):
    """Response model for health check"""
    status: Literal["healthy", "unhealthy"]
    service: str = "LightRAG"
    storage_type: str
    stats: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    

class ErrorResponse(BaseModel):
    """Response model for errors"""
    error: str
    status_code: int
    detail: Optional[str] = None
    

# Ingestion Models

class FileUploadResponse(BaseModel):
    """Response model for file upload"""
    success: bool
    filename: str
    content_type: str
    size: int
    document_id: Optional[str] = None
    message: Optional[str] = None
    error: Optional[str] = None
    

class IngestionStatusResponse(BaseModel):
    """Response model for ingestion status"""
    status: Literal["pending", "processing", "completed", "failed"]
    document_id: str
    filename: str
    progress: Optional[float] = None
    message: Optional[str] = None
    error: Optional[str] = None
    created_at: datetime
    updated_at: datetime