'use client';

import { motion } from 'framer-motion';
import { card, hoverLift } from '@/components/animations/variants';
import { ReactNode } from 'react';

interface CardProps {
  children: ReactNode;
  hover?: boolean;
  className?: string;
  onClick?: () => void;
}

export function Card({ children, hover = false, className = '', onClick }: CardProps) {
  return (
    <motion.div
      variants={card}
      initial="initial"
      animate="animate"
      exit="exit"
      {...(hover ? hoverLift : {})}
      onClick={onClick}
      className={`card ${className} ${onClick ? 'cursor-pointer' : ''}`}
    >
      {children}
    </motion.div>
  );
}
