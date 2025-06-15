import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import '@testing-library/jest-dom';
import ArticleList from '../ArticleList';

// Мокаем axios
jest.mock('axios', () => ({
  get: jest.fn()
}));

// Импортируем axios после мока
const axios = require('axios');

describe('ArticleList Component', () => {
  const mockArticles = [
    {
      id: 1,
      title: 'Test Article 1',
      slug: 'test-article-1',
      image: 'test-image-1.jpg',
      content: 'Test content 1',
      average_rating: 4.5,
      created_at: '2024-03-20T10:00:00Z'
    },
    {
      id: 2,
      title: 'Test Article 2',
      slug: 'test-article-2',
      image: 'test-image-2.jpg',
      content: 'Test content 2',
      average_rating: 3.8,
      created_at: '2024-03-19T10:00:00Z'
    }
  ];

  beforeEach(() => {
    // Очищаем все моки перед каждым тестом
    jest.clearAllMocks();
  });

  test('renders loading state initially', () => {
    axios.get.mockImplementation(() => new Promise(() => {}));
    render(<ArticleList />);
    expect(screen.getByText('Загрузка...')).toBeInTheDocument();
  });

  test('renders articles title', async () => {
    axios.get.mockResolvedValueOnce({ data: mockArticles });
    render(<ArticleList />);
    await waitFor(() => {
      expect(screen.getByText('Статьи')).toBeInTheDocument();
    });
  });

  test('renders first article', async () => {
    axios.get.mockResolvedValueOnce({ data: mockArticles });
    render(<ArticleList />);
    await waitFor(() => {
      expect(screen.getByText('Test Article 1')).toBeInTheDocument();
    });
  });

  test('renders second article', async () => {
    axios.get.mockResolvedValueOnce({ data: mockArticles });
    render(<ArticleList />);
    await waitFor(() => {
      expect(screen.getByText('Test Article 2')).toBeInTheDocument();
    });
  });

  test('renders error message when API call fails', async () => {
    axios.get.mockRejectedValueOnce(new Error('API Error'));
    render(<ArticleList />);
    await waitFor(() => {
      expect(screen.getByText('Не удалось загрузить статьи. Пожалуйста, попробуйте позже.')).toBeInTheDocument();
    });
  });

  test('displays first article rating', async () => {
    axios.get.mockResolvedValueOnce({ data: mockArticles });
    render(<ArticleList />);
    await waitFor(() => {
      expect(screen.getByText('Рейтинг: 4.5 ⭐')).toBeInTheDocument();
    });
  });

  test('displays second article rating', async () => {
    axios.get.mockResolvedValueOnce({ data: mockArticles });
    render(<ArticleList />);
    await waitFor(() => {
      expect(screen.getByText('Рейтинг: 3.8 ⭐')).toBeInTheDocument();
    });
  });

  test('handles image loading error for first article', async () => {
    axios.get.mockResolvedValueOnce({ data: mockArticles });
    render(<ArticleList />);
    await waitFor(() => {
      const images = screen.getAllByRole('img');
      const errorEvent = new Event('error');
      images[0].dispatchEvent(errorEvent);
      expect(images[0]).toHaveAttribute('src', '/placeholder.jpg');
    });
  });

  test('handles image loading error for second article', async () => {
    axios.get.mockResolvedValueOnce({ data: mockArticles });
    render(<ArticleList />);
    await waitFor(() => {
      const images = screen.getAllByRole('img');
      const errorEvent = new Event('error');
      images[1].dispatchEvent(errorEvent);
      expect(images[1]).toHaveAttribute('src', '/placeholder.jpg');
    });
  });

  test('displays article content', async () => {
    axios.get.mockResolvedValueOnce({ data: mockArticles });
    render(<ArticleList />);
    await waitFor(() => {
      expect(screen.getByText('Test content 1')).toBeInTheDocument();
      expect(screen.getByText('Test content 2')).toBeInTheDocument();
    });
  });
}); 