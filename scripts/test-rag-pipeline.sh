#!/bin/bash

# RAG Pipeline Integration Test Runner
# This script runs the complete end-to-end test for the RAG pipeline

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "========================================"
echo "RAG Pipeline Integration Test"
echo "========================================"

# Check if docker-compose is running
echo -e "${YELLOW}Checking Docker services...${NC}"
if ! docker-compose ps | grep -q "lightrag.*Up"; then
    echo -e "${RED}LightRAG service is not running!${NC}"
    echo "Please start services with: docker-compose up -d"
    exit 1
fi

# Check Python availability
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Python 3 is not installed!${NC}"
    exit 1
fi

# Install test dependencies if needed
echo -e "${YELLOW}Checking test dependencies...${NC}"
pip3 install requests --quiet 2>/dev/null || true

# Set environment variables
export LIGHTRAG_API_URL="${LIGHTRAG_API_URL:-http://localhost:8081}"

echo -e "${GREEN}Configuration:${NC}"
echo "  - LightRAG API: $LIGHTRAG_API_URL"
echo ""

# Run the integration test
echo -e "${YELLOW}Running integration tests...${NC}"
python3 tests/integration/test_rag_pipeline.py

# Check exit code
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Integration tests passed successfully!${NC}"
    exit 0
else
    echo -e "${RED}✗ Integration tests failed!${NC}"
    exit 1
fi