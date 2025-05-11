import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { api } from '@/shared/api';
import styles from './ProductsPage.module.css';

interface Product {
  id: number;
  title: string;
  price: number;
  image: string;
  description: string;
  average_rating: number;
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
        setProducts(response.data);
        setError(null);
      } catch (err) {
        setError('Не удалось загрузить товары');
        console.error('Error fetching products:', err);
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
              {product.image && (
                <img
                  src={product.image}
                  alt={product.title}
                  className={styles.image}
                />
              )}
            </div>
            <div className={styles.productContent}>
              <h2 className={styles.productTitle}>{product.title}</h2>
              <p className={styles.productPrice}>
                {product.price.toLocaleString('ru-RU')} ₽
              </p>
              <p className={styles.productExcerpt}>
                {product.description.substring(0, 100)}...
              </p>
              <div className={styles.productMeta}>
                <time dateTime={product.created_at}>
                  {new Date(product.created_at).toLocaleDateString('ru-RU')}
                </time>
                {product.average_rating > 0 && (
                  <span className={styles.rating}>
                    ★ {product.average_rating.toFixed(1)}
                  </span>
                )}
              </div>
            </div>
          </Link>
        ))}
      </div>
    </div>
  );
}; 