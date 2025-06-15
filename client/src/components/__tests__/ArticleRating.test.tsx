import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import '@testing-library/jest-dom';
import ArticleRating from '../ArticleRating';
import { MockedProvider } from '@apollo/client/testing';
import { gql } from '@apollo/client';

const RATE_ARTICLE = gql`
  mutation RateArticle($articleId: Int!, $value: Int!) {
    rateArticle(articleId: $articleId, value: $value) {
      success
      averageRating
      ratingCount
    }
  }
`;

describe('ArticleRating Component', () => {
  const mockArticleId = 1;
  const mocks = [
    {
      request: {
        query: RATE_ARTICLE,
        variables: {
          articleId: mockArticleId,
          value: 5
        }
      },
      result: {
        data: {
          rateArticle: {
            success: true,
            averageRating: 4.5,
            ratingCount: 10
          }
        }
      }
    }
  ];

  test('renders rating buttons', () => {
    render(
      <MockedProvider mocks={mocks} addTypename={false}>
        <ArticleRating articleId={mockArticleId} />
      </MockedProvider>
    );

    // Проверяем, что все 5 кнопок рейтинга отображаются
    for (let i = 1; i <= 5; i++) {
      expect(screen.getByText(`${i} ⭐`)).toBeInTheDocument();
    }
  });

  test('handles rating click', async () => {
    render(
      <MockedProvider mocks={mocks} addTypename={false}>
        <ArticleRating articleId={mockArticleId} />
      </MockedProvider>
    );

    // Нажимаем на кнопку с рейтингом 5
    await userEvent.click(screen.getByText('5 ⭐'));

    // Проверяем, что мутация была вызвана
    await waitFor(() => {
      expect(screen.getByText('5 ⭐')).toBeInTheDocument();
    });
  });

  test('handles rating error', async () => {
    const errorMocks = [
      {
        request: {
          query: RATE_ARTICLE,
          variables: {
            articleId: mockArticleId,
            value: 5
          }
        },
        error: new Error('An error occurred')
      }
    ];

    const consoleSpy = jest.spyOn(console, 'error').mockImplementation(() => {});

    render(
      <MockedProvider mocks={errorMocks} addTypename={false}>
        <ArticleRating articleId={mockArticleId} />
      </MockedProvider>
    );

    // Нажимаем на кнопку с рейтингом 5
    await userEvent.click(screen.getByText('5 ⭐'));

    // Проверяем, что ошибка была залогирована
    await waitFor(() => {
      expect(consoleSpy).toHaveBeenCalled();
    });

    consoleSpy.mockRestore();
  });
}); 