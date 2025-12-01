import Chatbot from './Chatbot';
import Dashboard from './Dashboard';

const Home = () => {
  return (
    <div className="flex min-h-screen flex-col items-center">
      <div className="w-full max-w-[1500px] px-4 py-4 sm:px-6 lg:px-8">
        <Dashboard />
      </div>

      <div className="w-full max-w-[1500px] px-4 py-4 sm:px-6 lg:px-8">
        <Chatbot />
      </div>
    </div>
  );
};

export default Home;
