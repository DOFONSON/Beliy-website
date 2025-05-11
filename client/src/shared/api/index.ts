import axios from 'axios';

export const api = axios.create({
  baseURL: 'http://localhost:8000/works/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Интерцептор для добавления токена к запросам
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Интерцептор для обработки ошибок
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      
      try {
        const refreshToken = localStorage.getItem('refresh');
        if (refreshToken) {
          const response = await axios.post('http://localhost:8000/works/api/auth/refresh/', {
            refresh: refreshToken
          });
          
          const { access } = response.data;
          localStorage.setItem('access', access);
          
          originalRequest.headers.Authorization = `Bearer ${access}`;
          return axios(originalRequest);
        }
      } catch (refreshError) {
        console.error('Token refresh failed:', refreshError);
        localStorage.removeItem('access');
        localStorage.removeItem('refresh');
        localStorage.removeItem('user');
        window.location.href = '/login';
      }
    }
    
    return Promise.reject(error);
  }
);

export const deleteComment = async (commentId: number) => {
  const response = await api.delete(`/comments/${commentId}/delete/`);
  return response.data;
};

export const getCart = async () => {
  const response = await api.get('/cart/');
  return response.data;
};

export const addToCart = async (productId: number, quantity: number = 1) => {
  const response = await api.post('/cart/add/', {
    product_id: productId,
    quantity
  });
  return response.data;
};

export const updateCartItem = async (itemId: number, quantity: number) => {
  const response = await api.put(`/cart/items/${itemId}/`, {
    quantity
  });
  return response.data;
};

export const removeFromCart = async (itemId: number) => {
  const response = await api.delete(`/cart/items/${itemId}/`);
  return response.data;
}; 