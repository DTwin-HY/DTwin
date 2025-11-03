import Chatbot from './Chatbot';
import InfoPanel from './InfoPanel';
import SalesCard from './SalesCard';

const Home = () => {
  return (
    <div className="bg-gray-100">
      <div className="w-full">
        <InfoPanel />
      </div>

      <div className="mx-auto grid grid-cols-1 px-4 sm:px-6 lg:grid-cols-2 lg:px-8 lg:py-6">
        <div className="lg:col-span-1">
          <SalesCard className="h-full w-full" />
        </div>

        <div className="lg:col-span-1">
          <div className="lg:sticky">
            <Chatbot />
          </div>
        </div>
      </div>
    </div>
  );
};

export default Home;
