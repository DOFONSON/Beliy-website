import { useState, useEffect } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { api } from '@/shared/api';
import { Slider } from '@/shared/ui/Slider/ui/Slider';
import { SwipeSlider } from '@/shared/ui/SwipeSlider/ui/SwipeSlider';
import { ActiveUsersList } from '@/shared/ui/ActiveUsersList/ui/ActiveUsersList';
import styles from './ArticlesPage.module.css';

interface Article {
  id: number;
  title: string;
  slug: string;
  content: string;
  image: string;
  average_rating: number;
  created_at: string;
}

interface Product {
  id: number;
  title: string;
  image: string;
  price: number;
  average_rating: number;
}

interface User {
  id: number;
  username: string;
  avatar_url: string;
  comments_count: number;
}

export const ArticlesPage = () => {
  const [articles, setArticles] = useState<Article[]>([]);
  const [products, setProducts] = useState<Product[]>([]);
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchParams] = useSearchParams();
  const searchQuery = searchParams.get('q') || '';

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [articlesResponse, productsResponse, usersResponse] = await Promise.all([
          api.get('/articles/'),
          api.get('/products/'),
          api.get('/users/active/')
        ]);
        setArticles(articlesResponse.data);
        setProducts(productsResponse.data);
        setUsers(usersResponse.data);
        setError(null);
      } catch (err) {
        setError('Не удалось загрузить данные');
        console.error('Error fetching data:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  const filteredArticles = articles.filter(article =>
    article.title.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const topRatedArticles = [...articles]
    .sort((a, b) => b.average_rating - a.average_rating)
    .slice(0, 8);

  const topRatedProducts = [...products]
    .sort((a, b) => b.average_rating - a.average_rating)
    .slice(0, 8);

  const activeUsers = [...users]
    .sort((a, b) => b.comments_count - a.comments_count)
    .slice(0, 9);

  if (loading) {
    return <div className={styles.loading}>Загрузка...</div>;
  }

  if (error) {
    return <div className={styles.error}>{error}</div>;
  }

  return (
    <div className={styles.articlesPage}>
      <SwipeSlider
        title="Популярные статьи"
        items={topRatedArticles}
        type="article"
      />
      
      <Slider
        title="Популярные товары"
        items={topRatedProducts}
        type="product"
      />

      <ActiveUsersList users={activeUsers} />

      <h1 className={styles.title}>Все статьи</h1>
      {searchQuery && (
        <div className={styles.searchResults}>
          Результаты поиска по запросу: "{searchQuery}"
        </div>
      )}
      <div className={styles.articlesGrid}>
        {filteredArticles.map((article) => (
          <article key={article.id} className={styles.articleCard}>
            {article.image && (
              <img
                src={article.image}
                alt={article.title}
                className={styles.articleImage}
              />
            )}
            <div className={styles.articleContent}>
              <h2 className={styles.articleTitle}>
                <Link to={`/articles/${article.slug}`}>{article.title}</Link>
              </h2>
              <p className={styles.articleExcerpt}>
                {article.content.substring(0, 150)}...
              </p>
              <div className={styles.articleMeta}>
                <time dateTime={article.created_at}>
                  {new Date(article.created_at).toLocaleDateString('ru-RU')}
                </time>
                {article.average_rating > 0 && (
                  <span className={styles.rating}>
                    ★ {article.average_rating.toFixed(1)}
                  </span>
                )}
              </div>
            </div>
          </article>
        ))}
      </div>
      {searchQuery && filteredArticles.length === 0 && (
        <div className={styles.noResults}>
          По вашему запросу ничего не найдено
        </div>
      )}
    </div>
  );
}; 