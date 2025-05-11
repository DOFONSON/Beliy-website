import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { api } from '@/shared/api';
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

export const ArticlesPage = () => {
  const [articles, setArticles] = useState<Article[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchArticles = async () => {
      try {
        const response = await api.get('/articles/');
        setArticles(response.data);
        setError(null);
      } catch (err) {
        setError('Не удалось загрузить статьи');
        console.error('Error fetching articles:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchArticles();
  }, []);

  if (loading) {
    return <div className={styles.loading}>Загрузка...</div>;
  }

  if (error) {
    return <div className={styles.error}>{error}</div>;
  }

  return (
    <div className={styles.articlesPage}>
      <h1 className={styles.title}>Статьи</h1>
      <div className={styles.articlesGrid}>
        {articles.map((article) => (
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
    </div>
  );
}; 