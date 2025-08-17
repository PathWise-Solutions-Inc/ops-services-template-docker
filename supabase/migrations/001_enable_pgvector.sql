-- Enable pgvector extension for vector similarity search
CREATE EXTENSION IF NOT EXISTS vector;

-- Create a sample table for testing vector functionality
CREATE TABLE IF NOT EXISTS vector_test (
    id SERIAL PRIMARY KEY,
    content TEXT,
    embedding vector(1536)  -- OpenAI text-embedding-ada-002 dimension
);

-- Create an index for vector similarity search
CREATE INDEX IF NOT EXISTS vector_test_embedding_idx 
ON vector_test 
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- Sample function to check if vector is working
CREATE OR REPLACE FUNCTION check_vector_extension()
RETURNS TABLE(extension_name TEXT, extension_version TEXT) 
LANGUAGE SQL
AS $$
    SELECT extname::TEXT, extversion::TEXT 
    FROM pg_extension 
    WHERE extname = 'vector';
$$;