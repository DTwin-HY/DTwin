import { useContext } from "react";
import { Navigate } from "react-router-dom";
import AuthContext from "./Auth";

const GuestRoute = ({ children }) => {
    const { isAuthenticated, loading } = useContext(AuthContext);
    if (loading) return <div className="flex items-center justify-center min-h-screen">Loading...</div>;
    if (isAuthenticated) return <Navigate to="/" />;
    return children;
};

export default GuestRoute
