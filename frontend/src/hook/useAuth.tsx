import { useState, useEffect } from 'react';
import { ENDPOINT_ME } from '../constants/endpoint/endpointUser';
import { authService } from '../services/api';

interface AuthState {
  token: string | null;
  username: string;
  isLoading: boolean;
  isAuthenticated: boolean;
}

export const useAuth = () => {
  const [authState, setAuthState] = useState<AuthState>({
    token: null,
    username: '',
    isLoading: true,
    isAuthenticated: false,
  });

  useEffect(() => {
    const checkAuth = async () => {
      const savedToken = localStorage.getItem('token');
      const savedUsername = localStorage.getItem('username');

      if (savedToken && savedUsername) {
        try {
          const response = await authService.me(savedToken);

          setAuthState({
            token: savedToken,
            username: savedUsername,
            isLoading: false,
            isAuthenticated: true,
          });
        } catch (error) {
          localStorage.removeItem('token');
          localStorage.removeItem('username');
          setAuthState({
            token: null,
            username: '',
            isLoading: false,
            isAuthenticated: false,
          });
        }
      } else {
        setAuthState({
          token: null,
          username: '',
          isLoading: false,
          isAuthenticated: false,
        });
      }
    };

    checkAuth();
  }, []);

  const login = (token: string, username: string) => {
    localStorage.setItem('token', token);
    localStorage.setItem('username', username);
    setAuthState({
      token,
      username,
      isLoading: false,
      isAuthenticated: true,
    });
  };

  const logout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('username');
    localStorage.removeItem('sessionId');
    setAuthState({
      token: null,
      username: '',
      isLoading: false,
      isAuthenticated: false,
    });
  };

  return {
    ...authState,
    login,
    logout,
  };
};
