# Network Architecture

## Overview

The Ops Services Template implements a multi-layered network architecture using Docker networks to ensure proper service isolation, security, and communication patterns. This document describes the network topology, security boundaries, and communication flows.

## Network Topology

```
┌─────────────────────────────────────────────────────────────────┐
│                         Internet                                │
└────────────────────────────┬────────────────────────────────────┘
                             │
                    ┌────────▼────────┐
                    │   Nginx Gateway  │
                    │   (Port 80/443)  │
                    └────────┬────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │            Frontend Network              │
        │              (Bridge)                    │
        └────────────────────┬────────────────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │            Backend Network               │
        │              (Bridge)                    │
        │                                          │
        │  ┌──────┐  ┌──────┐  ┌──────────┐     │
        │  │ n8n  │  │Redis │  │ LightRAG │     │
        │  └──────┘  └──────┘  └──────────┘     │
        │                                          │
        │  ┌──────────┐  ┌──────────┐            │
        │  │ Grafana  │  │Prometheus│            │
        │  └──────────┘  └──────────┘            │
        └────────────────────┬────────────────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │           Database Network               │
        │              (Bridge)                    │
        │                                          │
        │         ┌──────────────┐               │
        │         │  PostgreSQL   │               │
        │         │  (Supabase)   │               │
        │         └──────────────┘               │
        └──────────────────────────────────────────┘
```

## Network Definitions

### 1. Frontend Network
**Purpose**: Public-facing network for external client connections

**Services Connected**:
- Nginx (API Gateway)

**Characteristics**:
- Bridge driver for container-to-container communication
- Exposed ports: 80 (HTTP), 443 (HTTPS)
- All external traffic enters through this network
- Implements rate limiting and DDoS protection

**Security**:
- Only Nginx has access to this network
- All traffic must pass through Nginx authentication and authorization
- SSL/TLS termination happens here

### 2. Backend Network
**Purpose**: Internal service communication network

**Services Connected**:
- n8n (Workflow Automation)
- LightRAG (Graph RAG Service)
- Redis (Cache/Session Store)
- Kong (Supabase API Gateway)
- PostgREST (Supabase REST API)
- Grafana (Monitoring Dashboard)
- Prometheus (Metrics Collection)
- Nginx (Gateway - backend interface)

**Characteristics**:
- Bridge driver with internal DNS resolution
- No direct external access
- Service discovery through Docker DNS
- Internal load balancing

**Security**:
- Services can only communicate with authorized peers
- No direct internet access except through Nginx
- Internal authentication between services

### 3. Database Network
**Purpose**: Isolated network for database access

**Services Connected**:
- PostgreSQL (Primary Database)
- Services requiring database access:
  - n8n (for workflow storage)
  - LightRAG (for graph storage)
  - PostgREST (for API access)
  - Kong (for configuration)

**Characteristics**:
- Bridge driver with restricted access
- No external exposure
- Connection pooling enabled
- Persistent connections

**Security**:
- Most restrictive network
- Only services with explicit database requirements can connect
- Database credentials required for access
- No direct external access under any circumstances

## Communication Patterns

### External Client → Service
```
Client → Nginx (Frontend) → Nginx (Backend) → Target Service
```

1. Client connects to Nginx on port 80/443
2. Nginx validates authentication (JWT/API Key)
3. Nginx applies rate limiting
4. Request is proxied to backend service
5. Response follows reverse path

### Service → Service
```
Service A (Backend) → Service B (Backend)
```

- Direct communication within backend network
- Service discovery through Docker DNS
- Internal authentication tokens

### Service → Database
```
Service (Backend) → PostgreSQL (Database)
```

- Service must be connected to both backend and database networks
- Connection pooling through service configuration
- Credentials managed through environment variables

## Port Mappings

| Service | Internal Port | External Port | Network | Purpose |
|---------|--------------|---------------|---------|---------|
| Nginx | 80, 443 | 80, 443 | Frontend/Backend | API Gateway |
| n8n | 5678 | - | Backend | Workflow UI/API |
| PostgreSQL | 5432 | 5432* | Database | Database |
| LightRAG | 8080 | - | Backend | RAG API |
| Redis | 6379 | 6379* | Backend | Cache |
| Grafana | 3000 | - | Backend | Monitoring |
| Prometheus | 9090 | - | Backend | Metrics |
| Kong | 8000, 8443 | - | Backend | Supabase Gateway |
| PostgREST | 3000 | - | Backend | REST API |

*Development only, should be closed in production

## Security Boundaries

### Ingress Security
- All external traffic through Nginx
- Rate limiting per endpoint
- JWT/API Key validation
- CORS policy enforcement
- SSL/TLS encryption

### Network Isolation
- Services cannot cross network boundaries without explicit configuration
- Database network is completely isolated from external access
- Backend services cannot directly accept external connections

### Service Authentication
- JWT tokens for user authentication
- API keys for service-to-service communication
- Database credentials for data access
- Redis password for cache access

## Network Policies

### Default Deny
- All traffic is denied by default
- Explicit allow rules for authorized communication
- No service has internet access except through Nginx

### Egress Control
- Services cannot make external HTTP calls without proxy
- DNS resolution limited to internal services
- External API calls must go through n8n or designated services

### Monitoring Access
- Prometheus can scrape metrics from all backend services
- Grafana can only access Prometheus
- Health checks bypass authentication but are rate-limited

## Disaster Recovery

### Network Failure Scenarios

1. **Frontend Network Failure**
   - Impact: No external access
   - Recovery: Restart Nginx container
   - Monitoring: External health checks

2. **Backend Network Failure**
   - Impact: Service communication disrupted
   - Recovery: Restart affected containers
   - Monitoring: Internal health checks

3. **Database Network Failure**
   - Impact: Data access lost
   - Recovery: Restart database and dependent services
   - Monitoring: Database connection pool metrics

## Best Practices

### Service Deployment
1. Always specify network in service definition
2. Use least-privilege network access
3. Never expose database ports in production
4. Implement service-level authentication

### Network Configuration
1. Use explicit network names, not default
2. Configure DNS properly for service discovery
3. Implement network-level rate limiting
4. Monitor network traffic patterns

### Security Hardening
1. Regular security audits of network rules
2. Implement network segmentation
3. Use encrypted connections between services
4. Regular rotation of service credentials

## Troubleshooting

### Common Issues

1. **Service Cannot Connect to Database**
   - Check if service is in database network
   - Verify database credentials
   - Check connection pool settings

2. **External Access Blocked**
   - Verify Nginx is running
   - Check Nginx configuration
   - Verify port mappings

3. **Service Discovery Failing**
   - Check Docker DNS settings
   - Verify service names
   - Check network connectivity

### Diagnostic Commands

```bash
# List networks
docker network ls

# Inspect network
docker network inspect ops-services_backend

# Test connectivity
docker exec <container> ping <target-service>

# Check network configuration
docker exec <container> ip addr

# View network stats
docker stats --no-stream
```

## Network Monitoring

### Key Metrics
- Network latency between services
- Bandwidth utilization
- Connection pool usage
- Failed connection attempts
- Rate limit violations

### Monitoring Tools
- Prometheus: Network metrics collection
- Grafana: Network dashboard visualization
- Nginx logs: Access patterns and errors
- Docker stats: Container network usage

## Future Improvements

1. **Service Mesh Implementation**
   - Add Istio or Linkerd for advanced traffic management
   - Implement circuit breakers
   - Add distributed tracing

2. **Zero-Trust Networking**
   - Implement mTLS between services
   - Add service identity verification
   - Implement fine-grained network policies

3. **Advanced Load Balancing**
   - Add HAProxy for sophisticated load balancing
   - Implement health-based routing
   - Add automatic failover

## Appendix

### Docker Network Commands Reference

```bash
# Create custom network
docker network create --driver bridge custom-network

# Connect container to network
docker network connect <network> <container>

# Disconnect container from network
docker network disconnect <network> <container>

# Remove network
docker network rm <network>

# Prune unused networks
docker network prune
```

### Network Configuration in docker-compose.yml

```yaml
networks:
  frontend:
    driver: bridge
    ipam:
      config:
        - subnet: 172.20.0.0/16
  backend:
    driver: bridge
    ipam:
      config:
        - subnet: 172.21.0.0/16
  database:
    driver: bridge
    internal: true  # No external access
    ipam:
      config:
        - subnet: 172.22.0.0/16
```