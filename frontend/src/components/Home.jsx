import Chatbot from './Chatbot';
import InfoPanel from './InfoPanel';
import Dashboard from './Dashboard';

const Home = () => {
  return (
    <div className="bg-gray-100 min-h-screen flex flex-col items-center">
      <div className="w-full max-w-[1500px] px-4 sm:px-6 lg:px-8">
        <InfoPanel />
      </div>

      <div className="mx-auto grid grid-cols-1 px-4 sm:px-6">
        <div className="lg:col-span-1">
        </div>

        <div className="lg:col-span-1">
          <div>
            <Dashboard />
          </div>
          <div className="lg:sticky">
            <Chatbot />
          </div>
        </div>
      </div>
    </div>
  );
};

export default Home;
