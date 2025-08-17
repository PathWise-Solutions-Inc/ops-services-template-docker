#!/bin/bash

# Secure Secret Generation Script for Ops Services Template
# This script generates secure random secrets for all services

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if .env file already exists
if [ -f ".env" ]; then
    echo -e "${YELLOW}Warning: .env file already exists!${NC}"
    read -p "Do you want to overwrite it? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Aborted."
        exit 1
    fi
fi

echo -e "${GREEN}Generating secure secrets for Ops Services...${NC}"

# Function to generate random password
generate_password() {
    openssl rand -base64 32 | tr -d "=+/" | cut -c1-25
}

# Function to generate hex key
generate_hex_key() {
    openssl rand -hex 32
}

# Function to generate JWT secret
generate_jwt_secret() {
    openssl rand -base64 64 | tr -d "\n"
}

# Generate Supabase JWT keys
echo "Generating Supabase JWT keys..."
JWT_SECRET=$(generate_jwt_secret)
# Note: In production, these should be properly generated using Supabase CLI
# These are placeholder values
ANON_KEY="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZS1kZW1vIiwicm9sZSI6ImFub24iLCJleHAiOjE5ODM4MTI5OTZ9.CRXP1A7WOeoJeXxjNni43kdQwgnWNReilDMblYTn_I0"
SERVICE_KEY="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZS1kZW1vIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImV4cCI6MTk4MzgxMjk5Nn0.EGIM96RAZx35lJzdJsyH-qQwv8Hdp7fsn3W0YpN81IU"

# Create .env file
cat > .env << EOF
# Ops Services Template Environment Variables
# Generated on $(date)
# SECURITY WARNING: Keep this file secret and never commit to version control

# ============================================
# PostgreSQL Configuration
# ============================================
POSTGRES_PASSWORD=$(generate_password)
POSTGRES_USER=postgres
POSTGRES_DB=postgres

# ============================================
# Supabase Configuration
# ============================================
SUPABASE_JWT_SECRET=${JWT_SECRET}
SUPABASE_ANON_KEY=${ANON_KEY}
SUPABASE_SERVICE_ROLE_KEY=${SERVICE_KEY}
SUPABASE_PUBLIC_URL=http://localhost:8000
DEFAULT_ORGANIZATION_NAME=Default Organization
DEFAULT_PROJECT_NAME=Ops Services
PGRST_DB_SCHEMAS=public,storage,graphql_public
PGRST_DB_ANON_ROLE=anon
PGRST_JWT_EXP=3600

# ============================================
# n8n Configuration
# ============================================
N8N_BASIC_AUTH_ACTIVE=true
N8N_BASIC_AUTH_USER=admin
N8N_BASIC_AUTH_PASSWORD=$(generate_password)
N8N_ENCRYPTION_KEY=$(generate_hex_key)
N8N_HOST=localhost
N8N_PROTOCOL=http
N8N_WEBHOOK_URL=http://localhost:5678/
N8N_METRICS=true

# ============================================
# LightRAG Configuration
# ============================================
LIGHTRAG_STORAGE_TYPE=postgres
LIGHTRAG_DB_URL=postgresql://postgres:$(grep POSTGRES_PASSWORD .env | cut -d'=' -f2)@postgres:5432/lightrag
LIGHTRAG_API_KEY=$(generate_hex_key)
# Add your OpenAI API key here
OPENAI_API_KEY=sk-your-openai-api-key-here
LIGHTRAG_LOG_LEVEL=INFO

# ============================================
# Redis Configuration
# ============================================
REDIS_PASSWORD=$(generate_password)

# ============================================
# API Gateway Configuration
# ============================================
API_GATEWAY_DOMAIN=localhost
SSL_CERT_PATH=/etc/nginx/ssl/cert.pem
SSL_KEY_PATH=/etc/nginx/ssl/key.pem

# ============================================
# Monitoring Configuration
# ============================================
MONITORING_ADMIN_PASSWORD=$(generate_password)

# ============================================
# Development Settings
# ============================================
NODE_ENV=production
LOG_LEVEL=info
EOF

echo -e "${GREEN}✓ .env file created successfully!${NC}"
echo
echo -e "${YELLOW}Important reminders:${NC}"
echo "1. Add your OpenAI API key to OPENAI_API_KEY in .env"
echo "2. For production, generate proper Supabase keys using Supabase CLI"
echo "3. Keep .env file secure and never commit to version control"
echo "4. Consider using a secrets management system for production"
echo
echo -e "${GREEN}Credentials saved to .env file${NC}"
echo "n8n admin password: Check N8N_BASIC_AUTH_PASSWORD in .env"
echo "Grafana admin password: Check MONITORING_ADMIN_PASSWORD in .env"
echo "PostgreSQL password: Check POSTGRES_PASSWORD in .env"