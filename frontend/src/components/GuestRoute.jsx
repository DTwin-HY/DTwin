import { useContext } from 'react';
import { Navigate } from 'react-router-dom';
import AuthContext from './Auth';

const GuestRoute = ({ children }) => {
  const { isAuthenticated, loading } = useContext(AuthContext);
  if (loading)
    return <div className="flex min-h-screen items-center justify-center">Loading...</div>;
  if (isAuthenticated) return <Navigate to="/" replace />;
  return children;
};

export default GuestRoute;
