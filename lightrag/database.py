"""
PostgreSQL Database Integration for LightRAG
"""

import logging
import asyncio
from typing import Optional, Dict, Any
import asyncpg
import psycopg2
from psycopg2 import sql
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool

from config import settings

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Manages PostgreSQL database connections and initialization for LightRAG"""
    
    def __init__(self):
        self.connection_string = settings.db_url
        self.pool: Optional[asyncpg.Pool] = None
        self.engine = None
        self.session_factory = None
        
    async def initialize(self) -> bool:
        """Initialize database connection and schema"""
        try:
            # Create async connection pool
            self.pool = await asyncpg.create_pool(
                self.connection_string,
                min_size=2,
                max_size=settings.db_pool_size,
                command_timeout=60
            )
            
            # Create synchronous engine for LightRAG compatibility
            self.engine = create_engine(
                self.connection_string,
                poolclass=QueuePool,
                pool_size=settings.db_pool_size,
                max_overflow=settings.db_max_overflow,
                pool_pre_ping=True,
                echo=(settings.log_level == "DEBUG")
            )
            
            self.session_factory = sessionmaker(bind=self.engine)
            
            # Test connections
            await self._test_async_connection()
            self._test_sync_connection()
            
            # Initialize schema
            await self._initialize_schema()
            
            logger.info("Database connection established successfully")
            return True
            
        except Exception as e:
            logger.error(f"Database initialization failed: {e}")
            return False
    
    async def _test_async_connection(self):
        """Test async database connection"""
        async with self.pool.acquire() as conn:
            version = await conn.fetchval("SELECT version()")
            logger.info(f"PostgreSQL version: {version}")
    
    def _test_sync_connection(self):
        """Test synchronous database connection"""
        with self.engine.connect() as conn:
            result = conn.execute(text("SELECT current_database()"))
            db_name = result.scalar()
            logger.info(f"Connected to database: {db_name}")
    
    async def _initialize_schema(self):
        """Initialize database schema for LightRAG"""
        try:
            async with self.pool.acquire() as conn:
                # Create extension if not exists
                await conn.execute("CREATE EXTENSION IF NOT EXISTS vector")
                
                # Create schema for LightRAG tables
                await conn.execute("CREATE SCHEMA IF NOT EXISTS lightrag")
                
                # Create tables for LightRAG graph storage
                await conn.execute("""
                    CREATE TABLE IF NOT EXISTS lightrag.documents (
                        id SERIAL PRIMARY KEY,
                        document_id VARCHAR(255) UNIQUE NOT NULL,
                        content TEXT NOT NULL,
                        metadata JSONB DEFAULT '{}',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                await conn.execute("""
                    CREATE TABLE IF NOT EXISTS lightrag.entities (
                        id SERIAL PRIMARY KEY,
                        entity_id VARCHAR(255) UNIQUE NOT NULL,
                        name VARCHAR(255) NOT NULL,
                        entity_type VARCHAR(100),
                        description TEXT,
                        properties JSONB DEFAULT '{}',
                        embedding vector(1536), -- OpenAI text-embedding-3-small dimension
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                await conn.execute("""
                    CREATE TABLE IF NOT EXISTS lightrag.relationships (
                        id SERIAL PRIMARY KEY,
                        relationship_id VARCHAR(255) UNIQUE NOT NULL,
                        source_entity_id VARCHAR(255) NOT NULL,
                        target_entity_id VARCHAR(255) NOT NULL,
                        relationship_type VARCHAR(100) NOT NULL,
                        description TEXT,
                        properties JSONB DEFAULT '{}',
                        weight FLOAT DEFAULT 1.0,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (source_entity_id) REFERENCES lightrag.entities(entity_id) ON DELETE CASCADE,
                        FOREIGN KEY (target_entity_id) REFERENCES lightrag.entities(entity_id) ON DELETE CASCADE
                    )
                """)
                
                await conn.execute("""
                    CREATE TABLE IF NOT EXISTS lightrag.document_entities (
                        id SERIAL PRIMARY KEY,
                        document_id VARCHAR(255) NOT NULL,
                        entity_id VARCHAR(255) NOT NULL,
                        relevance_score FLOAT DEFAULT 1.0,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (document_id) REFERENCES lightrag.documents(document_id) ON DELETE CASCADE,
                        FOREIGN KEY (entity_id) REFERENCES lightrag.entities(entity_id) ON DELETE CASCADE,
                        UNIQUE(document_id, entity_id)
                    )
                """)
                
                await conn.execute("""
                    CREATE TABLE IF NOT EXISTS lightrag.chunks (
                        id SERIAL PRIMARY KEY,
                        chunk_id VARCHAR(255) UNIQUE NOT NULL,
                        document_id VARCHAR(255) NOT NULL,
                        content TEXT NOT NULL,
                        chunk_index INTEGER NOT NULL,
                        embedding vector(1536),
                        metadata JSONB DEFAULT '{}',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (document_id) REFERENCES lightrag.documents(document_id) ON DELETE CASCADE
                    )
                """)
                
                # Create indexes for performance
                await conn.execute("""
                    CREATE INDEX IF NOT EXISTS idx_entities_embedding 
                    ON lightrag.entities USING ivfflat (embedding vector_cosine_ops) 
                    WITH (lists = 100)
                """)
                
                await conn.execute("""
                    CREATE INDEX IF NOT EXISTS idx_chunks_embedding 
                    ON lightrag.chunks USING ivfflat (embedding vector_cosine_ops) 
                    WITH (lists = 100)
                """)
                
                await conn.execute("""
                    CREATE INDEX IF NOT EXISTS idx_entities_name 
                    ON lightrag.entities(name)
                """)
                
                await conn.execute("""
                    CREATE INDEX IF NOT EXISTS idx_relationships_source 
                    ON lightrag.relationships(source_entity_id)
                """)
                
                await conn.execute("""
                    CREATE INDEX IF NOT EXISTS idx_relationships_target 
                    ON lightrag.relationships(target_entity_id)
                """)
                
                logger.info("Database schema initialized successfully")
                
        except Exception as e:
            logger.error(f"Schema initialization failed: {e}")
            raise
    
    async def get_connection(self):
        """Get async database connection from pool"""
        return self.pool.acquire()
    
    def get_sync_session(self):
        """Get synchronous database session"""
        return self.session_factory()
    
    async def execute_query(self, query: str, *args) -> Any:
        """Execute async query"""
        async with self.pool.acquire() as conn:
            return await conn.fetch(query, *args)
    
    async def execute_command(self, command: str, *args) -> str:
        """Execute async command"""
        async with self.pool.acquire() as conn:
            return await conn.execute(command, *args)
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get database statistics"""
        try:
            async with self.pool.acquire() as conn:
                # Get counts
                doc_count = await conn.fetchval("SELECT COUNT(*) FROM lightrag.documents")
                entity_count = await conn.fetchval("SELECT COUNT(*) FROM lightrag.entities")
                rel_count = await conn.fetchval("SELECT COUNT(*) FROM lightrag.relationships")
                chunk_count = await conn.fetchval("SELECT COUNT(*) FROM lightrag.chunks")
                
                # Get database size
                db_size = await conn.fetchval("""
                    SELECT pg_size_pretty(pg_database_size(current_database()))
                """)
                
                return {
                    "documents": doc_count,
                    "entities": entity_count,
                    "relationships": rel_count,
                    "chunks": chunk_count,
                    "database_size": db_size,
                    "storage_type": "postgresql"
                }
                
        except Exception as e:
            logger.error(f"Failed to get database stats: {e}")
            return {
                "documents": 0,
                "entities": 0,
                "relationships": 0,
                "chunks": 0,
                "error": str(e)
            }
    
    async def close(self):
        """Close database connections"""
        if self.pool:
            await self.pool.close()
        if self.engine:
            self.engine.dispose()
        logger.info("Database connections closed")


# Global database manager instance
db_manager = DatabaseManager()


async def init_database() -> bool:
    """Initialize database connection"""
    return await db_manager.initialize()


async def get_db_stats() -> Dict[str, Any]:
    """Get database statistics"""
    return await db_manager.get_stats()


def get_connection_string() -> str:
    """Get database connection string"""
    return settings.db_url