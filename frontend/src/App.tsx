import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import {
  ThemeProvider,
  createTheme,
  CssBaseline,
  AppBar,
  Toolbar,
  Typography,
  Container,
  Box,
  Drawer,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  IconButton,
  Badge,
  Alert,
  Snackbar,
} from '@mui/material';
import {
  Menu as MenuIcon,
  Upload as UploadIcon,
  Chat as ChatIcon,
  Search as SearchIcon,
  Description as DocumentIcon,
  Dashboard as DashboardIcon,
  Settings as SettingsIcon,
  BubbleChart as GraphIcon,
} from '@mui/icons-material';

// Import components
import Dashboard from './components/Dashboard';
import DocumentUpload from './components/DocumentUpload';
import ChatInterface from './components/ChatInterface';
import DocumentList from './components/DocumentList';
import SearchInterface from './components/SearchInterface';
import KnowledgeGraph from './components/KnowledgeGraph';
import Settings from './components/Settings';

// Create theme
const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#2196f3',
    },
    secondary: {
      main: '#f50057',
    },
    background: {
      default: '#f5f5f5',
    },
  },
  typography: {
    h4: {
      fontWeight: 600,
    },
  },
});

interface SystemStatus {
  lightrag: boolean;
  supabase: boolean;
  n8n: boolean;
  redis: boolean;
}

function App() {
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [systemStatus, setSystemStatus] = useState<SystemStatus>({
    lightrag: false,
    supabase: false,
    n8n: false,
    redis: false,
  });
  const [notifications, setNotifications] = useState<string[]>([]);
  const [alertOpen, setAlertOpen] = useState(false);
  const [alertMessage, setAlertMessage] = useState('');
  const [alertSeverity, setAlertSeverity] = useState<'success' | 'error' | 'warning' | 'info'>('info');

  useEffect(() => {
    // Check system status on mount
    checkSystemStatus();
    // Set up periodic status check
    const interval = setInterval(checkSystemStatus, 30000);
    return () => clearInterval(interval);
  }, []);

  const checkSystemStatus = async () => {
    try {
      const response = await fetch('/api/lightrag/health');
      setSystemStatus(prev => ({ ...prev, lightrag: response.ok }));
    } catch (error) {
      setSystemStatus(prev => ({ ...prev, lightrag: false }));
    }
  };

  const showAlert = (message: string, severity: 'success' | 'error' | 'warning' | 'info' = 'info') => {
    setAlertMessage(message);
    setAlertSeverity(severity);
    setAlertOpen(true);
  };

  const menuItems = [
    { text: 'Dashboard', icon: <DashboardIcon />, path: '/' },
    { text: 'Upload Documents', icon: <UploadIcon />, path: '/upload' },
    { text: 'Document Library', icon: <DocumentIcon />, path: '/documents' },
    { text: 'Chat', icon: <ChatIcon />, path: '/chat' },
    { text: 'Search', icon: <SearchIcon />, path: '/search' },
    { text: 'Knowledge Graph', icon: <GraphIcon />, path: '/graph' },
    { text: 'Settings', icon: <SettingsIcon />, path: '/settings' },
  ];

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Router>
        <Box sx={{ display: 'flex' }}>
          <AppBar position="fixed">
            <Toolbar>
              <IconButton
                color="inherit"
                aria-label="open drawer"
                edge="start"
                onClick={() => setDrawerOpen(!drawerOpen)}
                sx={{ mr: 2 }}
              >
                <MenuIcon />
              </IconButton>
              <Typography variant="h6" noWrap component="div" sx={{ flexGrow: 1 }}>
                RAG System Interface
              </Typography>
              <Box sx={{ display: 'flex', gap: 2 }}>
                {Object.entries(systemStatus).map(([service, status]) => (
                  <Badge
                    key={service}
                    badgeContent={status ? '✓' : '✗'}
                    color={status ? 'success' : 'error'}
                  >
                    <Typography variant="caption">{service}</Typography>
                  </Badge>
                ))}
              </Box>
            </Toolbar>
          </AppBar>

          <Drawer
            variant="temporary"
            open={drawerOpen}
            onClose={() => setDrawerOpen(false)}
            sx={{
              width: 240,
              flexShrink: 0,
              '& .MuiDrawer-paper': {
                width: 240,
                boxSizing: 'border-box',
                top: '64px',
              },
            }}
          >
            <List>
              {menuItems.map((item) => (
                <ListItem
                  button
                  key={item.text}
                  component={Link}
                  to={item.path}
                  onClick={() => setDrawerOpen(false)}
                >
                  <ListItemIcon>{item.icon}</ListItemIcon>
                  <ListItemText primary={item.text} />
                </ListItem>
              ))}
            </List>
          </Drawer>

          <Box component="main" sx={{ flexGrow: 1, p: 3, mt: 8 }}>
            <Container maxWidth="xl">
              <Routes>
                <Route path="/" element={<Dashboard systemStatus={systemStatus} />} />
                <Route path="/upload" element={<DocumentUpload onAlert={showAlert} />} />
                <Route path="/documents" element={<DocumentList onAlert={showAlert} />} />
                <Route path="/chat" element={<ChatInterface onAlert={showAlert} />} />
                <Route path="/search" element={<SearchInterface onAlert={showAlert} />} />
                <Route path="/graph" element={<KnowledgeGraph />} />
                <Route path="/settings" element={<Settings />} />
              </Routes>
            </Container>
          </Box>
        </Box>

        <Snackbar
          open={alertOpen}
          autoHideDuration={6000}
          onClose={() => setAlertOpen(false)}
          anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
        >
          <Alert onClose={() => setAlertOpen(false)} severity={alertSeverity}>
            {alertMessage}
          </Alert>
        </Snackbar>
      </Router>
    </ThemeProvider>
  );
}

export default App;