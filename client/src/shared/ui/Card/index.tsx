import React from 'react';
import styles from './styles.module.css';

interface CardProps {
  children: React.ReactNode;
  className?: string;
}

export const Card: React.FC<CardProps> = ({ children, className }) => {
  return (
    <div className={`${styles.card} ${className || ''}`}>
      {children}
    </div>
  );
}; 