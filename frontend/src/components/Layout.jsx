import { useContext } from 'react';
import { Outlet, useNavigate } from 'react-router-dom';
import AuthContext from '../context/Auth';

const Layout = () => {
  const { logout, loading, user } = useContext(AuthContext);
  const navigate = useNavigate();

  return (
    <div className="flex min-h-screen flex-col">
      <header className="flex items-center justify-between px-6 py-4 text-white shadow">
        <h1
          className="text-xl font-bold text-black hover:cursor-pointer"
          onClick={() => navigate('/')}
        >
          DTwin
        </h1>
        {user && (
          <div className="flex gap-4">
            <button
              onClick={() => navigate('/chatbot')}
              className="rounded-lg bg-black px-4 py-2 transition-colors hover:cursor-pointer hover:border hover:bg-white hover:text-black"
            >
              Ask AI
            </button>
            <button
              onClick={logout}
              className="rounded-lg border px-4 py-2 text-black transition-colors hover:cursor-pointer hover:bg-black hover:text-white"
            >
              Logout
            </button>
          </div>
        )}
      </header>
      <main className="flex-1">
        {loading ? (
          <div className="flex h-full items-center justify-center">Loading...</div>
        ) : (
          <Outlet />
        )}
      </main>
      <footer className="p-4 text-center">&copy; {new Date().getFullYear()} DTwin</footer>{' '}
    </div>
  );
};

export default Layout;
