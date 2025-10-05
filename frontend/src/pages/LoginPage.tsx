import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Container,
  Box,
  Paper,
  Typography,
  TextField,
  Button,
  CircularProgress,
  Tabs,
  Tab,
} from '@mui/material';
import { Login } from '@mui/icons-material';
import { authService, ApiError } from '../services/api';

interface LoginPageProps {
  onLogin: (token: string, username: string) => void;
  onError: (message: string) => void;
  onSuccess: (message: string) => void;
}

const LoginPage: React.FC<LoginPageProps> = ({
  onLogin,
  onError,
  onSuccess,
}) => {
  const navigate = useNavigate();
  const [isRegistering, setIsRegistering] = useState(false);
  const [loading, setLoading] = useState(false);
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');

  const handleLogin = async () => {
    if (!username || !password) {
      onError("Nom d'utilisateur et mot de passe requis");
      return;
    }

    setLoading(true);
    try {
      const response = await authService.login({ username, password });
      onLogin(response.access_token, username);
      onSuccess('Connexion réussie !');
      navigate('/');
    } catch (error) {
      if (error instanceof ApiError) {
        onError(error.getFormattedMessage());
      } else {
        onError('Erreur de connexion');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleRegister = async () => {
    if (!username || !password) {
      onError("Nom d'utilisateur et mot de passe requis");
      return;
    }
    if (password.length < 6) {
      onError('Mot de passe trop court (min 6 caractères)');
      return;
    }

    setLoading(true);
    try {
      await authService.register({
        username,
        email: `${username}@example.com`,
        password,
      });
      onSuccess('Compte créé ! Vous pouvez vous connecter.');
      setIsRegistering(false);
      setPassword('');
    } catch (error) {
      if (error instanceof ApiError) {
        onError(error.getFormattedMessage());
      } else {
        onError("Erreur lors de l'inscription");
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container maxWidth="sm">
      <Box
        sx={{
          mt: 8,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
        }}
      >
        <Paper sx={{ p: 4, width: '100%' }}>
          <Typography variant="h4" component="h1" gutterBottom align="center">
            🤖 Chatbot Local
          </Typography>

          <Tabs
            value={isRegistering ? 1 : 0}
            onChange={(e, v) => setIsRegistering(v === 1)}
            centered
            sx={{ mt: 3 }}
          >
            <Tab label="Connexion" icon={<Login />} />
            <Tab label="Inscription" />
          </Tabs>

          <Box sx={{ mt: 3 }}>
            <TextField
              fullWidth
              label="Nom d'utilisateur"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              margin="normal"
              disabled={loading}
            />
            <TextField
              fullWidth
              label="Mot de passe"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              margin="normal"
              disabled={loading}
              helperText={isRegistering ? 'Minimum 6 caractères' : ''}
              onKeyDown={(e) =>
                e.key === 'Enter' &&
                (isRegistering ? handleRegister() : handleLogin())
              }
            />
            <Button
              fullWidth
              variant="contained"
              onClick={isRegistering ? handleRegister : handleLogin}
              sx={{ mt: 2 }}
              disabled={loading}
            >
              {loading ? (
                <CircularProgress size={24} />
              ) : isRegistering ? (
                'Créer un compte'
              ) : (
                'Se connecter'
              )}
            </Button>
          </Box>
        </Paper>
      </Box>
    </Container>
  );
};

export default LoginPage;
