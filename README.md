# Ops Services Template - Hybrid RAG Backend

[![Integration Tests](https://github.com/PathWise-Solutions-Inc/ops-services-template-docker/actions/workflows/integration-tests.yml/badge.svg)](https://github.com/PathWise-Solutions-Inc/ops-services-template-docker/actions)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue)](https://www.docker.com/)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

A production-ready, reusable Docker-composed backend template combining n8n workflow automation, Supabase (PostgreSQL with pgvector), and LightRAG (graph-enhanced retrieval) for building sophisticated hybrid RAG (Retrieval-Augmented Generation) applications.

## 🚀 Features

- **Hybrid RAG Architecture**: Combines vector similarity search with knowledge graph traversal
- **LightRAG Integration**: Graph-enhanced retrieval with entity and relationship extraction
- **PostgreSQL + pgvector**: Vector database for semantic search with 1536-dimension embeddings
- **n8n Workflow Automation**: Pre-built workflows for document ingestion and hybrid search
- **Supabase Components**: Self-hosted Supabase with Studio, PostgREST, and Kong gateway
- **Redis Caching**: Session management and caching layer
- **nginx API Gateway**: Reverse proxy with authentication and rate limiting
- **Monitoring Stack**: Prometheus and Grafana for metrics and visualization
- **Network Isolation**: Secure service separation with Docker networks
- **Integration Tests**: Comprehensive test suite validating the entire pipeline

## 📦 Quick Start

### Prerequisites

- Docker & Docker Compose
- Git
- Make (optional but recommended)
- 8GB+ RAM recommended

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/PathWise-Solutions-Inc/ops-services-template-docker.git
cd ops-services-template-docker
```

2. **Copy environment template**
```bash
cp .env.example .env
```

3. **Generate secrets**
```bash
./scripts/generate-secrets.sh
```

4. **Start services**
```bash
docker-compose up -d
```

5. **Verify installation**
```bash
make test-docker
```

## 🎯 Service Endpoints

| Service | URL | Description |
|---------|-----|-------------|
| n8n | http://localhost:5678 | Workflow automation platform |
| LightRAG API | http://localhost:8081 | Graph-enhanced retrieval API |
| Supabase Studio | http://localhost:3001 | Database management UI |
| pgAdmin | http://localhost:5050 | PostgreSQL administration |
| Grafana | http://localhost:3000 | Monitoring dashboards |
| Prometheus | http://localhost:9090 | Metrics collection |
| Kong Gateway | http://localhost:8000 | API gateway |

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         Frontend Network                     │
├─────────────────────────────────────────────────────────────┤
│                    nginx (API Gateway)                       │
├─────────────────────────────────────────────────────────────┤
│                         Backend Network                      │
├──────────────┬──────────────┬──────────────┬───────────────┤
│     n8n      │   LightRAG   │   Supabase   │     Redis     │
│  Workflows   │   Service    │   Services   │    Cache      │
├──────────────┴──────────────┴──────────────┴───────────────┤
│                        Database Network                      │
├─────────────────────────────────────────────────────────────┤
│                PostgreSQL with pgvector                      │
└─────────────────────────────────────────────────────────────┘
```

## 🔧 Configuration

### Environment Variables

Key environment variables (see `.env.example` for full list):

```bash
# Database
POSTGRES_PASSWORD=your-secure-password
POSTGRES_DB=postgres

# n8n
N8N_BASIC_AUTH_USER=admin
N8N_BASIC_AUTH_PASSWORD=your-password
N8N_ENCRYPTION_KEY=your-encryption-key

# Supabase
SUPABASE_JWT_SECRET=your-jwt-secret
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-key

# LightRAG
OPENAI_API_KEY=your-openai-key  # Optional for development
LIGHTRAG_STORAGE_TYPE=postgres

# Redis
REDIS_PASSWORD=your-redis-password
```

### Service Configuration

Each service can be customized via:
- Docker Compose override files
- Environment variables
- Configuration files in respective directories

## 🧪 Testing

### Run Integration Tests
```bash
make test-docker
```

### Test Individual Components
```bash
# Test LightRAG API
curl http://localhost:8081/health

# Test document ingestion
curl -X POST http://localhost:8081/ingest \
  -H "Content-Type: application/json" \
  -d '{"content": "Your document text here"}'

# Test query
curl -X POST http://localhost:8081/query \
  -H "Content-Type: application/json" \
  -d '{"query": "Your question here"}'
```

## 🎓 n8n Workflow Templates

Pre-built workflows in `n8n-workflows/`:

1. **Document Ingestion** - Ingest documents into both vector DB and knowledge graph
2. **Hybrid RAG Search** - Combine vector and graph search with ranking
3. **RAG Agent Chat** - Conversational interface with session management

See [n8n-workflows/README.md](n8n-workflows/README.md) for detailed documentation.

## 📊 Monitoring

### Grafana Dashboards
Access at http://localhost:3000 (admin/admin)
- Service health metrics
- Query performance
- Resource utilization

### Prometheus Metrics
Access at http://localhost:9090
- Service discovery
- Custom metrics
- Alert rules

## 🚢 Deployment

### Development
```bash
docker-compose up -d
```

### Production Considerations
1. Use proper SSL/TLS certificates
2. Configure secure passwords and keys
3. Set up backup procedures
4. Implement rate limiting
5. Configure monitoring alerts
6. Use external PostgreSQL for scaling

## 📝 API Documentation

### LightRAG API

**Health Check**
```http
GET /health
```

**Ingest Document**
```http
POST /ingest
Content-Type: application/json

{
  "content": "Document text",
  "metadata": {}
}
```

**Query Knowledge Base**
```http
POST /query
Content-Type: application/json

{
  "query": "Your question",
  "top_k": 5
}
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📚 Documentation

- [Network Architecture](docs/NETWORK_ARCHITECTURE.md)
- [Testing Guide](docs/TESTING.md)
- [n8n Workflows](n8n-workflows/README.md)
- [Project Status](PROJECT_STATUS.md)

## ⚠️ Known Issues

1. Supabase Studio may show API errors in local setup - this doesn't affect core functionality
2. First startup may take several minutes as Docker images are downloaded
3. pgvector index creation can be slow with large datasets

## 🛠️ Troubleshooting

### Services not starting
```bash
# Check logs
docker-compose logs [service-name]

# Restart specific service
docker-compose restart [service-name]
```

### Database connection issues
```bash
# Check PostgreSQL
docker exec ops-postgres psql -U postgres -c "SELECT 1"

# Verify pgvector extension
docker exec ops-postgres psql -U postgres -c "SELECT * FROM pg_extension WHERE extname='vector'"
```

### Clear all data and restart
```bash
docker-compose down -v
docker-compose up -d
```

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details

## 🙏 Acknowledgments

- [LightRAG](https://github.com/HKUDS/LightRAG) - Graph-enhanced retrieval
- [n8n](https://n8n.io) - Workflow automation
- [Supabase](https://supabase.com) - Open source Firebase alternative
- [pgvector](https://github.com/pgvector/pgvector) - Vector similarity search

## 💬 Support

- [GitHub Issues](https://github.com/PathWise-Solutions-Inc/ops-services-template-docker/issues)
- [Discussions](https://github.com/PathWise-Solutions-Inc/ops-services-template-docker/discussions)

---

Built with ❤️ by PathWise Solutions Inc.