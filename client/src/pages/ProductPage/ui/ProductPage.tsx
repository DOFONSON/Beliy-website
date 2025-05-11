import { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { useAuth } from '@/shared/hooks/useAuth';
import { api } from '@/shared/api';
import { Rating } from '@/features/Rating';
import { CommentForm } from '@/features/CommentForm';
import { CommentList } from '@/features/CommentList';
import { Button } from '@/shared/ui/Button';
import { useCart } from '@/features/CartIcon/model/CartContext';
import styles from './ProductPage.module.css';

interface Product {
  id: number;
  title: string;
  price: number;
  image: string;
  description: string;
  average_rating: number | null;
  created_at: string;
  comments: Comment[];
}

interface Comment {
  id: number;
  text: string;
  user: {
    username: string;
  };
  created_at: string;
}

export const ProductPage = () => {
  const { id } = useParams<{ id: string }>();
  const { isAuthenticated } = useAuth();
  const { refreshCart } = useCart();
  const [product, setProduct] = useState<Product | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [quantity, setQuantity] = useState(1);

  useEffect(() => {
    const fetchProduct = async () => {
      try {
        const response = await api.get(`/products/${id}/`);
        setProduct(response.data);
        setError(null);
      } catch (err) {
        setError('Не удалось загрузить товар');
        console.error('Error fetching product:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchProduct();
  }, [id]);

  const handleRatingSubmit = async (value: number) => {
    try {
      const response = await api.post(`/products/${product?.id}/rate/`, {
        rating: value
      });
      setProduct(prev => prev ? { ...prev, average_rating: response.data.average_rating } : null);
    } catch (err) {
      console.error('Error submitting rating:', err);
    }
  };

  const handleCommentSubmit = async (text: string) => {
    try {
      const response = await api.post(`/products/${product?.id}/comments/`, {
        text,
      });
      setProduct(prev => prev ? {
        ...prev,
        comments: [response.data, ...prev.comments],
      } : null);
    } catch (err) {
      console.error('Error submitting comment:', err);
    }
  };

  const handleAddToCart = async () => {
    try {
      await api.post('/cart/add/', {
        product_id: product?.id,
        quantity
      });
      // Обновляем состояние корзины
      await refreshCart();
    } catch (err) {
      console.error('Error adding to cart:', err);
    }
  };

  if (loading) {
    return <div className={styles.loading}>Загрузка...</div>;
  }

  if (error || !product) {
    return <div className={styles.error}>{error || 'Товар не найден'}</div>;
  }

  return (
    <div className={styles.productPage}>
      <article className={styles.product}>
        <div className={styles.productImage}>
          {product.image && (
            <img
              src={product.image}
              alt={product.title}
              className={styles.image}
            />
          )}
        </div>
        
        <div className={styles.productInfo}>
          <h1 className={styles.title}>{product.title}</h1>
          
          <div className={styles.meta}>
            <time dateTime={product.created_at}>
              {new Date(product.created_at).toLocaleDateString('ru-RU')}
            </time>
            {isAuthenticated && (
              <Rating
                value={product.average_rating || 0}
                onRate={handleRatingSubmit}
              />
            )}
          </div>

          <div className={styles.price}>
            {product.price.toLocaleString('ru-RU')} ₽
          </div>

          <div className={styles.description}>
            {product.description}
          </div>

          {isAuthenticated && (
            <div className={styles.addToCart}>
              <div className={styles.quantity}>
                <button 
                  onClick={() => setQuantity(prev => Math.max(1, prev - 1))}
                  className={styles.quantityButton}
                >
                  -
                </button>
                <span>{quantity}</span>
                <button 
                  onClick={() => setQuantity(prev => prev + 1)}
                  className={styles.quantityButton}
                >
                  +
                </button>
              </div>
              <Button onClick={handleAddToCart}>
                Добавить в корзину
              </Button>
            </div>
          )}

          <div className={styles.commentsSection}>
            <h2>Комментарии</h2>
            
            {isAuthenticated && (
              <CommentForm onSubmit={handleCommentSubmit} />
            )}

            <CommentList comments={product.comments} />
          </div>
        </div>
      </article>
    </div>
  );
}; 