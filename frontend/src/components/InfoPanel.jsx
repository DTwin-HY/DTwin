import { useState } from 'react';
import { Info, ChevronUp, Sparkles } from 'lucide-react';

const InfoPanel = () => {
  const [isExpanded, setIsExpanded] = useState(true);

  return (
    <div className="p-5">
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
        className={`overflow-hidden transition-all duration-300 ${
          isExpanded ? 'max-h-[600px] opacity-100' : 'max-h-0 opacity-0'
        }`}
      >
        <div className="rounded-b-2xl p-6 shadow-lg">
          <p className="text-gray-600">
            This interface lets you talk to a supervisor AI that coordinates specialised agents
            (sales, warehouse, research) to answer questions, run reports, and act as a real-time
            dashboard for your company.
          </p>

          <div className="mt-6 grid grid-cols-1 gap-4 sm:grid-cols-3">
            <div className="rounded-xl border border-indigo-100 bg-gradient-to-br from-indigo-50 to-white p-4 transition-all hover:shadow-md">
              <div className="text-xs font-semibold tracking-wide text-indigo-600 uppercase">
                What it does
              </div>
              <div className="mt-2 text-sm text-gray-700">
                Answer questions, generate reports, and surface live key metrics.
              </div>
            </div>
            <div className="rounded-xl border border-purple-100 bg-gradient-to-br from-purple-50 to-white p-4 transition-all hover:shadow-md">
              <div className="text-xs font-semibold tracking-wide text-purple-600 uppercase">
                How to use
              </div>
              <div className="mt-2 text-sm text-gray-700">
                Type a question to the supervisor, or use the sample prompts below.
              </div>
            </div>
            <div className="rounded-xl border border-blue-100 bg-gradient-to-br from-blue-50 to-white p-4 transition-all hover:shadow-md">
              <div className="text-xs font-semibold tracking-wide text-blue-600 uppercase">
                Data freshness
              </div>
              <div className="mt-2 text-sm text-gray-700">
                Sales and warehouse tiles update in real time (SSE). Chat history is saved.
              </div>
            </div>
          </div>

          <div className="mt-6 rounded-xl border border-gray-200 bg-gray-50 p-4">
            <div className="text-xs font-semibold tracking-wide text-gray-600 uppercase">
              Quick prompts
            </div>
            <div className="mt-3 flex flex-wrap gap-2">
              {[
                'Show me revenue and orders for today',
                'Which products are low in stock?',
                'Create a short sales summary for the last 24h',
                'Find top return reasons in the last 30 days',
              ].map((p) => (
                <button
                  key={p}
                  type="button"
                  onClick={() =>
                    window.dispatchEvent(new CustomEvent('example-prompt', { detail: p }))
                  }
                  className="rounded-full bg-white px-4 py-2 text-sm text-gray-700 shadow-sm transition-all hover:scale-105 hover:bg-indigo-50 hover:text-indigo-700 hover:shadow-md"
                >
                  {p}
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default InfoPanel;
