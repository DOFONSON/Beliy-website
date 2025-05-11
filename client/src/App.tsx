import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Layout } from './widgets/Layout';
import { LoginPage } from './pages/LoginPage';
import { RegisterPage } from './pages/RegisterPage';
import { ProfilePage } from './pages/ProfilePage';
import { ProductsPage } from './pages/ProductsPage';
import { ProductPage } from './pages/ProductPage';
import { CartPage } from './pages/CartPage';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route path="login" element={<LoginPage />} />
          <Route path="register" element={<RegisterPage />} />
          <Route path="profile" element={<ProfilePage />} />
          <Route path="products" element={<ProductsPage />} />
          <Route path="products/:id" element={<ProductPage />} />
          <Route path="cart" element={<CartPage />} />
        </Route>
      </Routes>
    </Router>
  );
}

export default App;