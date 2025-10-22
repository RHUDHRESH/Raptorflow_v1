/**
 * Loading Spinner Component
 * Various animated loading indicators
 */

'use client';

import React, { memo } from 'react';
import { motion } from 'framer-motion';

interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg';
  type?: 'spinner' | 'dots' | 'pulse' | 'bars';
  color?: string;
  className?: string;
}

/**
 * Spinner Type: Rotating Circle
 */
const SpinnerType = memo(({ size, color }: { size: string; color: string }) => (
  <motion.div
    animate={{ rotate: 360 }}
    transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
    className={`${size} border-4 border-gray-200 border-t-[${color}] rounded-full`}
  />
));

SpinnerType.displayName = 'SpinnerType';

/**
 * Dots Type: Bouncing Dots
 */
const DotsType = memo(({ color }: { color: string }) => (
  <div className="flex gap-1">
    {[0, 1, 2].map((i) => (
      <motion.div
        key={i}
        animate={{ y: [0, -10, 0] }}
        transition={{
          duration: 1,
          repeat: Infinity,
          delay: i * 0.1,
          ease: 'easeInOut',
        }}
        className={`w-2 h-2 rounded-full bg-[${color}]`}
      />
    ))}
  </div>
));

DotsType.displayName = 'DotsType';

/**
 * Pulse Type: Growing Circle
 */
const PulseType = memo(({ size, color }: { size: string; color: string }) => (
  <motion.div
    animate={{ scale: [1, 1.2, 1], opacity: [1, 0.5, 1] }}
    transition={{ duration: 2, repeat: Infinity, ease: 'easeInOut' }}
    className={`${size} rounded-full bg-[${color}]`}
  />
));

PulseType.displayName = 'PulseType';

/**
 * Bars Type: Animated Bars
 */
const BarsType = memo(({ color }: { color: string }) => (
  <div className="flex gap-1">
    {[0, 1, 2].map((i) => (
      <motion.div
        key={i}
        animate={{ height: ['20px', '40px', '20px'] }}
        transition={{
          duration: 1,
          repeat: Infinity,
          delay: i * 0.1,
          ease: 'easeInOut',
        }}
        className={`w-1 bg-[${color}]`}
      />
    ))}
  </div>
));

BarsType.displayName = 'BarsType';

/**
 * Main Loading Spinner Component
 */
const LoadingSpinnerComponent = memo(
  ({
    size = 'md',
    type = 'spinner',
    color = '#A68763',
    className = '',
  }: LoadingSpinnerProps) => {
    const getSizeClasses = () => {
      switch (size) {
        case 'sm':
          return 'w-6 h-6';
        case 'lg':
          return 'w-12 h-12';
        default:
          return 'w-8 h-8';
      }
    };

    return (
      <div className={`flex items-center justify-center ${className}`}>
        {type === 'spinner' && (
          <SpinnerType size={getSizeClasses()} color={color} />
        )}
        {type === 'dots' && <DotsType color={color} />}
        {type === 'pulse' && (
          <PulseType size={getSizeClasses()} color={color} />
        )}
        {type === 'bars' && <BarsType color={color} />}
      </div>
    );
  }
);

LoadingSpinnerComponent.displayName = 'LoadingSpinner';

export default LoadingSpinnerComponent;

/**
 * Skeleton Loading Component
 */
interface SkeletonProps {
  width?: string | number;
  height?: string | number;
  className?: string;
  count?: number;
  circle?: boolean;
}

export const SkeletonLoader = memo(
  ({
    width = '100%',
    height = '20px',
    className = '',
    count = 1,
    circle = false,
  }: SkeletonProps) => (
    <div className={className}>
      {Array.from({ length: count }).map((_, i) => (
        <motion.div
          key={i}
          animate={{
            backgroundPosition: ['200% 0', '-200% 0'],
          }}
          transition={{
            duration: 2,
            repeat: Infinity,
            ease: 'linear',
          }}
          className={`
            mb-2 last:mb-0
            bg-gradient-to-r from-gray-200 via-gray-100 to-gray-200
            bg-[200%_0]
            ${circle ? 'rounded-full' : 'rounded'}
          `}
          style={{
            width: typeof width === 'number' ? `${width}px` : width,
            height: typeof height === 'number' ? `${height}px` : height,
          }}
        />
      ))}
    </div>
  )
);

SkeletonLoader.displayName = 'SkeletonLoader';
