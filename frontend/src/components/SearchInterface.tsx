import React, { useState } from 'react';
import {
  Box,
  Paper,
  Typography,
  TextField,
  Button,
  Card,
  CardContent,
  Chip,
  Grid,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  LinearProgress,
  Accordion,
  AccordionSummary,
  AccordionDetails,
} from '@mui/material';
import {
  Search as SearchIcon,
  ExpandMore as ExpandIcon,
} from '@mui/icons-material';
import ReactMarkdown from 'react-markdown';
import { apiService } from '../services/api';

interface SearchInterfaceProps {
  onAlert: (message: string, severity: 'success' | 'error' | 'warning' | 'info') => void;
}

interface SearchResult {
  content: string;
  score: number;
  metadata: any;
  source?: string;
}

const SearchInterface: React.FC<SearchInterfaceProps> = ({ onAlert }) => {
  const [query, setQuery] = useState('');
  const [searchType, setSearchType] = useState('hybrid');
  const [results, setResults] = useState<SearchResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [searchTime, setSearchTime] = useState(0);

  const handleSearch = async () => {
    if (!query.trim()) {
      onAlert('Please enter a search query', 'warning');
      return;
    }

    setLoading(true);
    const startTime = Date.now();

    try {
      const response = await apiService.search({
        query,
        searchType,
        topK: 10,
      });

      setResults(response.results || []);
      setSearchTime(Date.now() - startTime);
      
      if (response.results?.length === 0) {
        onAlert('No results found', 'info');
      }
    } catch (error) {
      console.error('Search error:', error);
      onAlert('Search failed. Please try again.', 'error');
    } finally {
      setLoading(false);
    }
  };

  const getScoreColor = (score: number) => {
    if (score > 0.8) return 'success';
    if (score > 0.6) return 'warning';
    return 'default';
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Advanced Search
      </Typography>

      <Paper sx={{ p: 3, mb: 3 }}>
        <Grid container spacing={2} alignItems="center">
          <Grid item xs={12} md={7}>
            <TextField
              fullWidth
              label="Search Query"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
              placeholder="Enter your search query..."
            />
          </Grid>
          <Grid item xs={12} md={3}>
            <FormControl fullWidth>
              <InputLabel>Search Type</InputLabel>
              <Select
                value={searchType}
                label="Search Type"
                onChange={(e) => setSearchType(e.target.value)}
              >
                <MenuItem value="hybrid">Hybrid (Recommended)</MenuItem>
                <MenuItem value="vector">Vector Only</MenuItem>
                <MenuItem value="graph">Graph Only</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12} md={2}>
            <Button
              fullWidth
              variant="contained"
              startIcon={<SearchIcon />}
              onClick={handleSearch}
              disabled={loading}
              sx={{ height: '56px' }}
            >
              Search
            </Button>
          </Grid>
        </Grid>

        {loading && <LinearProgress sx={{ mt: 2 }} />}
      </Paper>

      {results.length > 0 && (
        <Box>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
            <Typography variant="h6">
              Results ({results.length})
            </Typography>
            <Typography variant="body2" color="textSecondary">
              Search completed in {searchTime}ms
            </Typography>
          </Box>

          {results.map((result, index) => (
            <Card key={index} sx={{ mb: 2 }}>
              <CardContent>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                  <Typography variant="h6">
                    Result #{index + 1}
                  </Typography>
                  <Box sx={{ display: 'flex', gap: 1 }}>
                    <Chip
                      label={`Score: ${(result.score * 100).toFixed(1)}%`}
                      color={getScoreColor(result.score)}
                      size="small"
                    />
                    <Chip
                      label={result.source || 'Unknown'}
                      size="small"
                      variant="outlined"
                    />
                  </Box>
                </Box>

                <Box sx={{ my: 2 }}>
                  <ReactMarkdown>{result.content}</ReactMarkdown>
                </Box>

                {result.metadata && Object.keys(result.metadata).length > 0 && (
                  <Accordion>
                    <AccordionSummary expandIcon={<ExpandIcon />}>
                      <Typography variant="body2">Metadata</Typography>
                    </AccordionSummary>
                    <AccordionDetails>
                      <pre style={{ fontSize: '0.875rem', overflow: 'auto' }}>
                        {JSON.stringify(result.metadata, null, 2)}
                      </pre>
                    </AccordionDetails>
                  </Accordion>
                )}
              </CardContent>
            </Card>
          ))}
        </Box>
      )}

      {!loading && results.length === 0 && query && (
        <Paper sx={{ p: 4, textAlign: 'center' }}>
          <Typography variant="h6" gutterBottom>
            No results yet
          </Typography>
          <Typography variant="body2" color="textSecondary">
            Enter a query and click search to find relevant information from your knowledge base.
          </Typography>
        </Paper>
      )}
    </Box>
  );
};

export default SearchInterface;