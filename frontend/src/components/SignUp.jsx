import { useState, useEffect, useContext } from 'react';
import '../index.css';
import { signup } from '../api/auth';
import { Link } from 'react-router-dom';
import AuthContext from './Auth';

const SignUp = () => {
  const [form, setForm] = useState({ username: '', password: '' });
  const [loading, setLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');
  const [successMessage, setSuccessMessage] = useState('');
  const { login } = useContext(AuthContext);

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
      setErrorMessage('Täytä käyttäjänimi ja salasana.');
      return;
    }

    setLoading(true);
    setErrorMessage('');
    setSuccessMessage('');

    try {
      const data = await signup({ username, password });
      if (data?.error) {
        setErrorMessage(data.error);
        return;
      }
      setSuccessMessage('Käyttäjä luotu!');
      setForm({ username: '', password: '' });
      login();
    } catch (err) {
      const apiErr = err?.response?.data?.error || err.message || 'Tuntematon virhe';
      setErrorMessage(apiErr);
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-gray-100 p-4">
      <img src="/vttlogo.png" alt="Logo" className="mb-5 ml-[45px] h-35 w-85 rounded-full" />
      <div className="mb-5 text-3xl font-bold">Sign up</div>

      <form
        onSubmit={handleSubmit}
        className="flex w-full max-w-md flex-col gap-4 rounded-xl bg-white p-6 shadow-md"
      >
        <label className="flex flex-col gap-1">
          <span className="text-sm font-medium text-gray-700">Username</span>
          <input
            type="text"
            name="username"
            value={form.username}
            onChange={handleChange}
            disabled={loading}
            className="rounded-lg border border-gray-300 p-3 focus:ring-2 focus:ring-blue-500 focus:outline-none"
            placeholder="Your username"
          />
        </label>

        <label className="flex flex-col gap-1">
          <span className="text-sm font-medium text-gray-700">Password</span>
          <input
            type="password"
            name="password"
            value={form.password}
            onChange={handleChange}
            disabled={loading}
            className="rounded-lg border border-gray-300 p-3 focus:ring-2 focus:ring-blue-500 focus:outline-none"
            placeholder="Your password"
          />
        </label>

        <button
          type="submit"
          disabled={loading}
          className="rounded-lg bg-blue-500 py-3 font-semibold text-white shadow transition-colors duration-200 hover:bg-blue-600 disabled:opacity-60"
        >
          {loading ? 'Creating...' : 'Sign Up'}
        </button>
      </form>

      <div className="mt-4 text-center">
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
