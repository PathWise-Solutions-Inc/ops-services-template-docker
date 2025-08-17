"""
Database initialization for LightRAG with PostgreSQL backend
"""

import os
import sys
import asyncio
import logging
from typing import Optional
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError, ProgrammingError
from tenacity import retry, stop_after_attempt, wait_exponential

from .config import settings

# Configure logging
logging.basicConfig(level=getattr(logging, settings.log_level))
logger = logging.getLogger(__name__)


class DatabaseInitializer:
    """Initialize PostgreSQL database for LightRAG"""
    
    def __init__(self):
        self.db_url = settings.db_url
        self.db_name = "lightrag"
        
    @retry(
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    def wait_for_postgres(self):
        """Wait for PostgreSQL to be ready"""
        # Connect to default postgres database first
        base_url = self.db_url.rsplit("/", 1)[0]
        postgres_url = f"{base_url}/postgres"
        
        logger.info("Waiting for PostgreSQL to be ready...")
        engine = create_engine(postgres_url)
        
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            logger.info("PostgreSQL is ready!")
            return True
        except OperationalError as e:
            logger.warning(f"PostgreSQL not ready yet: {e}")
            raise
        finally:
            engine.dispose()
    
    def create_database(self):
        """Create LightRAG database if it doesn't exist"""
        base_url = self.db_url.rsplit("/", 1)[0]
        postgres_url = f"{base_url}/postgres"
        
        engine = create_engine(postgres_url, isolation_level="AUTOCOMMIT")
        
        try:
            with engine.connect() as conn:
                # Check if database exists
                result = conn.execute(
                    text("SELECT 1 FROM pg_database WHERE datname = :dbname"),
                    {"dbname": self.db_name}
                )
                
                if not result.fetchone():
                    logger.info(f"Creating database '{self.db_name}'...")
                    conn.execute(text(f"CREATE DATABASE {self.db_name}"))
                    logger.info(f"Database '{self.db_name}' created successfully!")
                else:
                    logger.info(f"Database '{self.db_name}' already exists")
                    
        except ProgrammingError as e:
            logger.error(f"Error creating database: {e}")
            raise
        finally:
            engine.dispose()
    
    def create_extensions(self):
        """Create required PostgreSQL extensions"""
        engine = create_engine(self.db_url)
        
        extensions = ["vector", "pg_trgm", "uuid-ossp"]
        
        try:
            with engine.connect() as conn:
                for ext in extensions:
                    try:
                        conn.execute(text(f"CREATE EXTENSION IF NOT EXISTS \"{ext}\""))
                        conn.commit()
                        logger.info(f"Extension '{ext}' created/verified")
                    except ProgrammingError as e:
                        logger.warning(f"Could not create extension '{ext}': {e}")
                        # Continue anyway, extension might already exist
                        
        except Exception as e:
            logger.error(f"Error creating extensions: {e}")
            raise
        finally:
            engine.dispose()
    
    def create_tables(self):
        """Create LightRAG tables"""
        engine = create_engine(self.db_url)
        
        try:
            with engine.connect() as conn:
                # Create documents table
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS documents (
                        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                        filename TEXT NOT NULL,
                        content TEXT,
                        metadata JSONB,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """))
                
                # Create entities table
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS entities (
                        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                        name TEXT NOT NULL UNIQUE,
                        entity_type TEXT,
                        description TEXT,
                        metadata JSONB,
                        embedding vector(1536),
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """))
                
                # Create relationships table
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS relationships (
                        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                        source_entity_id UUID REFERENCES entities(id),
                        target_entity_id UUID REFERENCES entities(id),
                        relationship_type TEXT,
                        description TEXT,
                        weight FLOAT DEFAULT 1.0,
                        metadata JSONB,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """))
                
                # Create chunks table for RAG
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS chunks (
                        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                        document_id UUID REFERENCES documents(id),
                        chunk_index INTEGER,
                        content TEXT NOT NULL,
                        embedding vector(1536),
                        metadata JSONB,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """))
                
                # Create indexes
                conn.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_entities_embedding 
                    ON entities USING ivfflat (embedding vector_cosine_ops)
                    WITH (lists = 100)
                """))
                
                conn.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_chunks_embedding 
                    ON chunks USING ivfflat (embedding vector_cosine_ops)
                    WITH (lists = 100)
                """))
                
                conn.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_documents_metadata 
                    ON documents USING gin (metadata)
                """))
                
                conn.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_entities_name_trgm 
                    ON entities USING gin (name gin_trgm_ops)
                """))
                
                conn.commit()
                logger.info("All tables and indexes created successfully!")
                
        except Exception as e:
            logger.error(f"Error creating tables: {e}")
            raise
        finally:
            engine.dispose()
    
    def initialize(self):
        """Run full initialization sequence"""
        try:
            logger.info("Starting LightRAG database initialization...")
            
            # Wait for PostgreSQL
            self.wait_for_postgres()
            
            # Create database
            self.create_database()
            
            # Create extensions
            self.create_extensions()
            
            # Create tables
            self.create_tables()
            
            logger.info("LightRAG database initialization completed successfully!")
            return True
            
        except Exception as e:
            logger.error(f"Database initialization failed: {e}")
            raise


def run_initialization():
    """Run database initialization"""
    initializer = DatabaseInitializer()
    return initializer.initialize()


if __name__ == "__main__":
    # Run initialization when script is executed directly
    success = run_initialization()
    sys.exit(0 if success else 1)