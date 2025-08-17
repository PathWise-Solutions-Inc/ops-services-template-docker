#!/usr/bin/env python3
"""
Advanced integration test for the RAG pipeline.
Tests more complex scenarios including:
- Batch document processing
- Complex queries with context
- Graph traversal operations
- Performance benchmarking
- Error handling and recovery
"""

import os
import sys
import time
import json
import requests
import tempfile
import hashlib
import concurrent.futures
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime

# Configuration
LIGHTRAG_API_URL = os.getenv("LIGHTRAG_API_URL", "http://localhost:8081")
POSTGRES_URL = os.getenv("POSTGRES_URL", "postgresql://postgres:postgres@localhost:5432/postgres")
TEST_TIMEOUT = 30  # seconds
RETRY_DELAY = 2  # seconds


class AdvancedRAGTester:
    """Advanced integration test suite for RAG pipeline."""
    
    def __init__(self):
        self.api_url = LIGHTRAG_API_URL
        self.test_results = {}
        self.performance_metrics = {}
        self.test_data_ids = []
        
    def wait_for_services(self, max_retries: int = 15) -> bool:
        """Wait for all required services to be available."""
        print("Waiting for services to be ready...")
        
        services = {
            "LightRAG": f"{self.api_url}/health",
            "Nginx Gateway": "http://localhost/health",
        }
        
        for service_name, health_url in services.items():
            ready = False
            for attempt in range(max_retries):
                try:
                    response = requests.get(health_url, timeout=5)
                    if response.status_code == 200:
                        print(f"✓ {service_name} is ready")
                        ready = True
                        break
                except requests.exceptions.RequestException:
                    pass
                
                if attempt < max_retries - 1:
                    print(f"  {service_name} not ready, retrying...")
                    time.sleep(RETRY_DELAY)
            
            if not ready:
                print(f"✗ {service_name} is not available")
                return False
        
        return True
    
    def generate_test_corpus(self) -> List[Dict]:
        """Generate a larger corpus of test documents for comprehensive testing."""
        corpus = [
            # Technology domain
            {
                "id": "tech_1",
                "content": """
                The evolution of artificial intelligence has been marked by several breakthrough moments.
                In 2012, AlexNet revolutionized computer vision by winning the ImageNet competition.
                Geoffrey Hinton, Yann LeCun, and Yoshua Bengio received the Turing Award in 2018
                for their contributions to deep learning. OpenAI's GPT-3, released in 2020,
                demonstrated unprecedented language understanding capabilities with 175 billion parameters.
                The transformer architecture, introduced by Google researchers in 2017,
                became the foundation for modern NLP systems.
                """,
                "metadata": {
                    "domain": "technology",
                    "subdomain": "artificial_intelligence",
                    "year": 2023,
                    "importance": "high"
                }
            },
            {
                "id": "tech_2",
                "content": """
                Quantum computing represents a paradigm shift in computational power.
                IBM's quantum computer achieved 127 qubits in 2021, while Google claimed quantum supremacy
                in 2019 with their Sycamore processor. Companies like Rigetti Computing and IonQ
                are making quantum computing accessible through cloud services.
                Peter Shor's algorithm for factoring large numbers could break current encryption methods.
                Quantum entanglement and superposition enable parallel processing at unprecedented scales.
                Microsoft's Azure Quantum platform integrates multiple quantum hardware providers.
                """,
                "metadata": {
                    "domain": "technology",
                    "subdomain": "quantum_computing",
                    "year": 2023,
                    "importance": "high"
                }
            },
            # Healthcare domain
            {
                "id": "health_1",
                "content": """
                CRISPR gene editing technology has transformed medical research.
                Jennifer Doudna and Emmanuelle Charpentier won the Nobel Prize in Chemistry in 2020
                for developing CRISPR-Cas9. The first CRISPR therapy for sickle cell disease
                was approved by the FDA in 2023. Vertex Pharmaceuticals and CRISPR Therapeutics
                collaborated on this groundbreaking treatment called Casgevy.
                The technology allows precise DNA modifications to correct genetic defects.
                Ethical considerations around germline editing continue to spark debate.
                """,
                "metadata": {
                    "domain": "healthcare",
                    "subdomain": "gene_therapy",
                    "year": 2023,
                    "importance": "critical"
                }
            },
            {
                "id": "health_2",
                "content": """
                The COVID-19 pandemic accelerated mRNA vaccine development dramatically.
                Pfizer-BioNTech and Moderna developed vaccines in under a year using mRNA technology.
                Dr. Katalin Karikó's research on mRNA modifications was crucial for vaccine success.
                The vaccines teach cells to produce spike proteins, triggering immune responses.
                This platform technology could revolutionize vaccines for cancer and other diseases.
                BioNTech is now developing personalized cancer vaccines using similar approaches.
                """,
                "metadata": {
                    "domain": "healthcare",
                    "subdomain": "vaccines",
                    "year": 2023,
                    "importance": "critical"
                }
            },
            # Business domain
            {
                "id": "business_1",
                "content": """
                The rise of remote work has fundamentally changed corporate culture.
                Zoom's user base grew from 10 million to 300 million during 2020.
                Companies like Twitter and Shopify announced permanent remote work policies.
                Satya Nadella transformed Microsoft's culture emphasizing collaboration and cloud services.
                The hybrid work model combines office and remote work flexibility.
                GitLab operates as a fully distributed company with over 1,300 employees in 65 countries.
                """,
                "metadata": {
                    "domain": "business",
                    "subdomain": "workplace_culture",
                    "year": 2023,
                    "importance": "medium"
                }
            },
            # Science domain
            {
                "id": "science_1",
                "content": """
                The James Webb Space Telescope has revolutionized our understanding of the universe.
                Launched in December 2021, it can observe light from 13.6 billion years ago.
                The telescope discovered galaxies that formed just 300 million years after the Big Bang.
                Its infrared capabilities allow it to see through cosmic dust clouds.
                NASA, ESA, and CSA collaborated on this $10 billion project.
                The telescope's primary mirror consists of 18 hexagonal segments made of beryllium.
                """,
                "metadata": {
                    "domain": "science",
                    "subdomain": "astronomy",
                    "year": 2023,
                    "importance": "high"
                }
            }
        ]
        
        return corpus
    
    def test_batch_ingestion(self) -> bool:
        """Test batch document ingestion with performance metrics."""
        print("\n=== Testing Batch Document Ingestion ===")
        
        corpus = self.generate_test_corpus()
        start_time = time.time()
        successful = 0
        failed = 0
        
        # Test concurrent ingestion
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            futures = []
            
            for doc in corpus:
                future = executor.submit(self._ingest_document, doc)
                futures.append((doc['id'], future))
            
            for doc_id, future in futures:
                try:
                    result = future.result(timeout=30)
                    if result:
                        successful += 1
                        self.test_data_ids.append(doc_id)
                        print(f"✓ Ingested: {doc_id}")
                    else:
                        failed += 1
                        print(f"✗ Failed: {doc_id}")
                except Exception as e:
                    failed += 1
                    print(f"✗ Error ingesting {doc_id}: {str(e)}")
        
        elapsed_time = time.time() - start_time
        
        self.performance_metrics['batch_ingestion'] = {
            'total_documents': len(corpus),
            'successful': successful,
            'failed': failed,
            'elapsed_time': elapsed_time,
            'avg_time_per_doc': elapsed_time / len(corpus) if corpus else 0
        }
        
        self.test_results['batch_ingestion'] = {
            'passed': successful >= len(corpus) * 0.8,  # 80% success rate
            'metrics': self.performance_metrics['batch_ingestion']
        }
        
        print(f"\nBatch ingestion completed in {elapsed_time:.2f} seconds")
        print(f"Success rate: {successful}/{len(corpus)}")
        
        return self.test_results['batch_ingestion']['passed']
    
    def _ingest_document(self, doc: Dict) -> bool:
        """Helper to ingest a single document."""
        try:
            response = requests.post(
                f"{self.api_url}/api/ingest/text",
                json={
                    "text": doc['content'],
                    "metadata": doc['metadata']
                },
                timeout=15
            )
            return response.status_code == 200
        except:
            return False
    
    def test_complex_queries(self) -> bool:
        """Test complex multi-hop queries and reasoning."""
        print("\n=== Testing Complex Queries ===")
        
        complex_queries = [
            {
                "query": "What are the connections between quantum computing companies and their technologies?",
                "expected_entities": ["IBM", "Google", "Rigetti", "IonQ", "Microsoft"],
                "expected_relationships": ["developed", "achieved", "provides"]
            },
            {
                "query": "Trace the development of mRNA vaccines from research to approval",
                "expected_entities": ["Katalin Karikó", "Pfizer", "BioNTech", "Moderna"],
                "expected_relationships": ["developed", "research", "collaborated"]
            },
            {
                "query": "Compare the achievements of AI researchers who won awards",
                "expected_entities": ["Geoffrey Hinton", "Yann LeCun", "Yoshua Bengio", "Turing Award"],
                "expected_relationships": ["received", "contributed", "won"]
            },
            {
                "query": "What companies are involved in space exploration and their contributions?",
                "expected_entities": ["NASA", "ESA", "CSA", "James Webb"],
                "expected_relationships": ["collaborated", "launched", "discovered"]
            }
        ]
        
        successful = 0
        total_queries = len(complex_queries)
        
        for query_test in complex_queries:
            try:
                start_time = time.time()
                response = requests.post(
                    f"{self.api_url}/api/query",
                    json={
                        "query": query_test["query"],
                        "include_context": True,
                        "max_hops": 2
                    },
                    timeout=30
                )
                query_time = time.time() - start_time
                
                if response.status_code == 200:
                    result = response.json()
                    response_text = str(result).lower()
                    
                    # Check for expected entities
                    entities_found = sum(
                        1 for entity in query_test["expected_entities"]
                        if entity.lower() in response_text
                    )
                    
                    # Check for relationship types
                    relationships_found = sum(
                        1 for rel in query_test["expected_relationships"]
                        if rel.lower() in response_text
                    )
                    
                    entity_coverage = entities_found / len(query_test["expected_entities"])
                    relationship_coverage = relationships_found / len(query_test["expected_relationships"])
                    
                    print(f"✓ Query completed in {query_time:.2f}s")
                    print(f"  Query: {query_test['query'][:60]}...")
                    print(f"  Entity coverage: {entity_coverage:.1%}")
                    print(f"  Relationship coverage: {relationship_coverage:.1%}")
                    
                    if entity_coverage >= 0.6 and relationship_coverage >= 0.5:
                        successful += 1
                else:
                    print(f"✗ Query failed: {response.status_code}")
                    
            except Exception as e:
                print(f"✗ Error executing complex query: {str(e)}")
        
        self.test_results['complex_queries'] = {
            'passed': successful >= total_queries * 0.7,  # 70% success rate
            'successful': successful,
            'total': total_queries
        }
        
        return self.test_results['complex_queries']['passed']
    
    def test_graph_traversal(self) -> bool:
        """Test graph traversal and relationship exploration."""
        print("\n=== Testing Graph Traversal ===")
        
        tests_passed = 0
        total_tests = 4
        
        # Test 1: Find connected entities
        try:
            response = requests.post(
                f"{self.api_url}/api/graph/connected_entities",
                json={
                    "entity": "IBM",
                    "max_depth": 2
                },
                timeout=15
            )
            
            if response.status_code == 200:
                connected = response.json()
                print(f"✓ Found {len(connected.get('entities', []))} connected entities to IBM")
                tests_passed += 1
            else:
                print(f"✗ Connected entities query failed")
        except Exception as e:
            print(f"✗ Error in connected entities: {str(e)}")
        
        # Test 2: Find shortest path between entities
        try:
            response = requests.post(
                f"{self.api_url}/api/graph/shortest_path",
                json={
                    "source": "CRISPR",
                    "target": "FDA"
                },
                timeout=15
            )
            
            if response.status_code == 200:
                path = response.json()
                print(f"✓ Found path with {len(path.get('path', []))} steps")
                tests_passed += 1
            else:
                print(f"✗ Shortest path query failed")
        except Exception as e:
            print(f"✗ Error in shortest path: {str(e)}")
        
        # Test 3: Get entity relationships
        try:
            response = requests.post(
                f"{self.api_url}/api/graph/entity_relationships",
                json={"entity": "Microsoft"},
                timeout=15
            )
            
            if response.status_code == 200:
                relationships = response.json()
                print(f"✓ Found {len(relationships.get('relationships', []))} relationships for Microsoft")
                tests_passed += 1
            else:
                print(f"✗ Entity relationships query failed")
        except Exception as e:
            print(f"✗ Error in entity relationships: {str(e)}")
        
        # Test 4: Graph clustering/communities
        try:
            response = requests.get(
                f"{self.api_url}/api/graph/communities",
                timeout=15
            )
            
            if response.status_code == 200:
                communities = response.json()
                print(f"✓ Identified {len(communities.get('communities', []))} knowledge communities")
                tests_passed += 1
            else:
                print(f"✗ Community detection failed")
        except Exception as e:
            print(f"✗ Error in community detection: {str(e)}")
        
        self.test_results['graph_traversal'] = {
            'passed': tests_passed >= total_tests * 0.5,  # 50% success rate
            'successful': tests_passed,
            'total': total_tests
        }
        
        return self.test_results['graph_traversal']['passed']
    
    def test_error_handling(self) -> bool:
        """Test error handling and recovery mechanisms."""
        print("\n=== Testing Error Handling ===")
        
        error_tests = [
            {
                "name": "Invalid document format",
                "request": lambda: requests.post(
                    f"{self.api_url}/api/ingest/text",
                    json={"invalid_field": "test"},
                    timeout=5
                ),
                "expected_status": [400, 422]
            },
            {
                "name": "Empty query",
                "request": lambda: requests.post(
                    f"{self.api_url}/api/query",
                    json={"query": ""},
                    timeout=5
                ),
                "expected_status": [400, 422]
            },
            {
                "name": "Oversized document",
                "request": lambda: requests.post(
                    f"{self.api_url}/api/ingest/text",
                    json={"text": "x" * 1000000},  # 1MB of text
                    timeout=5
                ),
                "expected_status": [400, 413, 422]
            },
            {
                "name": "Non-existent entity query",
                "request": lambda: requests.post(
                    f"{self.api_url}/api/graph/entity_relationships",
                    json={"entity": "NonExistentEntity123456"},
                    timeout=5
                ),
                "expected_status": [200, 404]  # May return empty result or 404
            }
        ]
        
        passed = 0
        for test in error_tests:
            try:
                response = test["request"]()
                if response.status_code in test["expected_status"]:
                    print(f"✓ {test['name']}: Correctly handled (status {response.status_code})")
                    passed += 1
                else:
                    print(f"✗ {test['name']}: Unexpected status {response.status_code}")
            except Exception as e:
                print(f"✗ {test['name']}: Exception occurred: {str(e)}")
        
        self.test_results['error_handling'] = {
            'passed': passed >= len(error_tests) * 0.7,  # 70% success rate
            'successful': passed,
            'total': len(error_tests)
        }
        
        return self.test_results['error_handling']['passed']
    
    def test_performance_benchmarks(self) -> bool:
        """Run performance benchmarks for various operations."""
        print("\n=== Running Performance Benchmarks ===")
        
        benchmarks = {}
        
        # Benchmark 1: Query latency
        query_times = []
        for _ in range(5):
            start = time.time()
            try:
                response = requests.post(
                    f"{self.api_url}/api/query",
                    json={"query": "What are recent AI developments?"},
                    timeout=10
                )
                if response.status_code == 200:
                    query_times.append(time.time() - start)
            except:
                pass
        
        if query_times:
            benchmarks['avg_query_latency'] = sum(query_times) / len(query_times)
            benchmarks['min_query_latency'] = min(query_times)
            benchmarks['max_query_latency'] = max(query_times)
            print(f"✓ Query latency: avg={benchmarks['avg_query_latency']:.3f}s, "
                  f"min={benchmarks['min_query_latency']:.3f}s, "
                  f"max={benchmarks['max_query_latency']:.3f}s")
        
        # Benchmark 2: Concurrent query handling
        start = time.time()
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = []
            for i in range(10):
                future = executor.submit(
                    requests.post,
                    f"{self.api_url}/api/query",
                    json={"query": f"Test query {i}"},
                    timeout=10
                )
                futures.append(future)
            
            successful_concurrent = sum(
                1 for f in futures 
                if f.result().status_code == 200
            )
        
        concurrent_time = time.time() - start
        benchmarks['concurrent_queries'] = {
            'total': 10,
            'successful': successful_concurrent,
            'total_time': concurrent_time,
            'avg_time': concurrent_time / 10
        }
        print(f"✓ Concurrent queries: {successful_concurrent}/10 in {concurrent_time:.2f}s")
        
        # Benchmark 3: Graph operations
        graph_times = []
        for _ in range(3):
            start = time.time()
            try:
                response = requests.get(
                    f"{self.api_url}/api/stats",
                    timeout=5
                )
                if response.status_code == 200:
                    graph_times.append(time.time() - start)
            except:
                pass
        
        if graph_times:
            benchmarks['graph_stats_latency'] = sum(graph_times) / len(graph_times)
            print(f"✓ Graph stats latency: {benchmarks['graph_stats_latency']:.3f}s")
        
        self.performance_metrics['benchmarks'] = benchmarks
        
        # Performance thresholds
        passed = (
            benchmarks.get('avg_query_latency', float('inf')) < 5.0 and  # <5s avg query
            benchmarks.get('concurrent_queries', {}).get('successful', 0) >= 7  # 70% concurrent success
        )
        
        self.test_results['performance'] = {
            'passed': passed,
            'benchmarks': benchmarks
        }
        
        return passed
    
    def cleanup(self):
        """Clean up test data."""
        print("\n=== Cleaning Up Test Data ===")
        
        # Optional: Clear test documents from the system
        for doc_id in self.test_data_ids:
            try:
                requests.delete(
                    f"{self.api_url}/api/documents/{doc_id}",
                    timeout=5
                )
                print(f"✓ Removed test document: {doc_id}")
            except:
                pass  # API might not support deletion
    
    def generate_detailed_report(self) -> bool:
        """Generate a detailed test report with all metrics."""
        print("\n" + "=" * 70)
        print("ADVANCED RAG PIPELINE TEST REPORT")
        print("=" * 70)
        print(f"Test Date: {datetime.now().isoformat()}")
        print(f"LightRAG API: {self.api_url}")
        print()
        
        # Test Results Summary
        print("TEST RESULTS SUMMARY")
        print("-" * 40)
        
        all_passed = True
        for test_name, results in self.test_results.items():
            passed = results.get('passed', False)
            all_passed = all_passed and passed
            
            status = "✓ PASSED" if passed else "✗ FAILED"
            print(f"{test_name.replace('_', ' ').title():30} {status}")
            
            if 'successful' in results and 'total' in results:
                print(f"  Success rate: {results['successful']}/{results['total']}")
            
            if 'metrics' in results:
                for metric, value in results['metrics'].items():
                    if isinstance(value, float):
                        print(f"  {metric}: {value:.3f}")
                    else:
                        print(f"  {metric}: {value}")
        
        # Performance Metrics
        if self.performance_metrics:
            print("\nPERFORMANCE METRICS")
            print("-" * 40)
            
            if 'batch_ingestion' in self.performance_metrics:
                metrics = self.performance_metrics['batch_ingestion']
                print(f"Batch Ingestion:")
                print(f"  Documents processed: {metrics['total_documents']}")
                print(f"  Success rate: {metrics['successful']}/{metrics['total_documents']}")
                print(f"  Total time: {metrics['elapsed_time']:.2f}s")
                print(f"  Avg per document: {metrics['avg_time_per_doc']:.3f}s")
            
            if 'benchmarks' in self.performance_metrics:
                benchmarks = self.performance_metrics['benchmarks']
                print(f"\nQuery Performance:")
                if 'avg_query_latency' in benchmarks:
                    print(f"  Average latency: {benchmarks['avg_query_latency']:.3f}s")
                    print(f"  Min latency: {benchmarks['min_query_latency']:.3f}s")
                    print(f"  Max latency: {benchmarks['max_query_latency']:.3f}s")
                
                if 'concurrent_queries' in benchmarks:
                    conc = benchmarks['concurrent_queries']
                    print(f"\nConcurrent Processing:")
                    print(f"  Queries processed: {conc['total']}")
                    print(f"  Successful: {conc['successful']}")
                    print(f"  Total time: {conc['total_time']:.2f}s")
                    print(f"  Avg per query: {conc['avg_time']:.3f}s")
        
        print("\n" + "=" * 70)
        overall_status = "✓ ALL TESTS PASSED" if all_passed else "✗ SOME TESTS FAILED"
        print(f"OVERALL RESULT: {overall_status}")
        print("=" * 70)
        
        # Write report to file
        report_file = f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'api_url': self.api_url,
                'overall_passed': all_passed,
                'test_results': self.test_results,
                'performance_metrics': self.performance_metrics
            }, f, indent=2)
        print(f"\nDetailed report saved to: {report_file}")
        
        return all_passed
    
    def run(self) -> bool:
        """Run the complete advanced test suite."""
        print("Starting Advanced RAG Pipeline Tests")
        print("=" * 70)
        
        # Wait for services
        if not self.wait_for_services():
            print("ERROR: Required services are not available. Exiting.")
            return False
        
        # Run test sequence
        test_sequence = [
            ("Batch Ingestion", self.test_batch_ingestion),
            ("Complex Queries", self.test_complex_queries),
            ("Graph Traversal", self.test_graph_traversal),
            ("Error Handling", self.test_error_handling),
            ("Performance Benchmarks", self.test_performance_benchmarks)
        ]
        
        for test_name, test_func in test_sequence:
            try:
                print(f"\nRunning: {test_name}")
                test_func()
            except Exception as e:
                print(f"ERROR in {test_name}: {str(e)}")
                self.test_results[test_name.lower().replace(' ', '_')] = {
                    'passed': False,
                    'error': str(e)
                }
        
        # Cleanup
        self.cleanup()
        
        # Generate report
        return self.generate_detailed_report()


def main():
    """Main entry point."""
    tester = AdvancedRAGTester()
    success = tester.run()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()