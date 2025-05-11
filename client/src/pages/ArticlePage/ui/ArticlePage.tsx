import { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { useAuth } from '@/shared/hooks/useAuth';
import { api } from '@/shared/api';
import { Rating } from '@/features/Rating';
import { CommentForm } from '@/features/CommentForm';
import { CommentList } from '@/features/CommentList';
import styles from './ArticlePage.module.css';

interface Article {
  id: number;
  title: string;
  content: string;
  image: string;
  average_rating: number;
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

export const ArticlePage = () => {
  const { slug } = useParams<{ slug: string }>();
  const { isAuthenticated } = useAuth();
  const [article, setArticle] = useState<Article | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchArticle = async () => {
      try {
        const response = await api.get(`/articles/${slug}/`);
        setArticle(response.data);
        setError(null);
      } catch (err) {
        setError('Не удалось загрузить статью');
        console.error('Error fetching article:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchArticle();
  }, [slug]);

  const handleRatingSubmit = async (value: number) => {
    try {
      const response = await api.post(`/articles/${article?.id}/rate/`, {
        rating: value,
        token: localStorage.getItem('token')
      });
      setArticle(prev => prev ? { ...prev, average_rating: response.data.average_rating } : null);
    } catch (err) {
      console.error('Error submitting rating:', err);
    }
  };

  const handleCommentSubmit = async (text: string) => {
    try {
      const response = await api.post(`/articles/${article?.id}/comments/`, {
        text,
      });
      setArticle(prev => prev ? {
        ...prev,
        comments: [response.data, ...prev.comments],
      } : null);
    } catch (err) {
      console.error('Error submitting comment:', err);
    }
  };

  if (loading) {
    return <div className={styles.loading}>Загрузка...</div>;
  }

  if (error || !article) {
    return <div className={styles.error}>{error || 'Статья не найдена'}</div>;
  }

  return (
    <div className={styles.articlePage}>
      <article className={styles.article}>
        {article.image && (
          <img
            src={article.image}
            alt={article.title}
            className={styles.articleImage}
          />
        )}
        
        <h1 className={styles.articleTitle}>{article.title}</h1>
        
        <div className={styles.articleMeta}>
          <time dateTime={article.created_at}>
            {new Date(article.created_at).toLocaleDateString('ru-RU')}
          </time>
          {isAuthenticated && (
            <Rating
              value={article.average_rating}
              onRate={handleRatingSubmit}
            />
          )}
        </div>

        <div className={styles.articleContent}>
          {article.content}
        </div>

        <div className={styles.commentsSection}>
          <h2>Комментарии</h2>
          
          {isAuthenticated && (
            <CommentForm onSubmit={handleCommentSubmit} />
          )}

          <CommentList comments={article.comments} />
        </div>
      </article>
    </div>
  );
}; 