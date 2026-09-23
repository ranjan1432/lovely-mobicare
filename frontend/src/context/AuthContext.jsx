import {
  createContext,
  useContext,
  useEffect,
  useState,
} from "react";
import axios from "axios";

const AuthContext = createContext(null);

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ||
  "http://127.0.0.1:8000/api";

const TOKEN_KEY = "lovelyMobiCareToken";

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(
    () => localStorage.getItem(TOKEN_KEY)
  );
  const [authLoading, setAuthLoading] = useState(true);

  const getAuthHeaders = (authToken = token) => ({
    Authorization: `Token ${authToken}`,
  });

  const loadUser = async (authToken) => {
    if (!authToken) {
      setUser(null);
      setAuthLoading(false);
      return;
    }

    try {
      const response = await axios.get(
        `${API_BASE_URL}/accounts/me/`,
        {
          headers: getAuthHeaders(authToken),
        }
      );

      setUser(response.data);
    } catch (error) {
      localStorage.removeItem(TOKEN_KEY);
      setToken(null);
      setUser(null);
    } finally {
      setAuthLoading(false);
    }
  };

  useEffect(() => {
    loadUser(token);
  }, [token]);

  const login = async (email, password) => {
    const response = await axios.post(
      `${API_BASE_URL}/accounts/login/`,
      {
        email,
        password,
      }
    );

    const newToken = response.data.token;

    localStorage.setItem(TOKEN_KEY, newToken);
    setToken(newToken);

    if (response.data.user) {
      setUser(response.data.user);
    } else {
      await loadUser(newToken);
    }

    return response.data;
  };

  const register = async (formData) => {
    const response = await axios.post(
      `${API_BASE_URL}/accounts/register/`,
      formData
    );

    const newToken = response.data.token;

    if (newToken) {
      localStorage.setItem(TOKEN_KEY, newToken);
      setToken(newToken);

      if (response.data.user) {
        setUser(response.data.user);
      } else {
        await loadUser(newToken);
      }
    }

    return response.data;
  };

  const logout = async () => {
    try {
      if (token) {
        await axios.post(
          `${API_BASE_URL}/accounts/logout/`,
          {},
          {
            headers: getAuthHeaders(token),
          }
        );
      }
    } catch (error) {
      console.error("Logout error:", error);
    } finally {
      localStorage.removeItem(TOKEN_KEY);
      setToken(null);
      setUser(null);
    }
  };

  const value = {
    user,
    token,
    authLoading,
    isAuthenticated: Boolean(token && user),
    login,
    register,
    logout,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);

  if (!context) {
    throw new Error(
      "useAuth must be used inside AuthProvider"
    );
  }

  return context;
}

export default AuthContext;