/**
 * Animated Container Components
 * Reusable wrapper components with Framer Motion animations
 */

'use client';

import React, { ReactNode } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import * as AnimConfig from '@/lib/animation-config';

/**
 * Fade In Container
 */
export const FadeInContainer = React.forwardRef<
  HTMLDivElement,
  {
    children: ReactNode;
    delay?: number;
    duration?: number;
    className?: string;
  }
>(({ children, delay = 0, duration = 0.3, className = '' }, ref) => (
  <motion.div
    ref={ref}
    initial={{ opacity: 0 }}
    animate={{ opacity: 1 }}
    exit={{ opacity: 0 }}
    transition={{ duration, delay }}
    className={className}
  >
    {children}
  </motion.div>
));

FadeInContainer.displayName = 'FadeInContainer';

/**
 * Scale In Container
 */
export const ScaleInContainer = React.forwardRef<
  HTMLDivElement,
  {
    children: ReactNode;
    delay?: number;
    duration?: number;
    scale?: number;
    className?: string;
  }
>(({ children, delay = 0, duration = 0.3, scale = 0.95, className = '' }, ref) => (
  <motion.div
    ref={ref}
    initial={{ opacity: 0, scale }}
    animate={{ opacity: 1, scale: 1 }}
    exit={{ opacity: 0, scale }}
    transition={{ duration, delay }}
    className={className}
  >
    {children}
  </motion.div>
));

ScaleInContainer.displayName = 'ScaleInContainer';

/**
 * Slide In Container (from left)
 */
export const SlideInContainer = React.forwardRef<
  HTMLDivElement,
  {
    children: ReactNode;
    delay?: number;
    duration?: number;
    direction?: 'left' | 'right' | 'up' | 'down';
    distance?: number;
    className?: string;
  }
>(
  (
    {
      children,
      delay = 0,
      duration = 0.3,
      direction = 'left',
      distance = 20,
      className = '',
    },
    ref
  ) => {
    const getInitial = () => {
      switch (direction) {
        case 'right':
          return { opacity: 0, x: distance };
        case 'up':
          return { opacity: 0, y: distance };
        case 'down':
          return { opacity: 0, y: -distance };
        default:
          return { opacity: 0, x: -distance };
      }
    };

    return (
      <motion.div
        ref={ref}
        initial={getInitial()}
        animate={{ opacity: 1, x: 0, y: 0 }}
        exit={getInitial()}
        transition={{ duration, delay }}
        className={className}
      >
        {children}
      </motion.div>
    );
  }
);

SlideInContainer.displayName = 'SlideInContainer';

/**
 * Stagger Container (animates children sequentially)
 */
export const StaggerContainer = React.forwardRef<
  HTMLDivElement,
  {
    children: ReactNode;
    staggerDelay?: number;
    delayChildren?: number;
    className?: string;
  }
>(({ children, staggerDelay = 0.05, delayChildren = 0, className = '' }, ref) => (
  <motion.div
    ref={ref}
    variants={{
      hidden: { opacity: 0 },
      visible: {
        opacity: 1,
        transition: {
          staggerChildren: staggerDelay,
          delayChildren,
        },
      },
    }}
    initial="hidden"
    animate="visible"
    className={className}
  >
    {children}
  </motion.div>
));

StaggerContainer.displayName = 'StaggerContainer';

/**
 * Stagger Item (use inside StaggerContainer)
 */
export const StaggerItem = React.forwardRef<
  HTMLDivElement,
  {
    children: ReactNode;
    className?: string;
  }
>(({ children, className = '' }, ref) => (
  <motion.div
    ref={ref}
    variants={{
      hidden: { opacity: 0, y: 10 },
      visible: {
        opacity: 1,
        y: 0,
        transition: { duration: 0.3 },
      },
    }}
    className={className}
  >
    {children}
  </motion.div>
));

StaggerItem.displayName = 'StaggerItem';

/**
 * Modal Container (backdrop + content)
 */
export const ModalContainer = React.forwardRef<
  HTMLDivElement,
  {
    isOpen: boolean;
    onClose: () => void;
    children: ReactNode;
    className?: string;
  }
>(({ isOpen, onClose, children, className = '' }, ref) => (
  <AnimatePresence>
    {isOpen && (
      <motion.div
        ref={ref}
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        transition={{ duration: 0.2 }}
        onClick={onClose}
        className={`fixed inset-0 bg-black/50 z-40 ${className}`}
      >
        <motion.div
          initial={{ opacity: 0, scale: 0.9, y: 20 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.9, y: 20 }}
          transition={{ duration: 0.3 }}
          onClick={(e) => e.stopPropagation()}
          className="fixed top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 z-50"
        >
          {children}
        </motion.div>
      </motion.div>
    )}
  </AnimatePresence>
));

ModalContainer.displayName = 'ModalContainer';

/**
 * Expandable/Collapsible Container
 */
export const AccordionContainer = React.forwardRef<
  HTMLDivElement,
  {
    isExpanded: boolean;
    children: ReactNode;
    duration?: number;
    className?: string;
  }
>(({ isExpanded, children, duration = 0.3, className = '' }, ref) => (
  <motion.div
    ref={ref}
    initial={false}
    animate={{ height: isExpanded ? 'auto' : 0, opacity: isExpanded ? 1 : 0 }}
    transition={{ duration }}
    overflow="hidden"
    className={className}
  >
    <div className="overflow-hidden">{children}</div>
  </motion.div>
));

AccordionContainer.displayName = 'AccordionContainer';

/**
 * Tab Content Container (fade between tabs)
 */
export const TabContainer = React.forwardRef<
  HTMLDivElement,
  {
    isActive: boolean;
    children: ReactNode;
    duration?: number;
    className?: string;
  }
>(({ isActive, children, duration = 0.2, className = '' }, ref) => (
  <AnimatePresence mode="wait">
    {isActive && (
      <motion.div
        ref={ref}
        key="tab-content"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        transition={{ duration }}
        className={className}
      >
        {children}
      </motion.div>
    )}
  </AnimatePresence>
));

TabContainer.displayName = 'TabContainer';

/**
 * List Animation Container
 */
export const ListAnimationContainer = React.forwardRef<
  HTMLUListElement,
  {
    children: ReactNode;
    staggerDelay?: number;
    className?: string;
  }
>(({ children, staggerDelay = 0.05, className = '' }, ref) => (
  <motion.ul
    ref={ref}
    variants={{
      visible: {
        transition: {
          staggerChildren: staggerDelay,
        },
      },
    }}
    initial="hidden"
    animate="visible"
    className={className}
  >
    {children}
  </motion.ul>
));

ListAnimationContainer.displayName = 'ListAnimationContainer';

/**
 * List Item Animation
 */
export const ListItemAnimation = React.forwardRef<
  HTMLLIElement,
  {
    children: ReactNode;
    className?: string;
  }
>(({ children, className = '' }, ref) => (
  <motion.li
    ref={ref}
    variants={{
      hidden: { opacity: 0, x: -10 },
      visible: {
        opacity: 1,
        x: 0,
        transition: { duration: 0.2 },
      },
    }}
    className={className}
  >
    {children}
  </motion.li>
));

ListItemAnimation.displayName = 'ListItemAnimation';

/**
 * Page Transition Container
 */
export const PageTransitionContainer = React.forwardRef<
  HTMLDivElement,
  {
    children: ReactNode;
    delay?: number;
    duration?: number;
    className?: string;
  }
>(({ children, delay = 0, duration = 0.3, className = '' }, ref) => (
  <motion.div
    ref={ref}
    initial={{ opacity: 0, y: 10 }}
    animate={{ opacity: 1, y: 0 }}
    exit={{ opacity: 0, y: 10 }}
    transition={{ duration, delay }}
    className={className}
  >
    {children}
  </motion.div>
));

PageTransitionContainer.displayName = 'PageTransitionContainer';

/**
 * Animated Value Display (for numbers, counters)
 */
export const AnimatedValue = React.forwardRef<
  HTMLDivElement,
  {
    value: number;
    duration?: number;
    format?: (v: number) => string;
    className?: string;
  }
>(({ value, duration = 0.5, format = (v) => v.toFixed(0), className = '' }, ref) => {
  const motionValue = React.useRef<number>(0);
  const [displayValue, setDisplayValue] = React.useState(format(value));

  React.useEffect(() => {
    const controls = {
      animate: async () => {
        const start = motionValue.current;
        const step = (value - start) / (duration * 60);

        const interval = setInterval(() => {
          motionValue.current += step;

          if ((step > 0 && motionValue.current >= value) ||
              (step < 0 && motionValue.current <= value)) {
            motionValue.current = value;
            clearInterval(interval);
          }

          setDisplayValue(format(motionValue.current));
        }, 1000 / 60);
      },
    };

    controls.animate();
  }, [value, duration, format]);

  return (
    <div ref={ref} className={className}>
      {displayValue}
    </div>
  );
});

AnimatedValue.displayName = 'AnimatedValue';
