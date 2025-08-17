#!/bin/sh
# Custom entrypoint for Supabase Studio to configure API proxies

# Set up environment variables for API connections
export POSTGRES_META_URL=${POSTGRES_META_URL:-http://postgres-meta:8080}
export NEXT_PUBLIC_POSTGRES_META_URL=${POSTGRES_META_URL}

# Create a simple proxy configuration
cat > /app/api-proxy.js << 'EOF'
const { createProxyMiddleware } = require('http-proxy-middleware');

module.exports = function(app) {
  // Proxy pg-meta API calls
  app.use(
    '/api/pg-meta',
    createProxyMiddleware({
      target: process.env.POSTGRES_META_URL || 'http://postgres-meta:8080',
      changeOrigin: true,
      pathRewrite: {
        '^/api/pg-meta/default': '',
      },
      onProxyReq: (proxyReq, req, res) => {
        // Add database connection headers
        proxyReq.setHeader('Content-Type', 'application/json');
      },
      onError: (err, req, res) => {
        console.error('Proxy error:', err);
        res.status(500).json({ error: 'Proxy error', details: err.message });
      }
    })
  );
};
EOF

# Start the original entrypoint
exec docker-entrypoint.sh "$@"