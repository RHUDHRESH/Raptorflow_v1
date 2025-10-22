/**
 * Animation Configuration & Presets
 * Centralized animation settings for consistency and performance
 */

import { Variants, TargetAndTransition } from 'framer-motion';

/**
 * Easing functions for smooth animations
 */
export const EASINGS = {
  easeInOut: [0.4, 0, 0.2, 1],
  easeOut: [0, 0, 0.2, 1],
  easeIn: [0.4, 0, 1, 1],
  spring: { type: 'spring', stiffness: 100, damping: 10 },
  springSnappy: { type: 'spring', stiffness: 300, damping: 30 },
  springBouncy: { type: 'spring', stiffness: 100, damping: 5 },
};

/**
 * Fade In/Out Animations
 */
export const FADE_VARIANTS: Variants = {
  hidden: {
    opacity: 0,
    transition: { duration: 0.2 },
  },
  visible: {
    opacity: 1,
    transition: { duration: 0.3, ease: EASINGS.easeOut },
  },
  exit: {
    opacity: 0,
    transition: { duration: 0.2, ease: EASINGS.easeIn },
  },
};

/**
 * Scale Up Animations
 */
export const SCALE_UP_VARIANTS: Variants = {
  hidden: {
    opacity: 0,
    scale: 0.95,
    transition: { duration: 0.2 },
  },
  visible: {
    opacity: 1,
    scale: 1,
    transition: { duration: 0.3, ease: EASINGS.easeOut },
  },
  exit: {
    opacity: 0,
    scale: 0.95,
    transition: { duration: 0.2, ease: EASINGS.easeIn },
  },
};

/**
 * Slide In From Right
 */
export const SLIDE_RIGHT_VARIANTS: Variants = {
  hidden: {
    opacity: 0,
    x: 20,
    transition: { duration: 0.2 },
  },
  visible: {
    opacity: 1,
    x: 0,
    transition: { duration: 0.3, ease: EASINGS.easeOut },
  },
  exit: {
    opacity: 0,
    x: 20,
    transition: { duration: 0.2, ease: EASINGS.easeIn },
  },
};

/**
 * Slide In From Left
 */
export const SLIDE_LEFT_VARIANTS: Variants = {
  hidden: {
    opacity: 0,
    x: -20,
    transition: { duration: 0.2 },
  },
  visible: {
    opacity: 1,
    x: 0,
    transition: { duration: 0.3, ease: EASINGS.easeOut },
  },
  exit: {
    opacity: 0,
    x: -20,
    transition: { duration: 0.2, ease: EASINGS.easeIn },
  },
};

/**
 * Slide In From Top
 */
export const SLIDE_DOWN_VARIANTS: Variants = {
  hidden: {
    opacity: 0,
    y: -20,
    transition: { duration: 0.2 },
  },
  visible: {
    opacity: 1,
    y: 0,
    transition: { duration: 0.3, ease: EASINGS.easeOut },
  },
  exit: {
    opacity: 0,
    y: -20,
    transition: { duration: 0.2, ease: EASINGS.easeIn },
  },
};

/**
 * Slide In From Bottom
 */
export const SLIDE_UP_VARIANTS: Variants = {
  hidden: {
    opacity: 0,
    y: 20,
    transition: { duration: 0.2 },
  },
  visible: {
    opacity: 1,
    y: 0,
    transition: { duration: 0.3, ease: EASINGS.easeOut },
  },
  exit: {
    opacity: 0,
    y: 20,
    transition: { duration: 0.2, ease: EASINGS.easeIn },
  },
};

/**
 * Stagger Container (for animating children sequentially)
 */
export const STAGGER_CONTAINER_VARIANTS: Variants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.05,
      delayChildren: 0,
    },
  },
  exit: {
    opacity: 0,
    transition: {
      staggerChildren: 0.02,
    },
  },
};

/**
 * Stagger Item (use with stagger container)
 */
export const STAGGER_ITEM_VARIANTS: Variants = {
  hidden: { opacity: 0, y: 10 },
  visible: {
    opacity: 1,
    y: 0,
    transition: { duration: 0.3, ease: EASINGS.easeOut },
  },
  exit: {
    opacity: 0,
    y: 10,
    transition: { duration: 0.2, ease: EASINGS.easeIn },
  },
};

/**
 * Button Hover & Tap Animations
 */
export const BUTTON_VARIANTS: Variants = {
  rest: {
    scale: 1,
    boxShadow: '0px 2px 8px rgba(0, 0, 0, 0.1)',
  },
  hover: {
    scale: 1.02,
    boxShadow: '0px 4px 12px rgba(0, 0, 0, 0.15)',
    transition: { duration: 0.2, ease: EASINGS.easeOut },
  },
  tap: {
    scale: 0.98,
    boxShadow: '0px 1px 4px rgba(0, 0, 0, 0.1)',
    transition: { duration: 0.1 },
  },
};

/**
 * Panel Slide In from Side (for sidebars/panels)
 */
export const PANEL_VARIANTS: Variants = {
  hidden: {
    opacity: 0,
    x: -280,
    transition: { duration: 0.2 },
  },
  visible: {
    opacity: 1,
    x: 0,
    transition: { duration: 0.4, ease: EASINGS.easeOut },
  },
  exit: {
    opacity: 0,
    x: -280,
    transition: { duration: 0.3, ease: EASINGS.easeIn },
  },
};

/**
 * Modal Backdrop Fade
 */
export const BACKDROP_VARIANTS: Variants = {
  hidden: {
    opacity: 0,
    transition: { duration: 0.2 },
  },
  visible: {
    opacity: 1,
    transition: { duration: 0.3, ease: EASINGS.easeOut },
  },
  exit: {
    opacity: 0,
    transition: { duration: 0.2, ease: EASINGS.easeIn },
  },
};

/**
 * Modal Content Pop
 */
export const MODAL_VARIANTS: Variants = {
  hidden: {
    opacity: 0,
    scale: 0.9,
    y: 20,
    transition: { duration: 0.2 },
  },
  visible: {
    opacity: 1,
    scale: 1,
    y: 0,
    transition: { duration: 0.3, ease: EASINGS.easeOut },
  },
  exit: {
    opacity: 0,
    scale: 0.9,
    y: 20,
    transition: { duration: 0.2, ease: EASINGS.easeIn },
  },
};

/**
 * Rotate Animation (for spinners/loaders)
 */
export const ROTATE_VARIANTS: Variants = {
  animate: {
    rotate: 360,
    transition: {
      duration: 2,
      repeat: Infinity,
      ease: 'linear',
    },
  },
};

/**
 * Pulse Animation (for emphasis)
 */
export const PULSE_VARIANTS: Variants = {
  animate: {
    scale: [1, 1.05, 1],
    transition: {
      duration: 2,
      repeat: Infinity,
      ease: EASINGS.easeInOut,
    },
  },
};

/**
 * Bounce Animation
 */
export const BOUNCE_VARIANTS: Variants = {
  animate: {
    y: [0, -10, 0],
    transition: {
      duration: 1,
      repeat: Infinity,
      ease: EASINGS.easeInOut,
    },
  },
};

/**
 * Shimmer Loading Animation
 */
export const SHIMMER_VARIANTS: Variants = {
  animate: {
    backgroundPosition: ['200% 0', '-200% 0'],
    transition: {
      duration: 2,
      repeat: Infinity,
      ease: 'linear',
    },
  },
};

/**
 * Page Transition (between routes)
 */
export const PAGE_TRANSITION_VARIANTS: Variants = {
  hidden: {
    opacity: 0,
    y: 10,
    transition: { duration: 0.2 },
  },
  visible: {
    opacity: 1,
    y: 0,
    transition: { duration: 0.3, ease: EASINGS.easeOut },
  },
  exit: {
    opacity: 0,
    y: 10,
    transition: { duration: 0.2, ease: EASINGS.easeIn },
  },
};

/**
 * Table Row Hover Animation
 */
export const TABLE_ROW_VARIANTS: Variants = {
  rest: {
    backgroundColor: 'transparent',
  },
  hover: {
    backgroundColor: 'rgba(166, 135, 99, 0.05)',
    transition: { duration: 0.15, ease: EASINGS.easeOut },
  },
};

/**
 * List Item Animation
 */
export const LIST_ITEM_VARIANTS: Variants = {
  hidden: {
    opacity: 0,
    x: -10,
  },
  visible: {
    opacity: 1,
    x: 0,
    transition: { duration: 0.2, ease: EASINGS.easeOut },
  },
};

/**
 * Input Focus Animation
 */
export const INPUT_FOCUS_VARIANTS: Variants = {
  rest: {
    boxShadow: '0 0 0 0px rgba(166, 135, 99, 0)',
  },
  focus: {
    boxShadow: '0 0 0 3px rgba(166, 135, 99, 0.1)',
    transition: { duration: 0.2 },
  },
};

/**
 * Tab Switch Animation
 */
export const TAB_VARIANTS: Variants = {
  inactive: {
    color: '#2D2D2D',
    opacity: 0.6,
  },
  active: {
    color: '#2D2D2D',
    opacity: 1,
    transition: { duration: 0.2 },
    borderBottom: '2px solid #A68763',
  },
};

/**
 * Tooltip Animation
 */
export const TOOLTIP_VARIANTS: Variants = {
  hidden: {
    opacity: 0,
    scale: 0.95,
    y: -5,
  },
  visible: {
    opacity: 1,
    scale: 1,
    y: 0,
    transition: { duration: 0.15, ease: EASINGS.easeOut },
  },
};

/**
 * Dropdown Menu Animation
 */
export const DROPDOWN_VARIANTS: Variants = {
  hidden: {
    opacity: 0,
    scale: 0.95,
    y: -10,
    transition: { duration: 0.15 },
  },
  visible: {
    opacity: 1,
    scale: 1,
    y: 0,
    transition: { duration: 0.2, ease: EASINGS.easeOut },
  },
  exit: {
    opacity: 0,
    scale: 0.95,
    y: -10,
    transition: { duration: 0.15 },
  },
};

/**
 * Success Checkmark Animation
 */
export const SUCCESS_CHECKMARK_VARIANTS: Variants = {
  hidden: {
    opacity: 0,
    scale: 0,
  },
  visible: {
    opacity: 1,
    scale: 1,
    transition: {
      duration: 0.3,
      ease: EASINGS.springSnappy,
    },
  },
};

/**
 * Error Shake Animation
 */
export const ERROR_SHAKE_VARIANTS: Variants = {
  animate: {
    x: [-5, 5, -5, 5, 0],
    transition: {
      duration: 0.4,
      ease: EASINGS.easeInOut,
    },
  },
};

/**
 * Slide Toggle Animation
 */
export const TOGGLE_VARIANTS: Variants = {
  off: {
    x: 0,
    backgroundColor: '#D7C9AE',
  },
  on: {
    x: 24,
    backgroundColor: '#A68763',
  },
};

/**
 * Expand/Collapse Animation
 */
export const ACCORDION_VARIANTS: Variants = {
  collapsed: {
    height: 0,
    opacity: 0,
    transition: { duration: 0.3, ease: EASINGS.easeIn },
  },
  expanded: {
    height: 'auto',
    opacity: 1,
    transition: { duration: 0.3, ease: EASINGS.easeOut },
  },
};

/**
 * Animation Delay Helpers
 */
export const ANIMATION_DELAYS = {
  immediate: 0,
  short: 0.1,
  medium: 0.2,
  long: 0.3,
  xl: 0.5,
};

/**
 * Animation Duration Helpers
 */
export const ANIMATION_DURATIONS = {
  fast: 0.15,
  base: 0.2,
  slow: 0.3,
  slower: 0.5,
  slowest: 0.8,
};

/**
 * Combine animations (apply multiple animations to same element)
 */
export function combineVariants(
  variant1: Variants,
  variant2: Variants,
  variant: string
): TargetAndTransition {
  const combined: any = {};

  // Merge variant 1
  const v1 = variant1[variant] as any;
  if (v1) {
    Object.assign(combined, v1);
  }

  // Merge variant 2 (overwrites if same property)
  const v2 = variant2[variant] as any;
  if (v2) {
    Object.assign(combined, v2);
  }

  return combined;
}
