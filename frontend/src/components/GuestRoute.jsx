import { useContext } from 'react';
import { Navigate, Outlet } from 'react-router-dom';
import AuthContext from '../context/Auth';

const GuestRoute = () => {
  const { isAuthenticated, loading } = useContext(AuthContext);

  if (loading)
    return <div className="flex min-h-screen items-center justify-center">Loading...</div>;

  return !isAuthenticated ? <Outlet /> : <Navigate to="/" replace />;
};

export default GuestRoute;
