import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TablePagination,
  IconButton,
  Chip,
  TextField,
  InputAdornment,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
} from '@mui/material';
import {
  Search as SearchIcon,
  Visibility as ViewIcon,
  Delete as DeleteIcon,
  Download as DownloadIcon,
  Refresh as RefreshIcon,
} from '@mui/icons-material';
import { apiService } from '../services/api';

interface DocumentListProps {
  onAlert: (message: string, severity: 'success' | 'error' | 'warning' | 'info') => void;
}

interface Document {
  id: string;
  filename: string;
  content: string;
  metadata: any;
  created_at: string;
  entities_count: number;
  size: number;
}

const DocumentList: React.FC<DocumentListProps> = ({ onAlert }) => {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedDoc, setSelectedDoc] = useState<Document | null>(null);
  const [viewDialogOpen, setViewDialogOpen] = useState(false);

  useEffect(() => {
    fetchDocuments();
  }, []);

  const fetchDocuments = async () => {
    try {
      setLoading(true);
      // Mock data - replace with actual API call
      const mockDocs: Document[] = [
        {
          id: 'doc1',
          filename: 'AI Healthcare Report.pdf',
          content: 'Content preview...',
          metadata: { type: 'report', tags: ['AI', 'healthcare'] },
          created_at: new Date().toISOString(),
          entities_count: 45,
          size: 1024000,
        },
        {
          id: 'doc2',
          filename: 'Climate Change Analysis.txt',
          content: 'Content preview...',
          metadata: { type: 'article', tags: ['climate', 'environment'] },
          created_at: new Date().toISOString(),
          entities_count: 32,
          size: 512000,
        },
      ];
      setDocuments(mockDocs);
    } catch (error) {
      console.error('Failed to fetch documents:', error);
      onAlert('Failed to load documents', 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleViewDocument = (doc: Document) => {
    setSelectedDoc(doc);
    setViewDialogOpen(true);
  };

  const handleDeleteDocument = async (id: string) => {
    if (window.confirm('Are you sure you want to delete this document?')) {
      try {
        // await apiService.deleteDocument(id);
        setDocuments(prev => prev.filter(d => d.id !== id));
        onAlert('Document deleted successfully', 'success');
      } catch (error) {
        onAlert('Failed to delete document', 'error');
      }
    }
  };

  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(2) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(2) + ' MB';
  };

  const filteredDocuments = documents.filter(doc =>
    doc.filename.toLowerCase().includes(searchTerm.toLowerCase()) ||
    doc.metadata?.tags?.some((tag: string) => 
      tag.toLowerCase().includes(searchTerm.toLowerCase())
    )
  );

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Document Library
      </Typography>

      <Paper sx={{ p: 2, mb: 2 }}>
        <Box sx={{ display: 'flex', gap: 2, alignItems: 'center' }}>
          <TextField
            fullWidth
            variant="outlined"
            placeholder="Search documents..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <SearchIcon />
                </InputAdornment>
              ),
            }}
          />
          <Button
            variant="outlined"
            startIcon={<RefreshIcon />}
            onClick={fetchDocuments}
          >
            Refresh
          </Button>
        </Box>
      </Paper>

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Filename</TableCell>
              <TableCell>Type</TableCell>
              <TableCell>Tags</TableCell>
              <TableCell>Entities</TableCell>
              <TableCell>Size</TableCell>
              <TableCell>Created</TableCell>
              <TableCell>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {filteredDocuments
              .slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage)
              .map((doc) => (
                <TableRow key={doc.id}>
                  <TableCell>{doc.filename}</TableCell>
                  <TableCell>
                    <Chip label={doc.metadata?.type || 'document'} size="small" />
                  </TableCell>
                  <TableCell>
                    {doc.metadata?.tags?.map((tag: string) => (
                      <Chip key={tag} label={tag} size="small" sx={{ mr: 0.5 }} />
                    ))}
                  </TableCell>
                  <TableCell>{doc.entities_count}</TableCell>
                  <TableCell>{formatFileSize(doc.size)}</TableCell>
                  <TableCell>{new Date(doc.created_at).toLocaleDateString()}</TableCell>
                  <TableCell>
                    <IconButton size="small" onClick={() => handleViewDocument(doc)}>
                      <ViewIcon />
                    </IconButton>
                    <IconButton size="small">
                      <DownloadIcon />
                    </IconButton>
                    <IconButton size="small" onClick={() => handleDeleteDocument(doc.id)}>
                      <DeleteIcon />
                    </IconButton>
                  </TableCell>
                </TableRow>
              ))}
          </TableBody>
        </Table>
        <TablePagination
          rowsPerPageOptions={[5, 10, 25]}
          component="div"
          count={filteredDocuments.length}
          rowsPerPage={rowsPerPage}
          page={page}
          onPageChange={(e, newPage) => setPage(newPage)}
          onRowsPerPageChange={(e) => {
            setRowsPerPage(parseInt(e.target.value, 10));
            setPage(0);
          }}
        />
      </TableContainer>

      {/* View Document Dialog */}
      <Dialog open={viewDialogOpen} onClose={() => setViewDialogOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>{selectedDoc?.filename}</DialogTitle>
        <DialogContent>
          <Typography variant="body2" paragraph>
            {selectedDoc?.content}
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setViewDialogOpen(false)}>Close</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default DocumentList;