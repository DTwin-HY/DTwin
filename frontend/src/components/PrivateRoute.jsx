import { useContext } from 'react';
import { Navigate, Outlet } from 'react-router-dom';
import AuthContext from '../context/Auth';

const PrivateRoute = () => {
  const { isAuthenticated, loading } = useContext(AuthContext);

  if (loading)
    return <div className="flex min-h-screen items-center justify-center">Loading...</div>;

  return isAuthenticated ? <Outlet /> : <Navigate to="/signin" replace />;
};

export default PrivateRoute;
