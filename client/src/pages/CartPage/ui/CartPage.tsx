import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { api } from '@/shared/api';
import { useAuth } from '@/shared/hooks/useAuth';
import { useCart } from '@/features/CartIcon/model/CartContext';
import styles from './CartPage.module.css';

interface CartItem {
  id: number;
  product: {
    id: number;
    title: string;
    price: number;
    image: string | null;
  };
  quantity: number;
  total_price: number | null;
}

interface Cart {
  id: number;
  items: CartItem[];
  total_price: number;
}

export const CartPage = () => {
  const { token } = useAuth();
  const navigate = useNavigate();
  const { refreshCart } = useCart();
  const [cart, setCart] = useState<Cart | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchCart = async () => {
    try {
      const response = await api.get('/cart/', {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      // Получаем полные данные о продуктах для каждого элемента корзины
      const cartData = response.data;
      const itemsWithProducts = await Promise.all(
        cartData.items.map(async (item: any) => {
          try {
            const productResponse = await api.get(`/products/${item.product}/`);
            return {
              ...item,
              product: productResponse.data
            };
          } catch (err) {
            console.error(`Error fetching product ${item.product}:`, err);
            return item;
          }
        })
      );

      const updatedCart = {
        ...cartData,
        items: itemsWithProducts
      };

      console.log('Updated cart data:', updatedCart);
      setCart(updatedCart);
      setError(null);
    } catch (err) {
      setError('Ошибка при загрузке корзины');
      console.error('Error fetching cart:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleQuantityChange = async (itemId: number, newQuantity: number) => {
    if (newQuantity < 1) return;

    try {
      await api.patch(`/cart/items/${itemId}/`, 
        { quantity: newQuantity },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      fetchCart();
    } catch (err) {
      setError('Ошибка при обновлении количества');
      console.error('Error updating quantity:', err);
    }
  };

  const handleRemoveItem = async (itemId: number) => {
    try {
      await api.delete(`/cart/items/${itemId}/`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      fetchCart();
    } catch (err) {
      setError('Ошибка при удалении товара');
      console.error('Error removing item:', err);
    }
  };

  useEffect(() => {
    if (token) {
      fetchCart();
    }
  }, [token]);

  if (loading) {
    return <div className={styles.loading}>Загрузка корзины...</div>;
  }

  if (error) {
    return <div className={styles.error}>{error}</div>;
  }

  if (!cart || !cart.items || cart.items.length === 0) {
    return <div className={styles.empty}>Корзина пуста</div>;
  }

  console.log('Cart items:', cart.items);

  const totalPrice = cart.items.reduce((sum, item) => {
    if (!item.product) return sum;
    const itemPrice = item.total_price ?? (item.product.price * item.quantity);
    return sum + (itemPrice || 0);
  }, 0);

  return (
    <div className={styles.cartPage}>
      <h1>Корзина</h1>
      <div className={styles.cartItems}>
        {cart.items.map((item) => {
          console.log('Processing item:', item);
          
          if (!item.product) {
            console.log('Skipping item without product:', item);
            return null;
          }

          const itemTotalPrice = item.total_price ?? (item.product.price * item.quantity);

          return (
            <div key={item.id} className={styles.cartItem}>
              <div className={styles.productInfo}>
                {item.product.image && (
                  <img 
                    src={item.product.image} 
                    alt={item.product.title || 'Товар'}
                    className={styles.productImage}
                  />
                )}
                <div className={styles.productDetails}>
                  <h3>{item.product.title || 'Без названия'}</h3>
                  <p className={styles.price}>
                    {item.product.price?.toLocaleString('ru-RU') || '0'} ₽
                  </p>
                </div>
              </div>
              <div className={styles.quantityControls}>
                <button 
                  onClick={() => handleQuantityChange(item.id, item.quantity - 1)}
                  disabled={item.quantity <= 1}
                >
                  -
                </button>
                <span>{item.quantity}</span>
                <button 
                  onClick={() => handleQuantityChange(item.id, item.quantity + 1)}
                >
                  +
                </button>
              </div>
              <div className={styles.itemTotal}>
                {itemTotalPrice?.toLocaleString('ru-RU') || '0'} ₽
              </div>
              <button 
                className={styles.removeButton}
                onClick={() => handleRemoveItem(item.id)}
              >
                Удалить
              </button>
            </div>
          );
        })}
      </div>
      <div className={styles.cartTotal}>
        <h2>Итого: {totalPrice?.toLocaleString('ru-RU') || '0'} ₽</h2>
        <button className={styles.checkoutButton}>
          Оформить заказ
        </button>
      </div>
    </div>
  );
}; 