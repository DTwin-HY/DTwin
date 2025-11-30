import { useNavigate } from 'react-router-dom';

const DemoAdSection = () => {
  const navigate = useNavigate();

  return (
    <section className="flex min-h-[85vh] items-center justify-center">
      <div className="max-w-2xl px-6 text-center">
        <h3 className="mb-6 text-4xl font-semibold md:text-5xl">Try it yourself in the demo app</h3>

        <p className="mb-8 text-base leading-relaxed text-slate-300 md:text-lg">
          The sandbox environment uses fake company data to show how agents interact in practice.
          Explore the architecture, test what-if pricing scenarios, and understand how information
          flows across the graph.
        </p>

        <button
          onClick={() => navigate('/dashboard')}
          className="rounded-full bg-emerald-500 px-6 py-3 font-medium transition-all hover:cursor-pointer hover:bg-emerald-400"
        >
          Open Demo
        </button>
      </div>
    </section>
  );
};

export default DemoAdSection;
