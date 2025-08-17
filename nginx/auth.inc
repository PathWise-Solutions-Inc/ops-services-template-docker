# Authentication and Authorization Configuration

# JWT validation endpoint (internal)
location = /auth/verify {
    internal;
    
    # Set default response
    set $auth_response 401;
    
    # Check for Authorization header
    if ($http_authorization ~* "Bearer (.+)") {
        set $jwt_token $1;
    }
    
    # For development, you can bypass auth by setting this to 200
    # set $auth_response 200;
    
    # In production, forward to auth service for validation
    proxy_method POST;
    proxy_set_header Content-Type "application/json";
    proxy_set_header Authorization "Bearer $jwt_token";
    
    # This would typically go to an auth service
    # For now, we'll use a simple check against Supabase
    proxy_pass http://supabase/auth/v1/verify;
    
    # Set headers for upstream services
    proxy_set_header X-Original-URI $request_uri;
    proxy_set_header X-Original-Method $request_method;
    proxy_set_header X-Auth-Request-Redirect $request_uri;
    
    # Don't forward the body
    proxy_pass_request_body off;
    proxy_set_header Content-Length "";
    
    # Cache validation results
    proxy_cache auth_cache;
    proxy_cache_valid 200 10m;
    proxy_cache_valid 401 1m;
    proxy_cache_key "$http_authorization";
}

# Basic Auth endpoint (alternative to JWT)
location = /auth/basic {
    internal;
    
    # Check for Basic auth header
    if ($http_authorization ~* "Basic (.+)") {
        set $basic_auth $1;
    }
    
    # Validate against stored credentials
    # In production, this would check against a user database
    auth_basic "Restricted Access";
    auth_basic_user_file /etc/nginx/.htpasswd;
    
    return 200;
}

# Login endpoint
location /auth/login {
    limit_req zone=auth burst=5 nodelay;
    
    # CORS headers
    add_header Access-Control-Allow-Origin $cors_origin always;
    add_header Access-Control-Allow-Methods "POST, OPTIONS" always;
    add_header Access-Control-Allow-Headers "Content-Type" always;
    add_header Access-Control-Allow-Credentials true always;
    
    if ($request_method = OPTIONS) {
        return 204;
    }
    
    # Proxy to Supabase auth
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    
    proxy_pass http://supabase/auth/v1/token?grant_type=password;
}

# Logout endpoint
location /auth/logout {
    limit_req zone=auth burst=5 nodelay;
    
    # CORS headers
    add_header Access-Control-Allow-Origin $cors_origin always;
    add_header Access-Control-Allow-Methods "POST, OPTIONS" always;
    add_header Access-Control-Allow-Headers "Authorization" always;
    add_header Access-Control-Allow-Credentials true always;
    
    if ($request_method = OPTIONS) {
        return 204;
    }
    
    # Clear auth cookies if used
    add_header Set-Cookie "auth_token=; Path=/; Max-Age=0; HttpOnly; Secure; SameSite=Strict" always;
    
    # Proxy to Supabase logout
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_set_header Authorization $http_authorization;
    
    proxy_pass http://supabase/auth/v1/logout;
}

# Refresh token endpoint
location /auth/refresh {
    limit_req zone=auth burst=5 nodelay;
    
    # CORS headers
    add_header Access-Control-Allow-Origin $cors_origin always;
    add_header Access-Control-Allow-Methods "POST, OPTIONS" always;
    add_header Access-Control-Allow-Headers "Authorization, Content-Type" always;
    add_header Access-Control-Allow-Credentials true always;
    
    if ($request_method = OPTIONS) {
        return 204;
    }
    
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    
    proxy_pass http://supabase/auth/v1/token?grant_type=refresh_token;
}

# User info endpoint
location /auth/user {
    limit_req zone=general burst=10 nodelay;
    
    # Require authentication
    auth_request /auth/verify;
    auth_request_set $auth_user $upstream_http_x_auth_user;
    
    # CORS headers
    add_header Access-Control-Allow-Origin $cors_origin always;
    add_header Access-Control-Allow-Methods "GET, OPTIONS" always;
    add_header Access-Control-Allow-Headers "Authorization" always;
    add_header Access-Control-Allow-Credentials true always;
    
    if ($request_method = OPTIONS) {
        return 204;
    }
    
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_set_header Authorization $http_authorization;
    
    proxy_pass http://supabase/auth/v1/user;
}

# OAuth providers
location ~ ^/auth/oauth/(.+)$ {
    limit_req zone=auth burst=5 nodelay;
    
    # CORS headers
    add_header Access-Control-Allow-Origin $cors_origin always;
    add_header Access-Control-Allow-Methods "GET, POST, OPTIONS" always;
    add_header Access-Control-Allow-Headers "Content-Type" always;
    
    if ($request_method = OPTIONS) {
        return 204;
    }
    
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    
    proxy_pass http://supabase/auth/v1/authorize?provider=$1;
}

# API Key validation endpoint (for service-to-service auth)
location = /auth/api-key {
    internal;
    
    # Check for API key header
    if ($http_x_api_key = "") {
        return 401;
    }
    
    # In production, validate against stored API keys
    # For development, accept a known test key
    if ($http_x_api_key = $env_API_GATEWAY_KEY) {
        return 200;
    }
    
    return 401;
}

# Cache zone for auth responses
proxy_cache_path /var/cache/nginx/auth levels=1:2 keys_zone=auth_cache:10m 
                 max_size=10m inactive=10m use_temp_path=off;