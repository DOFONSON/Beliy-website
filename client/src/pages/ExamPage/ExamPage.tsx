import React, { useEffect, useState } from 'react';
import { getExams } from '@/shared/api';

interface Exam {
  id: number;
  title: string;
  created_at: string;
  exam_date: string;
  image: string | null;
  users: { id: number; username: string; first_name: string; last_name: string }[];
}

const FIO = 'Назаров Тимофей';
const GROUP = '231-322';

export const ExamPage: React.FC = () => {
  const [exams, setExams] = useState<Exam[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getExams()
      .then(data => {
        setExams(data);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, []);

  return (
    <div style={{ padding: 24 }}>
      <h1>Экзамены</h1>
      <h2>{FIO}, группа {GROUP}</h2>
      {loading ? (
        <p>Загрузка...</p>
      ) : exams.length === 0 ? (
        <p>Нет опубликованных экзаменов.</p>
      ) : (
        <table style={{ borderCollapse: 'collapse', width: '100%' }}>
          <thead>
            <tr>
              <th>Название экзамена</th>
              <th>Дата создания</th>
              <th>Дата проведения</th>
              <th>Изображение</th>
              <th>Пользователи</th>
            </tr>
          </thead>
          <tbody>
            {exams.map(exam => (
              <tr key={exam.id}>
                <td>{exam.title}</td>
                <td>{new Date(exam.created_at).toLocaleString()}</td>
                <td>{new Date(exam.exam_date).toLocaleString()}</td>
                <td>
                  {exam.image ? (
                    <img src={exam.image} alt="Задание" style={{ maxWidth: 100, maxHeight: 100 }} />
                  ) : (
                    '—'
                  )}
                </td>
                <td>
                  {exam.users && exam.users.length > 0
                    ? exam.users.map(u => `${u.first_name || ''} ${u.last_name || ''}`.trim() || u.username).join(', ')
                    : '—'}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
};

export default ExamPage; 