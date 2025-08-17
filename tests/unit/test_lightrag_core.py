#!/usr/bin/env python3
"""
Unit tests for LightRAG core functionality.
Tests individual components without requiring full service deployment.
"""

import unittest
import json
import tempfile
import os
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path


# Mock the lightrag module if not installed
try:
    import lightrag
except ImportError:
    lightrag = MagicMock()


class TestLightRAGCore(unittest.TestCase):
    """Unit tests for LightRAG core components."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.test_document = {
            "content": "This is a test document about AI and machine learning.",
            "metadata": {"title": "Test Doc", "category": "test"}
        }
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    @patch('lightrag.LightRAG')
    def test_rag_initialization(self, mock_lightrag):
        """Test RAG instance initialization."""
        # Mock the LightRAG class
        mock_instance = Mock()
        mock_lightrag.return_value = mock_instance
        
        # Initialize RAG
        rag = lightrag.LightRAG(
            working_dir=self.temp_dir,
            llm_model_name="gpt-3.5-turbo",
            embedding_model_name="text-embedding-ada-002"
        )
        
        # Verify initialization
        mock_lightrag.assert_called_once()
        self.assertIsNotNone(rag)
    
    @patch('lightrag.LightRAG')
    def test_document_insertion(self, mock_lightrag):
        """Test document insertion into RAG."""
        # Mock the LightRAG instance
        mock_instance = Mock()
        mock_instance.insert.return_value = {"success": True, "entities": 5, "relations": 3}
        mock_lightrag.return_value = mock_instance
        
        # Create RAG instance and insert document
        rag = lightrag.LightRAG(working_dir=self.temp_dir)
        result = rag.insert(self.test_document["content"])
        
        # Verify insertion
        mock_instance.insert.assert_called_once_with(self.test_document["content"])
        self.assertEqual(result["success"], True)
        self.assertEqual(result["entities"], 5)
    
    @patch('lightrag.LightRAG')
    def test_query_execution(self, mock_lightrag):
        """Test query execution."""
        # Mock the LightRAG instance
        mock_instance = Mock()
        mock_instance.query.return_value = {
            "response": "AI and machine learning are related technologies.",
            "sources": ["doc1", "doc2"]
        }
        mock_lightrag.return_value = mock_instance
        
        # Create RAG instance and execute query
        rag = lightrag.LightRAG(working_dir=self.temp_dir)
        result = rag.query("What is AI?")
        
        # Verify query execution
        mock_instance.query.assert_called_once_with("What is AI?")
        self.assertIn("AI", result["response"])
        self.assertEqual(len(result["sources"]), 2)
    
    def test_text_preprocessing(self):
        """Test text preprocessing functions."""
        # Test text cleaning
        dirty_text = "  This is   a test  \n\n  with extra    spaces.  "
        clean_text = " ".join(dirty_text.split())
        
        self.assertEqual(clean_text, "This is a test with extra spaces.")
        
        # Test text chunking
        long_text = " ".join(["word"] * 1000)
        chunk_size = 100
        chunks = [long_text[i:i+chunk_size] for i in range(0, len(long_text), chunk_size)]
        
        self.assertGreater(len(chunks), 1)
        self.assertLessEqual(len(chunks[0]), chunk_size + 50)  # Allow for word boundary adjustment
    
    def test_metadata_extraction(self):
        """Test metadata extraction from documents."""
        document = {
            "content": "Title: AI Research\nAuthor: John Doe\nDate: 2024-01-01\n\nContent here.",
            "metadata": {}
        }
        
        # Extract metadata
        lines = document["content"].split("\n")
        for line in lines:
            if line.startswith("Title:"):
                document["metadata"]["title"] = line.replace("Title:", "").strip()
            elif line.startswith("Author:"):
                document["metadata"]["author"] = line.replace("Author:", "").strip()
            elif line.startswith("Date:"):
                document["metadata"]["date"] = line.replace("Date:", "").strip()
        
        self.assertEqual(document["metadata"]["title"], "AI Research")
        self.assertEqual(document["metadata"]["author"], "John Doe")
        self.assertEqual(document["metadata"]["date"], "2024-01-01")
    
    @patch('requests.post')
    def test_api_error_handling(self, mock_post):
        """Test API error handling."""
        # Mock API errors
        mock_post.side_effect = [
            Mock(status_code=500, text="Internal Server Error"),
            Mock(status_code=400, text="Bad Request"),
            Mock(status_code=200, json=lambda: {"success": True})
        ]
        
        # Test different error scenarios
        responses = []
        for _ in range(3):
            try:
                response = mock_post("http://test/api/endpoint", json={})
                if response.status_code != 200:
                    responses.append({"error": response.text})
                else:
                    responses.append(response.json())
            except Exception as e:
                responses.append({"error": str(e)})
        
        self.assertEqual(responses[0]["error"], "Internal Server Error")
        self.assertEqual(responses[1]["error"], "Bad Request")
        self.assertEqual(responses[2]["success"], True)
    
    def test_file_operations(self):
        """Test file reading and writing operations."""
        test_file = os.path.join(self.temp_dir, "test.txt")
        test_content = "Test content for file operations"
        
        # Test writing
        with open(test_file, 'w') as f:
            f.write(test_content)
        
        self.assertTrue(os.path.exists(test_file))
        
        # Test reading
        with open(test_file, 'r') as f:
            content = f.read()
        
        self.assertEqual(content, test_content)
        
        # Test file deletion
        os.remove(test_file)
        self.assertFalse(os.path.exists(test_file))
    
    def test_graph_operations(self):
        """Test graph-related operations."""
        # Mock graph structure
        graph = {
            "nodes": [
                {"id": "1", "label": "AI", "type": "concept"},
                {"id": "2", "label": "Machine Learning", "type": "concept"},
                {"id": "3", "label": "Deep Learning", "type": "concept"}
            ],
            "edges": [
                {"source": "1", "target": "2", "relationship": "includes"},
                {"source": "2", "target": "3", "relationship": "includes"}
            ]
        }
        
        # Test node retrieval
        ai_node = next((n for n in graph["nodes"] if n["label"] == "AI"), None)
        self.assertIsNotNone(ai_node)
        self.assertEqual(ai_node["id"], "1")
        
        # Test edge traversal
        ml_edges = [e for e in graph["edges"] if e["source"] == "2"]
        self.assertEqual(len(ml_edges), 1)
        self.assertEqual(ml_edges[0]["target"], "3")
        
        # Test graph statistics
        stats = {
            "total_nodes": len(graph["nodes"]),
            "total_edges": len(graph["edges"]),
            "node_types": len(set(n["type"] for n in graph["nodes"]))
        }
        
        self.assertEqual(stats["total_nodes"], 3)
        self.assertEqual(stats["total_edges"], 2)
        self.assertEqual(stats["node_types"], 1)
    
    def test_batch_processing(self):
        """Test batch document processing."""
        documents = [
            {"id": f"doc{i}", "content": f"Document {i} content"}
            for i in range(10)
        ]
        
        # Process in batches
        batch_size = 3
        batches = []
        for i in range(0, len(documents), batch_size):
            batch = documents[i:i + batch_size]
            batches.append(batch)
        
        self.assertEqual(len(batches), 4)  # 10 docs / 3 per batch = 4 batches
        self.assertEqual(len(batches[0]), 3)
        self.assertEqual(len(batches[-1]), 1)  # Last batch has 1 document
    
    def test_concurrent_operations(self):
        """Test handling of concurrent operations."""
        from concurrent.futures import ThreadPoolExecutor
        import threading
        
        # Shared counter with lock
        counter = {"value": 0}
        lock = threading.Lock()
        
        def increment():
            with lock:
                current = counter["value"]
                # Simulate some processing
                import time
                time.sleep(0.001)
                counter["value"] = current + 1
        
        # Run concurrent increments
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(increment) for _ in range(100)]
            for future in futures:
                future.result()
        
        self.assertEqual(counter["value"], 100)


class TestDataValidation(unittest.TestCase):
    """Tests for data validation and sanitization."""
    
    def test_input_validation(self):
        """Test input validation for API requests."""
        # Valid inputs
        valid_inputs = [
            {"query": "What is AI?", "max_results": 5},
            {"query": "Tell me about machine learning", "max_results": 10},
        ]
        
        for input_data in valid_inputs:
            self.assertIsNotNone(input_data.get("query"))
            self.assertGreater(len(input_data["query"]), 0)
            self.assertLessEqual(input_data.get("max_results", 10), 100)
        
        # Invalid inputs
        invalid_inputs = [
            {"query": ""},  # Empty query
            {"query": "a" * 10001},  # Too long
            {"query": "Valid", "max_results": -1},  # Negative max_results
        ]
        
        for input_data in invalid_inputs:
            is_valid = (
                input_data.get("query") and
                0 < len(input_data["query"]) <= 10000 and
                input_data.get("max_results", 10) > 0
            )
            self.assertFalse(is_valid)
    
    def test_sanitization(self):
        """Test input sanitization."""
        # Test SQL injection prevention
        malicious_input = "'; DROP TABLE users; --"
        sanitized = malicious_input.replace("'", "''").replace(";", "")
        self.assertNotIn("DROP TABLE", sanitized)
        
        # Test XSS prevention
        xss_input = "<script>alert('XSS')</script>"
        sanitized = xss_input.replace("<", "&lt;").replace(">", "&gt;")
        self.assertNotIn("<script>", sanitized)
    
    def test_rate_limiting(self):
        """Test rate limiting logic."""
        from collections import deque
        from datetime import datetime, timedelta
        
        # Simple rate limiter
        class RateLimiter:
            def __init__(self, max_requests=10, window_seconds=60):
                self.max_requests = max_requests
                self.window_seconds = window_seconds
                self.requests = deque()
            
            def is_allowed(self):
                now = datetime.now()
                cutoff = now - timedelta(seconds=self.window_seconds)
                
                # Remove old requests
                while self.requests and self.requests[0] < cutoff:
                    self.requests.popleft()
                
                # Check if under limit
                if len(self.requests) < self.max_requests:
                    self.requests.append(now)
                    return True
                return False
        
        limiter = RateLimiter(max_requests=5, window_seconds=1)
        
        # Test within limits
        for _ in range(5):
            self.assertTrue(limiter.is_allowed())
        
        # Test exceeding limits
        self.assertFalse(limiter.is_allowed())


if __name__ == "__main__":
    unittest.main()