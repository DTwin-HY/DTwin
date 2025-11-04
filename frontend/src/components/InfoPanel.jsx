import { useState } from 'react';
import { Info, ChevronUp, Sparkles } from 'lucide-react';

const InfoPanel = () => {
  const [isExpanded, setIsExpanded] = useState(false);

  return (
    <div className="p-5 px-10">
      <div
        className={`bg-white shadow-md transition-all duration-300 ${
          isExpanded ? 'rounded-t-xl' : 'rounded-xl'
        }`}
      >
        <button
          onClick={() => setIsExpanded(!isExpanded)}
          className="flex w-full items-center justify-between px-6 py-4 text-left transition-all hover:brightness-110"
        >
          <div className="flex items-center gap-3">
            <Sparkles className="h-6 w-6" />
            <div>
              <h1 className="text-xl font-bold">Digital Twin — Company Supervisor</h1>
            </div>
          </div>
          <div className="rounded-full bg-white/20 p-2 transition-transform duration-300">
            {isExpanded ? <ChevronUp className="h-5 w-5" /> : <Info className="h-5 w-5" />}
          </div>
        </button>
      </div>

      <div
        className={`overflow-hidden bg-white transition-all duration-300 ${
          isExpanded ? 'max-h-[600px] opacity-100' : 'max-h-0 opacity-0'
        }`}
      >
        <div className="rounded-b-2xl p-6 shadow-lg">
          <p className="text-gray-600">
            This interface lets you talk to a supervisor AI that coordinates specialised agents
            (sales, warehouse, research) to answer questions, run reports, and act as a real-time
            dashboard for your company.
          </p>
        </div>
      </div>
    </div>
  );
};

export default InfoPanel;
