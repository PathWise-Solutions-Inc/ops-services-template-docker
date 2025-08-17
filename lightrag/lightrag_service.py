"""
LightRAG Service Implementation
"""

import os
import uuid
import logging
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime
import hashlib
import json

# Import LightRAG library
try:
    from lightrag import LightRAG, QueryParam
    from lightrag.llm import gpt_4o_mini_complete, gpt_4o_complete
    from lightrag.embed import openai_embedding
    LIGHTRAG_AVAILABLE = True
except ImportError as e:
    logging.warning(f"LightRAG library not available: {e}")
    LIGHTRAG_AVAILABLE = False

from config import settings
from database import db_manager

logger = logging.getLogger(__name__)


class MockLightRAG:
    """Mock LightRAG for development when library is not available"""
    
    def __init__(self, working_dir: str, **kwargs):
        self.working_dir = working_dir
        logger.info("Using Mock LightRAG for development")
    
    async def ainsert(self, content: str) -> str:
        """Mock document insertion"""
        doc_id = str(uuid.uuid4())
        logger.info(f"Mock: Inserting document {doc_id[:8]} with {len(content)} chars")
        
        # Store in database for persistence
        try:
            async with db_manager.get_connection() as conn:
                await conn.execute("""
                    INSERT INTO lightrag.documents (document_id, content, metadata)
                    VALUES ($1, $2, $3)
                    ON CONFLICT (document_id) DO UPDATE SET
                    content = EXCLUDED.content,
                    updated_at = CURRENT_TIMESTAMP
                """, doc_id, content, json.dumps({"mock": True}))
        except Exception as e:
            logger.error(f"Failed to store mock document: {e}")
        
        return doc_id
    
    async def aquery(self, query: str, param: Optional[Any] = None) -> str:
        """Mock query processing"""
        logger.info(f"Mock: Processing query: {query[:50]}...")
        
        # Try to find relevant content from stored documents
        try:
            async with db_manager.get_connection() as conn:
                results = await conn.fetch("""
                    SELECT content, metadata 
                    FROM lightrag.documents 
                    WHERE content ILIKE $1 
                    LIMIT 3
                """, f"%{query.split()[0] if query.split() else query}%")
                
                if results:
                    relevant_content = "\n".join([row['content'][:200] for row in results])
                    return f"Based on the stored documents, here's relevant information: {relevant_content}..."
                
        except Exception as e:
            logger.error(f"Mock query failed: {e}")
        
        return f"Mock response for query: '{query}'. This is a simulated response demonstrating that the LightRAG service is processing your request."


class LightRAGService:
    """LightRAG service wrapper with database integration"""
    
    def __init__(self):
        self.rag = None
        self.initialized = False
        
    async def initialize(self) -> bool:
        """Initialize LightRAG service"""
        try:
            # Ensure database is initialized
            if not db_manager.pool:
                await db_manager.initialize()
            
            # Initialize LightRAG
            if LIGHTRAG_AVAILABLE and settings.openai_api_key:
                # Use real LightRAG with OpenAI
                self.rag = LightRAG(
                    working_dir=settings.working_dir,
                    llm_model_func=gpt_4o_mini_complete,
                    embedding_func=openai_embedding
                )
                logger.info("LightRAG initialized with OpenAI integration")
            else:
                # Use mock LightRAG for development
                self.rag = MockLightRAG(working_dir=settings.working_dir)
                logger.info("LightRAG initialized in mock mode")
            
            self.initialized = True
            return True
            
        except Exception as e:
            logger.error(f"LightRAG service initialization failed: {e}")
            self.initialized = False
            return False
    
    async def insert_document(self, content: str, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Insert a document into the knowledge graph"""
        if not self.initialized:
            await self.initialize()
        
        try:
            start_time = datetime.now()
            
            # Generate document ID
            doc_id = hashlib.md5(content.encode()).hexdigest()
            
            # Insert into LightRAG
            result = await self.rag.ainsert(content)
            
            # Store metadata in database
            metadata = metadata or {}
            metadata.update({
                "processed_at": start_time.isoformat(),
                "content_length": len(content),
                "lightrag_result": str(result)
            })
            
            # Store in our database for tracking
            async with db_manager.get_connection() as conn:
                await conn.execute("""
                    INSERT INTO lightrag.documents (document_id, content, metadata)
                    VALUES ($1, $2, $3)
                    ON CONFLICT (document_id) DO UPDATE SET
                    content = EXCLUDED.content,
                    metadata = EXCLUDED.metadata,
                    updated_at = CURRENT_TIMESTAMP
                """, doc_id, content, json.dumps(metadata))
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            logger.info(f"Document {doc_id[:8]} processed in {processing_time:.2f}s")
            
            return {
                "success": True,
                "document_id": doc_id,
                "content_length": len(content),
                "processing_time": processing_time,
                "metadata": metadata
            }
            
        except Exception as e:
            logger.error(f"Document insertion failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def query(self, query_text: str, mode: str = "hybrid", top_k: int = 5) -> Dict[str, Any]:
        """Query the knowledge graph"""
        if not self.initialized:
            await self.initialize()
        
        try:
            start_time = datetime.now()
            
            # Map mode to LightRAG QueryParam
            if LIGHTRAG_AVAILABLE:
                if mode == "naive":
                    param = QueryParam(mode="naive")
                elif mode == "local":
                    param = QueryParam(mode="local")
                elif mode == "global":
                    param = QueryParam(mode="global")
                else:  # hybrid
                    param = QueryParam(mode="hybrid")
            else:
                param = None
            
            # Execute query
            response = await self.rag.aquery(query_text, param=param)
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            logger.info(f"Query processed in {processing_time:.2f}s: {query_text[:50]}...")
            
            return {
                "success": True,
                "query": query_text,
                "mode": mode,
                "response": response,
                "processing_time": processing_time
            }
            
        except Exception as e:
            logger.error(f"Query failed: {e}")
            return {
                "success": False,
                "query": query_text,
                "mode": mode,
                "error": str(e)
            }
    
    async def get_graph_stats(self) -> Dict[str, Any]:
        """Get statistics about the knowledge graph"""
        try:
            # Get database stats
            db_stats = await db_manager.get_stats()
            
            # Add LightRAG-specific stats
            stats = {
                "success": True,
                "stats": {
                    **db_stats,
                    "service_status": "initialized" if self.initialized else "not_initialized",
                    "lightrag_available": LIGHTRAG_AVAILABLE,
                    "openai_configured": bool(settings.openai_api_key),
                    "storage_type": settings.storage_type
                }
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get graph stats: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def delete_document(self, document_id: str) -> Dict[str, Any]:
        """Delete a document from the knowledge graph"""
        try:
            # Remove from database
            async with db_manager.get_connection() as conn:
                result = await conn.execute("""
                    DELETE FROM lightrag.documents WHERE document_id = $1
                """, document_id)
                
                # Also clean up related entities and relationships
                await conn.execute("""
                    DELETE FROM lightrag.document_entities WHERE document_id = $1
                """, document_id)
            
            return {
                "success": True,
                "message": f"Document {document_id} deleted successfully"
            }
            
        except Exception as e:
            logger.error(f"Failed to delete document {document_id}: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def close(self):
        """Close the service"""
        # LightRAG doesn't need explicit closing
        self.initialized = False
        logger.info("LightRAG service closed")


# Global service instance
lightrag_service = LightRAGService()


async def get_service() -> LightRAGService:
    """Get the LightRAG service instance"""
    if not lightrag_service.initialized:
        await lightrag_service.initialize()
    return lightrag_service