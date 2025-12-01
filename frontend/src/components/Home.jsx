import Chatbot from './Chatbot';
import Dashboard from './Dashboard';

const Home = () => {
  return (
    <div className="bg-gray-100 min-h-screen flex flex-col items-center">
      <div className="w-full max-w-[1500px] px-4 sm:px-6 lg:px-8 py-4">
        <Dashboard />
      </div>

      <div className="w-full max-w-[1500px] px-4 sm:px-6 lg:px-8 py-4">
        <Chatbot />
      </div>
    </div>
  );
};

export default Home;