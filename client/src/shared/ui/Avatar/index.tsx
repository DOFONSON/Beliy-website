import React from 'react';
import styles from './styles.module.css';

interface AvatarProps {
  src?: string;
  alt?: string;
  size?: 'small' | 'medium' | 'large';
  className?: string;
}

export const Avatar: React.FC<AvatarProps> = ({
  src,
  alt = 'Avatar',
  size = 'medium',
  className,
}) => {
  return (
    <div className={`${styles.avatar} ${styles[size]} ${className || ''}`}>
      {src ? (
        <img src={src} alt={alt} className={styles.image} />
      ) : (
        <div className={styles.placeholder}>
          {alt.charAt(0).toUpperCase()}
        </div>
      )}
    </div>
  );
}; 