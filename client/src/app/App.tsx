import { RouterProvider, createBrowserRouter } from 'react-router-dom';
import { routeConfig } from './providers/router/config';
import { Layout } from '@/widgets/Layout';

const router = createBrowserRouter([
  {
    path: '/',
    element: <Layout />,
    children: routeConfig,
  },
]);

export const App = () => {
  return <RouterProvider router={router} />;
}; 