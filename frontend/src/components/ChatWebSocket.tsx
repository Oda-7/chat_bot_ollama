import React, { useState, useEffect, useRef, useCallback } from 'react';
import {
  Box,
  TextField,
  Button,
  Paper,
  Typography,
  IconButton,
  Avatar,
  Chip,
  Alert,
  LinearProgress,
  Tooltip,
  Switch,
  FormControlLabel,
} from '@mui/material';
import {
  Send,
  SmartToy,
  Person,
  Source,
  Wifi,
  WifiOff,
} from '@mui/icons-material';
import { format } from 'date-fns';
import { fr } from 'date-fns/locale';
import ReactMarkdown from 'react-markdown';
import getUrlBase from '../utils/getUrlBase';

interface Message {
  id: string;
  type: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: string;
  user_id?: string;
  username?: string;
  llm_used?: string;
  response_time?: number;
  tokens_used?: number;
  rag_sources?: Array<{ filename: string; similarity: number }>;
}

interface ChatWebSocketProps {
  sessionId?: string;
  token: string;
  username?: string;
  onError?: (error: string) => void;
  onSuccess?: (message: string) => void;
  onSessionCreated?: (sessionId: string) => void;
}

const ChatWebSocket: React.FC<ChatWebSocketProps> = ({
  sessionId,
  token,
  username,
  onError,
  onSuccess,
  onSessionCreated,
}) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [newMessage, setNewMessage] = useState('');
  const [isConnected, setIsConnected] = useState(false);
  const [isConnecting, setIsConnecting] = useState(true);
  const [aiThinking, setAiThinking] = useState(false);
  const [useRag, setUseRag] = useState(true);
  const [isLoading, setIsLoading] = useState(false);
  const [reconnectAttempts, setReconnectAttempts] = useState(0);
  const maxReconnectAttempts = 5;

  const ws = useRef<WebSocket | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const reconnectTimer = useRef<NodeJS.Timeout | null>(null);

  const handleWebSocketMessage = useCallback(
    (data: any) => {
      try {
        switch (data.type) {
          case 'ai_message_stream': {
            setAiThinking(true);
            setMessages((prev) => {
              const lastMsg = prev[prev.length - 1];
              if (
                !lastMsg ||
                lastMsg.type !== 'assistant' ||
                lastMsg.id !== 'streaming_ai'
              ) {
                return [
                  ...prev,
                  {
                    id: 'streaming_ai',
                    type: 'assistant',
                    content: data.content,
                    timestamp: data.timestamp,
                    llm_used: 'mistral:7b',
                  },
                ];
              }

              return prev.map((msg, idx) =>
                idx === prev.length - 1 && msg.id === 'streaming_ai'
                  ? { ...msg, content: msg.content + data.content }
                  : msg
              );
            });
            break;
          }
          case 'connection_established':
            setMessages((prev) =>
              prev.filter((msg) => msg.id !== 'system_welcome')
            );

            setMessages((prev) => [
              ...prev,
              {
                id: `welcome_${Date.now()}`,
                type: 'assistant',
                content: `👋 Bonjour ${data.username} ! Je suis l'IA du chatbot, comment puis-je t'aider ?`,
                timestamp: data.timestamp,
                llm_used: 'mistral:7b',
              },
            ]);
            break;

          case 'ai_thinking':
            setAiThinking(true);
            break;

          case 'ai_message': {
            setAiThinking(false);
            setIsLoading(false);
            setMessages((prev) => {
              if (
                prev.length > 0 &&
                prev[prev.length - 1].id === 'streaming_ai'
              ) {
                return [
                  ...prev.slice(0, -1),
                  {
                    id: data.message_id,
                    type: 'assistant',
                    content: prev[prev.length - 1].content || data.content,
                    timestamp: data.timestamp,
                    llm_used: data.llm_used,
                    response_time: data.response_time,
                    tokens_used: data.tokens_used,
                    rag_sources: data.rag_sources,
                  },
                ];
              }

              return [
                ...prev,
                {
                  id: data.message_id,
                  type: 'assistant',
                  content: data.content,
                  timestamp: data.timestamp,
                  llm_used: data.llm_used,
                  response_time: data.response_time,
                  tokens_used: data.tokens_used,
                  rag_sources: data.rag_sources,
                },
              ];
            });
            if (onSuccess) {
              onSuccess(`Réponse générée en ${data.response_time}ms`);
            }
            break;
          }

          case 'ai_error':
            setAiThinking(false);
            setMessages((prev) => [
              ...prev,
              {
                id: `error_${Date.now()}`,
                type: 'system',
                content: `Erreur IA: ${data.error}`,
                timestamp: data.timestamp,
              },
            ]);
            break;

          case 'error':
            if (onError) {
              onError(data.message);
            }
            break;

          default:
            console.log('Message WebSocket non géré:');
        }
      } catch (error) {
        console.error('Erreur dans handleWebSocketMessage:', error);
      }
    },
    [setMessages, setAiThinking, onError, onSuccess]
  );

  const connectWebSocket = useCallback(async () => {
    if (!sessionId || !token) {
      return;
    }

    if (ws.current && ws.current.readyState === WebSocket.OPEN) {
      return;
    }

    try {
      const apiBase = getUrlBase();
      let wsBase = apiBase.replace(/^http/, 'ws').replace(/\/+$/, '');

      const wsUrl = `${wsBase}/api/v1/ws/chat/${sessionId}?token=${encodeURIComponent(
        token
      )}`;

      ws.current = new WebSocket(wsUrl);

      if (ws.current) {
        setIsConnecting(true);
        ws.current.onopen = () => {
          console.log('WebSocket connecté');
          setIsConnected(true);
          setIsConnecting(false);
          setReconnectAttempts(0);
        };

        ws.current.onmessage = (event) => {
          const data = JSON.parse(event.data);
          handleWebSocketMessage(data);
        };

        ws.current.onclose = (event) => {
          if (event.code === 1006) {
            console.warn(
              'Fermeture anormale du WebSocket (1006): probablement une déconnexion réseau ou backend.'
            );
          }
          setIsConnected(false);
          setAiThinking(false);
          setIsLoading(false);
          setIsConnecting(false);
        };

        ws.current.onerror = (error) => {
          console.error('Erreur WebSocket:', error);
          setIsConnected(false);
          setIsConnecting(false);
          if (onError) {
            onError(
              'Erreur de connexion WebSocket. Veuillez vérifier le token ou la session et réessayer.'
            );
          }
        };
      }
    } catch (error) {
      console.error('Erreur lors de la connexion WebSocket:', error);
      if (onError) {
        onError('Impossible de se connecter au chat en temps réel');
      }
    }
  }, [sessionId, token, onError, handleWebSocketMessage]);

  useEffect(() => {
    if (!ws.current && sessionId && token) {
      connectWebSocket();
    }

    return () => {
      if (ws.current) {
        ws.current.close();
        setAiThinking(false);
        setIsLoading(false);
      }

      if (reconnectTimer.current) {
        clearTimeout(reconnectTimer.current);
      }
    };
  }, [sessionId, token]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const sendMessage = () => {
    if (
      !newMessage.trim() ||
      !ws.current ||
      ws.current.readyState !== WebSocket.OPEN ||
      !sessionId
    ) {
      return;
    }

    setIsLoading(true);
    setAiThinking(true);

    setMessages((prev) => [
      ...prev,
      {
        id: `user_${Date.now()}`,
        type: 'user',
        content: newMessage.trim(),
        timestamp: new Date().toISOString(),
        username,
      },
    ]);

    const messageData = {
      type: 'chat_message',
      content: newMessage.trim(),
      use_rag: useRag,
    };

    ws.current.send(JSON.stringify(messageData));
    setNewMessage('');
    setIsLoading(false);
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const formatTimestamp = (timestamp: string) => {
    return format(new Date(timestamp), 'HH:mm', { locale: fr });
  };

  return (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      {/* Header avec statut connexion */}
      <Box sx={{ p: 2, borderBottom: 1, borderColor: 'divider' }}>
        {isConnecting && (
          <Box sx={{ mb: 2 }}>
            <LinearProgress />
            <Typography variant="body2" sx={{ mt: 1, fontStyle: 'italic' }}>
              {reconnectAttempts > 0
                ? `Reconnexion en cours (${reconnectAttempts}/${maxReconnectAttempts})...`
                : 'Connexion au chat en cours...'}
            </Typography>
          </Box>
        )}
        <Box
          sx={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
          }}
        >
          <Typography variant="h6">
            Chat IA - Session {sessionId?.slice(0, 8) || 'Nouvelle'}
          </Typography>

          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <FormControlLabel
              control={
                <Switch
                  checked={useRag}
                  onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
                    setUseRag(e.target.checked)
                  }
                  size="small"
                />
              }
              label={
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                  <Source fontSize="small" />
                  <Typography variant="caption">RAG</Typography>
                </Box>
              }
            />

            <Tooltip title={isConnected ? 'Connecté' : 'Déconnecté'}>
              <IconButton size="small">
                {isConnected ? (
                  <Wifi color="success" />
                ) : (
                  <WifiOff color="error" />
                )}
              </IconButton>
            </Tooltip>
          </Box>
        </Box>
      </Box>

      {/* Zone de messages */}
      <Box sx={{ flex: 1, overflow: 'auto', p: 1 }}>
        {messages.map((message) => (
          <Box
            key={message.id}
            sx={{
              display: 'flex',
              mb: 2,
              alignItems: 'flex-start',
              justifyContent:
                message.type === 'user' ? 'flex-end' : 'flex-start',
            }}
          >
            {message.type !== 'user' && (
              <Avatar sx={{ mr: 1, mt: 0.5 }}>
                <SmartToy />
              </Avatar>
            )}

            <Paper
              sx={{
                p: 2,
                maxWidth: '70%',
                bgcolor:
                  message.type === 'user'
                    ? 'primary.main'
                    : message.type === 'system'
                    ? 'error.light'
                    : 'grey.100',
                color:
                  message.type === 'user'
                    ? 'primary.contrastText'
                    : 'text.primary',
              }}
            >
              <ReactMarkdown>{message.content}</ReactMarkdown>

              <Box
                sx={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  mt: 1,
                }}
              >
                <Typography variant="caption" sx={{ opacity: 0.7 }}>
                  {formatTimestamp(message.timestamp)}
                </Typography>

                {message.type === 'assistant' && (
                  <Box sx={{ display: 'flex', gap: 1 }}>
                    {message.llm_used && (
                      <Chip
                        label={message.llm_used}
                        size="small"
                        variant="outlined"
                      />
                    )}
                    {message.response_time && (
                      <Chip
                        label={`${(message.response_time / 1000).toFixed(1)}s`}
                        size="small"
                        variant="outlined"
                      />
                    )}
                    {message.tokens_used && (
                      <Chip
                        label={`${message.tokens_used} tokens`}
                        size="small"
                        variant="outlined"
                      />
                    )}
                  </Box>
                )}
              </Box>

              {/* Sources RAG */}
              {message.rag_sources && message.rag_sources.length > 0 && (
                <Box sx={{ mt: 1 }}>
                  <Typography variant="caption" sx={{ fontWeight: 'bold' }}>
                    Sources utilisées:
                  </Typography>
                  {message.rag_sources.map((source, idx) => (
                    <Chip
                      key={idx}
                      label={`${source.filename} (${(
                        source.similarity * 100
                      ).toFixed(0)}%)`}
                      size="small"
                      variant="outlined"
                      sx={{ ml: 0.5, mt: 0.5 }}
                    />
                  ))}
                </Box>
              )}
            </Paper>

            {message.type === 'user' && (
              <Avatar sx={{ ml: 1, mt: 0.5 }}>
                <Person />
              </Avatar>
            )}
          </Box>
        ))}

        {/* Indicateur IA en streaming (réponse progressive) */}
        {aiThinking && (
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
            <Avatar sx={{ mr: 1 }}>
              <SmartToy />
            </Avatar>
            <Paper sx={{ p: 2, bgcolor: 'grey.100', width: '70%' }}>
              <Typography variant="body2" sx={{ fontStyle: 'italic' }}>
                L'IA réfléchit...
              </Typography>
              <LinearProgress sx={{ mt: 1 }} />
            </Paper>
          </Box>
        )}

        <div ref={messagesEndRef} />
      </Box>

      {/* Zone de saisie */}
      <Box sx={{ p: 2, borderTop: 1, borderColor: 'divider' }}>
        {!isConnected && (
          <>
            <Alert severity="warning" sx={{ mb: 2 }}>
              Connexion WebSocket fermée. Reconnexion automatique...
            </Alert>
            <Button
              variant="outlined"
              color="primary"
              onClick={connectWebSocket}
              sx={{ mb: 2 }}
            >
              Se reconnecter
            </Button>
          </>
        )}

        {/* ModernSpinner supprimé, on n'affiche plus de spinner lors de l'envoi */}

        <Box sx={{ display: 'flex', gap: 1 }}>
          <TextField
            fullWidth
            multiline
            maxRows={4}
            value={newMessage}
            onChange={(e: React.ChangeEvent<HTMLInputElement>) => {
              setNewMessage(e.target.value);
            }}
            placeholder="Tapez votre message..."
            disabled={!isConnected || isLoading}
            onKeyDown={(e: React.KeyboardEvent<HTMLInputElement>) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
              }
            }}
          />

          <Button
            variant="contained"
            onClick={sendMessage}
            disabled={!newMessage.trim() || !isConnected || isLoading}
            sx={{ minWidth: 'auto', px: 2 }}
          >
            <Send />
          </Button>
        </Box>
      </Box>
    </Box>
  );
};

export default ChatWebSocket;
