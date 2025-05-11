import React, { createContext, useContext, useState, useEffect } from 'react';
import { api } from '@/shared/api';

interface CartContextType {
  itemCount: number;
  refreshCart: () => Promise<void>;
}

const CartContext = createContext<CartContextType>({
  itemCount: 0,
  refreshCart: async () => {},
});

export const useCart = () => useContext(CartContext);

export const CartProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [itemCount, setItemCount] = useState(0);

  const refreshCart = async () => {
    try {
      const response = await api.get('/cart/');
      const items = response.data.items || [];
      const totalItems = items.reduce((sum: number, item: any) => sum + item.quantity, 0);
      setItemCount(totalItems);
    } catch (err) {
      console.error('Error fetching cart:', err);
    }
  };

  useEffect(() => {
    refreshCart();
  }, []);

  return (
    <CartContext.Provider value={{ itemCount, refreshCart }}>
      {children}
    </CartContext.Provider>
  );
}; 