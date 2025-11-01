import { useState } from 'react';
import Chatbot from './Chatbot';
import InfoPanel from './InfoPanel';
import SalesCard from './SalesCard';

const Home = () => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
      <div className="w-full">
        <InfoPanel />
      </div>

      <div className="mx-auto px-4 py-6 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
          <div className="space-y-6 lg:col-span-1">
            <SalesCard className="h-full w-full" />
          </div>

          <div className="lg:col-span-1">
            <div className="sticky">
              <Chatbot />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Home;
