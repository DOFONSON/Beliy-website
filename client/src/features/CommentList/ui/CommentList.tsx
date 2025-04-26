import React from 'react';
import styles from './CommentList.module.css';

interface Comment {
  id: number;
  text: string;
  user: {
    username: string;
  };
  created_at: string;
}

interface CommentListProps {
  comments: Comment[];
}

export const CommentList: React.FC<CommentListProps> = ({ comments }) => {
  if (comments.length === 0) {
    return <div className={styles.noComments}>Нет комментариев</div>;
  }

  return (
    <div className={styles.commentList}>
      {comments.map((comment) => (
        <div key={comment.id} className={styles.comment}>
          <div className={styles.commentHeader}>
            <span className={styles.author}>{comment.user.username}</span>
            <time className={styles.date} dateTime={comment.created_at}>
              {new Date(comment.created_at).toLocaleDateString('ru-RU')}
            </time>
          </div>
          <p className={styles.text}>{comment.text}</p>
        </div>
      ))}
    </div>
  );
}; 