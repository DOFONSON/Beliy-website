import { useState } from 'react';
import styles from './Rating.module.css';

interface RatingProps {
  value: number;
  onRate: (value: number) => void;
}

export const Rating = ({ value, onRate }: RatingProps) => {
  const [hoveredRating, setHoveredRating] = useState(0);
  const stars = [1, 2, 3, 4, 5];

  return (
    <div className={styles.rating}>
      <span className={styles.label}>Рейтинг: {value.toFixed(1)}</span>
      <div className={styles.stars}>
        {stars.map((star) => (
          <button
            key={star}
            className={styles.star}
            onClick={() => onRate(star)}
            onMouseEnter={() => setHoveredRating(star)}
            onMouseLeave={() => setHoveredRating(0)}
            type="button"
            aria-label={`Rate ${star} stars`}
          >
            <span
              className={`${styles.starIcon} ${
                (hoveredRating || value) >= star ? styles.filled : ''
              }`}
            >
              ★
            </span>
          </button>
        ))}
      </div>
    </div>
  );
}; 