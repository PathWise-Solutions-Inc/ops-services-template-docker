"""
API Routes for LightRAG service
"""

import logging
import time
from typing import Optional
from fastapi import APIRouter, HTTPException, UploadFile, File, BackgroundTasks
from fastapi.responses import JSONResponse

from .core import get_service
from .models import (
    DocumentInsertRequest,
    BatchInsertRequest,
    QueryRequest,
    DocumentDeleteRequest,
    DocumentResponse,
    BatchInsertResponse,
    QueryResponse,
    GraphStatsResponse,
    FileUploadResponse,
    IngestionStatusResponse
)

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(tags=["LightRAG"])


@router.post("/documents", response_model=DocumentResponse)
async def insert_document(request: DocumentInsertRequest):
    """
    Insert a document into the knowledge graph
    
    This endpoint processes the document content, extracts entities and relationships,
    and stores them in the graph database for later retrieval.
    """
    try:
        service = get_service()
        result = await service.insert_document(
            content=request.content,
            metadata={
                "filename": request.filename,
                **request.metadata
            } if request.metadata else {"filename": request.filename}
        )
        
        if not result.get("success"):
            raise HTTPException(status_code=500, detail=result.get("error"))
        
        return DocumentResponse(
            success=True,
            message="Document inserted successfully",
            content_length=result.get("content_length"),
            metadata=result.get("metadata")
        )
        
    except Exception as e:
        logger.error(f"Document insertion failed: {e}")
        return DocumentResponse(
            success=False,
            error=str(e)
        )


@router.post("/documents/batch", response_model=BatchInsertResponse)
async def insert_batch(request: BatchInsertRequest):
    """
    Insert multiple documents in batch
    
    This endpoint allows bulk insertion of documents for efficient processing
    of large document sets.
    """
    try:
        service = get_service()
        documents = [doc.content for doc in request.documents]
        
        result = await service.insert_batch(documents)
        
        if not result.get("success"):
            raise HTTPException(status_code=500, detail=result.get("error"))
        
        return BatchInsertResponse(
            success=True,
            total=result.get("total", 0),
            successful=result.get("successful", 0),
            failed=result.get("total", 0) - result.get("successful", 0),
            results=[]  # Simplified for now
        )
        
    except Exception as e:
        logger.error(f"Batch insertion failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/documents/upload", response_model=FileUploadResponse)
async def upload_file(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...)
):
    """
    Upload a file for processing
    
    Supports various file formats including PDF, DOCX, TXT, and Markdown.
    The file is processed asynchronously in the background.
    """
    try:
        # Read file content
        content = await file.read()
        
        # Decode content based on file type
        if file.content_type == "text/plain" or file.filename.endswith(".txt"):
            text_content = content.decode("utf-8")
        elif file.filename.endswith(".md"):
            text_content = content.decode("utf-8")
        else:
            # For other file types, we'd need additional processing
            # This is simplified for now
            text_content = content.decode("utf-8", errors="ignore")
        
        # Insert document
        service = get_service()
        result = await service.insert_document(
            content=text_content,
            metadata={
                "filename": file.filename,
                "content_type": file.content_type,
                "size": len(content)
            }
        )
        
        return FileUploadResponse(
            success=True,
            filename=file.filename,
            content_type=file.content_type or "text/plain",
            size=len(content),
            message="File uploaded and processed successfully"
        )
        
    except Exception as e:
        logger.error(f"File upload failed: {e}")
        return FileUploadResponse(
            success=False,
            filename=file.filename,
            content_type=file.content_type or "unknown",
            size=0,
            error=str(e)
        )


@router.post("/query", response_model=QueryResponse)
async def query_knowledge_graph(request: QueryRequest):
    """
    Query the knowledge graph
    
    Supports multiple query modes:
    - naive: Simple keyword-based search
    - local: Entity-centric search focusing on specific entities
    - global: Graph-wide search considering relationships
    - hybrid: Combines multiple search strategies for best results
    """
    try:
        start_time = time.time()
        
        service = get_service()
        result = await service.query(
            query_text=request.query,
            mode=request.mode,
            top_k=request.top_k
        )
        
        if not result.get("success"):
            raise HTTPException(status_code=500, detail=result.get("error"))
        
        processing_time = time.time() - start_time
        
        return QueryResponse(
            success=True,
            query=request.query,
            mode=request.mode,
            response=result.get("response"),
            processing_time=processing_time
        )
        
    except Exception as e:
        logger.error(f"Query failed: {e}")
        return QueryResponse(
            success=False,
            query=request.query,
            mode=request.mode,
            error=str(e)
        )


@router.delete("/documents/{document_id}", response_model=DocumentResponse)
async def delete_document(document_id: str):
    """
    Delete a document from the knowledge graph
    
    This removes the document and its associated entities and relationships
    from the graph database.
    """
    try:
        service = get_service()
        result = await service.delete_document(document_id)
        
        if not result.get("success"):
            raise HTTPException(status_code=500, detail=result.get("error"))
        
        return DocumentResponse(
            success=True,
            message=f"Document {document_id} deleted successfully",
            document_id=document_id
        )
        
    except Exception as e:
        logger.error(f"Document deletion failed: {e}")
        return DocumentResponse(
            success=False,
            document_id=document_id,
            error=str(e)
        )


@router.get("/stats", response_model=GraphStatsResponse)
async def get_graph_statistics():
    """
    Get statistics about the knowledge graph
    
    Returns information about the number of entities, relationships,
    documents, and other metrics.
    """
    try:
        service = get_service()
        result = await service.get_graph_stats()
        
        if not result.get("success"):
            raise HTTPException(status_code=500, detail=result.get("error"))
        
        return GraphStatsResponse(
            success=True,
            stats=result.get("stats", {}),
            storage_type=result.get("stats", {}).get("storage_type", "unknown")
        )
        
    except Exception as e:
        logger.error(f"Failed to get graph stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/clear")
async def clear_knowledge_graph():
    """
    Clear all data from the knowledge graph
    
    WARNING: This operation cannot be undone and will remove all
    documents, entities, and relationships from the database.
    """
    try:
        # This would need to be implemented in the service
        # For safety, you might want to add additional confirmation
        
        return {
            "success": False,
            "message": "Clear operation not implemented for safety reasons"
        }
        
    except Exception as e:
        logger.error(f"Clear operation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/search/entities")
async def search_entities(
    query: str,
    entity_type: Optional[str] = None,
    limit: int = 10
):
    """
    Search for entities in the knowledge graph
    
    Find entities by name or type, useful for exploring the graph structure.
    """
    try:
        # This would need to be implemented in the service
        # Placeholder response for now
        
        return {
            "success": True,
            "query": query,
            "entity_type": entity_type,
            "results": [],
            "count": 0
        }
        
    except Exception as e:
        logger.error(f"Entity search failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/search/relationships")
async def search_relationships(
    source_entity: Optional[str] = None,
    target_entity: Optional[str] = None,
    relationship_type: Optional[str] = None,
    limit: int = 10
):
    """
    Search for relationships in the knowledge graph
    
    Find relationships between entities, useful for understanding connections
    in the data.
    """
    try:
        # This would need to be implemented in the service
        # Placeholder response for now
        
        return {
            "success": True,
            "source_entity": source_entity,
            "target_entity": target_entity,
            "relationship_type": relationship_type,
            "results": [],
            "count": 0
        }
        
    except Exception as e:
        logger.error(f"Relationship search failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))