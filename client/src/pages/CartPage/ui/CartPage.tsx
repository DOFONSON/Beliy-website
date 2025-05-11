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

export const CartPage = () => {
  const { isAuthenticated } = useAuth();
  const navigate = useNavigate();
  const { refreshCart } = useCart();
  const [cartItems, setCartItems] = useState<CartItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!isAuthenticated) {
      navigate('/login');
      return;
    }

    const fetchCart = async () => {
      try {
        const response = await api.get('/cart/');
        const items = (response.data.items || []).map((item: any) => ({
          id: item.id || 0,
          product: {
            id: item.product?.id || 0,
            title: item.product?.title || 'Без названия',
            price: item.product?.price || 0,
            image: item.product?.image || null
          },
          quantity: item.quantity || 0,
          total_price: item.total_price || (item.product?.price || 0) * (item.quantity || 0)
        }));
        setCartItems(items);
        setError(null);
      } catch (err) {
        setError('Не удалось загрузить корзину');
        console.error('Error fetching cart:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchCart();
  }, [isAuthenticated, navigate]);

  const handleQuantityChange = async (itemId: number, newQuantity: number) => {
    try {
      if (newQuantity < 1) {
        await handleRemoveItem(itemId);
        return;
      }

      await api.put(`/cart/items/${itemId}/`, {
        quantity: newQuantity
      });
      
      const response = await api.get('/cart/');
      const items = (response.data.items || []).map((item: any) => ({
        id: item.id || 0,
        product: {
          id: item.product?.id || 0,
          title: item.product?.title || 'Без названия',
          price: item.product?.price || 0,
          image: item.product?.image || null
        },
        quantity: item.quantity || 0,
        total_price: item.total_price || (item.product?.price || 0) * (item.quantity || 0)
      }));
      setCartItems(items);
      await refreshCart();
    } catch (err) {
      console.error('Error updating cart item:', err);
    }
  };

  const handleRemoveItem = async (itemId: number) => {
    try {
      await api.delete(`/cart/items/${itemId}/`);
      setCartItems(prevItems => prevItems.filter(item => item.id !== itemId));
      await refreshCart();
    } catch (err) {
      console.error('Error removing cart item:', err);
    }
  };

  if (loading) {
    return <div className={styles.loading}>Загрузка...</div>;
  }

  if (error) {
    return <div className={styles.error}>{error}</div>;
  }

  if (!cartItems || cartItems.length === 0) {
    return (
      <div className={styles.emptyCart}>
        <h2>Корзина пуста</h2>
        <p>Добавьте товары в корзину, чтобы оформить заказ</p>
      </div>
    );
  }

  const totalPrice = cartItems.reduce((sum, item) => {
    const itemPrice = item.total_price || (item.product?.price || 0) * (item.quantity || 0);
    return sum + itemPrice;
  }, 0);

  return (
    <div className={styles.cartPage}>
      <h1 className={styles.title}>Корзина</h1>
      <div className={styles.cartItems}>
        {cartItems.map((item) => {
          const itemPrice = item.total_price || (item.product?.price || 0) * (item.quantity || 0);
          return (
            <div key={item.id} className={styles.cartItem}>
              <div className={styles.itemImage}>
                {item.product?.image && (
                  <img
                    src={item.product.image}
                    alt={item.product?.title || 'Товар'}
                    className={styles.image}
                  />
                )}
              </div>
              <div className={styles.itemInfo}>
                <h3 className={styles.itemTitle}>{item.product?.title || 'Без названия'}</h3>
                <p className={styles.itemPrice}>
                  {(item.product?.price || 0).toLocaleString('ru-RU')} ₽
                </p>
              </div>
              <div className={styles.itemQuantity}>
                <button
                  onClick={() => handleQuantityChange(item.id, item.quantity - 1)}
                  className={styles.quantityButton}
                >
                  -
                </button>
                <span>{item.quantity || 0}</span>
                <button
                  onClick={() => handleQuantityChange(item.id, item.quantity + 1)}
                  className={styles.quantityButton}
                >
                  +
                </button>
              </div>
              <div className={styles.itemTotal}>
                {itemPrice.toLocaleString('ru-RU')} ₽
              </div>
              <button
                onClick={() => handleRemoveItem(item.id)}
                className={styles.removeButton}
              >
                Удалить
              </button>
            </div>
          );
        })}
      </div>
      <div className={styles.cartSummary}>
        <div className={styles.total}>
          <span>Итого:</span>
          <span className={styles.totalPrice}>
            {totalPrice.toLocaleString('ru-RU')} ₽
          </span>
        </div>
        <button className={styles.checkoutButton}>
          Оформить заказ
        </button>
      </div>
    </div>
  );
}; 