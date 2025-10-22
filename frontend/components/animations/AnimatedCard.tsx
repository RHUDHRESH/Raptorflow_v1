/**
 * Animated Card Component
 * Card with hover lift and shadow animations
 */

'use client';

import React, { memo, ReactNode } from 'react';
import { motion } from 'framer-motion';

interface AnimatedCardProps {
  children: ReactNode;
  onClick?: () => void;
  isClickable?: boolean;
  variant?: 'default' | 'elevated' | 'outlined';
  hoverScale?: number;
  className?: string;
}

/**
 * Animated Card Component
 */
const AnimatedCardComponent = memo(
  ({
    children,
    onClick,
    isClickable = false,
    variant = 'default',
    hoverScale = 1.02,
    className = '',
  }: AnimatedCardProps) => {
    const getVariantClasses = () => {
      switch (variant) {
        case 'elevated':
          return 'bg-white shadow-md';
        case 'outlined':
          return 'bg-white border border-[#D7C9AE]';
        default:
          return 'bg-gray-50 border border-[#D7C9AE]';
      }
    };

    return (
      <motion.div
        whileHover={isClickable ? { scale: hoverScale, y: -4 } : {}}
        whileTap={isClickable ? { scale: 0.98 } : {}}
        onClick={onClick}
        className={`
          p-4
          rounded-lg
          transition-shadow
          ${getVariantClasses()}
          ${isClickable ? 'cursor-pointer' : ''}
          ${className}
        `}
      >
        {children}
      </motion.div>
    );
  }
);

AnimatedCardComponent.displayName = 'AnimatedCard';

export default AnimatedCardComponent;
