import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { getCart } from '../../api';
import styles from './styles.module.css';

export const CartIcon: React.FC = () => {
  const [itemCount, setItemCount] = useState(0);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchCartCount = async () => {
      try {
        const cart = await getCart();
        setItemCount(cart.items.length);
      } catch (err) {
        console.error('Failed to fetch cart:', err);
      }
    };

    fetchCartCount();
  }, []);

  if (itemCount === 0) return null;

  return (
    <div className={styles.cartIcon} onClick={() => navigate('/cart')}>
      <svg 
        xmlns="http://www.w3.org/2000/svg" 
        width="24" 
        height="24" 
        viewBox="0 0 24 24" 
        fill="none" 
        stroke="currentColor" 
        strokeWidth="2" 
        strokeLinecap="round" 
        strokeLinejoin="round"
      >
        <circle cx="9" cy="21" r="1"></circle>
        <circle cx="20" cy="21" r="1"></circle>
        <path d="M1 1h4l2.68 13.39a2 2 0 0 0 2 1.61h9.72a2 2 0 0 0 2-1.61L23 6H6"></path>
      </svg>
      {itemCount > 0 && (
        <span className={styles.badge}>{itemCount}</span>
      )}
    </div>
  );
}; 