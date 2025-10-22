/**
 * Strategy Workspace Page - Optimized Version
 * Main page component for the strategy workspace with 3-pane layout
 * Uses code splitting for optimal performance
 */

'use client';

import React, { useState, useEffect, Suspense } from 'react';
import { useStrategyWorkspace } from '@/hooks/useStrategyWorkspace';
import {
  DynamicContextIntakePanel,
  DynamicStrategyCanvasPanel,
  DynamicRationalesPanel,
  preloadCriticalComponents,
} from '@/lib/dynamic-imports';

/**
 * Skeleton loader for panels during lazy loading
 */
const PanelSkeleton = () => (
  <div className="animate-pulse space-y-4 p-4">
    <div className="h-6 bg-gray-200 rounded w-1/3"></div>
    <div className="space-y-3">
      <div className="h-4 bg-gray-200 rounded"></div>
      <div className="h-4 bg-gray-200 rounded w-5/6"></div>
      <div className="h-4 bg-gray-200 rounded w-4/6"></div>
    </div>
  </div>
);

/**
 * Loading screen for initial workspace load
 */
const LoadingScreen = () => (
  <div className="flex items-center justify-center h-screen bg-[#EAE0D2]">
    <div className="text-center">
      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-[#A68763] mx-auto mb-4"></div>
      <p className="text-[#2D2D2D]">Loading workspace...</p>
    </div>
  </div>
);

/**
 * Error screen
 */
const ErrorScreen = ({ error }: { error: string }) => (
  <div className="flex items-center justify-center h-screen bg-[#EAE0D2]">
    <div className="text-center">
      <p className="text-red-600 mb-4">Error loading workspace</p>
      <p className="text-[#2D2D2D]">{error}</p>
    </div>
  </div>
);

/**
 * Desktop 3-pane layout with lazy-loaded panels
 */
const DesktopLayout = ({ workspace }: { workspace: any }) => (
  <div className="flex h-screen gap-4 p-4 bg-[#EAE0D2]">
    {/* Left pane: Context Intake (25% width) */}
    <div className="w-1/4 bg-white rounded-lg shadow-sm border border-[#D7C9AE] flex flex-col overflow-hidden">
      <div className="px-4 py-3 border-b border-[#D7C9AE]">
        <h2 className="text-lg font-semibold text-[#2D2D2D]">Context</h2>
        <p className="text-sm text-[#2D2D2D]/60 mt-1">Add evidence and insights</p>
      </div>
      <div className="flex-1 overflow-auto">
        <Suspense fallback={<PanelSkeleton />}>
          <DynamicContextIntakePanel workspace={workspace} />
        </Suspense>
      </div>
    </div>

    {/* Center pane: Strategy Canvas (50% width) */}
    <div className="w-1/2 bg-white rounded-lg shadow-sm border border-[#D7C9AE] flex flex-col overflow-hidden">
      <div className="px-4 py-3 border-b border-[#D7C9AE]">
        <h2 className="text-lg font-semibold text-[#2D2D2D]">Strategy</h2>
        <p className="text-sm text-[#2D2D2D]/60 mt-1">Jobs, ICPs, Channels & AISAS</p>
      </div>
      <div className="flex-1 overflow-auto">
        <Suspense fallback={<PanelSkeleton />}>
          <DynamicStrategyCanvasPanel workspace={workspace} />
        </Suspense>
      </div>
    </div>

    {/* Right pane: Rationales (25% width) */}
    <div className="w-1/4 bg-white rounded-lg shadow-sm border border-[#D7C9AE] flex flex-col overflow-hidden">
      <div className="px-4 py-3 border-b border-[#D7C9AE]">
        <h2 className="text-lg font-semibold text-[#2D2D2D]">Why</h2>
        <p className="text-sm text-[#2D2D2D]/60 mt-1">Evidence & explanations</p>
      </div>
      <div className="flex-1 overflow-auto">
        <Suspense fallback={<PanelSkeleton />}>
          <DynamicRationalesPanel workspace={workspace} />
        </Suspense>
      </div>
    </div>
  </div>
);

/**
 * Mobile tab-based layout with lazy-loaded panels
 */
const MobileLayout = ({
  workspace,
  activeTab,
  setActiveTab,
}: {
  workspace: any;
  activeTab: string;
  setActiveTab: (tab: string) => void;
}) => (
  <div className="flex flex-col h-screen bg-[#EAE0D2]">
    {/* Mobile tab navigation */}
    <div className="flex border-b border-[#D7C9AE] bg-white sticky top-0">
      {['context', 'strategy', 'rationales'].map((tab) => (
        <button
          key={tab}
          onClick={() => setActiveTab(tab)}
          className={`flex-1 px-4 py-3 text-center font-medium transition-colors ${
            activeTab === tab
              ? 'text-[#A68763] border-b-2 border-[#A68763]'
              : 'text-[#2D2D2D]'
          }`}
        >
          {tab === 'context' && 'Context'}
          {tab === 'strategy' && 'Strategy'}
          {tab === 'rationales' && 'Why'}
        </button>
      ))}
    </div>

    {/* Mobile content area */}
    <div className="flex-1 overflow-auto">
      <Suspense fallback={<PanelSkeleton />}>
        {activeTab === 'context' && (
          <DynamicContextIntakePanel workspace={workspace} />
        )}
        {activeTab === 'strategy' && (
          <DynamicStrategyCanvasPanel workspace={workspace} />
        )}
        {activeTab === 'rationales' && (
          <DynamicRationalesPanel workspace={workspace} />
        )}
      </Suspense>
    </div>
  </div>
);

/**
 * Main Strategy Page Component
 */
export default function StrategyPage({
  params,
}: {
  params: { workspaceId: string };
}) {
  const [activeTab, setActiveTab] = useState<'context' | 'strategy' | 'rationales'>('context');
  const [isMobileLayout, setIsMobileLayout] = useState(false);
  const { workspace, loading, error } = useStrategyWorkspace(params.workspaceId);

  // Detect mobile layout and preload critical components on mount
  useEffect(() => {
    const handleResize = () => {
      setIsMobileLayout(window.innerWidth < 600);
    };

    // Initial check
    handleResize();

    // Listen for resize
    window.addEventListener('resize', handleResize);

    // Preload critical components
    preloadCriticalComponents();

    return () => window.removeEventListener('resize', handleResize);
  }, []);

  // Loading state
  if (loading) {
    return <LoadingScreen />;
  }

  // Error state
  if (error) {
    return <ErrorScreen error={error} />;
  }

  // Render appropriate layout
  return isMobileLayout ? (
    <MobileLayout workspace={workspace} activeTab={activeTab} setActiveTab={setActiveTab} />
  ) : (
    <DesktopLayout workspace={workspace} />
  );
}
