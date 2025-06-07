import { useState, useCallback } from 'react';
import { login as loginApi } from '../services/api';

export const useAuth = () => {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [isLoggingIn, setIsLoggingIn] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  const login = useCallback(async () => {
    try {
      setIsLoggingIn(true);
      setError(null);
      
      await loginApi();
      
      setIsLoggedIn(true);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred during login');
    } finally {
      setIsLoggingIn(false);
    }
  }, []);
  
  return {
    isLoggedIn,
    isLoggingIn,
    error,
    login,
  };
};