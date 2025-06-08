import React, { useState, useRef, TouchEvent } from 'react';
import { Link } from 'react-router-dom';
import styles from './styles.module.css';

interface SwipeSliderItem {
  id: number;
  title: string;
  image: string;
  slug?: string;
  rating?: number;
  price?: number;
}

interface SwipeSliderProps {
  title: string;
  items: SwipeSliderItem[];
  type: 'article' | 'product';
}

export const SwipeSlider: React.FC<SwipeSliderProps> = ({ title, items, type }) => {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [touchStart, setTouchStart] = useState<number | null>(null);
  const [touchEnd, setTouchEnd] = useState<number | null>(null);
  const sliderRef = useRef<HTMLDivElement>(null);

  const minSwipeDistance = 50;

  const onTouchStart = (e: TouchEvent) => {
    setTouchEnd(null);
    setTouchStart(e.targetTouches[0].clientX);
  };

  const onTouchMove = (e: TouchEvent) => {
    setTouchEnd(e.targetTouches[0].clientX);
  };

  const onTouchEnd = () => {
    if (!touchStart || !touchEnd) return;
    
    const distance = touchStart - touchEnd;
    const isLeftSwipe = distance > minSwipeDistance;
    const isRightSwipe = distance < -minSwipeDistance;

    if (isLeftSwipe) {
      nextSlide();
    }
    if (isRightSwipe) {
      prevSlide();
    }
  };

  const nextSlide = () => {
    setCurrentIndex((prevIndex) => 
      prevIndex + 1 >= items.length ? 0 : prevIndex + 1
    );
  };

  const prevSlide = () => {
    setCurrentIndex((prevIndex) => 
      prevIndex - 1 < 0 ? items.length - 1 : prevIndex - 1
    );
  };

  const getVisibleItems = (): SwipeSliderItem[] => {
    const visibleItems: SwipeSliderItem[] = [];
    for (let i = 0; i < 3; i++) {
      const index = (currentIndex + i) % items.length;
      visibleItems.push(items[index]);
    }
    return visibleItems;
  };

  const visibleItems = getVisibleItems();

  return (
    <div className={styles.swipeSliderContainer}>
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
      <div 
        ref={sliderRef}
        className={styles.sliderContent}
        onTouchStart={onTouchStart}
        onTouchMove={onTouchMove}
        onTouchEnd={onTouchEnd}
      >
        {visibleItems.map((item, index) => (
          <Link
            key={item.id}
            to={type === 'article' ? `/articles/${item.slug}` : `/products/${item.id}`}
            className={`${styles.sliderItem} ${index === 1 ? styles.activeItem : ''}`}
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
      <div className={styles.sliderDots}>
        {items.map((_, index) => (
          <button
            key={index}
            className={`${styles.dot} ${index === currentIndex ? styles.activeDot : ''}`}
            onClick={() => setCurrentIndex(index)}
          />
        ))}
      </div>
    </div>
  );
}; 