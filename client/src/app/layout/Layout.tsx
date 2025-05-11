import React from 'react';
import { Outlet } from 'react-router-dom';
import { Header } from '../../widgets/Header';
import styles from './styles.module.css';

export const Layout: React.FC = () => {
  return (
    <div className={styles.layout}>
      <Header />
      <main className={styles.main}>
        <Outlet />
      </main>
    </div>
  );
}; 