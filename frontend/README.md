# RAG System Frontend Interface

A modern React-based web interface for interacting with the hybrid RAG (Retrieval-Augmented Generation) backend system.

## Features

### 🎯 Dashboard
- Real-time system status monitoring
- Knowledge base statistics
- Query performance metrics
- Resource usage visualization
- Recent activity tracking

### 📤 Document Upload
- Drag-and-drop file upload
- Multiple file format support (TXT, MD, PDF, JSON, DOCX, CSV)
- Batch upload with progress tracking
- Metadata tagging
- Processing status indicators

### 💬 Chat Interface
- Conversational AI powered by RAG
- Session management
- Source attribution
- Confidence scoring
- Export chat history
- Suggested questions

### 🔍 Advanced Search
- Three search modes:
  - Hybrid (combines vector and graph)
  - Vector-only (semantic similarity)
  - Graph-only (relationship traversal)
- Result ranking and scoring
- Metadata display
- Search performance metrics

### 📚 Document Library
- Browse uploaded documents
- Filter and search capabilities
- View document metadata
- Entity count display
- Download and delete options

### 🕸️ Knowledge Graph
- Visualization placeholder for graph structure
- Node and edge statistics
- Interactive controls (coming soon)

### ⚙️ Settings
- API configuration
- Model parameters
- Application preferences
- Theme customization

## Quick Start

### Development Mode

1. **Install dependencies:**
```bash
cd frontend
npm install
```

2. **Start development server:**
```bash
npm start
```

The app will open at http://localhost:3000

### Docker Mode

**Development (with hot-reloading):**
```bash
docker-compose up frontend
```

Access at http://localhost:3002

**Production build:**
```bash
docker-compose -f docker-compose.yml up frontend
```

## Configuration

### Environment Variables

Create a `.env` file in the frontend directory:

```env
REACT_APP_API_URL=http://localhost/api
REACT_APP_LIGHTRAG_URL=http://localhost:8081
```

### API Endpoints

The frontend connects to:
- **Main API Gateway**: Port 80 (nginx)
- **LightRAG Service**: Port 8081
- **n8n Workflows**: Port 5678

## Project Structure

```
frontend/
├── public/              # Static assets
│   └── index.html       # HTML template
├── src/
│   ├── components/      # React components
│   │   ├── Dashboard.tsx
│   │   ├── DocumentUpload.tsx
│   │   ├── ChatInterface.tsx
│   │   ├── DocumentList.tsx
│   │   ├── SearchInterface.tsx
│   │   ├── KnowledgeGraph.tsx
│   │   └── Settings.tsx
│   ├── services/        # API services
│   │   └── api.ts       # API client
│   ├── styles/          # CSS files
│   │   └── index.css
│   ├── App.tsx          # Main app component
│   └── index.tsx        # Entry point
├── Dockerfile           # Production build
├── Dockerfile.dev       # Development build
├── nginx.conf          # Nginx configuration
├── package.json        # Dependencies
└── tsconfig.json       # TypeScript config
```

## Usage Guide

### Uploading Documents

1. Navigate to "Upload Documents"
2. Drag files or click to browse
3. Configure metadata (source, type, tags)
4. Click "Upload All"
5. Monitor progress in real-time

### Chatting with RAG

1. Go to "Chat"
2. Type your question
3. View AI response with sources
4. Continue conversation with context
5. Export chat history if needed

### Searching Knowledge Base

1. Open "Search"
2. Enter query terms
3. Select search type
4. Review ranked results
5. Explore metadata and sources

### Managing Documents

1. Visit "Document Library"
2. Search or filter documents
3. View document details
4. Download or delete as needed

## Development

### Available Scripts

- `npm start` - Run development server
- `npm build` - Build for production
- `npm test` - Run tests
- `npm run eject` - Eject from Create React App

### Technology Stack

- **React 18** - UI framework
- **TypeScript** - Type safety
- **Material-UI** - Component library
- **React Router** - Navigation
- **Axios** - HTTP client
- **Recharts** - Data visualization
- **React Markdown** - Markdown rendering
- **React Dropzone** - File uploads

### Connecting to Backend

The frontend uses proxy configuration in development and nginx reverse proxy in production to connect to backend services:

```javascript
// API calls are proxied through nginx
const response = await fetch('/api/lightrag/health');

// Direct LightRAG calls
const response = await fetch('http://localhost:8081/ingest');
```

## Troubleshooting

### Common Issues

**CORS Errors**
- Ensure nginx is running and properly configured
- Check API endpoint URLs in environment variables

**Connection Refused**
- Verify all backend services are running
- Check Docker network configuration
- Confirm port mappings

**Build Failures**
- Clear node_modules and reinstall
- Check Node.js version (18+ required)
- Verify TypeScript configuration

**Hot Reload Not Working**
- Set CHOKIDAR_USEPOLLING=true in Docker
- Check volume mounts in docker-compose

## Contributing

1. Create feature branch
2. Make changes
3. Test thoroughly
4. Submit pull request

## Future Enhancements

- [ ] Real knowledge graph visualization with D3.js
- [ ] WebSocket support for real-time updates
- [ ] Advanced document preview
- [ ] Batch operations for documents
- [ ] User authentication and authorization
- [ ] Dark mode theme
- [ ] Export to various formats
- [ ] Collaborative features
- [ ] Mobile responsive improvements
- [ ] Offline support with service workers

## License

MIT