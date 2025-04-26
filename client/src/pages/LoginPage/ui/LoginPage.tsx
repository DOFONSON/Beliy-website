import { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '@/shared/hooks/useAuth';
import { useForm } from 'react-hook-form';
import { yupResolver } from '@hookform/resolvers/yup';
import * as yup from 'yup';
import styles from './LoginPage.module.css';

interface LoginFormData {
  username: string;
  password: string;
}

const schema = yup.object({
  username: yup.string().required('Имя пользователя обязательно'),
  password: yup.string().required('Пароль обязателен'),
}).required();

export const LoginPage = () => {
  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [error, setError] = useState('');

  const { register, handleSubmit, formState: { errors } } = useForm<LoginFormData>({
    resolver: yupResolver(schema)
  });

  const onSubmit = async (data: LoginFormData) => {
    const result = await login(data);
    if (result.success) {
      const from = location.state?.from?.pathname || '/';
      navigate(from, { replace: true });
    } else {
      setError(result.error || 'Произошла ошибка при входе');
    }
  };

  return (
    <div className={styles.loginPage}>
      <div className={styles.loginForm}>
        <h1>Вход</h1>
        {error && <div className={styles.error}>{error}</div>}
        <form onSubmit={handleSubmit(onSubmit)}>
          <div className={styles.formGroup}>
            <label htmlFor="username">Имя пользователя</label>
            <input
              id="username"
              type="text"
              {...register('username')}
              className={errors.username ? styles.inputError : ''}
            />
            {errors.username && (
              <span className={styles.errorMessage}>{errors.username.message}</span>
            )}
          </div>

          <div className={styles.formGroup}>
            <label htmlFor="password">Пароль</label>
            <input
              id="password"
              type="password"
              {...register('password')}
              className={errors.password ? styles.inputError : ''}
            />
            {errors.password && (
              <span className={styles.errorMessage}>{errors.password.message}</span>
            )}
          </div>

          <button type="submit" className={styles.submitButton}>
            Войти
          </button>
        </form>
      </div>
    </div>
  );
}; 