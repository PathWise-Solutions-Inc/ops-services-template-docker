import axios, { AxiosInstance } from 'axios';

interface IngestDocumentRequest {
  content: string;
  metadata?: any;
}

interface IngestDocumentResponse {
  status: string;
  message: string;
  document_id: string;
  entities_extracted: number;
  processing_time: number;
}

interface SearchRequest {
  query: string;
  searchType: string;
  topK: number;
}

interface SearchResponse {
  query: string;
  results: Array<{
    content: string;
    score: number;
    metadata: any;
    source?: string;
  }>;
  processing_time: number;
  message: string;
}

interface ChatRequest {
  message: string;
  sessionId?: string;
}

interface ChatResponse {
  session_id: string;
  message: string;
  sources?: any[];
  entities?: string[];
  confidence?: number;
}

class ApiService {
  private api: AxiosInstance;
  private lightragApi: AxiosInstance;

  constructor() {
    // Main API client for nginx gateway
    this.api = axios.create({
      baseURL: process.env.REACT_APP_API_URL || 'http://localhost/api',
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Direct LightRAG API client
    this.lightragApi = axios.create({
      baseURL: process.env.REACT_APP_LIGHTRAG_URL || 'http://localhost:8081',
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Request interceptor for auth
    this.api.interceptors.request.use(
      (config) => {
        const token = localStorage.getItem('authToken');
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => {
        return Promise.reject(error);
      }
    );

    // Response interceptor for error handling
    this.api.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response?.status === 401) {
          // Handle unauthorized
          localStorage.removeItem('authToken');
          window.location.href = '/login';
        }
        return Promise.reject(error);
      }
    );
  }

  // Document operations
  async ingestDocument(data: IngestDocumentRequest): Promise<IngestDocumentResponse> {
    const response = await this.lightragApi.post<IngestDocumentResponse>('/ingest', data);
    return response.data;
  }

  async getDocuments() {
    const response = await this.api.get('/documents');
    return response.data;
  }

  async deleteDocument(id: string) {
    const response = await this.api.delete(`/documents/${id}`);
    return response.data;
  }

  // Search operations
  async search(data: SearchRequest): Promise<SearchResponse> {
    // Map searchType to the query endpoint
    const endpoint = '/query';
    const payload = {
      query: data.query,
      top_k: data.topK,
    };
    
    const response = await this.lightragApi.post<SearchResponse>(endpoint, payload);
    return response.data;
  }

  // Chat operations
  async chat(data: ChatRequest): Promise<ChatResponse> {
    // For now, use the query endpoint as a simple chat interface
    // In production, this would connect to the n8n chat workflow
    const response = await this.lightragApi.post('/query', {
      query: data.message,
      top_k: 5,
    });

    // Transform the response to match chat format
    return {
      session_id: data.sessionId || `session-${Date.now()}`,
      message: response.data.results?.[0]?.content || 'I could not find relevant information for your query.',
      sources: response.data.results?.map((r: any) => r.metadata?.source || 'knowledge_graph'),
      confidence: response.data.results?.[0]?.score,
    };
  }

  // Health check
  async checkHealth() {
    try {
      const response = await this.lightragApi.get('/health');
      return response.data;
    } catch {
      return { status: 'error', service: 'lightrag' };
    }
  }

  // Stats
  async getStats() {
    const response = await this.api.get('/stats');
    return response.data;
  }

  // n8n Workflow triggers
  async triggerWorkflow(workflowId: string, data: any) {
    const response = await this.api.post(`/n8n/webhook/${workflowId}`, data);
    return response.data;
  }
}

export const apiService = new ApiService();