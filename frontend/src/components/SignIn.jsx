// src/pages/SignIn.jsx
import { useState, useEffect, useContext } from "react";
import "../index.css";
import { signin } from "../api/auth";
import { Link } from "react-router-dom";
import AuthContext from "./Auth";

const SignIn = () => {
  const [form, setForm] = useState({ username: "", password: "" });
  const [loading, setLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");
  const [successMessage, setSuccessMessage] = useState("");
  const { login } = useContext(AuthContext);

  useEffect(() => {
    if (successMessage) {
      const t = setTimeout(() => setSuccessMessage(""), 5000);
      return () => clearTimeout(t);
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
      setErrorMessage("Täytä käyttäjänimi ja salasana.");
      return;
    }

    setLoading(true);
    setErrorMessage("");
    setSuccessMessage("");

    try {
      const data = await signin({ username, password });
      if (data?.error) {
        setErrorMessage(data.error);
        return;
      }
      setSuccessMessage("Kirjautuminen onnistui!");
      setForm({ username: "", password: "" });
      login();

    } catch (err) {
      const apiErr = err?.response?.data?.error || err.message || "Tuntematon virhe";
      setErrorMessage(apiErr);
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-gray-100 p-4">
    <img
        src="/vttlogo.png"
        alt="Logo"
        className="w-85 h-35 mb-5 ml-[45px] rounded-full"
    />
      <div className="text-3xl font-bold mb-5">Sign in</div>

      <form
        onSubmit={handleSubmit}
        className="flex flex-col gap-4 w-full max-w-md bg-white p-6 rounded-xl shadow-md"
      >
        <label className="flex flex-col gap-1">
          <span className="text-sm font-medium text-gray-700">Username</span>
          <input
            type="text"
            name="username"
            value={form.username}
            onChange={handleChange}
            required
            disabled={loading}
            className="border border-gray-300 rounded-lg p-3 focus:outline-none focus:ring-2 focus:ring-blue-500"
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
            required
            disabled={loading}
            className="border border-gray-300 rounded-lg p-3 focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Your password"
          />
        </label>

        <button
          type="submit"
          disabled={loading}
          className="bg-blue-500 text-white font-semibold py-3 rounded-lg shadow hover:bg-blue-600 transition-colors duration-200 disabled:opacity-60"
        >
          {loading ? "Signing in..." : "Sign In"}
        </button>
      </form>

      <div className="mt-4 text-center">
        <Link to="/signup" className="text-blue-500 hover:underline">Sign Up</Link>
      </div>

      {loading && (
        <div className="mt-4 w-full max-w-md p-4 rounded-lg border border-blue-300 bg-blue-100 text-blue-800 shadow">
          <p className="font-medium">Processing…</p>
        </div>
      )}

      {successMessage && !loading && !errorMessage && (
        <div className="mt-4 w-full max-w-md p-4 rounded-lg border border-green-300 bg-green-100 text-green-800 shadow">
          <p className="font-medium">{successMessage}</p>
        </div>
      )}

      {errorMessage && !loading && (
        <div className="mt-4 w-full max-w-md p-4 rounded-lg border border-red-300 bg-red-100 text-red-800 shadow">
          <p className="font-medium">{errorMessage}</p>
        </div>
      )}
    </div>
  );
};

export default SignIn;
