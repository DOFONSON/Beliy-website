import React, { useEffect, useState } from 'react';
import axios from 'axios';
import './ArticleList.css';

interface Article {
  id: number;
  title: string;
  slug: string;
  image: string;
  content: string;
  average_rating: number;
  created_at: string;
}

const ArticleList: React.FC = () => {
  const [articles, setArticles] = useState<Article[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchArticles = async () => {
      try {
        setLoading(true);
        const response = await axios.get('http://localhost:8000/works/api/articles/');
        setArticles(response.data);
        setError(null);
      } catch (error) {
        console.error('Error fetching articles:', error);
        setError('Не удалось загрузить статьи. Пожалуйста, попробуйте позже.');
      } finally {
        setLoading(false);
      }
    };

    fetchArticles();
  }, []);

  if (loading) {
    return <div className="loading">Загрузка...</div>;
  }

  if (error) {
    return <div className="error">{error}</div>;
  }

  return (
    <div className="articles-container">
      <h1 className="articles-title">Статьи</h1>
      <div className="articles-grid">
        {articles.map((article) => (
          <article key={article.id} className="article-card">
            {article.image && (
              <img 
                src={article.image} 
                alt={article.title} 
                className="article-image"
                onError={(e) => {
                  const target = e.target as HTMLImageElement;
                  target.src = '/placeholder.jpg';
                }}
              />
            )}
            <div className="article-content">
              <h2 className="article-title">{article.title}</h2>
              <p className="article-text">{article.content}</p>
              {article.average_rating && (
                <div className="article-rating">
                  Рейтинг: {article.average_rating.toFixed(1)} ⭐
                </div>
              )}
              <div className="article-date">
                {new Date(article.created_at).toLocaleDateString('ru-RU')}
              </div>
            </div>
          </article>
        ))}
      </div>
    </div>
  );
};

export default ArticleList; 