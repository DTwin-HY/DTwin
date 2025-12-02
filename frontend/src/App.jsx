import { Routes, Route } from 'react-router-dom';
import SignUp from './components/SignUp';
import Login from './components/SignIn';
import PrivateRoute from './components/PrivateRoute';
import GuestRoute from './components/GuestRoute';
import Layout from './components/Layout';
import Home from './components/Home';
import LandingPage from './components/LandingPage/LandingPage';

const App = () => {
  return (
    <Routes>
      <Route path="/" element={<LandingPage />} />

      <Route element={<GuestRoute />}>
        <Route path="/signin" element={<Login />} />
        <Route path="/signup" element={<SignUp />} />
      </Route>

      <Route path="/dashboard" element={<Layout />}>
        <Route element={<PrivateRoute />}>
          <Route index element={<Home />} />
        </Route>
      </Route>
    </Routes>
  );
};

export default App;
