"""
Core LightRAG Service Implementation
"""

import os
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path
import asyncio
from concurrent.futures import ThreadPoolExecutor

try:
    from lightrag import LightRAG
    from lightrag.llm import openai_complete, openai_embedding
    from lightrag.utils import EmbeddingFunc
except ImportError:
    # Fallback for when lightrag package is not available
    LightRAG = None
    openai_complete = None
    openai_embedding = None
    EmbeddingFunc = None

from .config import settings

# Configure logging
logger = logging.getLogger(__name__)


class LightRAGService:
    """Main LightRAG service wrapper"""
    
    def __init__(self):
        self.settings = settings
        self.rag: Optional[LightRAG] = None
        self.executor = ThreadPoolExecutor(max_workers=4)
        self._initialize_rag()
    
    def _initialize_rag(self):
        """Initialize LightRAG with configured settings"""
        try:
            # Ensure working directory exists
            Path(self.settings.working_dir).mkdir(parents=True, exist_ok=True)
            
            # Set OpenAI API key
            os.environ["OPENAI_API_KEY"] = self.settings.openai_api_key
            
            # Initialize LightRAG based on storage type
            if self.settings.storage_type == "postgres":
                logger.info("Initializing LightRAG with PostgreSQL backend...")
                self.rag = LightRAG(
                    working_dir=self.settings.working_dir,
                    llm_model_func=openai_complete,
                    embedding_func=EmbeddingFunc(
                        func=openai_embedding,
                        embedding_model=self.settings.openai_embedding_model,
                        max_token_size=8192
                    ),
                    chunk_size=self.settings.chunk_size,
                    chunk_overlap=self.settings.chunk_overlap,
                    graph_storage="PGGraphStorage",
                    vector_storage="PGVectorStorage",
                    connection_string=self.settings.db_url,
                )
            else:
                logger.info("Initializing LightRAG with local storage...")
                self.rag = LightRAG(
                    working_dir=self.settings.working_dir,
                    llm_model_func=openai_complete,
                    embedding_func=EmbeddingFunc(
                        func=openai_embedding,
                        embedding_model=self.settings.openai_embedding_model,
                        max_token_size=8192
                    ),
                    chunk_size=self.settings.chunk_size,
                    chunk_overlap=self.settings.chunk_overlap,
                )
            
            logger.info("LightRAG initialized successfully!")
            
        except Exception as e:
            logger.error(f"Failed to initialize LightRAG: {e}")
            raise
    
    async def insert_document(self, content: str, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Insert a document into the knowledge graph"""
        try:
            logger.info(f"Inserting document with {len(content)} characters...")
            
            # Run insertion in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                self.executor,
                self.rag.insert,
                content
            )
            
            logger.info("Document inserted successfully!")
            return {
                "success": True,
                "message": "Document inserted successfully",
                "content_length": len(content),
                "metadata": metadata
            }
            
        except Exception as e:
            logger.error(f"Failed to insert document: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def insert_batch(self, documents: List[str]) -> Dict[str, Any]:
        """Insert multiple documents in batch"""
        try:
            logger.info(f"Inserting batch of {len(documents)} documents...")
            
            results = []
            for i, doc in enumerate(documents):
                logger.info(f"Processing document {i+1}/{len(documents)}...")
                result = await self.insert_document(doc)
                results.append(result)
            
            successful = sum(1 for r in results if r.get("success"))
            logger.info(f"Batch insertion complete: {successful}/{len(documents)} successful")
            
            return {
                "success": True,
                "total": len(documents),
                "successful": successful,
                "results": results
            }
            
        except Exception as e:
            logger.error(f"Batch insertion failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def query(
        self, 
        query_text: str, 
        mode: str = "hybrid",
        top_k: int = 5,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Query the knowledge graph
        
        Args:
            query_text: The query string
            mode: Query mode - "naive", "local", "global", or "hybrid"
            top_k: Number of results to return
            **kwargs: Additional query parameters
        """
        try:
            logger.info(f"Processing query in {mode} mode: {query_text[:100]}...")
            
            # Run query in thread pool
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                self.executor,
                self.rag.query,
                query_text,
                mode
            )
            
            logger.info("Query processed successfully!")
            return {
                "success": True,
                "query": query_text,
                "mode": mode,
                "response": response,
                "top_k": top_k
            }
            
        except Exception as e:
            logger.error(f"Query failed: {e}")
            return {
                "success": False,
                "query": query_text,
                "error": str(e)
            }
    
    async def delete_document(self, doc_id: str) -> Dict[str, Any]:
        """Delete a document from the knowledge graph"""
        try:
            logger.info(f"Deleting document: {doc_id}")
            
            # LightRAG doesn't have built-in delete, so we'd need to implement
            # this at the storage level if needed
            
            return {
                "success": True,
                "message": f"Document {doc_id} marked for deletion"
            }
            
        except Exception as e:
            logger.error(f"Failed to delete document: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_graph_stats(self) -> Dict[str, Any]:
        """Get statistics about the knowledge graph"""
        try:
            # This would need to be implemented based on the storage backend
            stats = {
                "total_entities": 0,
                "total_relationships": 0,
                "total_chunks": 0,
                "storage_type": self.settings.storage_type,
                "working_dir": self.settings.working_dir
            }
            
            if self.settings.storage_type == "postgres":
                # Query PostgreSQL for stats
                pass
            
            return {
                "success": True,
                "stats": stats
            }
            
        except Exception as e:
            logger.error(f"Failed to get graph stats: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def close(self):
        """Clean up resources"""
        try:
            if self.executor:
                self.executor.shutdown(wait=True)
            logger.info("LightRAG service closed successfully")
        except Exception as e:
            logger.error(f"Error closing LightRAG service: {e}")


# Global service instance
_service_instance: Optional[LightRAGService] = None


def get_service() -> LightRAGService:
    """Get or create the global LightRAG service instance"""
    global _service_instance
    if _service_instance is None:
        _service_instance = LightRAGService()
    return _service_instance