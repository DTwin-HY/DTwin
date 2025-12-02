import { useContext, useEffect } from 'react';
import { Outlet, useNavigate, useLocation } from 'react-router-dom';
import AuthContext from '../context/Auth';

const Layout = () => {
  const { logout, loading, user } = useContext(AuthContext);
  const navigate = useNavigate();
  const location = useLocation();
  
  const isDashboard = location.pathname === '/dashboard';

  useEffect(() => {
    const isDashboard = location.pathname === '/dashboard';

    document.body.style.backgroundColor = isDashboard ? '#ffffff' : '';
    document.documentElement.style.backgroundColor = isDashboard ? '#ffffff' : '';

    return () => {
      document.body.style.backgroundColor = '';
      document.documentElement.style.backgroundColor = '';
    };
  }, [location.pathname]);


  return (
    <div className="flex min-h-screen flex-col" style={isDashboard ? { backgroundColor: '#ffffff' } : {}}>
      <header className="flex items-center justify-between px-6 py-4 shadow" style={isDashboard ? { backgroundColor: '#ffffff' } : {}}>
        <h1
          className={isDashboard ? 'text-xl font-bold hover:cursor-pointer hover:opacity-70' : 'text-gradient text-xl font-bold hover:cursor-pointer hover:opacity-70'}
          style={isDashboard ? { color: '#1f2937' } : {}}
          onClick={() => navigate('/')}
        >
          DTwin
        </h1>
        {user && (
          <div className="flex gap-4">
            <button
              onClick={logout}
              className="rounded-lg border px-4 py-2 transition-colors hover:cursor-pointer hover:opacity-70"
              style={isDashboard ? { 
                borderColor: '#d1d5db', 
                color: '#1f2937',
                backgroundColor: 'transparent'
              } : {
                borderColor: 'hsl(var(--accent))'
              }}
            >
              Logout
            </button>
          </div>
        )}
      </header>
      <main className="flex-1" style={isDashboard ? { backgroundColor: '#ffffff' } : {}}>
        {loading ? (
          <div className="flex h-full items-center justify-center" style={isDashboard ? { color: '#1f2937' } : {}}>Loading...</div>
        ) : (
          <Outlet />
        )}
      </main>
      <footer className="p-4 text-center" style={isDashboard ? { backgroundColor: '#ffffff', color: '#6b7280' } : {}}>
        &copy; {new Date().getFullYear()} DTwin
      </footer>
    </div>
  );
};

export default Layout;
