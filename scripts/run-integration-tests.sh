#!/bin/bash

# Comprehensive Integration Test Runner for RAG Pipeline
# This script orchestrates multiple test suites and generates a combined report

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
TEST_DIR="${PROJECT_ROOT}/tests/integration"
REPORT_DIR="${PROJECT_ROOT}/test-reports"

# Test mode selection
TEST_MODE="${1:-all}"  # Options: basic, advanced, performance, all

# Functions
print_header() {
    echo ""
    echo "========================================"
    echo "$1"
    echo "========================================"
}

check_prerequisites() {
    print_header "Checking Prerequisites"
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}✗ Docker is not installed${NC}"
        exit 1
    fi
    echo -e "${GREEN}✓ Docker found${NC}"
    
    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        echo -e "${RED}✗ Docker Compose is not installed${NC}"
        exit 1
    fi
    echo -e "${GREEN}✓ Docker Compose found${NC}"
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        echo -e "${RED}✗ Python 3 is not installed${NC}"
        exit 1
    fi
    echo -e "${GREEN}✓ Python 3 found${NC}"
    
    # Install Python dependencies
    echo -e "${YELLOW}Installing test dependencies...${NC}"
    pip3 install requests pytest concurrent-futures --quiet 2>/dev/null || true
}

check_services() {
    print_header "Checking Service Status"
    
    local services_running=true
    
    # Check if containers are running
    if ! docker-compose ps | grep -q "lightrag.*Up"; then
        echo -e "${YELLOW}⚠ LightRAG service is not running${NC}"
        services_running=false
    else
        echo -e "${GREEN}✓ LightRAG service is running${NC}"
    fi
    
    if ! docker-compose ps | grep -q "postgres.*Up"; then
        echo -e "${YELLOW}⚠ PostgreSQL is not running${NC}"
        services_running=false
    else
        echo -e "${GREEN}✓ PostgreSQL is running${NC}"
    fi
    
    if ! docker-compose ps | grep -q "nginx.*Up"; then
        echo -e "${YELLOW}⚠ Nginx gateway is not running${NC}"
        services_running=false
    else
        echo -e "${GREEN}✓ Nginx gateway is running${NC}"
    fi
    
    if [ "$services_running" = false ]; then
        echo -e "${YELLOW}Starting services...${NC}"
        docker-compose up -d
        echo "Waiting for services to be ready..."
        sleep 10
    fi
}

run_health_checks() {
    print_header "Running Health Checks"
    
    # LightRAG health check
    echo -n "LightRAG API: "
    if curl -s http://localhost:8081/health 2>/dev/null | grep -q "healthy"; then
        echo -e "${GREEN}✓ Healthy${NC}"
    else
        echo -e "${RED}✗ Unhealthy${NC}"
        echo "Checking LightRAG logs..."
        docker-compose logs --tail=20 lightrag
        return 1
    fi
    
    # Nginx health check
    echo -n "Nginx Gateway: "
    if curl -s http://localhost/health 2>/dev/null; then
        echo -e "${GREEN}✓ Healthy${NC}"
    else
        echo -e "${YELLOW}⚠ Gateway may not be configured${NC}"
    fi
    
    # PostgreSQL check
    echo -n "PostgreSQL with pgvector: "
    if docker-compose exec -T postgres psql -U postgres -c "SELECT * FROM pg_extension WHERE extname='vector'" 2>/dev/null | grep -q "vector"; then
        echo -e "${GREEN}✓ pgvector installed${NC}"
    else
        echo -e "${RED}✗ pgvector not installed${NC}"
        return 1
    fi
}

run_basic_tests() {
    print_header "Running Basic Integration Tests"
    
    cd "$PROJECT_ROOT"
    
    # Set environment variables
    export LIGHTRAG_API_URL="${LIGHTRAG_API_URL:-http://localhost:8081}"
    export PYTHONUNBUFFERED=1
    
    echo -e "${BLUE}Executing: test_rag_pipeline.py${NC}"
    python3 "${TEST_DIR}/test_rag_pipeline.py"
    
    return $?
}

run_advanced_tests() {
    print_header "Running Advanced Integration Tests"
    
    cd "$PROJECT_ROOT"
    
    # Set environment variables
    export LIGHTRAG_API_URL="${LIGHTRAG_API_URL:-http://localhost:8081}"
    export PYTHONUNBUFFERED=1
    
    echo -e "${BLUE}Executing: test_advanced_pipeline.py${NC}"
    python3 "${TEST_DIR}/test_advanced_pipeline.py"
    
    return $?
}

run_performance_tests() {
    print_header "Running Performance Tests"
    
    echo -e "${YELLOW}Performance testing suite...${NC}"
    
    # Create sample large dataset for performance testing
    echo "Generating large test dataset..."
    python3 -c "
import json
import random

domains = ['tech', 'health', 'business', 'science']
docs = []
for i in range(100):
    doc = {
        'id': f'perf_test_{i}',
        'content': f'This is test document {i} with content about {random.choice(domains)}. ' * 50,
        'metadata': {
            'domain': random.choice(domains),
            'index': i
        }
    }
    docs.append(doc)

with open('/tmp/perf_test_data.json', 'w') as f:
    json.dump(docs, f)
print(f'Generated {len(docs)} test documents')
"
    
    # Run performance test
    python3 -c "
import requests
import json
import time
import concurrent.futures

api_url = 'http://localhost:8081'

# Load test data
with open('/tmp/perf_test_data.json', 'r') as f:
    docs = json.load(f)

print('Starting performance test with {} documents'.format(len(docs)))

# Test ingestion performance
start_time = time.time()
successful = 0

with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
    futures = []
    for doc in docs[:20]:  # Test with subset
        future = executor.submit(
            requests.post,
            f'{api_url}/api/ingest/text',
            json={'text': doc['content'], 'metadata': doc['metadata']},
            timeout=10
        )
        futures.append(future)
    
    for future in concurrent.futures.as_completed(futures):
        try:
            if future.result().status_code == 200:
                successful += 1
        except:
            pass

elapsed = time.time() - start_time
print(f'Ingested {successful}/20 documents in {elapsed:.2f} seconds')
print(f'Throughput: {successful/elapsed:.2f} docs/sec')

# Test query performance
query_times = []
for i in range(10):
    start = time.time()
    try:
        response = requests.post(
            f'{api_url}/api/query',
            json={'query': f'Tell me about document {i}'},
            timeout=5
        )
        if response.status_code == 200:
            query_times.append(time.time() - start)
    except:
        pass

if query_times:
    avg_query_time = sum(query_times) / len(query_times)
    print(f'Average query time: {avg_query_time:.3f} seconds')
    print(f'Min query time: {min(query_times):.3f} seconds')
    print(f'Max query time: {max(query_times):.3f} seconds')
"
    
    # Cleanup
    rm -f /tmp/perf_test_data.json
}

run_docker_tests() {
    print_header "Running Tests in Docker Container"
    
    cd "$PROJECT_ROOT"
    
    echo -e "${BLUE}Building test container...${NC}"
    docker-compose -f docker-compose.yml -f docker-compose.test.yml build test-runner
    
    echo -e "${BLUE}Running containerized tests...${NC}"
    docker-compose -f docker-compose.yml -f docker-compose.test.yml run --rm test-runner
    
    return $?
}

create_test_report() {
    print_header "Generating Test Report"
    
    # Create report directory if it doesn't exist
    mkdir -p "$REPORT_DIR"
    
    # Generate timestamp
    TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
    REPORT_FILE="${REPORT_DIR}/integration_test_report_${TIMESTAMP}.txt"
    
    {
        echo "RAG Pipeline Integration Test Report"
        echo "===================================="
        echo "Date: $(date)"
        echo "Test Mode: $TEST_MODE"
        echo ""
        echo "Environment:"
        echo "  - Docker version: $(docker --version)"
        echo "  - Docker Compose version: $(docker-compose --version)"
        echo "  - Python version: $(python3 --version)"
        echo ""
        echo "Services Status:"
        docker-compose ps
        echo ""
        echo "Test Results:"
        echo "See individual test outputs above"
    } > "$REPORT_FILE"
    
    echo -e "${GREEN}Report saved to: $REPORT_FILE${NC}"
}

cleanup() {
    print_header "Cleanup"
    
    echo "Cleaning up test artifacts..."
    
    # Remove temporary test files
    rm -f /tmp/test_*.txt
    rm -f /tmp/perf_test_data.json
    
    # Optional: Stop services
    read -p "Stop Docker services? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        docker-compose down
        echo -e "${GREEN}✓ Services stopped${NC}"
    fi
}

# Main execution
main() {
    echo -e "${BLUE}╔════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║   RAG Pipeline Integration Test Suite  ║${NC}"
    echo -e "${BLUE}╚════════════════════════════════════════╝${NC}"
    echo ""
    echo "Test Mode: $TEST_MODE"
    echo ""
    
    # Prerequisites
    check_prerequisites
    
    # Service checks
    check_services
    
    # Health checks
    if ! run_health_checks; then
        echo -e "${RED}Health checks failed. Please check service logs.${NC}"
        exit 1
    fi
    
    # Run tests based on mode
    case "$TEST_MODE" in
        basic)
            run_basic_tests
            TEST_EXIT_CODE=$?
            ;;
        advanced)
            run_advanced_tests
            TEST_EXIT_CODE=$?
            ;;
        performance)
            run_performance_tests
            TEST_EXIT_CODE=$?
            ;;
        docker)
            run_docker_tests
            TEST_EXIT_CODE=$?
            ;;
        all)
            echo -e "${YELLOW}Running all test suites...${NC}"
            
            run_basic_tests
            BASIC_EXIT=$?
            
            run_advanced_tests
            ADVANCED_EXIT=$?
            
            run_performance_tests
            PERF_EXIT=$?
            
            # Overall exit code
            TEST_EXIT_CODE=0
            if [ $BASIC_EXIT -ne 0 ] || [ $ADVANCED_EXIT -ne 0 ] || [ $PERF_EXIT -ne 0 ]; then
                TEST_EXIT_CODE=1
            fi
            ;;
        *)
            echo -e "${RED}Invalid test mode: $TEST_MODE${NC}"
            echo "Usage: $0 [basic|advanced|performance|docker|all]"
            exit 1
            ;;
    esac
    
    # Generate report
    create_test_report
    
    # Final summary
    print_header "Test Summary"
    
    if [ $TEST_EXIT_CODE -eq 0 ]; then
        echo -e "${GREEN}╔════════════════════════════════════════╗${NC}"
        echo -e "${GREEN}║        ✓ ALL TESTS PASSED             ║${NC}"
        echo -e "${GREEN}╚════════════════════════════════════════╝${NC}"
    else
        echo -e "${RED}╔════════════════════════════════════════╗${NC}"
        echo -e "${RED}║        ✗ SOME TESTS FAILED            ║${NC}"
        echo -e "${RED}╚════════════════════════════════════════╝${NC}"
    fi
    
    # Cleanup
    cleanup
    
    exit $TEST_EXIT_CODE
}

# Trap to ensure cleanup on exit
trap cleanup EXIT

# Run main function
main