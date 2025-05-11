import { Link, Outlet, useNavigate } from 'react-router-dom';
import { useAuth } from '@/shared/hooks/useAuth';
import styles from './Layout.module.css';

export const Layout = () => {
  const { isAuthenticated, user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <div className={styles.layout}>
      <header className={styles.header}>
        <div className={styles.container}>
          <Link to="/" className={styles.logo}>
            Мой блог
          </Link>
          <nav className={styles.nav}>
            {isAuthenticated ? (
              <>
                <span className={styles.username}>
                  {user?.username}
                </span>
                <Link to="/profile" className={styles.authLink}>
                  Профиль
                </Link>
                <button
                  onClick={handleLogout}
                  className={styles.logoutButton}
                >
                  Выйти
                </button>
              </>
            ) : (
              <>
                <Link to="/login" className={styles.authLink}>
                  Войти
                </Link>
                <Link to="/register" className={styles.authLink}>
                  Регистрация
                </Link>
              </>
            )}
          </nav>
        </div>
      </header>

      <main className={styles.main}>
        <div className={styles.container}>
          <Outlet />
        </div>
      </main>

      <footer className={styles.footer}>
        <div className={styles.container}>
          <p>&copy; 2024 Мой блог. Все права защищены.</p>
        </div>
      </footer>
    </div>
  );
}; 