import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { api } from '@/shared/api';
import styles from './ArticleList.module.css';

interface Article {
  id: number;
  slug: string;
  title: string;
  content: string;
  image: string;
  created_at: string;
}

export const ArticleList: React.FC = () => {
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
    <div className={styles.articleList}>
      <h1 className={styles.title}>Статьи</h1>
      <div className={styles.grid}>
        {articles.map((article) => (
          <Link
            key={article.id}
            to={`/article/${article.slug}`}
            className={styles.articleCard}
          >
            {article.image && (
              <img
                src={article.image}
                alt={article.title}
                className={styles.articleImage}
              />
            )}
            <div className={styles.articleContent}>
              <h2 className={styles.articleTitle}>{article.title}</h2>
              <time className={styles.articleDate} dateTime={article.created_at}>
                {new Date(article.created_at).toLocaleDateString('ru-RU')}
              </time>
              <p className={styles.articleExcerpt}>
                {article.content.slice(0, 150)}...
              </p>
            </div>
          </Link>
        ))}
      </div>
    </div>
  );
}; 