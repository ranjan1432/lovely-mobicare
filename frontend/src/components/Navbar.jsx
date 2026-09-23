import { useEffect, useState } from "react";
import {
  NavLink,
  useLocation,
  useNavigate,
} from "react-router-dom";

import logo from "../assets/lovely-mobi-care-logo.jpeg";

import { useCart } from "../context/CartContext";
import { useAuth } from "../context/AuthContext";

import "./Navbar.css";

function Navbar() {
  const { cartCount } = useCart();

  const {
    user,
    isAuthenticated,
    authLoading,
    logout,
  } = useAuth();

  const [menuOpen, setMenuOpen] = useState(false);
  const [logoutLoading, setLogoutLoading] =
    useState(false);

  const location = useLocation();
  const navigate = useNavigate();

  const toggleMenu = () => {
    setMenuOpen((currentState) => !currentState);
  };

  const closeMenu = () => {
    setMenuOpen(false);
  };

  /*
    URL / PAGE change aana udane
    mobile navbar automatic-ah close aagum
  */
  useEffect(() => {
    setMenuOpen(false);
  }, [location.pathname]);

  /*
    Logged-in user-ku display panna name.
    first_name illana email use pannuvom.
  */
  const displayName =
    user?.first_name?.trim() ||
    user?.username?.trim() ||
    user?.email?.split("@")[0] ||
    "Account";

  /*
    Logout
  */
  const handleLogout = async () => {
    try {
      setLogoutLoading(true);

      await logout();

      closeMenu();

      navigate("/", {
        replace: true,
      });
    } finally {
      setLogoutLoading(false);
    }
  };

  return (
    <header className="navbar">
      <div className="navbar-container">
        {/* BRAND */}
        <NavLink
          to="/"
          className="navbar-brand"
          onClick={closeMenu}
        >
          <img
            src={logo}
            alt="Lovely Mobi Care Logo"
            className="brand-logo"
          />

          <div className="brand-text">
            <span>Lovely Mobi Care</span>

            <small>
              Mobile Sales & Service
            </small>
          </div>
        </NavLink>

        {/* MOBILE MENU BUTTON */}
        <button
          type="button"
          className={`menu-button ${
            menuOpen ? "menu-button-open" : ""
          }`}
          onClick={toggleMenu}
          aria-label={
            menuOpen
              ? "Close navigation menu"
              : "Open navigation menu"
          }
          aria-expanded={menuOpen}
        >
          {menuOpen ? "✕" : "☰"}
        </button>

        {/* NAVIGATION */}
        <nav
          className={`nav-links ${
            menuOpen ? "open" : ""
          }`}
        >
          <NavLink
            to="/"
            onClick={closeMenu}
          >
            Home
          </NavLink>

          <NavLink
            to="/products"
            onClick={closeMenu}
          >
            Products
          </NavLink>

          <NavLink
            to="/services"
            onClick={closeMenu}
          >
            Services
          </NavLink>

          <NavLink
            to="/checkout"
            onClick={closeMenu}
          >
            Checkout
          </NavLink>

          <NavLink
            to="/my-orders"
            onClick={closeMenu}
          >
            My Orders
          </NavLink>

          <NavLink
            to="/contact"
            onClick={closeMenu}
          >
            Contact
          </NavLink>

          {/* CART */}
          <NavLink
            to="/cart"
            className="cart-link"
            onClick={closeMenu}
          >
            🛒 Cart

            {cartCount > 0 && (
              <span className="cart-count">
                {cartCount}
              </span>
            )}
          </NavLink>

          {/* AUTH */}
          {!authLoading && (
            <>
              {!isAuthenticated ? (
                <NavLink
                  to="/login"
                  className="login-link"
                  onClick={closeMenu}
                >
                  👤 Login
                </NavLink>
              ) : (
                <div className="navbar-account">
                  <span className="navbar-user">
                    👤 Hi, {displayName}
                  </span>

                  <button
                    type="button"
                    className="logout-button"
                    onClick={handleLogout}
                    disabled={logoutLoading}
                  >
                    {logoutLoading
                      ? "Logging out..."
                      : "Logout"}
                  </button>
                </div>
              )}
            </>
          )}
        </nav>
      </div>
    </header>
  );
}

export default Navbar;