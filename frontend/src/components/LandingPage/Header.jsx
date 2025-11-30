import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';

const Header = () => {
  const navigate = useNavigate();

  return (
    <motion.header
      initial={{ y: -100 }} // Start above screen
      animate={{ y: 0 }} // Drop down on page load
      transition={{ duration: 0.6 }} // Smooth drop
      className="fixed top-0 right-0 left-0 z-50 bg-transparent duration-300"
    >
      <div className="container mx-auto flex h-16 items-center justify-between">
        <motion.div whileHover={{ scale: 1.05 }} className="cursor-pointer">
          <span className="text-lg font-bold hover:cursor-pointer">DTwin</span>
        </motion.div>

        <motion.div whileHover={{ scale: 1.05 }}>
          <button
            onClick={() => navigate('/dashboard')}
            className="rounded-lg font-medium hover:cursor-pointer"
          >
            Explore Demo
          </button>
        </motion.div>
      </div>
    </motion.header>
  );
};

export default Header;
