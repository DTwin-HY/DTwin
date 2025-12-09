import { motion as Motion } from 'framer-motion';
import Chatbot from './Chatbot';
import Dashboard from './Dashboard';

const Home = () => {
  return (
    <Motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, ease: 'easeOut' }}
      className="flex min-h-screen flex-col items-center"
      style={{ backgroundColor: '#ffffff', minHeight: '100vh' }}
    >
      <div className="w-full max-w-[1500px] px-4 py-4 sm:px-6 lg:px-8">
        <Dashboard />
      </div>

      <div className="min-h-[60vh] w-full max-w-[1500px] px-4 py-4 sm:px-6 lg:px-8">
        <Chatbot />
      </div>
    </Motion.div>
  );
};

export default Home;
