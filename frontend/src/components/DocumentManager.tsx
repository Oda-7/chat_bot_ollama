import React, { useState, useCallback } from 'react';
import { apiService } from '../services/api';
import {
  Box,
  Button,
  Paper,
  Typography,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  IconButton,
  LinearProgress,
  Alert,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Chip,
  Divider,
} from '@mui/material';
import {
  CloudUpload,
  Description,
  Delete,
  Search,
  CheckCircle,
  Error as ErrorIcon,
  Pending,
} from '@mui/icons-material';
import { format } from 'date-fns';
import { fr } from 'date-fns/locale';
import {
  ENDPOINT_DOCUMENT,
  ENDPOINT_DOCUMENTS,
  ENDPOINT_UPLOAD_DOCUMENTS,
} from '../constants/endpoint/endpointDocument';
import { DOCUMENT_ALLOWED_TYPES } from '../constants/document/documentAllowedTypes';
import { DOCUMENT_ALLOWED_EXTENSIONS } from '../constants/document/documentAllowedExtensions';

interface Document {
  id: string;
  filename: string;
  content_preview: string;
  file_size: number;
  chunk_count: number;
  status: 'processing' | 'processed' | 'error';
  created_at: string;
}

interface DocumentManagerProps {
  token: string;
  onError?: (error: string) => void;
  onSuccess?: (message: string) => void;
}

const DocumentManager: React.FC<DocumentManagerProps> = ({
  token,
  onError,
  onSuccess,
}) => {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [uploading, setUploading] = useState(false);
  const [loading, setLoading] = useState(false);
  const [searchDialogOpen, setSearchDialogOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<any[]>([]);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const showError = useCallback((msg: string) => {
    setErrorMsg(msg);
    setTimeout(() => setErrorMsg(null), 5000);
  }, []);

  const loadDocuments = useCallback(async () => {
    setLoading(true);
    try {
      const docs = await apiService.get<Document[]>(ENDPOINT_DOCUMENTS, {
        headers: { Authorization: `Bearer ${token}` },
      });

      setDocuments(docs || []);
    } catch (error) {
      showError('Impossible de charger les documents');
      console.error('Erreur chargement documents:', error);
    } finally {
      setLoading(false);
    }
  }, [token, onError, showError]);

  React.useEffect(() => {
    loadDocuments();
  }, []);

  const handleFileUpload = useCallback(
    async (event: React.ChangeEvent<HTMLInputElement>) => {
      const file = event.target.files?.[0];
      if (!file) return;

      const maxSize = 10 * 1024 * 1024; // 10MB
      if (file.size > maxSize) {
        if (onError) {
          onError('Fichier trop volumineux (max 10MB)');
        }
        return;
      }
      const fileExtension = file.name.split('.').pop()?.toLowerCase() || '';

      const isValidExtension =
        DOCUMENT_ALLOWED_EXTENSIONS.includes(fileExtension);
      const isValidType = DOCUMENT_ALLOWED_TYPES.includes(file.type);

      if (!isValidExtension && !isValidType) {
        if (onError) {
          onError(
            `Fichier non supporté: ${file.name}\n` +
              `Extension: ${fileExtension || 'aucune'}\n` +
              `Type: ${file.type || 'inconnu'}\n\n` +
              `Extensions autorisées: ${DOCUMENT_ALLOWED_EXTENSIONS.join(', ')}`
          );
        }
        return;
      }

      setUploading(true);

      try {
        const formData = new FormData();
        formData.append('file', file);
        formData.append('title', file.name);

        await apiService.postForm(ENDPOINT_UPLOAD_DOCUMENTS, formData, {
          headers: { Authorization: `Bearer ${token}` },
        });

        if (onSuccess) onSuccess(`Document "${file.name}" uploadé avec succès`);
        await loadDocuments();
      } catch (error) {
        console.error('Erreur upload:', error);
        if (onError && error instanceof Error) {
          onError(`Erreur upload: ${error.message}`);
        }
      } finally {
        setUploading(false);
        event.target.value = '';
      }
    },
    [token, onError, onSuccess, loadDocuments]
  );

  const handleDeleteDocument = async (docId: string, filename: string) => {
    if (!window.confirm(`Supprimer le document "${filename}" ?`)) {
      return;
    }

    try {
      await apiService.delete(`${ENDPOINT_DOCUMENTS}/${docId}`, {
        headers: { Authorization: `Bearer ${token}` },
      });

      if (onSuccess) onSuccess(`Document "${filename}" supprimé`);
      await loadDocuments();
    } catch (error) {
      console.error('Erreur suppression:', error);
      if (onError) {
        onError(`Impossible de supprimer "${filename}"`);
      }
    }
  };

  const handleSearch = async () => {
    if (!searchQuery.trim()) return;

    setLoading(true);
    try {
      const form = new FormData();
      form.append('query', searchQuery);
      form.append('top_k', '10');
      form.append('similarity_threshold', '0.5');

      const results = await apiService.postForm<any>(ENDPOINT_DOCUMENT, form, {
        headers: { Authorization: `Bearer ${token}` },
      });

      setSearchResults(results?.results || results || []);
    } catch (error) {
      console.error('Erreur recherche:', error);
      if (onError && error instanceof Error) onError(error.message);
    } finally {
      setLoading(false);
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'processed':
        return <CheckCircle color="success" />;
      case 'processing':
        return <Pending color="warning" />;
      case 'error':
        return <ErrorIcon color="error" />;
      default:
        return <Pending />;
    }
  };

  const getStatusColor = (
    status: string
  ):
    | 'default'
    | 'primary'
    | 'secondary'
    | 'error'
    | 'info'
    | 'success'
    | 'warning' => {
    switch (status) {
      case 'processed':
        return 'success';
      case 'processing':
        return 'warning';
      case 'error':
        return 'error';
      default:
        return 'default';
    }
  };

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  return (
    <Box sx={{ p: 2 }}>
      {/* Header avec upload */}
      <Box
        sx={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          mb: 3,
        }}
      >
        <Typography variant="h5">Mes Documents ({documents.length})</Typography>

        <Box sx={{ display: 'flex', gap: 1 }}>
          <Button
            variant="outlined"
            startIcon={<Search />}
            onClick={() => setSearchDialogOpen(true)}
            disabled={documents.length === 0}
          >
            Rechercher
          </Button>

          <label htmlFor="file-upload">
            <input
              id="file-upload"
              type="file"
              accept=".txt,.pdf,.html,application/json, .csv, .xlsx, .docx, .md, .xml, .xls"
              style={{ display: 'none' }}
              onChange={handleFileUpload}
            />
            <Button
              variant="contained"
              component="span"
              startIcon={<CloudUpload />}
            >
              Uploader
            </Button>
          </label>
        </Box>
      </Box>

      {uploading && (
        <Box sx={{ mb: 2 }}>
          <Alert severity="info">Upload en cours...</Alert>
          <LinearProgress sx={{ mt: 1 }} />
        </Box>
      )}

      {loading ? (
        <Box sx={{ textAlign: 'center', py: 4 }}>
          <LinearProgress sx={{ mb: 2 }} />
          <Typography>Chargement des documents...</Typography>
        </Box>
      ) : documents.length === 0 ? (
        <Paper sx={{ p: 4, textAlign: 'center', bgcolor: 'grey.50' }}>
          <Description sx={{ fontSize: 64, color: 'grey.400', mb: 2 }} />
          <Typography variant="h6" color="text.secondary" gutterBottom>
            Aucun document
          </Typography>
          <Typography color="text.secondary" component="span">
            Uploadez des documents pour enrichir les réponses de l'IA avec vos
            propres données.
          </Typography>
          <Typography variant="caption" color="text.secondary">
            Formats supportés: TXT, PDF, HTML, JSON (max 10MB)
          </Typography>
        </Paper>
      ) : (
        <List>
          {documents.map((doc) => (
            <React.Fragment key={doc.id}>
              <ListItem>
                <Box sx={{ display: 'flex', alignItems: 'center', mr: 2 }}>
                  {getStatusIcon(doc.status)}
                </Box>

                <ListItemText
                  disableTypography
                  primary={
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <Typography variant="subtitle1">
                        {doc.filename}
                      </Typography>
                      <Chip
                        label={doc.status}
                        size="small"
                        color={getStatusColor(doc.status)}
                        variant="outlined"
                      />
                    </Box>
                  }
                  secondary={
                    <Box>
                      <Typography
                        variant="body2"
                        color="text.secondary"
                        component="span"
                        sx={{ display: 'block', mb: 1 }}
                      >
                        {doc.content_preview}
                      </Typography>
                      <Box sx={{ display: 'flex', gap: 2, mt: 1 }}>
                        <Typography variant="caption">
                          📄 {formatFileSize(doc.file_size)}
                        </Typography>
                        <Typography variant="caption">
                          🧩 {doc.chunk_count} chunks
                        </Typography>
                        <Typography variant="caption">
                          📅{' '}
                          {format(
                            new Date(doc.created_at),
                            'dd/MM/yyyy HH:mm',
                            { locale: fr }
                          )}
                        </Typography>
                      </Box>
                    </Box>
                  }
                />

                <ListItemSecondaryAction>
                  <IconButton
                    edge="end"
                    onClick={() => handleDeleteDocument(doc.id, doc.filename)}
                    color="error"
                  >
                    <Delete />
                  </IconButton>
                </ListItemSecondaryAction>
              </ListItem>
              <Divider />
            </React.Fragment>
          ))}
        </List>
      )}

      {/* Dialog de recherche */}
      <Dialog
        open={searchDialogOpen}
        onClose={() => setSearchDialogOpen(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>Rechercher dans les documents</DialogTitle>
        <DialogContent>
          <Box sx={{ mb: 2 }}>
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Que recherchez-vous ?"
              style={{ width: '100%', padding: '8px', marginBottom: '16px' }}
              onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
            />
            <Button
              variant="contained"
              onClick={handleSearch}
              disabled={!searchQuery.trim()}
            >
              Rechercher
            </Button>
          </Box>

          {searchResults.length > 0 && (
            <Box>
              <Typography variant="h6" gutterBottom>
                Résultats ({searchResults.length})
              </Typography>
              {searchResults.map((result, idx) => (
                <Paper key={idx} sx={{ p: 2, mb: 2, bgcolor: 'grey.50' }}>
                  <Box
                    sx={{
                      display: 'flex',
                      justifyContent: 'space-between',
                      mb: 1,
                    }}
                  >
                    <Typography variant="subtitle2" color="primary">
                      📄 {result.filename}
                    </Typography>
                    <Chip
                      label={`${(result.similarity * 100).toFixed(
                        0
                      )}% pertinence`}
                      size="small"
                      color="primary"
                      variant="outlined"
                    />
                  </Box>
                  <Typography variant="body2">
                    {String(result.content).substring(0, 300)}...
                  </Typography>
                </Paper>
              ))}
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setSearchDialogOpen(false)}>Fermer</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default DocumentManager;
