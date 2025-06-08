import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../../shared/hooks/useAuth';
import { CartIcon } from '../../../shared/ui/CartIcon';
import { SearchBar } from '../../../shared/ui/SearchBar/ui/SearchBar';
import styles from './styles.module.css';

export const Header: React.FC = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <header className={styles.header}>
      <div className={styles.logo}>
        <Link to="/">Beliy</Link>
      </div>
      <div className={styles.searchWrapper}>
        <SearchBar />
      </div>
      <nav className={styles.nav}>
        <Link to="/products" className={styles.navLink}>Products</Link>
        {user ? (
          <div className={styles.userSection}>
            <CartIcon />
            <div className={styles.profileMenu}>
              <img 
                src={user.avatar_url || '/default-avatar.png'} 
                alt={user.username} 
                className={styles.avatar}
              />
              <div className={styles.dropdown}>
                <Link to="/profile" className={styles.dropdownItem}>Profile</Link>
                <button onClick={handleLogout} className={styles.dropdownItem}>
                  Logout
                </button>
              </div>
            </div>
          </div>
        ) : (
          <div className={styles.authButtons}>
            <Link to="/login" className={styles.loginButton}>Login</Link>
            <Link to="/register" className={styles.registerButton}>Register</Link>
          </div>
        )}
      </nav>
    </header>
  );
}; 