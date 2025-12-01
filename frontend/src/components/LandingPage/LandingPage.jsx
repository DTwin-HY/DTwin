import Header from './Header';
import HeroSection from './Hero';
import ScrollGraphSection from './ScrollGraphSection';
import DemoAdSection from './DemoAd';

const LandingPage = () => {
  return (
    <div>
      <Header />
      <HeroSection />
      <ScrollGraphSection />
      <DemoAdSection />

      <footer className="top-8 border border-slate-800 py-6">
        <div className="container mx-auto flex flex-col items-center justify-between md:flex-row">
          <div className="text-muted-foreground text-sm">
            © 2025 Digital Twin Simulation Project
          </div>
          <div className="text-sm">
            <a href="https://github.com/DTwin-HY/DTwin" target="_blank">
              GitHub Repository
            </a>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default LandingPage;
