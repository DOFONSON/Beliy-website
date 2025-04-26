import { useState } from 'react';
import styles from './CommentForm.module.css';

interface CommentFormProps {
  onSubmit: (text: string) => void;
}

export const CommentForm = ({ onSubmit }: CommentFormProps) => {
  const [text, setText] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (text.trim()) {
      onSubmit(text);
      setText('');
    }
  };

  return (
    <form className={styles.commentForm} onSubmit={handleSubmit}>
      <textarea
        className={styles.textarea}
        value={text}
        onChange={(e) => setText(e.target.value)}
        placeholder="Напишите комментарий..."
        rows={3}
      />
      <button
        type="submit"
        className={styles.submitButton}
        disabled={!text.trim()}
      >
        Отправить
      </button>
    </form>
  );
}; 