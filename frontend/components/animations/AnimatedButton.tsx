/**
 * Animated Button Component
 * Button with hover, tap, and loading animations
 */

'use client';

import React, { memo } from 'react';
import { motion } from 'framer-motion';

interface AnimatedButtonProps {
  children: React.ReactNode;
  onClick?: () => void;
  disabled?: boolean;
  loading?: boolean;
  variant?: 'primary' | 'secondary' | 'danger' | 'success';
  size?: 'sm' | 'md' | 'lg';
  className?: string;
  showLoadingDot?: boolean;
}

/**
 * Loading Dot Animation
 */
const LoadingDot = memo(() => (
  <motion.span
    initial={{ scale: 0, opacity: 0 }}
    animate={{ scale: 1, opacity: 1 }}
    exit={{ scale: 0, opacity: 0 }}
    transition={{ duration: 0.2 }}
    className="inline-block ml-2"
  >
    <motion.span
      animate={{ opacity: [1, 0.5, 1] }}
      transition={{ duration: 1, repeat: Infinity }}
      className="inline-block"
    >
      ●
    </motion.span>
  </motion.span>
));

LoadingDot.displayName = 'LoadingDot';

/**
 * Main Animated Button Component
 */
const AnimatedButtonComponent = ({
  children,
  onClick,
  disabled = false,
  loading = false,
  variant = 'primary',
  size = 'md',
  className = '',
  showLoadingDot = true,
}: AnimatedButtonProps) => {
  const getVariantClasses = () => {
    switch (variant) {
      case 'danger':
        return 'bg-red-600 text-white hover:bg-red-700';
      case 'success':
        return 'bg-green-600 text-white hover:bg-green-700';
      case 'secondary':
        return 'bg-[#D7C9AE] text-[#2D2D2D] hover:bg-[#D7C9AE]/80';
      default:
        return 'bg-[#A68763] text-white hover:bg-[#A68763]/90';
    }
  };

  const getSizeClasses = () => {
    switch (size) {
      case 'sm':
        return 'px-3 py-1 text-sm';
      case 'lg':
        return 'px-6 py-3 text-lg';
      default:
        return 'px-4 py-2 text-base';
    }
  };

  return (
    <motion.button
      whileHover={!disabled ? { scale: 1.02 } : {}}
      whileTap={!disabled ? { scale: 0.98 } : {}}
      onClick={onClick}
      disabled={disabled || loading}
      className={`
        ${getSizeClasses()}
        ${getVariantClasses()}
        rounded-lg
        font-medium
        transition-colors
        disabled:opacity-50
        disabled:cursor-not-allowed
        ${className}
      `}
    >
      {loading && showLoadingDot ? (
        <>
          {children}
          <LoadingDot />
        </>
      ) : (
        children
      )}
    </motion.button>
  );
};

AnimatedButtonComponent.displayName = 'AnimatedButton';

export default memo(AnimatedButtonComponent);
