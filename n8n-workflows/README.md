# n8n Workflow Templates for Hybrid RAG System

This directory contains pre-built n8n workflow templates that demonstrate how to build hybrid RAG (Retrieval-Augmented Generation) agents using both vector search (Supabase/pgvector) and graph-enhanced retrieval (LightRAG).

## Available Workflows

### 1. Document Ingestion (`document-ingestion-rag.json`)

**Purpose**: Ingest documents into both LightRAG knowledge graph and Supabase vector database.

**Features**:
- Accepts documents via webhook endpoint
- Extracts content and metadata
- Sends to LightRAG for entity/relationship extraction
- Optionally generates embeddings and stores in pgvector
- Returns comprehensive ingestion status

**Webhook Endpoint**: `POST /webhook/ingest-document`

**Input Format**:
```json
{
  "content": "Document text content...",
  "source": "web|file|api",
  "type": "article|report|documentation",
  "tags": ["tag1", "tag2"],
  "store_vector": true
}
```

### 2. Hybrid RAG Search (`hybrid-rag-search.json`)

**Purpose**: Perform intelligent search combining vector similarity and graph traversal.

**Features**:
- Supports three search modes: vector-only, graph-only, or hybrid
- Generates query embeddings for vector search
- Queries LightRAG for graph-based results
- Intelligently ranks and combines results
- Augments response with LLM for natural language answers

**Webhook Endpoint**: `POST /webhook/search`

**Input Format**:
```json
{
  "query": "What is the impact of AI on healthcare?",
  "search_type": "hybrid|vector|graph",
  "top_k": 5
}
```

**Search Types**:
- `vector`: Uses only Supabase pgvector similarity search
- `graph`: Uses only LightRAG knowledge graph traversal
- `hybrid`: Combines both approaches with intelligent ranking

### 3. RAG Agent Chat (`rag-agent-chat.json`)

**Purpose**: Conversational AI agent with persistent context and RAG capabilities.

**Features**:
- Session management with Redis
- Conversation history tracking
- Entity and intent extraction
- Context-aware responses
- Fallback handling for out-of-scope queries
- Source attribution

**Webhook Endpoint**: `POST /webhook/chat`

**Input Format**:
```json
{
  "message": "Tell me about Dr. Sarah Johnson's research",
  "session_id": "optional-session-id"
}
```

**Response Format**:
```json
{
  "session_id": "generated-or-provided-id",
  "message": "AI response based on knowledge base...",
  "sources": ["source1", "source2"],
  "entities": ["Dr. Sarah Johnson", "AI", "healthcare"],
  "confidence": 0.85
}
```

## Setup Instructions

### 1. Import Workflows into n8n

1. Access n8n at http://localhost:5678
2. Navigate to Workflows > Import
3. Select each JSON file and import

### 2. Configure Credentials

Each workflow requires the following credentials to be configured in n8n:

#### OpenAI Credentials
- Name: `OpenAI`
- API Key: Your OpenAI API key
- Used for: Embeddings and LLM responses

#### LightRAG API Credentials
- Name: `LightRAG API`
- Type: HTTP Basic Auth (if configured)
- URL: `http://lightrag:8080`
- Used for: Knowledge graph operations

#### Supabase Credentials
- Name: `Supabase`
- URL: `http://kong:8000`
- API Key: Your Supabase anon key
- Used for: Vector database operations

#### Redis Credentials
- Name: `Redis`
- Host: `redis`
- Port: `6379`
- Password: As configured in docker-compose
- Used for: Session management

### 3. Activate Workflows

1. Open each imported workflow
2. Click the "Active" toggle to enable
3. Test webhook endpoints are accessible

## Integration Examples

### Python Client Example

```python
import requests
import json

# Base URL for n8n webhooks
N8N_URL = "http://localhost:5678/webhook"

# Ingest a document
def ingest_document(content, source="api", store_vector=True):
    response = requests.post(
        f"{N8N_URL}/ingest-document",
        json={
            "content": content,
            "source": source,
            "type": "article",
            "tags": ["auto-ingested"],
            "store_vector": store_vector
        }
    )
    return response.json()

# Perform hybrid search
def search(query, search_type="hybrid", top_k=5):
    response = requests.post(
        f"{N8N_URL}/search",
        json={
            "query": query,
            "search_type": search_type,
            "top_k": top_k
        }
    )
    return response.json()

# Chat with agent
def chat(message, session_id=None):
    payload = {"message": message}
    if session_id:
        payload["session_id"] = session_id
    
    response = requests.post(
        f"{N8N_URL}/chat",
        json=payload
    )
    return response.json()

# Example usage
if __name__ == "__main__":
    # Ingest a document
    doc_result = ingest_document(
        "AI is transforming healthcare through predictive analytics..."
    )
    print(f"Document ingested: {doc_result}")
    
    # Search for information
    search_result = search("AI in healthcare", search_type="hybrid")
    print(f"Search results: {json.dumps(search_result, indent=2)}")
    
    # Start a chat session
    chat_result = chat("What are the latest developments in AI healthcare?")
    session_id = chat_result["session_id"]
    print(f"Agent response: {chat_result['message']}")
    
    # Continue conversation
    followup = chat("Tell me more about predictive analytics", session_id)
    print(f"Followup response: {followup['message']}")
```

### JavaScript/Node.js Example

```javascript
const axios = require('axios');

const N8N_URL = 'http://localhost:5678/webhook';

// Ingest document
async function ingestDocument(content, options = {}) {
  const response = await axios.post(`${N8N_URL}/ingest-document`, {
    content,
    source: options.source || 'api',
    type: options.type || 'article',
    tags: options.tags || [],
    store_vector: options.storeVector !== false
  });
  return response.data;
}

// Hybrid search
async function search(query, searchType = 'hybrid', topK = 5) {
  const response = await axios.post(`${N8N_URL}/search`, {
    query,
    search_type: searchType,
    top_k: topK
  });
  return response.data;
}

// Chat with agent
async function chat(message, sessionId = null) {
  const payload = { message };
  if (sessionId) payload.session_id = sessionId;
  
  const response = await axios.post(`${N8N_URL}/chat`, payload);
  return response.data;
}

// Example usage
(async () => {
  try {
    // Ingest
    const docResult = await ingestDocument('AI healthcare content...');
    console.log('Document ingested:', docResult);
    
    // Search
    const searchResult = await search('AI healthcare');
    console.log('Search results:', searchResult);
    
    // Chat
    const chatResult = await chat('Tell me about AI in healthcare');
    console.log('Agent:', chatResult.message);
  } catch (error) {
    console.error('Error:', error.message);
  }
})();
```

## Workflow Customization

### Adjusting Search Weights

In `hybrid-rag-search.json`, modify the ranking function to adjust how vector vs graph results are weighted:

```javascript
// Current: 50/50 split
result.score * 0.5  // Change 0.5 to adjust weight

// Example: Favor graph search (70/30)
vectorScore * 0.3  // Vector gets 30% weight
graphScore * 0.7   // Graph gets 70% weight
```

### Modifying Context Window

In `rag-agent-chat.json`, adjust the conversation history size:

```javascript
const contextWindow = 10; // Change this value
```

### Adding Custom Entity Extraction

Enhance entity extraction in `rag-agent-chat.json`:

```javascript
// Add custom patterns
const customPatterns = [
  /\b[A-Z0-9]{6,}\b/g,  // Product codes
  /\d{3}-\d{3}-\d{4}/g, // Phone numbers
];
```

## Performance Considerations

1. **Embedding Generation**: Cache embeddings when possible to reduce API calls
2. **Session Management**: Configure Redis TTL appropriately for your use case
3. **Search Optimization**: Use appropriate `top_k` values (5-10 recommended)
4. **Rate Limiting**: Implement rate limiting on webhook endpoints in production

## Troubleshooting

### Common Issues

1. **Webhook Not Accessible**
   - Ensure workflow is active
   - Check n8n is running: `docker ps | grep n8n`
   - Verify webhook URL format

2. **Credentials Error**
   - Double-check all credential configurations
   - Ensure service names match docker-compose setup
   - Test connections from n8n credential settings

3. **Search Returns No Results**
   - Verify documents are ingested successfully
   - Check LightRAG and Supabase services are running
   - Review search query formatting

4. **Session Not Persisting**
   - Confirm Redis is running and accessible
   - Check Redis password configuration
   - Verify session TTL settings

## Advanced Features

### Multi-Modal Search

Extend workflows to support image and document file searches by adding:
- File upload handling
- OCR for images
- PDF text extraction
- Multi-modal embeddings

### Feedback Loop

Implement user feedback to improve search quality:
- Add feedback webhook endpoint
- Store feedback in database
- Use for result re-ranking
- Train custom ranking models

### Analytics Dashboard

Track usage and performance:
- Log all queries and responses
- Monitor response times
- Track popular queries
- Identify knowledge gaps

## Support

For issues or questions:
1. Check service logs: `docker-compose logs n8n`
2. Review n8n execution history for debugging
3. Consult main project documentation
4. Submit issues to project repository