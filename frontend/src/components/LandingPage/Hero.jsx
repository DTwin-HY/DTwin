import { motion as Motion, useScroll, useTransform } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { Sparkles, ArrowDown } from 'lucide-react';

const HeroSection = () => {
  const { scrollYProgress } = useScroll();
  const navigate = useNavigate();

  const heroOpacity = useTransform(scrollYProgress, [0, 0.3], [1, 0]);
  const heroY = useTransform(scrollYProgress, [0, 0.3], [0, -100]);

  return (
    <div>
      <section className="min-h-screen">
        <Motion.div style={{ opacity: heroOpacity, y: heroY }}>
          <div className="mx-auto max-w-5xl py-44 text-center">
            <Motion.div
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.8, delay: 0.2 }}
              className="mb-8 inline-flex items-center gap-2 rounded-full border px-5 py-2.5"
            >
              <Sparkles className="h-4 w-4" />
              <span className="text-sm font-medium">
                Research Project • LangGraph Multi-Agent System
              </span>
            </Motion.div>

            <Motion.h1
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 1, delay: 0.3 }}
              className="mb-8 text-6xl leading-tight font-black tracking-tight md:text-7xl lg:text-8xl"
            >
              <span className="text-gradient">Multi-Agent Business Simulation</span>
            </Motion.h1>

            <Motion.p
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 1, delay: 0.4 }}
              className="mx-auto mb-12 max-w-3xl text-xl leading-relaxed md:text-2xl"
            >
              A student-built prototype that demonstrates how autonomous agents can model company
              dynamics, simulate strategic choices, and visualize their results in real time.
            </Motion.p>

            <Motion.div
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 1, delay: 0.5 }}
              className="gap-4 sm:flex-row"
            >
              <button
                onClick={() => navigate('/dashboard')}
                className="text-gradient gap-2 rounded-full border border-[hsl(var(--accent))] px-6 py-2 text-lg font-semibold hover:cursor-pointer hover:opacity-60"
              >
                Explore Demo
              </button>
            </Motion.div>

            <Motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 1, delay: 1 }}
              className="mt-16 flex flex-col items-center text-gray-200"
            >
              <span className="mb-3 text-sm uppercase">Agent Architecture</span>
              <Motion.div
                animate={{ y: [0, 8, 0] }}
                transition={{ repeat: Infinity, duration: 1.5, ease: 'easeInOut' }}
              >
                <ArrowDown className="h-5 w-5" />
              </Motion.div>
            </Motion.div>
          </div>
        </Motion.div>
      </section>
    </div>
  );
};

export default HeroSection;
