import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Tabs,
  Tab,
  Alert,
  AppBar,
  Toolbar,
  Typography,
  Button,
} from '@mui/material';
import { Chat, Storage, Logout } from '@mui/icons-material';
import ChatWebSocket from '../components/ChatWebSocket';
import DocumentManager from '../components/DocumentManager';
import getUrlBase from '../utils/getUrlBase';
import { ENDPOINT_SESSION } from '../constants/endpoint/endpointSession';
import { ENDPOINT_API_V1 } from '../constants/endpoint/endpointApi';

interface HomePageProps {
  token: string;
  username: string;
  onLogout: () => void;
  onError: (message: string) => void;
  onSuccess: (message: string) => void;
}

const HomePage: React.FC<HomePageProps> = ({
  token,
  username,
  onLogout,
  onError,
  onSuccess,
}) => {
  const [tabValue, setTabValue] = useState(0);
  const [sessionId, setSessionId] = useState('');

  useEffect(() => {
    const savedSession = localStorage.getItem('sessionId');
    if (savedSession) {
      setSessionId(savedSession);
    } else {
      createSession();
    }
  }, []);

  const createSession = async () => {
    const sessionUrl = `${getUrlBase()}${ENDPOINT_API_V1}${ENDPOINT_SESSION}`;
    try {
      const response = await fetch(sessionUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          title: `Chat avec ${username} - ${new Date().toLocaleString()}`,
        }),
      });

      if (response.ok) {
        const data = await response.json();
        setSessionId(data.session_id);
        localStorage.setItem('sessionId', data.session_id);
      }
    } catch (error) {
      console.error('Erreur création session:', error);
    }
  };

  return (
    <Box sx={{ flexGrow: 1 }}>
      <AppBar position="static">
        <Toolbar>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            🤖 Chatbot Local - Bienvenue {username}
          </Typography>
          <Button color="inherit" onClick={onLogout} startIcon={<Logout />}>
            Déconnexion
          </Button>
        </Toolbar>
      </AppBar>

      <Container maxWidth="xl">
        <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
          <Tabs value={tabValue} onChange={(e, v) => setTabValue(v)}>
            <Tab label="Chat" icon={<Chat />} />
            <Tab label="Documents" icon={<Storage />} />
          </Tabs>
        </Box>

        {tabValue === 0 && (
          <Box sx={{ p: 3 }}>
            {sessionId ? (
              <ChatWebSocket
                sessionId={sessionId}
                token={token}
                username={username}
                onError={onError}
                onSuccess={onSuccess}
                onSessionCreated={setSessionId}
              />
            ) : (
              <Alert severity="info">Création de la session en cours...</Alert>
            )}
          </Box>
        )}

        {tabValue === 1 && (
          <Box sx={{ p: 3 }}>
            <DocumentManager
              token={token}
              onError={onError}
              onSuccess={onSuccess}
            />
          </Box>
        )}
      </Container>
    </Box>
  );
};

export default HomePage;
