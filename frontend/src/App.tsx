// export default App;
import React, { useState } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { Snackbar, Alert } from '@mui/material';
import LoginPage from './pages/LoginPage';
import HomePage from './pages/HomePage';
import { useAuth } from './hook/useAuth';
import ProtectedRoute from './components/auth/ProtectedRoute';

function App() {
  const { token, username, isLoading, isAuthenticated, login, logout } =
    useAuth();
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const handleLogin = (newToken: string, newUsername: string) => {
    login(newToken, newUsername);
  };

  const handleLogout = () => {
    logout();
    setSuccess('Déconnexion réussie');
  };

  if (isLoading) {
    return null;
  }

  return (
    <BrowserRouter>
      <Routes>
        {/* Redirection automatique si déjà connecté */}
        <Route
          path="/login"
          element={
            isAuthenticated ? (
              <Navigate to="/" replace />
            ) : (
              <LoginPage
                onLogin={handleLogin}
                onError={setError}
                onSuccess={setSuccess}
              />
            )
          }
        />

        <Route
          path="/"
          element={
            <ProtectedRoute token={token} isLoading={isLoading}>
              <HomePage
                token={token!}
                username={username}
                onLogout={handleLogout}
                onError={setError}
                onSuccess={setSuccess}
              />
            </ProtectedRoute>
          }
        />

        {/* Redirection par défaut */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>

      {/* Messages globaux */}
      <Snackbar
        open={!!error}
        autoHideDuration={6000}
        onClose={() => setError('')}
      >
        <Alert severity="error" onClose={() => setError('')}>
          {error}
        </Alert>
      </Snackbar>
      <Snackbar
        open={!!success}
        autoHideDuration={4000}
        onClose={() => setSuccess('')}
      >
        <Alert severity="success" onClose={() => setSuccess('')}>
          {success}
        </Alert>
      </Snackbar>
    </BrowserRouter>
  );
}

export default App;
