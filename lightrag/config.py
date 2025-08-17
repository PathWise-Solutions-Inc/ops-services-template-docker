"""
LightRAG Configuration Settings
"""

import os
from typing import Optional, Dict, Any
from pydantic_settings import BaseSettings
from pydantic import Field, validator


class Settings(BaseSettings):
    """LightRAG service configuration"""
    
    # Service Settings
    service_name: str = "lightrag-service"
    api_host: str = Field(default="0.0.0.0", env="API_HOST")
    api_port: int = Field(default=8080, env="API_PORT")
    api_key: str = Field(default="", env="LIGHTRAG_API_KEY")
    
    # LightRAG Core Settings
    working_dir: str = Field(default="/app/data", env="LIGHTRAG_WORKING_DIR")
    storage_type: str = Field(default="postgres", env="LIGHTRAG_STORAGE_TYPE")
    log_level: str = Field(default="INFO", env="LIGHTRAG_LOG_LEVEL")
    
    # Database Settings
    db_url: str = Field(
        default="postgresql://postgres:postgres@postgres:5432/lightrag",
        env="LIGHTRAG_DB_URL"
    )
    db_pool_size: int = Field(default=10, env="DB_POOL_SIZE")
    db_max_overflow: int = Field(default=20, env="DB_MAX_OVERFLOW")
    
    # OpenAI Settings
    openai_api_key: str = Field(default="", env="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-4-turbo-preview", env="OPENAI_MODEL")
    openai_embedding_model: str = Field(
        default="text-embedding-3-small", 
        env="OPENAI_EMBEDDING_MODEL"
    )
    
    # LightRAG Algorithm Settings
    chunk_size: int = Field(default=1200, env="LIGHTRAG_CHUNK_SIZE")
    chunk_overlap: int = Field(default=100, env="LIGHTRAG_CHUNK_OVERLAP")
    max_tokens: int = Field(default=4096, env="LIGHTRAG_MAX_TOKENS")
    temperature: float = Field(default=0.7, env="LIGHTRAG_TEMPERATURE")
    
    # Graph Settings
    max_graph_nodes: int = Field(default=10000, env="MAX_GRAPH_NODES")
    max_graph_edges: int = Field(default=50000, env="MAX_GRAPH_EDGES")
    entity_extraction_batch_size: int = Field(default=10, env="ENTITY_BATCH_SIZE")
    
    # Cache Settings
    enable_cache: bool = Field(default=True, env="ENABLE_CACHE")
    cache_ttl: int = Field(default=3600, env="CACHE_TTL")  # seconds
    redis_url: str = Field(
        default="redis://:redis@redis:6379/0",
        env="REDIS_URL"
    )
    
    # Security Settings
    cors_origins: list[str] = Field(
        default=["http://localhost:3000", "http://localhost:5678"],
        env="CORS_ORIGINS"
    )
    jwt_secret: str = Field(default="", env="JWT_SECRET")
    jwt_algorithm: str = Field(default="HS256", env="JWT_ALGORITHM")
    jwt_expiration: int = Field(default=3600, env="JWT_EXPIRATION")  # seconds
    
    # Monitoring
    enable_metrics: bool = Field(default=True, env="ENABLE_METRICS")
    metrics_port: int = Field(default=9091, env="METRICS_PORT")
    
    @validator("openai_api_key")
    def validate_openai_key(cls, v):
        if not v or v == "sk-your-openai-api-key-here":
            # Allow empty key for development/testing
            logger = __import__('logging').getLogger(__name__)
            logger.warning("OpenAI API key not configured - using mock responses")
            return ""
        return v
    
    @validator("storage_type")
    def validate_storage_type(cls, v):
        allowed_types = ["postgres", "local", "memory"]
        if v not in allowed_types:
            raise ValueError(f"Storage type must be one of: {allowed_types}")
        return v
    
    def get_lightrag_config(self) -> Dict[str, Any]:
        """Get configuration dict for LightRAG initialization"""
        config = {
            "working_dir": self.working_dir,
            "llm_model_name": self.openai_model,
            "embedding_model_name": self.openai_embedding_model,
            "chunk_size": self.chunk_size,
            "chunk_overlap": self.chunk_overlap,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
        }
        
        if self.storage_type == "postgres":
            config["graph_storage"] = "PGGraphStorage"
            config["vector_storage"] = "PGVectorStorage"
            config["connection_string"] = self.db_url
        elif self.storage_type == "local":
            config["graph_storage"] = "NetworkXStorage"
            config["vector_storage"] = "ChromaVectorStorage"
        
        return config
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Create global settings instance
settings = Settings()