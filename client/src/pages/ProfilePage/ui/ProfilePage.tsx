import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../../shared/hooks/useAuth';
import { api } from '../../../shared/api';
import { Button } from '../../../shared/ui/Button';
import { Input } from '../../../shared/ui/Input';
import { Textarea } from '../../../shared/ui/Textarea';
import { Avatar } from '../../../shared/ui/Avatar';
import styles from './styles.module.css';

interface UserData {
  first_name: string;
  last_name: string;
  email: string;
  bio: string;
}

export const ProfilePage: React.FC = () => {
  const navigate = useNavigate();
  const { user, logout } = useAuth();
  const [loading, setLoading] = useState(true);
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
        setError('Failed to load user data');
      } finally {
        setLoading(false);
      }
    };

    if (user) {
      fetchUserData();
    } else {
      navigate('/login');
    }
  }, [user, navigate]);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
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

      await api.patch('/auth/profile/', formDataToSend, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      setSuccess('Profile updated successfully');
    } catch (err) {
      setError('Failed to update profile');
    }
  };

  if (loading) {
    return <div className={styles.profilePage}>Loading...</div>;
  }

  return (
    <div className={styles.profilePage}>
      <form onSubmit={handleSubmit} className={styles.profileForm}>
        <div className={styles.avatarSection}>
          <Avatar
            src={avatarPreview || undefined}
            alt={`${formData.first_name} ${formData.last_name}`}
            size="large"
          />
          <div className={styles.avatarUpload}>
            <input
              type="file"
              id="avatar"
              accept="image/*"
              onChange={handleAvatarChange}
              className={styles.fileInput}
            />
            <label htmlFor="avatar" className={styles.uploadLabel}>
              Change Avatar
            </label>
          </div>
        </div>

        <div className={styles.formGroup}>
          <Input
            label="First Name"
            name="first_name"
            value={formData.first_name}
            onChange={handleInputChange}
          />
        </div>

        <div className={styles.formGroup}>
          <Input
            label="Last Name"
            name="last_name"
            value={formData.last_name}
            onChange={handleInputChange}
          />
        </div>

        <div className={styles.formGroup}>
          <Input
            label="Email"
            name="email"
            type="email"
            value={formData.email}
            onChange={handleInputChange}
          />
        </div>

        <div className={styles.formGroup}>
          <Textarea
            label="Bio"
            name="bio"
            value={formData.bio}
            onChange={handleInputChange}
          />
        </div>

        {error && <div className={styles.error}>{error}</div>}
        {success && <div className={styles.success}>{success}</div>}

        <Button type="submit" variant="primary" fullWidth>
          Save Changes
        </Button>
      </form>
    </div>
  );
}; 