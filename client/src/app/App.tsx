import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Layout } from '../widgets/Layout';
import { LoginPage } from '../pages/LoginPage';
import { RegisterPage } from '../pages/RegisterPage';
import { ProfilePage } from '../pages/ProfilePage';
import { ProductsPage } from '../pages/ProductsPage';
import { ProductPage } from '../pages/ProductPage';
import { CartPage } from '../pages/CartPage';
import { ArticlesPage } from '../pages/ArticlesPage';
import { ArticlePage } from '../pages/ArticlePage';
import { CartProvider } from '@/features/CartIcon/model/CartContext';

function App() {
  return (
    <Router>
      <CartProvider>
        <Routes>
          <Route path="/" element={<Layout />}>
            <Route index element={<ArticlesPage />} />
            <Route path="articles/:slug" element={<ArticlePage />} />
            <Route path="login" element={<LoginPage />} />
            <Route path="register" element={<RegisterPage />} />
            <Route path="profile" element={<ProfilePage />} />
            <Route path="products" element={<ProductsPage />} />
            <Route path="products/:id" element={<ProductPage />} />
            <Route path="cart" element={<CartPage />} />
          </Route>
        </Routes>
      </CartProvider>
    </Router>
  );
}

export default App; 