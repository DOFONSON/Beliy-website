import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import styles from './styles.module.css';

interface SliderItem {
  id: number;
  title: string;
  image: string;
  slug?: string;
  rating?: number;
  price?: number;
}

interface SliderProps {
  title: string;
  items: SliderItem[];
  type: 'article' | 'product';
}

export const Slider: React.FC<SliderProps> = ({ title, items, type }) => {
  const [currentIndex, setCurrentIndex] = useState(0);
  const itemsPerPage = 4;

  const nextSlide = () => {
    setCurrentIndex((prevIndex) => 
      prevIndex + itemsPerPage >= items.length ? 0 : prevIndex + itemsPerPage
    );
  };

  const prevSlide = () => {
    setCurrentIndex((prevIndex) => 
      prevIndex - itemsPerPage < 0 ? Math.max(0, items.length - itemsPerPage) : prevIndex - itemsPerPage
    );
  };

  const visibleItems = items.slice(currentIndex, currentIndex + itemsPerPage);

  return (
    <div className={styles.sliderContainer}>
      <div className={styles.sliderHeader}>
        <h2 className={styles.sliderTitle}>{title}</h2>
        <div className={styles.sliderControls}>
          <button onClick={prevSlide} className={styles.sliderButton}>
            ←
          </button>
          <button onClick={nextSlide} className={styles.sliderButton}>
            →
          </button>
        </div>
      </div>
      <div className={styles.sliderContent}>
        {visibleItems.map((item) => (
          <Link
            key={item.id}
            to={type === 'article' ? `/articles/${item.slug}` : `/products/${item.id}`}
            className={styles.sliderItem}
          >
            <div className={styles.itemImageContainer}>
              <img src={item.image} alt={item.title} className={styles.itemImage} />
              {item.rating && (
                <div className={styles.rating}>
                  ★ {item.rating.toFixed(1)}
                </div>
              )}
            </div>
            <h3 className={styles.itemTitle}>{item.title}</h3>
            {type === 'product' && item.price && (
              <div className={styles.itemPrice}>{item.price} ₽</div>
            )}
          </Link>
        ))}
      </div>
    </div>
  );
}; 