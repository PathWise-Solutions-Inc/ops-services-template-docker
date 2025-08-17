# RAG Pipeline Testing Documentation

## Overview

This document describes the comprehensive testing infrastructure for the Ops Services RAG Pipeline, including integration tests, performance benchmarks, and continuous integration workflows.

## Test Structure

```
tests/
├── integration/
│   ├── test_rag_pipeline.py      # Basic integration tests
│   ├── test_advanced_pipeline.py  # Advanced test scenarios
│   └── Dockerfile.test            # Containerized test environment
└── unit/
    └── test_lightrag_core.py      # Unit tests for core components
```

## Test Suites

### 1. Basic Integration Tests (`test_rag_pipeline.py`)

Tests fundamental RAG pipeline operations:

- **Document Ingestion**: Text and file-based ingestion
- **Query Retrieval**: Basic query functionality
- **Graph Operations**: Entity and relationship extraction
- **Health Checks**: Service availability verification

**Run locally:**
```bash
python tests/integration/test_rag_pipeline.py
```

### 2. Advanced Integration Tests (`test_advanced_pipeline.py`)

Comprehensive testing including:

- **Batch Processing**: Concurrent document ingestion
- **Complex Queries**: Multi-hop graph traversal
- **Error Handling**: Invalid input management
- **Performance Benchmarks**: Latency and throughput metrics

**Run locally:**
```bash
python tests/integration/test_advanced_pipeline.py
```

### 3. Performance Tests

Dedicated performance testing:

- Query latency benchmarks
- Concurrent request handling
- Large dataset ingestion
- Resource utilization monitoring

**Run performance suite:**
```bash
./scripts/run-integration-tests.sh performance
```

## Running Tests

### Quick Start

```bash
# Run all tests with single command
make test

# Or use the comprehensive test runner
./scripts/run-integration-tests.sh all
```

### Test Modes

The test runner supports different modes:

```bash
# Basic tests only
./scripts/run-integration-tests.sh basic

# Advanced tests only
./scripts/run-integration-tests.sh advanced

# Performance benchmarks
./scripts/run-integration-tests.sh performance

# Docker containerized tests
./scripts/run-integration-tests.sh docker

# All test suites
./scripts/run-integration-tests.sh all
```

### Using Make Commands

```bash
# Start services and run tests
make quick-test

# Run tests locally
make test-local

# Run tests in Docker
make test-docker

# Check service health
make health-check
```

### Docker-Based Testing

Run tests in an isolated container:

```bash
# Build and run test container
docker-compose -f docker-compose.yml -f docker-compose.test.yml up --build

# Run specific test file
docker-compose -f docker-compose.yml -f docker-compose.test.yml run --rm test-runner python test_advanced_pipeline.py
```

## Test Configuration

### Environment Variables

Configure test behavior with environment variables:

```bash
# API endpoint
export LIGHTRAG_API_URL=http://localhost:8081

# Test timeout
export TEST_TIMEOUT=30

# Retry delay
export RETRY_DELAY=2
```

### Test Data

Sample test documents are located in `test-documents/`:
- `sample.txt`: Basic text document for ingestion testing

The test suites generate synthetic documents covering multiple domains:
- Technology (AI, quantum computing)
- Healthcare (gene therapy, vaccines)
- Business (remote work, corporate culture)
- Science (astronomy, climate)

## Performance Benchmarks

### Metrics Collected

1. **Ingestion Performance**
   - Documents per second
   - Batch processing throughput
   - Entity extraction rate

2. **Query Performance**
   - Average query latency
   - Min/max response times
   - Concurrent query handling

3. **Graph Operations**
   - Traversal speed
   - Relationship discovery time
   - Community detection performance

### Performance Targets

- Average query latency: < 2 seconds
- Batch ingestion: > 10 docs/second
- Concurrent queries: > 10 simultaneous
- Service availability: > 99.9%

## Continuous Integration

### GitHub Actions Workflow

Automated testing on:
- Push to main/develop branches
- Pull requests
- Daily scheduled runs (2 AM UTC)
- Manual workflow dispatch

### CI Test Matrix

```yaml
strategy:
  matrix:
    test-suite: [basic, advanced]
```

### CI Performance Monitoring

Performance tests run on:
- Scheduled daily runs
- Manual trigger with 'performance' mode
- Automatic failure if latency > 5 seconds

## Test Reports

### Report Generation

Tests generate detailed JSON reports:

```json
{
  "timestamp": "2024-01-15T10:30:00Z",
  "api_url": "http://localhost:8081",
  "overall_passed": true,
  "test_results": {
    "batch_ingestion": {
      "passed": true,
      "successful": 6,
      "total": 6
    }
  },
  "performance_metrics": {
    "avg_query_latency": 1.234
  }
}
```

### Report Location

Reports are saved to:
- Local: `test_report_YYYYMMDD_HHMMSS.json`
- CI: Uploaded as artifacts
- Directory: `test-reports/` (when using test runner)

## Troubleshooting

### Common Issues

1. **Services not running**
   ```bash
   # Check service status
   docker-compose ps
   
   # Start services
   docker-compose up -d
   ```

2. **Health check failures**
   ```bash
   # Check LightRAG logs
   docker-compose logs lightrag
   
   # Verify pgvector installation
   docker-compose exec postgres psql -U postgres -c "SELECT * FROM pg_extension WHERE extname='vector'"
   ```

3. **Test timeouts**
   ```bash
   # Increase timeout
   export TEST_TIMEOUT=60
   
   # Check service performance
   docker stats
   ```

### Debug Mode

Enable verbose output:

```bash
# Python tests
PYTHONUNBUFFERED=1 python tests/integration/test_rag_pipeline.py

# Docker compose
docker-compose up  # Without -d for live logs
```

## Test Development

### Adding New Tests

1. Create test file in `tests/integration/`
2. Follow naming convention: `test_*.py`
3. Include in test runner script
4. Update CI workflow if needed

### Test Structure Template

```python
class TestNewFeature:
    def __init__(self):
        self.api_url = LIGHTRAG_API_URL
        self.test_results = {}
    
    def test_feature(self) -> bool:
        """Test specific feature."""
        # Implementation
        pass
    
    def run(self) -> bool:
        """Run all tests."""
        # Orchestration
        pass
```

## Best Practices

1. **Isolation**: Each test should be independent
2. **Cleanup**: Always clean up test data
3. **Idempotency**: Tests should produce same results on repeated runs
4. **Documentation**: Document expected behavior and edge cases
5. **Performance**: Monitor test execution time
6. **Coverage**: Aim for comprehensive scenario coverage

## Coverage Goals

- **Unit Tests**: 80% code coverage
- **Integration Tests**: All API endpoints
- **Performance Tests**: Critical user paths
- **Error Handling**: All error conditions

## Future Enhancements

- [ ] Load testing with K6 or Locust
- [ ] Security testing suite
- [ ] Chaos engineering tests
- [ ] Visual regression testing for UI components
- [ ] Contract testing for API compatibility
- [ ] Automated accessibility testing

## Support

For test-related issues:
1. Check service logs: `docker-compose logs`
2. Review test output carefully
3. Ensure all prerequisites are installed
4. Verify environment configuration
5. Consult troubleshooting section above