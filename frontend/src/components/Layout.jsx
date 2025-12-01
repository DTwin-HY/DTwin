import { useContext } from 'react';
import { Outlet, useNavigate } from 'react-router-dom';
import AuthContext from '../context/Auth';

const Layout = () => {
  const { logout, loading, user } = useContext(AuthContext);
  const navigate = useNavigate();

  return (
    <div className="flex min-h-screen flex-col">
      <header className="flex items-center justify-between px-6 py-4 shadow">
        <h1
          className="text-gradient text-xl font-bold hover:cursor-pointer hover:opacity-70"
          onClick={() => navigate('/')}
        >
          DTwin
        </h1>
        {user && (
          <div className="flex gap-4">
            <button
              onClick={logout}
              className="rounded-lg border border-[hsl(var(--accent))] px-4 py-2 transition-colors hover:cursor-pointer hover:bg-black hover:opacity-70"
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
