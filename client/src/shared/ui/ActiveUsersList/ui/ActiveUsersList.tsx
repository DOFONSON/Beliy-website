import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import styles from './styles.module.css';

interface User {
  id: number;
  username: string;
  avatar_url: string;
  comments_count: number;
}

interface ActiveUsersListProps {
  users: User[];
}

export const ActiveUsersList: React.FC<ActiveUsersListProps> = ({ users }) => {
  const [startIndex, setStartIndex] = useState(0);
  const visibleCount = 3;

  const nextUsers = () => {
    setStartIndex((prevIndex) => 
      prevIndex + visibleCount >= users.length ? 0 : prevIndex + visibleCount
    );
  };

  const prevUsers = () => {
    setStartIndex((prevIndex) => 
      prevIndex - visibleCount < 0 ? Math.max(0, users.length - visibleCount) : prevIndex - visibleCount
    );
  };

  const visibleUsers = users.slice(startIndex, startIndex + visibleCount);

  return (
    <div className={styles.activeUsersContainer}>
      <h2 className={styles.title}>Самые активные пользователи</h2>
      <div className={styles.listContainer}>
        <div className={styles.usersList}>
          {visibleUsers.map((user) => (
            <Link
              key={user.id}
              to={`/profile/${user.id}`}
              className={styles.userItem}
            >
              <div className={styles.userInfo}>
                <span className={styles.username}>{user.username}</span>
                <span className={styles.commentsCount}>
                  {user.comments_count} комментариев
                </span>
              </div>
              <img
                src={user.avatar_url || '/default-avatar.png'}
                alt={user.username}
                className={styles.avatar}
              />
            </Link>
          ))}
        </div>
        <div className={styles.scrollControls}>
          <button onClick={prevUsers} className={styles.scrollButton}>
            ↑
          </button>
          <button onClick={nextUsers} className={styles.scrollButton}>
            ↓
          </button>
        </div>
      </div>
    </div>
  );
}; 