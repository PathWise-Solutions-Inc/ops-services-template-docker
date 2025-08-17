# Health Check Configuration
# Aggregates health status from all services

location /health/all {
    access_log off;
    
    # Only allow internal and monitoring IPs
    allow 10.0.0.0/8;
    allow 172.16.0.0/12;
    allow 192.168.0.0/16;
    allow 127.0.0.1;
    deny all;
    
    default_type application/json;
    
    # This would typically be handled by a health check aggregator
    # For now, return a simple JSON response
    return 200 '{
        "status": "healthy",
        "timestamp": "$time_iso8601",
        "services": {
            "nginx": "healthy",
            "n8n": "check /health/n8n",
            "supabase": "check /health/supabase",
            "lightrag": "check /health/lightrag",
            "redis": "check /health/redis"
        }
    }';
}

# Individual service health checks
location /health/n8n {
    access_log off;
    internal;
    
    proxy_connect_timeout 2s;
    proxy_read_timeout 2s;
    proxy_pass http://n8n/healthz;
}

location /health/supabase {
    access_log off;
    internal;
    
    proxy_connect_timeout 2s;
    proxy_read_timeout 2s;
    proxy_pass http://supabase/health;
}

location /health/lightrag {
    access_log off;
    internal;
    
    proxy_connect_timeout 2s;
    proxy_read_timeout 2s;
    proxy_pass http://lightrag/health;
}

location /health/redis {
    access_log off;
    internal;
    
    # Redis doesn't have HTTP health check, so we use a TCP check
    # This would typically be handled by a separate health check script
    return 200 "redis health check via TCP";
}

location /health/postgres {
    access_log off;
    internal;
    
    # PostgreSQL health would be checked via pg_isready
    # This would typically be handled by a separate health check script
    return 200 "postgres health check via pg_isready";
}

# Readiness check
location /ready {
    access_log off;
    
    # Check if all critical services are ready
    # In production, this would aggregate actual service readiness
    return 200 "ready\n";
}

# Liveness check
location /alive {
    access_log off;
    return 200 "alive\n";
}