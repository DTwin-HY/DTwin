import { useState, useRef, useEffect } from 'react';
import { motion, useScroll, useMotionValueEvent } from 'motion/react';
import Graph from './Graph';
import { STEPS, SCENARIO_STEPS } from './stepsData';

const ScrollGraphSection = () => {
  // --------------------
  // Scrollable text state handling
  // --------------------

  const [activeIndex, setActiveIndex] = useState(0);
  const stepsRef = useRef(null);

  const { scrollYProgress } = useScroll({
    target: stepsRef,
    offset: ['start center', 'end center'],
  });

  // --------------------
  // Example scenario animation state handling
  // --------------------

  const [isScenarioRunning, setIsScenarioRunning] = useState(false);
  const [scenarioStepIndex, setScenarioStepIndex] = useState(0);

  const isScenarioRunningRef = useRef(false);

  useEffect(() => {
    isScenarioRunningRef.current = isScenarioRunning;
  }, [isScenarioRunning]);

  // --------------------
  // Scrollable text logic
  // --------------------

  useMotionValueEvent(scrollYProgress, 'change', (latest) => {
    if (isScenarioRunningRef.current) return;

    const index = Math.min(STEPS.length - 1, Math.max(0, Math.round(latest * (STEPS.length - 1))));
    setActiveIndex(index);
  });

  // --------------------
  // Example scenario animation logic
  // --------------------

  const runScenario = () => {
    setIsScenarioRunning(true);
    setScenarioStepIndex(0);
  };

  useEffect(() => {
    if (!isScenarioRunning) return;

    const delayPerStep = 1800;

    if (scenarioStepIndex >= SCENARIO_STEPS.length) {
      setIsScenarioRunning(false);
      return;
    }

    const timeoutId = setTimeout(() => setScenarioStepIndex((prev) => prev + 1), delayPerStep);
    return () => clearTimeout(timeoutId);
  }, [isScenarioRunning, scenarioStepIndex]);

  // --------------------
  // Derived values for rendering
  // --------------------

  const activeStep = STEPS[activeIndex];

  const scenarioStep =
    scenarioStepIndex > 0 && scenarioStepIndex <= SCENARIO_STEPS.length
      ? SCENARIO_STEPS[scenarioStepIndex - 1]
      : null;

  const shownScenarioSteps =
    scenarioStepIndex > 0
      ? SCENARIO_STEPS.slice(0, Math.min(scenarioStepIndex, SCENARIO_STEPS.length))
      : [];

  const activeNodeId = isScenarioRunning && scenarioStep ? scenarioStep.nodeId : activeStep.nodeId;

  return (
    <section className="bg-bg text-text min-h-[70vh] py-28">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true }}
        transition={{ duration: 0.6 }}
        className="mb-16 text-center"
      >
        <h2 className="mb-4 text-4xl font-bold md:text-5xl">The Agent Architecture</h2>
        <p className="text-muted mx-auto max-w-2xl text-lg">
          Scroll to understand each agent, then run a pricing scenario to see how the graph behaves
          and jump into the sandbox to try it yourself.
        </p>
      </motion.div>

      <div className="mx-auto max-w-7xl gap-16 px-6 lg:grid lg:grid-cols-[minmax(0,1.3fr)_minmax(0,1fr)]">
        {/* Left side, scrollable */}
        <div>
          <div ref={stepsRef}>
            {STEPS.map((step, index) => {
              const isActive = index === activeIndex && !isScenarioRunning;
              return (
                <div key={step.id} className="flex min-h-[70vh] items-center">
                  <div
                    className={`transition-opacity duration-300 ${
                      isActive ? 'opacity-100' : 'opacity-40'
                    }`}
                  >
                    <h3 className="text-3xl font-semibold md:text-4xl">{step.title}</h3>
                    <p className="text-muted mt-4 max-w-xl leading-relaxed md:text-lg">
                      {step.body}
                    </p>
                  </div>
                </div>
              );
            })}
          </div>

          {/* Example scenario section */}
          <div className="flex min-h-[70vh] items-center">
            <div className="max-w-xl rounded-3xl px-5 py-6">
              <p className="text-accent text-xs font-semibold uppercase">Example scenario</p>
              <h3 className="mt-3 text-2xl font-semibold">
                “If I raise this product’s price by
                <span className="text-accent font-semibold">10%</span>, how much revenue do we
                make?”
              </h3>

              <div className="mt-4 flex flex-wrap items-center gap-3 text-xs">
                <button
                  type="button"
                  onClick={runScenario}
                  disabled={isScenarioRunning}
                  className={`text-gradient inline-flex items-center gap-1 rounded-full border border-[hsl(var(--accent))] px-4 py-2 font-medium transition ${
                    isScenarioRunning
                      ? 'bg-surface text-muted cursor-not-allowed'
                      : 'bg-accent text-bg hover:bg-accent-hover'
                  }`}
                >
                  {isScenarioRunning ? (
                    <>
                      <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-emerald-300" />
                      Running pricing scenario…
                    </>
                  ) : scenarioStepIndex > 0 ? (
                    <>
                      <span className="h-1.5 w-1.5 rounded-full bg-emerald-300" />
                      Replay pricing scenario
                    </>
                  ) : (
                    <>
                      <span className="h-1.5 w-1.5 rounded-full bg-emerald-300" />
                      Run pricing scenario
                    </>
                  )}
                </button>
              </div>

              {/* Example scenario steps */}
              {shownScenarioSteps.length > 0 && (
                <div className="mt-4 space-y-3">
                  {shownScenarioSteps.map((step, index) => (
                    <div key={step.id} className="rounded-2xl py-3">
                      <div className="mb-1 flex items-center justify-between gap-3">
                        <span className="text-accent font-semibold uppercase">
                          Phase {index + 1}
                        </span>
                        <span className="text-muted">
                          {index + 1} / {SCENARIO_STEPS.length}
                        </span>
                      </div>
                      <p>{step.caption}</p>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Right side, graph */}
        <div className="h-[420px] sm:h-[500px] md:h-[560px] lg:sticky lg:top-40 lg:h-[640px]">
          <Graph activeNodeId={activeNodeId} />
        </div>
      </div>
    </section>
  );
};

export default ScrollGraphSection;
