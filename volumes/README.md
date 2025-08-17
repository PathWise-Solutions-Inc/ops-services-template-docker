# Volumes Directory

This directory contains persistent data volumes for the Docker services.

## Directory Structure

- `n8n/` - n8n workflow data and credentials
- `postgres/` - PostgreSQL database files
- `redis/` - Redis persistence files  
- `lightrag/` - LightRAG knowledge graph data

## Important Notes

- These directories are mounted as Docker volumes
- Data persists between container restarts
- **DO NOT** commit these directories to version control
- Ensure proper permissions (usually handled by Docker)

## Backup

Regular backups should be performed on:
- PostgreSQL data (critical)
- n8n workflows and credentials
- LightRAG knowledge graph data

Use the `scripts/backup.sh` script for automated backups.