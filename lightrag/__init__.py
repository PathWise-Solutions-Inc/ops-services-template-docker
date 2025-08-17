"""
LightRAG Service Package
Graph-enhanced retrieval system for hybrid RAG applications
"""

__version__ = "0.1.0"
__author__ = "Ops Services Team"

from .config import settings
from .core import LightRAGService

__all__ = ["settings", "LightRAGService", "__version__"]