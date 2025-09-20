import { Routes, Route } from 'react-router-dom';
import Home from './components/Home';
import SignUp from './components/SignUp';
import Login from './components/SignIn';
import PrivateRoute from './components/PrivateRoute';
import GuestRoute from './components/GuestRoute';
import Layout from './components/Layout';

const App = () => {
  return (
    <Routes>
      <Route path="/" element={<Layout />}>
        <Route element={<PrivateRoute />}>
          <Route index element={<Home />} />
        </Route>
        <Route element={<GuestRoute />}>
          <Route path="/signin" element={<Login />} />
          <Route path="/signup" element={<SignUp />} />
        </Route>
      </Route>
    </Routes>
  );
};

export default App;
