import React, { useState, useEffect, useRef } from 'react';
import {
  Box,
  Paper,
  TextField,
  IconButton,
  Typography,
  List,
  ListItem,
  Avatar,
  Chip,
  Card,
  CardContent,
  Divider,
  Button,
  CircularProgress,
  Accordion,
  AccordionSummary,
  AccordionDetails,
} from '@mui/material';
import {
  Send as SendIcon,
  Person as PersonIcon,
  SmartToy as BotIcon,
  ExpandMore as ExpandIcon,
  Clear as ClearIcon,
  Download as DownloadIcon,
  ContentCopy as CopyIcon,
} from '@mui/icons-material';
import ReactMarkdown from 'react-markdown';
import { apiService } from '../services/api';

interface ChatInterfaceProps {
  onAlert: (message: string, severity: 'success' | 'error' | 'warning' | 'info') => void;
}

interface Message {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: Date;
  sources?: any[];
  confidence?: number;
}

interface ChatSession {
  id: string;
  messages: Message[];
  created: Date;
  title?: string;
}

const ChatInterface: React.FC<ChatInterfaceProps> = ({ onAlert }) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [sessionId, setSessionId] = useState<string>('');
  const [sessions, setSessions] = useState<ChatSession[]>([]);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // Initialize session on mount
    startNewSession();
  }, []);

  useEffect(() => {
    // Scroll to bottom when messages change
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const startNewSession = () => {
    const newSessionId = `session-${Date.now()}`;
    setSessionId(newSessionId);
    setMessages([
      {
        id: '1',
        role: 'system',
        content: 'Welcome! I can help you explore your knowledge base. Ask me anything about your uploaded documents.',
        timestamp: new Date(),
      },
    ]);
    
    // Save session
    const newSession: ChatSession = {
      id: newSessionId,
      messages: [],
      created: new Date(),
      title: 'New Chat',
    };
    setSessions(prev => [...prev, newSession]);
  };

  const sendMessage = async () => {
    if (!input.trim()) return;

    const userMessage: Message = {
      id: `msg-${Date.now()}`,
      role: 'user',
      content: input,
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      // Call the chat API
      const response = await apiService.chat({
        message: input,
        sessionId: sessionId,
      });

      const assistantMessage: Message = {
        id: `msg-${Date.now()}-assistant`,
        role: 'assistant',
        content: response.message,
        timestamp: new Date(),
        sources: response.sources,
        confidence: response.confidence,
      };

      setMessages(prev => [...prev, assistantMessage]);
      
      // Update session
      setSessions(prev =>
        prev.map(s =>
          s.id === sessionId
            ? { ...s, messages: [...messages, userMessage, assistantMessage] }
            : s
        )
      );
    } catch (error) {
      console.error('Chat error:', error);
      onAlert('Failed to get response. Please try again.', 'error');
      
      const errorMessage: Message = {
        id: `msg-${Date.now()}-error`,
        role: 'assistant',
        content: 'I apologize, but I encountered an error processing your request. Please try again.',
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const copyMessage = (content: string) => {
    navigator.clipboard.writeText(content);
    onAlert('Message copied to clipboard', 'success');
  };

  const exportChat = () => {
    const chatContent = messages
      .map(m => `${m.role.toUpperCase()}: ${m.content}`)
      .join('\n\n');
    
    const blob = new Blob([chatContent], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `chat-${sessionId}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    
    onAlert('Chat exported successfully', 'success');
  };

  const suggestedQuestions = [
    'What documents have been uploaded?',
    'Summarize the key topics in the knowledge base',
    'What are the main entities in the documents?',
    'Show me relationships between concepts',
  ];

  return (
    <Box sx={{ height: 'calc(100vh - 120px)', display: 'flex' }}>
      {/* Main Chat Area */}
      <Box sx={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
        <Paper sx={{ p: 2, mb: 2 }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Typography variant="h5">RAG Chat Assistant</Typography>
            <Box>
              <Button
                startIcon={<ClearIcon />}
                onClick={startNewSession}
                sx={{ mr: 1 }}
              >
                New Chat
              </Button>
              <Button
                startIcon={<DownloadIcon />}
                onClick={exportChat}
                disabled={messages.length <= 1}
              >
                Export
              </Button>
            </Box>
          </Box>
        </Paper>

        {/* Messages Area */}
        <Paper sx={{ flex: 1, overflow: 'auto', p: 2, mb: 2 }}>
          <List>
            {messages.map((message) => (
              <ListItem
                key={message.id}
                sx={{
                  flexDirection: message.role === 'user' ? 'row-reverse' : 'row',
                  alignItems: 'flex-start',
                  mb: 2,
                }}
              >
                <Avatar
                  sx={{
                    bgcolor: message.role === 'user' ? 'primary.main' : 'secondary.main',
                    mx: 1,
                  }}
                >
                  {message.role === 'user' ? <PersonIcon /> : <BotIcon />}
                </Avatar>
                <Box sx={{ maxWidth: '70%' }}>
                  <Card
                    sx={{
                      bgcolor: message.role === 'user' ? 'primary.light' : 'background.paper',
                      color: message.role === 'user' ? 'white' : 'text.primary',
                    }}
                  >
                    <CardContent>
                      {message.role === 'assistant' ? (
                        <ReactMarkdown>{message.content}</ReactMarkdown>
                      ) : (
                        <Typography>{message.content}</Typography>
                      )}
                      
                      {message.confidence !== undefined && (
                        <Box sx={{ mt: 1 }}>
                          <Chip
                            label={`Confidence: ${(message.confidence * 100).toFixed(0)}%`}
                            size="small"
                            color={message.confidence > 0.7 ? 'success' : 'warning'}
                          />
                        </Box>
                      )}
                    </CardContent>
                  </Card>
                  
                  <Box sx={{ display: 'flex', gap: 1, mt: 1, alignItems: 'center' }}>
                    <Typography variant="caption" color="textSecondary">
                      {message.timestamp.toLocaleTimeString()}
                    </Typography>
                    <IconButton size="small" onClick={() => copyMessage(message.content)}>
                      <CopyIcon fontSize="small" />
                    </IconButton>
                  </Box>

                  {message.sources && message.sources.length > 0 && (
                    <Accordion sx={{ mt: 1 }}>
                      <AccordionSummary expandIcon={<ExpandIcon />}>
                        <Typography variant="caption">
                          Sources ({message.sources.length})
                        </Typography>
                      </AccordionSummary>
                      <AccordionDetails>
                        {message.sources.map((source, idx) => (
                          <Typography key={idx} variant="caption" display="block">
                            • {source}
                          </Typography>
                        ))}
                      </AccordionDetails>
                    </Accordion>
                  )}
                </Box>
              </ListItem>
            ))}
            {loading && (
              <ListItem sx={{ justifyContent: 'center' }}>
                <CircularProgress size={24} />
              </ListItem>
            )}
            <div ref={messagesEndRef} />
          </List>
        </Paper>

        {/* Input Area */}
        <Paper sx={{ p: 2 }}>
          {messages.length === 1 && (
            <Box sx={{ mb: 2 }}>
              <Typography variant="body2" color="textSecondary" gutterBottom>
                Suggested questions:
              </Typography>
              <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                {suggestedQuestions.map((question) => (
                  <Chip
                    key={question}
                    label={question}
                    onClick={() => setInput(question)}
                    clickable
                  />
                ))}
              </Box>
            </Box>
          )}
          
          <Box sx={{ display: 'flex', gap: 1 }}>
            <TextField
              fullWidth
              multiline
              maxRows={4}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Ask a question about your documents..."
              disabled={loading}
            />
            <IconButton
              color="primary"
              onClick={sendMessage}
              disabled={loading || !input.trim()}
              sx={{ alignSelf: 'flex-end' }}
            >
              <SendIcon />
            </IconButton>
          </Box>
        </Paper>
      </Box>

      {/* Sessions Sidebar */}
      <Paper sx={{ width: 300, ml: 2, p: 2, overflow: 'auto' }}>
        <Typography variant="h6" gutterBottom>
          Recent Sessions
        </Typography>
        <Divider sx={{ mb: 2 }} />
        <List>
          {sessions.map((session) => (
            <ListItem
              key={session.id}
              button
              selected={session.id === sessionId}
              onClick={() => {
                setSessionId(session.id);
                setMessages(session.messages);
              }}
            >
              <ListItemText
                primary={session.title || 'Untitled Chat'}
                secondary={session.created.toLocaleDateString()}
              />
            </ListItem>
          ))}
        </List>
      </Paper>
    </Box>
  );
};

export default ChatInterface;