import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/Auth';

const SignUp = () => {
  const [form, setForm] = useState({ username: '', password: '' });
  const [loading, setLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');
  const [successMessage, setSuccessMessage] = useState('');

  const { createUser } = useAuth();

  useEffect(() => {
    if (successMessage) {
      const timer = setTimeout(() => setSuccessMessage(''), 5000);
      return () => clearTimeout(timer);
    }
  }, [successMessage]);

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    const username = form.username.trim();
    const password = form.password;

    if (!username || !password) {
      setErrorMessage('Please fill in username and password');
      return;
    }

    setLoading(true);
    setErrorMessage('');
    setSuccessMessage('');

    try {
      const data = await createUser({ username, password });
      if (data.error) {
        setErrorMessage(data.error);
      } else {
        setSuccessMessage('User created, redirecting...');
        setForm({ username: '', password: '' });
      }
    } catch (err) {
      const apiErr = err?.response?.data?.error || err.message || 'Unknown error';
      setErrorMessage(apiErr);
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-[hsl(var(--background))] p-4 text-[hsl(var(--foreground))]">
      <div className="text-gradient mb-5 text-3xl font-bold">Sign up</div>

      <form
        onSubmit={handleSubmit}
        className="flex w-full max-w-md flex-col gap-4 rounded-2xl border border-[hsl(var(--accent))]/30 bg-[hsl(var(--background))]/60 p-6 shadow-lg backdrop-blur-xl"
      >
        <label className="flex flex-col gap-1">
          <span className="text-sm font-medium text-[hsl(var(--foreground))]/80">Username</span>
          <input
            type="text"
            name="username"
            value={form.username}
            onChange={handleChange}
            disabled={loading}
            className="rounded-lg border border-[hsl(var(--accent))]/40 bg-[hsl(var(--background))]/70 p-3 text-[hsl(var(--foreground))] placeholder:text-[hsl(var(--foreground))]/40 focus:ring-2 focus:ring-[hsl(var(--accent))] focus:outline-none"
            placeholder="Your username"
          />
        </label>

        <label className="flex flex-col gap-1">
          <span className="text-sm font-medium text-[hsl(var(--foreground))]/80">Password</span>
          <input
            type="password"
            name="password"
            value={form.password}
            onChange={handleChange}
            disabled={loading}
            className="rounded-lg border border-[hsl(var(--accent))]/40 bg-[hsl(var(--background))]/70 p-3 text-[hsl(var(--foreground))] placeholder:text-[hsl(var(--foreground))]/40 focus:ring-2 focus:ring-[hsl(var(--accent))] focus:outline-none"
            placeholder="Your password"
          />
        </label>

        <button
          type="submit"
          disabled={loading}
          className="rounded-lg bg-[hsl(var(--accent))] py-3 font-semibold text-[hsl(var(--accent-foreground))] shadow transition-colors duration-200 hover:bg-[hsl(var(--violet-light))] disabled:opacity-60"
        >
          {loading ? 'Creating...' : 'Sign Up'}
        </button>
      </form>

      <div className="mt-4 text-center">
        Already have an account?{' '}
        <Link to="/signin" className="text-blue-500 hover:underline">
          Sign In
        </Link>
      </div>

      {loading && (
        <div className="mt-4 w-full max-w-md rounded-lg border border-blue-300 bg-blue-100 p-4 text-blue-800 shadow">
          <p className="font-medium">Processing…</p>
        </div>
      )}

      {successMessage && !loading && !errorMessage && (
        <div className="mt-4 w-full max-w-md rounded-lg border border-green-300 bg-green-100 p-4 text-green-800 shadow">
          <p className="font-medium">{successMessage}</p>
        </div>
      )}

      {errorMessage && !loading && (
        <div className="mt-4 w-full max-w-md rounded-lg border border-red-300 bg-red-100 p-4 text-red-800 shadow">
          <p className="font-medium">{errorMessage}</p>
        </div>
      )}
    </div>
  );
};

export default SignUp;
