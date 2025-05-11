import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@/shared/hooks/useAuth';
import { api } from '@/shared/api';
import { Button } from '@/shared/ui/Button';
import { Input } from '@/shared/ui/Input';
import { Textarea } from '@/shared/ui/Textarea';
import { Avatar } from '@/shared/ui/Avatar';
import styles from './styles.module.css';

interface UserData {
  first_name: string;
  last_name: string;
  email: string;
  bio: string;
}

export const ProfilePage: React.FC = () => {
  const navigate = useNavigate();
  const { user, isAuthenticated } = useAuth();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [formData, setFormData] = useState<UserData>({
    first_name: '',
    last_name: '',
    email: '',
    bio: '',
  });
  const [avatar, setAvatar] = useState<File | null>(null);
  const [avatarPreview, setAvatarPreview] = useState<string | null>(null);

  useEffect(() => {
    if (!isAuthenticated) {
      navigate('/login');
      return;
    }

    const fetchUserData = async () => {
      try {
        const response = await api.get('/auth/profile/');
        const userData = response.data;
        setFormData({
          first_name: userData.first_name || '',
          last_name: userData.last_name || '',
          email: userData.email || '',
          bio: userData.bio || '',
        });
        if (userData.avatar_url) {
          setAvatarPreview(userData.avatar_url);
        }
      } catch (err) {
        setError('Ошибка при загрузке данных профиля');
        console.error('Error fetching profile:', err);
      }
    };

    fetchUserData();
  }, [isAuthenticated, navigate]);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleAvatarChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setAvatar(file);
      const reader = new FileReader();
      reader.onloadend = () => {
        setAvatarPreview(reader.result as string);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setSuccess(null);

    try {
      const formDataToSend = new FormData();
      Object.entries(formData).forEach(([key, value]) => {
        formDataToSend.append(key, value);
      });
      if (avatar) {
        formDataToSend.append('avatar', avatar);
      }

      const response = await api.patch('/auth/profile/', formDataToSend, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      setSuccess('Профиль успешно обновлен');
      setFormData({
        first_name: response.data.first_name || '',
        last_name: response.data.last_name || '',
        email: response.data.email || '',
        bio: response.data.bio || '',
      });
      if (response.data.avatar_url) {
        setAvatarPreview(response.data.avatar_url);
      }
    } catch (err) {
      setError('Ошибка при обновлении профиля');
      console.error('Error updating profile:', err);
    } finally {
      setLoading(false);
    }
  };

  if (!isAuthenticated) {
    return null;
  }

  return (
    <div className={styles.profilePage}>
      <h1>Профиль пользователя</h1>
      
      <form onSubmit={handleSubmit} className={styles.profileForm}>
        <div className={styles.avatarSection}>
          <Avatar
            src={avatarPreview || user?.avatar_url}
            alt={user?.username || 'User avatar'}
            size="large"
          />
          <div className={styles.avatarUpload}>
            <input
              type="file"
              accept="image/*"
              onChange={handleAvatarChange}
              id="avatar-upload"
              className={styles.fileInput}
            />
            <label htmlFor="avatar-upload" className={styles.uploadLabel}>
              Изменить аватар
            </label>
          </div>
        </div>

        <div className={styles.formGroup}>
          <Input
            label="Имя"
            name="first_name"
            value={formData.first_name}
            onChange={handleInputChange}
            placeholder="Введите имя"
          />
        </div>

        <div className={styles.formGroup}>
          <Input
            label="Фамилия"
            name="last_name"
            value={formData.last_name}
            onChange={handleInputChange}
            placeholder="Введите фамилию"
          />
        </div>

        <div className={styles.formGroup}>
          <Input
            label="Email"
            name="email"
            type="email"
            value={formData.email}
            onChange={handleInputChange}
            placeholder="Введите email"
          />
        </div>

        <div className={styles.formGroup}>
          <Textarea
            label="О себе"
            name="bio"
            value={formData.bio}
            onChange={handleInputChange}
            placeholder="Расскажите о себе"
          />
        </div>

        {error && <div className={styles.error}>{error}</div>}
        {success && <div className={styles.success}>{success}</div>}

        <Button type="submit" disabled={loading}>
          {loading ? 'Сохранение...' : 'Сохранить изменения'}
        </Button>
      </form>
    </div>
  );
}; 