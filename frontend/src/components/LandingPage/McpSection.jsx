import { motion as Motion } from 'framer-motion';
import { Network } from 'lucide-react';

const McpSection = () => {
  return (
    <section className="relative z-10 overflow-hidden bg-[hsl(var(--background))] py-24">
      <div className="relative mx-auto max-w-4xl px-6 text-center">
        <Motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
        >
          <div className="mb-6 flex justify-center">
            <div className="rounded-full bg-indigo-500/10 p-4 text-indigo-400 ring-1 ring-indigo-500/20 shadow-[0_0_20px_-5px_rgba(99,102,241,0.3)]">
              <Network className="h-8 w-8" />
            </div>
          </div>

          <h2 className="mb-6 text-3xl font-bold md:text-4xl">
            Powered by Model Context Protocol
          </h2>

          <p className="mx-auto max-w-2xl text-lg leading-relaxed text-slate-300">
            Our system utilizes the{' '}
            <span className="font-medium text-indigo-400">
              Model Context Protocol (MCP)
            </span>{' '}
            to standardize how agents access external data. Whether fetching weather
            forecasts or querying the database, MCP ensures our LLMs receive
            structured, secure, and relevant context for every decision.
          </p>
        </Motion.div>
      </div>
    </section>
  );
};

export default McpSection;
