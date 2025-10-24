/**
 * Dynamic Imports Configuration
 * Handles lazy loading of components to improve initial load time
 */

import dynamic from 'next/dynamic';
import React from 'react';

/**
 * Skeleton Loader Component
 * Displayed while lazy-loaded component is loading
 */
const SkeletonLoader = () => (
  <div className="animate-pulse space-y-4">
    <div className="h-12 bg-gray-200 rounded"></div>
    <div className="space-y-2">
      <div className="h-4 bg-gray-200 rounded w-3/4"></div>
      <div className="h-4 bg-gray-200 rounded w-1/2"></div>
    </div>
  </div>
);

/**
 * Error Fallback Component
 * Displayed if lazy-loaded component fails to load
 */
const ErrorFallback = () => (
  <div className="p-4 bg-red-50 border border-red-200 rounded">
    <p className="text-red-800 font-medium">Failed to load component</p>
    <p className="text-red-700 text-sm mt-1">Please refresh the page and try again.</p>
  </div>
);

/**
 * Dynamic import configuration for Strategy components
 */

export const DynamicStrategyCanvasPanel = dynamic(
  () => import('../components/strategy/StrategyCanvasPanel'),
  {
    loading: () => <SkeletonLoader />,
    ssr: true,
  }
);

export const DynamicContextIntakePanel = dynamic(
  () => import('../components/strategy/ContextIntakePanel'),
  {
    loading: () => <SkeletonLoader />,
    ssr: true,
  }
);

export const DynamicRationalesPanel = dynamic(
  () => import('../components/strategy/RationalesPanel'),
  {
    loading: () => <SkeletonLoader />,
    ssr: false, // Load on client-side only (not critical)
  }
);

export const DynamicJobEditor = dynamic(
  () => import('../components/strategy/JobEditor'),
  {
    loading: () => <SkeletonLoader />,
    ssr: false,
  }
);

export const DynamicICPEditor = dynamic(
  () => import('../components/strategy/ICPEditor'),
  {
    loading: () => <SkeletonLoader />,
    ssr: false,
  }
);

export const DynamicAvatarEditor = dynamic(
  () => import('../components/strategy/AvatarEditor'),
  {
    loading: () => <SkeletonLoader />,
    ssr: false,
  }
);

export const DynamicChannelMatrix = dynamic(
  () => import('../components/strategy/ChannelMatrix'),
  {
    loading: () => <SkeletonLoader />,
    ssr: false,
  }
);

/**
 * Dynamic import configuration for UI components
 */

export const DynamicToast = dynamic(
  () => import('../components/ui/Toast'),
  {
    ssr: true,
  }
);

export const DynamicConfirmationDialog = dynamic(
  () => import('../components/ui/ConfirmationDialog'),
  {
    ssr: false,
  }
);

/**
 * Higher-order function to wrap dynamic imports with error handling
 */
export function withDynamicImport<P extends object>(
  Component: React.ComponentType<P>,
  fallback?: React.ComponentType
) {
  return React.lazy(() =>
    Promise.resolve(Component).catch(() => {
      return { default: fallback || ErrorFallback };
    })
  );
}

/**
 * Preload utility for critical components
 * Call during page load to start loading before rendering
 */
export function preloadComponent(componentName: keyof typeof preloadMap) {
  if (preloadMap[componentName]) {
    preloadMap[componentName]();
  }
}

/**
 * Map of preload functions for each dynamic component
 */
const preloadMap = {
  StrategyCanvasPanel: () =>
    import('../components/strategy/StrategyCanvasPanel'),
  ContextIntakePanel: () =>
    import('../components/strategy/ContextIntakePanel'),
  RationalesPanel: () =>
    import('../components/strategy/RationalesPanel'),
  JobEditor: () => import('../components/strategy/JobEditor'),
  ICPEditor: () => import('../components/strategy/ICPEditor'),
  AvatarEditor: () => import('../components/strategy/AvatarEditor'),
  ChannelMatrix: () => import('../components/strategy/ChannelMatrix'),
  Toast: () => import('../components/ui/Toast'),
  ConfirmationDialog: () => import('../components/ui/ConfirmationDialog'),
};

/**
 * Preload all critical components on app load
 */
export function preloadCriticalComponents() {
  preloadComponent('StrategyCanvasPanel');
  preloadComponent('ContextIntakePanel');
  preloadComponent('ChannelMatrix');
}
