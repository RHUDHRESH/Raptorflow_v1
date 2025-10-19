export const card = {
  initial: { 
    opacity: 0, 
    y: 8, 
    filter: 'blur(4px)' 
  },
  animate: { 
    opacity: 1, 
    y: 0, 
    filter: 'blur(0px)', 
    transition: { 
      duration: 0.22, 
      ease: [0.22, 0.61, 0.36, 1] 
    } 
  },
  exit: { 
    opacity: 0, 
    y: -6, 
    transition: { 
      duration: 0.16, 
      ease: [0.34, 1.56, 0.64, 1] 
    } 
  }
};

export const hoverLift = {
  whileHover: { 
    y: -2, 
    scale: 1.01, 
    transition: { duration: 0.12 } 
  }
};

export const staggerContainer = {
  animate: {
    transition: {
      staggerChildren: 0.08,
      delayChildren: 0.1
    }
  }
};

export const fadeInUp = {
  initial: { opacity: 0, y: 20 },
  animate: { 
    opacity: 1, 
    y: 0,
    transition: { duration: 0.3 }
  }
};

export const scaleIn = {
  initial: { scale: 0.95, opacity: 0 },
  animate: { 
    scale: 1, 
    opacity: 1,
    transition: { duration: 0.2 }
  }
};

export const slideIn = {
  initial: { x: -20, opacity: 0 },
  animate: { 
    x: 0, 
    opacity: 1,
    transition: { duration: 0.3 }
  }
};

// BASE UI COMPONENTS
