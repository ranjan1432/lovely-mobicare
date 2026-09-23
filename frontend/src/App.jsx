import { Routes, Route } from "react-router-dom";

import Navbar from "./components/Navbar";
import Footer from "./components/Footer";
import ProtectedRoute from "./components/ProtectedRoute";

import Home from "./pages/Home";
import ProductsPage from "./pages/ProductsPage";
import CartPage from "./pages/CartPage";
import CheckoutPage from "./pages/CheckoutPage";
import ServicePage from "./pages/ServicePage";
import ContactPage from "./pages/ContactPage";
import MyOrdersPage from "./pages/MyOrdersPage";
import AuthPage from "./pages/AuthPage";

function App() {
  return (
    <div className="app">
      <Navbar />

      <main className="main-content">
        <Routes>
          <Route
            path="/"
            element={<Home />}
          />

          <Route
            path="/products"
            element={<ProductsPage />}
          />

          <Route
            path="/cart"
            element={<CartPage />}
          />

          {/* LOGIN / REGISTER */}
          <Route
            path="/login"
            element={<AuthPage />}
          />

          <Route
            path="/register"
            element={<AuthPage />}
          />

          {/* PROTECTED CHECKOUT */}
          <Route
            path="/checkout"
            element={
              <ProtectedRoute>
                <CheckoutPage />
              </ProtectedRoute>
            }
          />

          <Route
            path="/services"
            element={<ServicePage />}
          />

          <Route
            path="/my-orders"
            element={<MyOrdersPage />}
          />

          <Route
            path="/contact"
            element={<ContactPage />}
          />
        </Routes>
      </main>

      <Footer />
    </div>
  );
}

export default App;