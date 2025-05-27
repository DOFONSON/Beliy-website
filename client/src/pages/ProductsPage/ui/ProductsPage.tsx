import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { api } from '@/shared/api';
import styles from './ProductsPage.module.css';

interface Product {
  id: number;
  title: string;
  price: number;
  image: string;
  image_url: string;
  description: string;
  average_rating: number;
  category_name: string;
  quantity: number;
  is_available: boolean;
  status: string;
  created_at: string;
}

export const ProductsPage = () => {
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchProducts = async () => {
      try {
        const response = await api.get('/products/');
        console.log('Products response:', response.data); // Для отладки
        setProducts(response.data);
        setError(null);
      } catch (err) {
        console.error('Error fetching products:', err);
        setError('Не удалось загрузить товары. Пожалуйста, попробуйте позже.');
      } finally {
        setLoading(false);
      }
    };

    fetchProducts();
  }, []);

  if (loading) {
    return <div className={styles.loading}>Загрузка...</div>;
  }

  if (error) {
    return <div className={styles.error}>{error}</div>;
  }

  if (products.length === 0) {
    return <div className={styles.noProducts}>Товары не найдены</div>;
  }

  return (
    <div className={styles.productsPage}>
      <h1 className={styles.title}>Товары</h1>
      <div className={styles.productsGrid}>
        {products.map((product) => (
          <Link 
            to={`/products/${product.id}`} 
            key={product.id}
            className={styles.productCard}
          >
            <div className={styles.productImage}>
              {(product.image || product.image_url) && (
                <img
                  src={product.image_url || product.image}
                  alt={product.title}
                  className={styles.image}
                />
              )}
            </div>
            <div className={styles.productContent}>
              <h2 className={styles.productTitle}>{product.title}</h2>
              <p className={styles.productPrice}>
                {product.price?.toLocaleString('ru-RU') || '0'} ₽
              </p>
              <p className={styles.productExcerpt}>
                {product.description?.substring(0, 100)}...
              </p>
              <div className={styles.productMeta}>
                <span className={styles.category}>{product.category_name}</span>
                {product.average_rating > 0 && (
                  <span className={styles.rating}>
                    ★ {product.average_rating.toFixed(1)}
                  </span>
                )}
              </div>
              {!product.is_available && (
                <div className={styles.unavailable}>Нет в наличии</div>
              )}
            </div>
          </Link>
        ))}
      </div>
    </div>
  );
}; 