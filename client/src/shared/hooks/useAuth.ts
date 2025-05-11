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
  first_name: string;
  last_name: string;
  full_name: string;
  avatar_url: string | null;
  bio: string | null;
  date_joined: string;
}

interface LoginData {
  username: string;
  password: string;
}

interface RegisterData extends LoginData {
  email: string;
  first_name?: string;
  last_name?: string;
}

interface ApiError {
  error: string;
  message?: string;
}

export const useAuth = () => {
  const [authState, setAuthState] = useState<AuthState>(() => {
    const token = localStorage.getItem('access');
    const user = JSON.parse(localStorage.getItem('user') || 'null');
    if (token) {
      api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
    }
    return {
      isAuthenticated: !!token,
      user,
      token,
    };
  });

  const checkAuth = useCallback(async () => {
    const token = localStorage.getItem('access');
    if (!token) {
      setAuthState({
        isAuthenticated: false,
        user: null,
        token: null,
      });
      return;
    }

    try {
      api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
      const response = await api.get('/auth/check/');
      const { user } = response.data;
      
      setAuthState({
        isAuthenticated: true,
        user,
        token,
      });
    } catch (error) {
      localStorage.removeItem('access');
      localStorage.removeItem('refresh');
      localStorage.removeItem('user');
      delete api.defaults.headers.common['Authorization'];
      setAuthState({
        isAuthenticated: false,
        user: null,
        token: null,
      });
    }
  }, []);

  useEffect(() => {
    checkAuth();
  }, [checkAuth]);

  const login = useCallback(async (data: LoginData) => {
    try {
      const response = await api.post('/auth/login/', data);
      const { access, refresh, user } = response.data;
      
      if (!access || !user) {
        throw new Error('Invalid response from server');
      }
      
      localStorage.setItem('access', access);
      localStorage.setItem('refresh', refresh);
      localStorage.setItem('user', JSON.stringify(user));
      
      api.defaults.headers.common['Authorization'] = `Bearer ${access}`;
      
      setAuthState({
        isAuthenticated: true,
        user,
        token: access,
      });

      return { success: true };
    } catch (error) {
      const axiosError = error as AxiosError<ApiError>;
      console.error('Login error:', axiosError.response?.data);
      return {
        success: false,
        error: axiosError.response?.data?.error || 'Ошибка при входе',
      };
    }
  }, []);

  const register = useCallback(async (data: RegisterData) => {
    try {
      const response = await api.post('/auth/register/', data);
      const { access, refresh, user } = response.data;
      
      if (!access || !user) {
        throw new Error('Invalid response from server');
      }
      
      localStorage.setItem('access', access);
      localStorage.setItem('refresh', refresh);
      localStorage.setItem('user', JSON.stringify(user));
      
      api.defaults.headers.common['Authorization'] = `Bearer ${access}`;
      
      setAuthState({
        isAuthenticated: true,
        user,
        token: access,
      });

      return { success: true };
    } catch (error) {
      const axiosError = error as AxiosError<ApiError>;
      console.error('Registration error:', axiosError.response?.data);
      return {
        success: false,
        error: axiosError.response?.data?.error || 'Ошибка при регистрации',
      };
    }
  }, []);

  const logout = useCallback(() => {
    localStorage.removeItem('access');
    localStorage.removeItem('refresh');
    localStorage.removeItem('user');
    delete api.defaults.headers.common['Authorization'];
    
    setAuthState({
      isAuthenticated: false,
      user: null,
      token: null,
    });
  }, []);

  return {
    ...authState,
    login,
    register,
    logout,
  };
}; 