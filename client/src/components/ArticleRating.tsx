import { useMutation, gql } from '@apollo/client';

const RATE_ARTICLE = gql`
  mutation RateArticle($articleId: Int!, $value: Int!) {
    rateArticle(articleId: $articleId, value: $value) {
      success
      averageRating
      ratingCount
    }
  }
`;

const ArticleRating = ({ articleId }: { articleId: number }) => {
  const [rateArticle] = useMutation(RATE_ARTICLE);

  const handleRating = async (value: number) => {
    try {
      await rateArticle({
        variables: {
          articleId,
          value
        }
      });
    } catch (error) {
      console.error('Error rating article:', error);
    }
  };

  return (
    <div className="rating">
      {[1, 2, 3, 4, 5].map((value) => (
        <button
          key={value}
          onClick={() => handleRating(value)}
          className="rating-star"
        >
          {value} ⭐
        </button>
      ))}
    </div>
  );
};

export default ArticleRating; 