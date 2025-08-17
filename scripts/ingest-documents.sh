#!/bin/bash

# LightRAG Document Ingestion Script
# This script provides utilities for ingesting documents into the LightRAG knowledge graph

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
LIGHTRAG_API_URL="${LIGHTRAG_API_URL:-http://localhost:8080}"
LIGHTRAG_API_KEY="${LIGHTRAG_API_KEY:-}"
DEFAULT_DOCS_DIR="${DEFAULT_DOCS_DIR:-./test-documents}"

# Function to display usage
usage() {
    cat << EOF
Usage: $0 [OPTIONS] COMMAND [ARGS]

Commands:
    file FILE_PATH          Ingest a single file
    directory DIR_PATH      Ingest all files in a directory
    url URL                 Ingest content from a URL
    batch FILE_LIST         Ingest files listed in a text file
    test                    Run test ingestion with sample documents
    stats                   Get knowledge graph statistics
    clear                   Clear all data (requires confirmation)

Options:
    -h, --help             Show this help message
    -k, --api-key KEY      API key for authentication
    -u, --url URL          LightRAG API URL (default: http://localhost:8080)
    -r, --recursive        Process directories recursively
    -e, --extensions EXT   File extensions to process (comma-separated)
    -v, --verbose          Verbose output

Examples:
    $0 file /path/to/document.pdf
    $0 directory /path/to/docs -r -e pdf,txt,md
    $0 batch file_list.txt
    $0 test
    $0 stats

EOF
    exit 0
}

# Function to check if LightRAG is accessible
check_lightrag() {
    echo -e "${BLUE}Checking LightRAG service...${NC}"
    
    response=$(curl -s -o /dev/null -w "%{http_code}" "${LIGHTRAG_API_URL}/health")
    
    if [ "$response" -eq 200 ]; then
        echo -e "${GREEN}✓ LightRAG service is healthy${NC}"
        return 0
    else
        echo -e "${RED}✗ LightRAG service is not accessible at ${LIGHTRAG_API_URL}${NC}"
        echo "Please ensure the service is running with: docker-compose up lightrag"
        return 1
    fi
}

# Function to ingest a single file
ingest_file() {
    local file_path="$1"
    
    if [ ! -f "$file_path" ]; then
        echo -e "${RED}Error: File not found: $file_path${NC}"
        return 1
    fi
    
    echo -e "${BLUE}Ingesting file: $file_path${NC}"
    
    # Prepare the API request
    local filename=$(basename "$file_path")
    local auth_header=""
    
    if [ -n "$LIGHTRAG_API_KEY" ]; then
        auth_header="-H \"Authorization: Bearer ${LIGHTRAG_API_KEY}\""
    fi
    
    # Upload the file
    response=$(curl -s -X POST \
        ${auth_header} \
        -F "file=@${file_path}" \
        "${LIGHTRAG_API_URL}/api/documents/upload")
    
    # Check if successful
    if echo "$response" | grep -q '"success":true'; then
        echo -e "${GREEN}✓ Successfully ingested: $filename${NC}"
        return 0
    else
        echo -e "${RED}✗ Failed to ingest: $filename${NC}"
        echo "Response: $response"
        return 1
    fi
}

# Function to ingest a directory
ingest_directory() {
    local dir_path="$1"
    local recursive="${2:-false}"
    local extensions="${3:-}"
    
    if [ ! -d "$dir_path" ]; then
        echo -e "${RED}Error: Directory not found: $dir_path${NC}"
        return 1
    fi
    
    echo -e "${BLUE}Ingesting directory: $dir_path${NC}"
    echo "Recursive: $recursive"
    echo "Extensions: ${extensions:-all supported}"
    
    local find_cmd="find \"$dir_path\""
    
    if [ "$recursive" = "false" ]; then
        find_cmd="$find_cmd -maxdepth 1"
    fi
    
    find_cmd="$find_cmd -type f"
    
    # Add extension filters if specified
    if [ -n "$extensions" ]; then
        IFS=',' read -ra EXT_ARRAY <<< "$extensions"
        local ext_pattern=""
        for ext in "${EXT_ARRAY[@]}"; do
            if [ -n "$ext_pattern" ]; then
                ext_pattern="$ext_pattern -o"
            fi
            ext_pattern="$ext_pattern -name \"*.${ext}\""
        done
        find_cmd="$find_cmd \\( $ext_pattern \\)"
    else
        # Default supported extensions
        find_cmd="$find_cmd \\( -name \"*.txt\" -o -name \"*.md\" -o -name \"*.pdf\" -o -name \"*.docx\" -o -name \"*.html\" -o -name \"*.json\" -o -name \"*.csv\" \\)"
    fi
    
    # Execute find and process files
    local total=0
    local success=0
    local failed=0
    
    while IFS= read -r file; do
        ((total++))
        echo -e "\n${BLUE}[$total] Processing: $(basename "$file")${NC}"
        
        if ingest_file "$file"; then
            ((success++))
        else
            ((failed++))
        fi
    done < <(eval "$find_cmd")
    
    echo -e "\n${GREEN}=== Ingestion Summary ===${NC}"
    echo "Total files: $total"
    echo "Successful: $success"
    echo "Failed: $failed"
}

# Function to ingest from URL
ingest_url() {
    local url="$1"
    
    echo -e "${BLUE}Ingesting content from URL: $url${NC}"
    
    # Download content
    local temp_file=$(mktemp)
    
    if curl -s -L "$url" -o "$temp_file"; then
        # Determine filename from URL
        local filename=$(basename "$url")
        if [ -z "$filename" ] || [ "$filename" = "/" ]; then
            filename="webpage.html"
        fi
        
        # Move to temp location with proper name
        local named_file="/tmp/$filename"
        mv "$temp_file" "$named_file"
        
        # Ingest the file
        ingest_file "$named_file"
        
        # Clean up
        rm -f "$named_file"
    else
        echo -e "${RED}Failed to download content from URL${NC}"
        rm -f "$temp_file"
        return 1
    fi
}

# Function to ingest batch from file list
ingest_batch() {
    local list_file="$1"
    
    if [ ! -f "$list_file" ]; then
        echo -e "${RED}Error: List file not found: $list_file${NC}"
        return 1
    fi
    
    echo -e "${BLUE}Processing batch from: $list_file${NC}"
    
    local total=0
    local success=0
    local failed=0
    
    while IFS= read -r line; do
        # Skip empty lines and comments
        if [ -z "$line" ] || [[ "$line" =~ ^# ]]; then
            continue
        fi
        
        ((total++))
        echo -e "\n${BLUE}[$total] Processing: $line${NC}"
        
        # Check if it's a URL or file
        if [[ "$line" =~ ^https?:// ]]; then
            if ingest_url "$line"; then
                ((success++))
            else
                ((failed++))
            fi
        else
            if ingest_file "$line"; then
                ((success++))
            else
                ((failed++))
            fi
        fi
    done < "$list_file"
    
    echo -e "\n${GREEN}=== Batch Summary ===${NC}"
    echo "Total items: $total"
    echo "Successful: $success"
    echo "Failed: $failed"
}

# Function to run test ingestion
run_test() {
    echo -e "${BLUE}Running test ingestion...${NC}"
    
    # Create test documents directory if it doesn't exist
    mkdir -p "$DEFAULT_DOCS_DIR"
    
    # Create sample documents if they don't exist
    if [ ! -f "$DEFAULT_DOCS_DIR/sample.txt" ]; then
        create_sample_documents
    fi
    
    # Ingest test documents
    ingest_directory "$DEFAULT_DOCS_DIR" false
}

# Function to create sample documents
create_sample_documents() {
    echo -e "${YELLOW}Creating sample documents...${NC}"
    
    # Sample text document
    cat > "$DEFAULT_DOCS_DIR/sample.txt" << 'EOF'
Introduction to LightRAG

LightRAG is a graph-enhanced retrieval system designed for building sophisticated RAG 
(Retrieval-Augmented Generation) applications. It combines the power of vector search 
with graph-based knowledge representation.

Key Features:
1. Entity and relationship extraction
2. Multi-modal document support
3. Hybrid search capabilities
4. PostgreSQL backend support
5. Real-time knowledge graph updates

Use Cases:
- Question answering systems
- Document intelligence
- Knowledge management
- Semantic search applications
EOF
    
    # Sample markdown document
    cat > "$DEFAULT_DOCS_DIR/architecture.md" << 'EOF'
# System Architecture

## Overview
The system consists of multiple microservices orchestrated with Docker Compose.

## Core Services

### n8n
Workflow automation platform for orchestrating data pipelines and integrations.

### Supabase
PostgreSQL database with vector search capabilities via pgvector extension.

### LightRAG
Graph-enhanced retrieval system for intelligent document processing.

### Redis
In-memory cache for session management and performance optimization.

## Network Architecture
- Frontend network: Public-facing services
- Backend network: Internal service communication
- Database network: Isolated database access
EOF
    
    # Sample JSON document
    cat > "$DEFAULT_DOCS_DIR/config.json" << 'EOF'
{
  "service": "LightRAG",
  "version": "1.0.0",
  "features": {
    "entity_extraction": true,
    "relationship_mapping": true,
    "vector_search": true,
    "graph_traversal": true
  },
  "storage": {
    "type": "postgresql",
    "vector_dimensions": 1536,
    "max_chunk_size": 1200
  }
}
EOF
    
    echo -e "${GREEN}✓ Sample documents created in $DEFAULT_DOCS_DIR${NC}"
}

# Function to get graph statistics
get_stats() {
    echo -e "${BLUE}Fetching knowledge graph statistics...${NC}"
    
    local auth_header=""
    if [ -n "$LIGHTRAG_API_KEY" ]; then
        auth_header="-H \"Authorization: Bearer ${LIGHTRAG_API_KEY}\""
    fi
    
    response=$(curl -s ${auth_header} "${LIGHTRAG_API_URL}/api/stats")
    
    if echo "$response" | grep -q '"success":true'; then
        echo -e "${GREEN}Knowledge Graph Statistics:${NC}"
        echo "$response" | python3 -m json.tool 2>/dev/null || echo "$response"
    else
        echo -e "${RED}Failed to fetch statistics${NC}"
        echo "$response"
    fi
}

# Function to clear the knowledge graph
clear_graph() {
    echo -e "${RED}WARNING: This will delete all data from the knowledge graph!${NC}"
    echo -n "Are you sure? Type 'yes' to confirm: "
    read confirmation
    
    if [ "$confirmation" != "yes" ]; then
        echo "Operation cancelled"
        return 0
    fi
    
    echo -e "${YELLOW}Clearing knowledge graph...${NC}"
    
    local auth_header=""
    if [ -n "$LIGHTRAG_API_KEY" ]; then
        auth_header="-H \"Authorization: Bearer ${LIGHTRAG_API_KEY}\""
    fi
    
    response=$(curl -s -X POST ${auth_header} "${LIGHTRAG_API_URL}/api/clear")
    echo "$response"
}

# Parse command line arguments
RECURSIVE=false
EXTENSIONS=""
VERBOSE=false

while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            usage
            ;;
        -k|--api-key)
            LIGHTRAG_API_KEY="$2"
            shift 2
            ;;
        -u|--url)
            LIGHTRAG_API_URL="$2"
            shift 2
            ;;
        -r|--recursive)
            RECURSIVE=true
            shift
            ;;
        -e|--extensions)
            EXTENSIONS="$2"
            shift 2
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        file)
            check_lightrag || exit 1
            ingest_file "$2"
            exit $?
            ;;
        directory)
            check_lightrag || exit 1
            ingest_directory "$2" "$RECURSIVE" "$EXTENSIONS"
            exit $?
            ;;
        url)
            check_lightrag || exit 1
            ingest_url "$2"
            exit $?
            ;;
        batch)
            check_lightrag || exit 1
            ingest_batch "$2"
            exit $?
            ;;
        test)
            check_lightrag || exit 1
            run_test
            exit $?
            ;;
        stats)
            check_lightrag || exit 1
            get_stats
            exit $?
            ;;
        clear)
            check_lightrag || exit 1
            clear_graph
            exit $?
            ;;
        *)
            echo -e "${RED}Unknown command: $1${NC}"
            usage
            ;;
    esac
done

# If no command provided, show usage
usage