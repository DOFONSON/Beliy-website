import { useState, useCallback, useEffect } from 'react';
import { api } from '@/shared/api';
import { AxiosError } from 'axios';

interface AuthState {
  isAuthenticated: boolean;
  user: User | null;
  token: string | null;
}

interface User {
  id: number;
  username: string;
  email: string;
}

interface LoginData {
  username: string;
  password: string;
}

interface RegisterData extends LoginData {
  email: string;
}

interface ApiError {
  message: string;
}

export const useAuth = () => {
  const [authState, setAuthState] = useState<AuthState>(() => {
    const token = localStorage.getItem('token');
    return {
      isAuthenticated: !!token,
      user: JSON.parse(localStorage.getItem('user') || 'null'),
      token,
    };
  });

  const login = useCallback(async (data: LoginData) => {
    try {
      const response = await api.post('/auth/login/', data);
      const { token, user } = response.data;
      
      localStorage.setItem('token', token);
      localStorage.setItem('user', JSON.stringify(user));
      
      setAuthState({
        isAuthenticated: true,
        user,
        token,
      });

      return { success: true };
    } catch (error) {
      const axiosError = error as AxiosError<ApiError>;
      return {
        success: false,
        error: axiosError.response?.data?.message || 'Ошибка при входе',
      };
    }
  }, []);

  const register = useCallback(async (data: RegisterData) => {
    try {
      const response = await api.post('/auth/register/', data);
      const { token, user } = response.data;
      
      localStorage.setItem('token', token);
      localStorage.setItem('user', JSON.stringify(user));
      
      setAuthState({
        isAuthenticated: true,
        user,
        token,
      });

      return { success: true };
    } catch (error) {
      const axiosError = error as AxiosError<ApiError>;
      return {
        success: false,
        error: axiosError.response?.data?.message || 'Ошибка при регистрации',
      };
    }
  }, []);

  const logout = useCallback(() => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    
    setAuthState({
      isAuthenticated: false,
      user: null,
      token: null,
    });
  }, []);

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (token) {
      api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
    }
  }, [authState.token]);

  return {
    ...authState,
    login,
    register,
    logout,
  };
}; 