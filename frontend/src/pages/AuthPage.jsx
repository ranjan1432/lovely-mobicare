import { useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import "./AuthPage.css";

function AuthPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const { login, register } = useAuth();

  const [mode, setMode] = useState("login");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const [loginData, setLoginData] = useState({
    email: "",
    password: "",
  });

  const [registerData, setRegisterData] = useState({
    first_name: "",
    last_name: "",
    email: "",
    password: "",
    password_confirm: "",
  });

  const destination =
    location.state?.from?.pathname || "/";

  const handleLoginChange = (event) => {
    const { name, value } = event.target;

    setLoginData((current) => ({
      ...current,
      [name]: value,
    }));
  };

  const handleRegisterChange = (event) => {
    const { name, value } = event.target;

    setRegisterData((current) => ({
      ...current,
      [name]: value,
    }));
  };

  const handleLogin = async (event) => {
    event.preventDefault();
    setError("");

    if (!loginData.email.trim()) {
      setError("Please enter your email address.");
      return;
    }

    if (!loginData.password) {
      setError("Please enter your password.");
      return;
    }

    try {
      setLoading(true);

      await login(
        loginData.email.trim(),
        loginData.password
      );

      navigate(destination, {
        replace: true,
      });
    } catch (err) {
      setError(
        err.response?.data?.detail ||
          err.response?.data?.non_field_errors?.[0] ||
          "Unable to login. Please check your email and password."
      );
    } finally {
      setLoading(false);
    }
  };

  const handleRegister = async (event) => {
    event.preventDefault();
    setError("");

    if (!registerData.first_name.trim()) {
      setError("Please enter your first name.");
      return;
    }

    if (!registerData.email.trim()) {
      setError("Please enter your email address.");
      return;
    }

    if (registerData.password.length < 8) {
      setError(
        "Password must contain at least 8 characters."
      );
      return;
    }

    if (
      registerData.password !==
      registerData.password_confirm
    ) {
      setError("Passwords do not match.");
      return;
    }

    try {
      setLoading(true);

      await register({
  first_name: registerData.first_name.trim(),
  last_name: registerData.last_name.trim(),
  email: registerData.email.trim(),
  password: registerData.password,
  confirm_password:
    registerData.password_confirm,
});

      navigate(destination, {
        replace: true,
      });
    } catch (err) {
      const data = err.response?.data;

      const message =
  data?.first_name?.[0] ||
  data?.last_name?.[0] ||
  data?.email?.[0] ||
  data?.password?.[0] ||
  data?.confirm_password?.[0] ||
  data?.non_field_errors?.[0] ||
  data?.detail ||
  "Unable to create your account.";

      setError(message);
    } finally {
      setLoading(false);
    }
  };

  const switchMode = (newMode) => {
    setMode(newMode);
    setError("");
  };

  return (
    <div className="auth-page">
      <div className="auth-background-shape auth-shape-one" />
      <div className="auth-background-shape auth-shape-two" />

      <div className="auth-container">
        {/* LEFT SIDE */}
        <section className="auth-showcase">
          <div className="auth-brand-badge">
            LOVELY MOBI CARE
          </div>

          <h1>
            Your trusted destination for{" "}
            <span>mobile accessories.</span>
          </h1>

          <p>
            Shop quality accessories and manage your
            orders securely with Lovely Mobi Care.
          </p>

          <div className="auth-gadget-display">
            <div className="auth-phone">
              <div className="phone-speaker" />

              <div className="phone-screen">
                <div className="phone-logo">
                  LM
                </div>

                <span>Lovely Mobi Care</span>
              </div>
            </div>

            <div className="auth-earbuds">
              <div className="earbud earbud-left">
                ♪
              </div>

              <div className="earbud earbud-right">
                ♪
              </div>

              <div className="earbuds-case">
                <span>100%</span>
              </div>
            </div>

            <div className="auth-charger">
              <div className="charger-pin" />
              <strong>⚡</strong>
            </div>
          </div>

          <div className="auth-features">
            <div>
              <span>✓</span>
              <p>
                <strong>Quality Products</strong>
                Trusted mobile accessories
              </p>
            </div>

            <div>
              <span>✓</span>
              <p>
                <strong>Secure Orders</strong>
                Safe account access
              </p>
            </div>

            <div>
              <span>✓</span>
              <p>
                <strong>Easy Tracking</strong>
                Check your orders anytime
              </p>
            </div>
          </div>
        </section>

        {/* RIGHT SIDE */}
        <section className="auth-card">
          <div className="auth-card-header">
            <span className="auth-small-title">
              WELCOME
            </span>

            <h2>
              {mode === "login"
                ? "Sign in to your account"
                : "Create your account"}
            </h2>

            <p>
              {mode === "login"
                ? "Enter your details to continue shopping."
                : "Join Lovely Mobi Care and start shopping."}
            </p>
          </div>

          <div className="auth-tabs">
            <button
              type="button"
              className={
                mode === "login" ? "active" : ""
              }
              onClick={() => switchMode("login")}
            >
              Sign In
            </button>

            <button
              type="button"
              className={
                mode === "register" ? "active" : ""
              }
              onClick={() =>
                switchMode("register")
              }
            >
              Sign Up
            </button>
          </div>

          {error && (
            <div className="auth-error">
              <span>!</span>
              {error}
            </div>
          )}

          {mode === "login" ? (
            <form
              className="auth-form"
              onSubmit={handleLogin}
            >
              <div className="auth-field">
                <label htmlFor="login-email">
                  Email Address
                </label>

                <div className="auth-input">
                  <span>✉</span>

                  <input
                    id="login-email"
                    type="email"
                    name="email"
                    value={loginData.email}
                    onChange={handleLoginChange}
                    placeholder="Enter your email"
                    autoComplete="email"
                  />
                </div>
              </div>

              <div className="auth-field">
                <label htmlFor="login-password">
                  Password
                </label>

                <div className="auth-input">
                  <span>🔒</span>

                  <input
                    id="login-password"
                    type="password"
                    name="password"
                    value={loginData.password}
                    onChange={handleLoginChange}
                    placeholder="Enter your password"
                    autoComplete="current-password"
                  />
                </div>
              </div>

              <button
                type="submit"
                className="auth-submit"
                disabled={loading}
              >
                {loading
                  ? "Signing In..."
                  : "Sign In"}
              </button>

              <p className="auth-switch-text">
                Don't have an account?{" "}
                <button
                  type="button"
                  onClick={() =>
                    switchMode("register")
                  }
                >
                  Create Account
                </button>
              </p>
            </form>
          ) : (
            <form
              className="auth-form"
              onSubmit={handleRegister}
            >
              <div className="auth-name-row">
                <div className="auth-field">
                  <label htmlFor="first-name">
                    First Name
                  </label>

                  <div className="auth-input">
                    <span>👤</span>

                    <input
                      id="first-name"
                      type="text"
                      name="first_name"
                      value={
                        registerData.first_name
                      }
                      onChange={
                        handleRegisterChange
                      }
                      placeholder="First name"
                      autoComplete="given-name"
                    />
                  </div>
                </div>

                <div className="auth-field">
                  <label htmlFor="last-name">
                    Last Name
                  </label>

                  <div className="auth-input">
                    <span>👤</span>

                    <input
                      id="last-name"
                      type="text"
                      name="last_name"
                      value={
                        registerData.last_name
                      }
                      onChange={
                        handleRegisterChange
                      }
                      placeholder="Last name"
                      autoComplete="family-name"
                    />
                  </div>
                </div>
              </div>

              <div className="auth-field">
                <label htmlFor="register-email">
                  Email Address
                </label>

                <div className="auth-input">
                  <span>✉</span>

                  <input
                    id="register-email"
                    type="email"
                    name="email"
                    value={registerData.email}
                    onChange={
                      handleRegisterChange
                    }
                    placeholder="Enter your email"
                    autoComplete="email"
                  />
                </div>
              </div>

              <div className="auth-field">
                <label htmlFor="register-password">
                  Password
                </label>

                <div className="auth-input">
                  <span>🔒</span>

                  <input
                    id="register-password"
                    type="password"
                    name="password"
                    value={
                      registerData.password
                    }
                    onChange={
                      handleRegisterChange
                    }
                    placeholder="Create password"
                    autoComplete="new-password"
                  />
                </div>
              </div>

              <div className="auth-field">
                <label htmlFor="confirm-password">
                  Confirm Password
                </label>

                <div className="auth-input">
                  <span>🔒</span>

                  <input
                    id="confirm-password"
                    type="password"
                    name="password_confirm"
                    value={
                      registerData.password_confirm
                    }
                    onChange={
                      handleRegisterChange
                    }
                    placeholder="Confirm password"
                    autoComplete="new-password"
                  />
                </div>
              </div>

              <button
                type="submit"
                className="auth-submit"
                disabled={loading}
              >
                {loading
                  ? "Creating Account..."
                  : "Create Account"}
              </button>

              <p className="auth-switch-text">
                Already have an account?{" "}
                <button
                  type="button"
                  onClick={() =>
                    switchMode("login")
                  }
                >
                  Sign In
                </button>
              </p>
            </form>
          )}
        </section>
      </div>
    </div>
  );
}

export default AuthPage;