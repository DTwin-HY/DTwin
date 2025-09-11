import { Routes, Route } from 'react-router-dom'
import Home from './components/Home'
import SignUp from './components/SignUp'
import Login from './components/SignIn'
import PrivateRoute from './components/PrivateRoute'
import GuestRoute from './components/GuestRoute'
import "./index.css";


const App = () => {
  return (
    <Routes>
      <Route path="/" element={<PrivateRoute><Home /></PrivateRoute>} />
      <Route path="/signin" element={<GuestRoute><Login /></GuestRoute>} />
      <Route path="/signup" element={<GuestRoute><SignUp /></GuestRoute>} />
    </Routes>
  );
};

export default App;
