# Ops Services Template Makefile
# Provides convenient commands for managing the Docker services and testing

.PHONY: help up down restart logs test test-local test-docker clean

# Default target
help:
	@echo "Available commands:"
	@echo "  make up          - Start all services"
	@echo "  make down        - Stop all services"
	@echo "  make restart     - Restart all services"
	@echo "  make logs        - Show logs for all services"
	@echo "  make test        - Run integration tests (local)"
	@echo "  make test-docker - Run integration tests in Docker"
	@echo "  make clean       - Clean up volumes and test data"
	@echo ""
	@echo "Service-specific commands:"
	@echo "  make logs-lightrag  - Show LightRAG logs"
	@echo "  make logs-nginx     - Show Nginx logs"
	@echo "  make shell-lightrag - Open shell in LightRAG container"

# Service management
up:
	docker-compose up -d
	@echo "Waiting for services to be ready..."
	@sleep 5
	@echo "Services started. Check status with: docker-compose ps"

down:
	docker-compose down

restart:
	docker-compose restart

logs:
	docker-compose logs -f

# Service-specific commands
logs-lightrag:
	docker-compose logs -f lightrag

logs-nginx:
	docker-compose logs -f nginx

shell-lightrag:
	docker-compose exec lightrag /bin/bash

# Testing
test: test-local

test-local:
	@echo "Running integration tests locally..."
	@./scripts/test-rag-pipeline.sh

test-docker:
	@echo "Running integration tests in Docker..."
	@docker-compose -f docker-compose.yml -f docker-compose.test.yml run --rm test-runner

# Run quick health checks
health-check:
	@echo "Checking service health..."
	@echo -n "LightRAG API: "
	@curl -s http://localhost:8081/health | grep -q "healthy" && echo "✓ Healthy" || echo "✗ Unhealthy"
	@echo -n "Nginx Gateway: "
	@curl -s http://localhost/health | grep -q "ok" && echo "✓ Healthy" || echo "✗ Unhealthy"

# Development helpers
dev-setup:
	@echo "Setting up development environment..."
	@cp .env.example .env.local 2>/dev/null || true
	@./scripts/generate-secrets.sh
	@echo "Development environment ready!"

# Clean up
clean:
	@echo "Cleaning up..."
	docker-compose down -v
	rm -rf volumes/lightrag/data/*
	rm -rf volumes/postgres/data/*
	rm -rf test-documents/*.processed
	@echo "Cleanup complete!"

# Quick test workflow
quick-test: up health-check test-local
	@echo "Quick test complete!"