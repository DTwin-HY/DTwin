import { createContext, useState, useEffect, useContext } from 'react';
import { useNavigate } from 'react-router-dom';
import { checkAuth, signin, signup, signout } from '../api/authapi';

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    const initAuth = async () => {
      try {
        const data = await checkAuth();
        setUser(data.user || null);
      } catch {
        setUser(null);
      } finally {
        setLoading(false);
      }
    };
    initAuth();
  }, []);

  const login = async (credentials) => {
    try {
      const data = await signin(credentials);
      setUser(data.user);
      navigate('/');
      return data;
    } catch (err) {
      const apiErr = err?.response?.data?.error || err.message || 'Unknown error';
      setUser(null);

      return { error: apiErr };
    }
  };

  const createUser = async (credentials) => {
    try {
      const data = await signup(credentials);
      setUser(data.user);
      navigate('/');
      return data;
    } catch (err) {
      const apiErr = err?.response?.data?.error || err.message || 'Unknown error';
      setUser(null);

      return { error: apiErr };
    }
  };

  const logout = async () => {
    try {
      await signout();
    } catch (err) {
      console.error('Logout failed', err);
    } finally {
      setUser(null);
      navigate('/signin');
    }
  };

  return (
    <AuthContext.Provider
      value={{ user, loading, login, logout, createUser, isAuthenticated: !!user }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);

export default AuthContext;
