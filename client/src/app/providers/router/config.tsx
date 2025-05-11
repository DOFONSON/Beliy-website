import { RouteObject } from 'react-router-dom';
import { ArticleList } from '@/pages/ArticleList';
import { ArticlePage } from '@/pages/ArticlePage';
import { LoginPage } from '@/pages/LoginPage';
import { RegisterPage } from '@/pages/RegisterPage';
import { ProfilePage } from '@/pages/ProfilePage';
import { ProtectedRoute } from './ProtectedRoute';

export enum AppRoutes {
  MAIN = 'main',
  ARTICLE = 'article',
  LOGIN = 'login',
  REGISTER = 'register',
  PROFILE = 'profile',
}

export const RoutePath: Record<AppRoutes, string> = {
  [AppRoutes.MAIN]: '/',
  [AppRoutes.ARTICLE]: '/article/:slug',
  [AppRoutes.LOGIN]: '/login',
  [AppRoutes.REGISTER]: '/register',
  [AppRoutes.PROFILE]: '/profile',
};

export const routeConfig: RouteObject[] = [
  {
    path: RoutePath.main,
    element: <ArticleList />,
  },
  {
    path: RoutePath.article,
    element: (
      <ProtectedRoute>
        <ArticlePage />
      </ProtectedRoute>
    ),
  },
  {
    path: RoutePath.login,
    element: <LoginPage />,
  },
  {
    path: RoutePath.register,
    element: <RegisterPage />,
  },
  {
    path: RoutePath.profile,
    element: (
      <ProtectedRoute>
        <ProfilePage />
      </ProtectedRoute>
    ),
  },
]; 