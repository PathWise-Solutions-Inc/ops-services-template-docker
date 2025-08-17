import React, { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import {
  Box,
  Paper,
  Typography,
  Button,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  ListItemSecondaryAction,
  IconButton,
  LinearProgress,
  Chip,
  Grid,
  Card,
  CardContent,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Alert,
} from '@mui/material';
import {
  CloudUpload as UploadIcon,
  Description as FileIcon,
  Delete as DeleteIcon,
  Send as SendIcon,
  CheckCircle as SuccessIcon,
  Error as ErrorIcon,
} from '@mui/icons-material';
import { apiService } from '../services/api';

interface DocumentUploadProps {
  onAlert: (message: string, severity: 'success' | 'error' | 'warning' | 'info') => void;
}

interface UploadFile {
  id: string;
  file: File;
  status: 'pending' | 'uploading' | 'success' | 'error';
  progress: number;
  message?: string;
  metadata?: {
    source?: string;
    type?: string;
    tags?: string[];
  };
}

const DocumentUpload: React.FC<DocumentUploadProps> = ({ onAlert }) => {
  const [files, setFiles] = useState<UploadFile[]>([]);
  const [uploading, setUploading] = useState(false);
  const [metadata, setMetadata] = useState({
    source: 'manual',
    type: 'document',
    tags: '',
  });

  const onDrop = useCallback((acceptedFiles: File[]) => {
    const newFiles = acceptedFiles.map((file) => ({
      id: Math.random().toString(36).substr(2, 9),
      file,
      status: 'pending' as const,
      progress: 0,
    }));
    setFiles((prev) => [...prev, ...newFiles]);
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'text/*': ['.txt', '.md', '.csv'],
      'application/pdf': ['.pdf'],
      'application/json': ['.json'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
    },
  });

  const removeFile = (id: string) => {
    setFiles((prev) => prev.filter((f) => f.id !== id));
  };

  const uploadFile = async (uploadFile: UploadFile) => {
    try {
      // Update status to uploading
      setFiles((prev) =>
        prev.map((f) =>
          f.id === uploadFile.id
            ? { ...f, status: 'uploading', progress: 0 }
            : f
        )
      );

      // Read file content
      const content = await readFileContent(uploadFile.file);

      // Simulate progress
      for (let i = 0; i <= 90; i += 10) {
        setFiles((prev) =>
          prev.map((f) =>
            f.id === uploadFile.id ? { ...f, progress: i } : f
          )
        );
        await new Promise((resolve) => setTimeout(resolve, 100));
      }

      // Upload to API
      const response = await apiService.ingestDocument({
        content,
        metadata: {
          filename: uploadFile.file.name,
          source: metadata.source,
          type: metadata.type,
          tags: metadata.tags.split(',').map((t) => t.trim()).filter(Boolean),
          size: uploadFile.file.size,
          mimeType: uploadFile.file.type,
        },
      });

      // Update status to success
      setFiles((prev) =>
        prev.map((f) =>
          f.id === uploadFile.id
            ? {
                ...f,
                status: 'success',
                progress: 100,
                message: `Document ID: ${response.document_id}`,
              }
            : f
        )
      );

      onAlert(`Successfully uploaded ${uploadFile.file.name}`, 'success');
    } catch (error) {
      console.error('Upload error:', error);
      setFiles((prev) =>
        prev.map((f) =>
          f.id === uploadFile.id
            ? {
                ...f,
                status: 'error',
                progress: 0,
                message: 'Upload failed',
              }
            : f
        )
      );
      onAlert(`Failed to upload ${uploadFile.file.name}`, 'error');
    }
  };

  const readFileContent = (file: File): Promise<string> => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = (e) => resolve(e.target?.result as string);
      reader.onerror = reject;
      reader.readAsText(file);
    });
  };

  const uploadAll = async () => {
    setUploading(true);
    const pendingFiles = files.filter((f) => f.status === 'pending');
    
    for (const file of pendingFiles) {
      await uploadFile(file);
    }
    
    setUploading(false);
  };

  const clearCompleted = () => {
    setFiles((prev) => prev.filter((f) => f.status !== 'success'));
  };

  const getStatusIcon = (status: UploadFile['status']) => {
    switch (status) {
      case 'success':
        return <SuccessIcon color="success" />;
      case 'error':
        return <ErrorIcon color="error" />;
      default:
        return <FileIcon />;
    }
  };

  const getStatusColor = (status: UploadFile['status']) => {
    switch (status) {
      case 'success':
        return 'success';
      case 'error':
        return 'error';
      case 'uploading':
        return 'primary';
      default:
        return 'default';
    }
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Document Upload
      </Typography>

      <Grid container spacing={3}>
        {/* Upload Area */}
        <Grid item xs={12} md={8}>
          <Paper
            {...getRootProps()}
            sx={{
              p: 4,
              textAlign: 'center',
              cursor: 'pointer',
              backgroundColor: isDragActive ? 'action.hover' : 'background.paper',
              border: '2px dashed',
              borderColor: isDragActive ? 'primary.main' : 'divider',
              transition: 'all 0.3s',
              '&:hover': {
                backgroundColor: 'action.hover',
              },
            }}
          >
            <input {...getInputProps()} />
            <UploadIcon sx={{ fontSize: 64, color: 'action.disabled', mb: 2 }} />
            <Typography variant="h6" gutterBottom>
              {isDragActive
                ? 'Drop files here'
                : 'Drag & drop files here, or click to select'}
            </Typography>
            <Typography variant="body2" color="textSecondary">
              Supported formats: TXT, MD, PDF, JSON, DOCX, CSV
            </Typography>
          </Paper>

          {/* File List */}
          {files.length > 0 && (
            <Paper sx={{ mt: 3, p: 2 }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
                <Typography variant="h6">Files ({files.length})</Typography>
                <Box>
                  <Button
                    variant="contained"
                    startIcon={<SendIcon />}
                    onClick={uploadAll}
                    disabled={uploading || files.every((f) => f.status !== 'pending')}
                    sx={{ mr: 1 }}
                  >
                    Upload All
                  </Button>
                  <Button
                    variant="outlined"
                    onClick={clearCompleted}
                    disabled={!files.some((f) => f.status === 'success')}
                  >
                    Clear Completed
                  </Button>
                </Box>
              </Box>

              <List>
                {files.map((file) => (
                  <ListItem key={file.id}>
                    <ListItemIcon>{getStatusIcon(file.status)}</ListItemIcon>
                    <ListItemText
                      primary={file.file.name}
                      secondary={
                        <Box>
                          <Typography variant="caption">
                            {(file.file.size / 1024).toFixed(2)} KB
                          </Typography>
                          {file.message && (
                            <Typography variant="caption" display="block">
                              {file.message}
                            </Typography>
                          )}
                          {file.status === 'uploading' && (
                            <LinearProgress
                              variant="determinate"
                              value={file.progress}
                              sx={{ mt: 1 }}
                            />
                          )}
                        </Box>
                      }
                    />
                    <Chip
                      label={file.status}
                      size="small"
                      color={getStatusColor(file.status)}
                      sx={{ mr: 2 }}
                    />
                    <ListItemSecondaryAction>
                      <IconButton
                        edge="end"
                        onClick={() => removeFile(file.id)}
                        disabled={file.status === 'uploading'}
                      >
                        <DeleteIcon />
                      </IconButton>
                    </ListItemSecondaryAction>
                  </ListItem>
                ))}
              </List>
            </Paper>
          )}
        </Grid>

        {/* Metadata Configuration */}
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Upload Settings
              </Typography>

              <FormControl fullWidth margin="normal">
                <InputLabel>Source</InputLabel>
                <Select
                  value={metadata.source}
                  label="Source"
                  onChange={(e) =>
                    setMetadata({ ...metadata, source: e.target.value })
                  }
                >
                  <MenuItem value="manual">Manual Upload</MenuItem>
                  <MenuItem value="web">Web Scrape</MenuItem>
                  <MenuItem value="api">API Import</MenuItem>
                  <MenuItem value="email">Email Attachment</MenuItem>
                </Select>
              </FormControl>

              <FormControl fullWidth margin="normal">
                <InputLabel>Document Type</InputLabel>
                <Select
                  value={metadata.type}
                  label="Document Type"
                  onChange={(e) =>
                    setMetadata({ ...metadata, type: e.target.value })
                  }
                >
                  <MenuItem value="document">Document</MenuItem>
                  <MenuItem value="article">Article</MenuItem>
                  <MenuItem value="report">Report</MenuItem>
                  <MenuItem value="research">Research Paper</MenuItem>
                  <MenuItem value="manual">Manual/Guide</MenuItem>
                  <MenuItem value="code">Code</MenuItem>
                </Select>
              </FormControl>

              <TextField
                fullWidth
                margin="normal"
                label="Tags (comma-separated)"
                value={metadata.tags}
                onChange={(e) =>
                  setMetadata({ ...metadata, tags: e.target.value })
                }
                placeholder="ai, healthcare, research"
                helperText="Add tags to help organize and search documents"
              />

              <Alert severity="info" sx={{ mt: 2 }}>
                These settings will be applied to all uploaded documents in this batch.
              </Alert>
            </CardContent>
          </Card>

          <Card sx={{ mt: 2 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Processing Options
              </Typography>
              <Typography variant="body2" color="textSecondary" paragraph>
                Documents will be processed with:
              </Typography>
              <List dense>
                <ListItem>
                  <ListItemText primary="Entity extraction" />
                </ListItem>
                <ListItem>
                  <ListItemText primary="Relationship mapping" />
                </ListItem>
                <ListItem>
                  <ListItemText primary="Vector embedding generation" />
                </ListItem>
                <ListItem>
                  <ListItemText primary="Knowledge graph integration" />
                </ListItem>
              </List>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default DocumentUpload;