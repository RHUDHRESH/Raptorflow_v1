/**
 * Strategy Workspace Page
 * Main page component for the strategy workspace with 3-pane layout
 */

'use client';

import React, { useState, useEffect } from 'react';
import ContextIntakePanel from '@/components/strategy/ContextIntakePanel';
import StrategyCanvasPanel from '@/components/strategy/StrategyCanvasPanel';
import RationalesPanel from '@/components/strategy/RationalesPanel';
import { useStrategyWorkspace } from '@/hooks/useStrategyWorkspace';

export default function StrategyPage({
  params,
}: {
  params: { workspaceId: string };
}) {
  const [activeTab, setActiveTab] = useState<'context' | 'strategy' | 'rationales'>('context');
  const { workspace, loading, error } = useStrategyWorkspace(params.workspaceId);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen bg-[#EAE0D2]">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-[#A68763] mx-auto mb-4"></div>
          <p className="text-[#2D2D2D]">Loading workspace...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-screen bg-[#EAE0D2]">
        <div className="text-center">
          <p className="text-red-600 mb-4">Error loading workspace</p>
          <p className="text-[#2D2D2D]">{error}</p>
        </div>
      </div>
    );
  }

  // Mobile layout: Tab navigation
  const isMobileLayout = typeof window !== 'undefined' && window.innerWidth < 600;

  if (isMobileLayout) {
    return (
      <div className="flex flex-col h-screen bg-[#EAE0D2]">
        {/* Mobile tab navigation */}
        <div className="flex border-b border-[#D7C9AE] bg-white">
          <button
            onClick={() => setActiveTab('context')}
            className={`flex-1 px-4 py-3 text-center font-medium transition-colors ${
              activeTab === 'context'
                ? 'text-[#A68763] border-b-2 border-[#A68763]'
                : 'text-[#2D2D2D]'
            }`}
          >
            Context
          </button>
          <button
            onClick={() => setActiveTab('strategy')}
            className={`flex-1 px-4 py-3 text-center font-medium transition-colors ${
              activeTab === 'strategy'
                ? 'text-[#A68763] border-b-2 border-[#A68763]'
                : 'text-[#2D2D2D]'
            }`}
          >
            Strategy
          </button>
          <button
            onClick={() => setActiveTab('rationales')}
            className={`flex-1 px-4 py-3 text-center font-medium transition-colors ${
              activeTab === 'rationales'
                ? 'text-[#A68763] border-b-2 border-[#A68763]'
                : 'text-[#2D2D2D]'
            }`}
          >
            Why
          </button>
        </div>

        {/* Mobile content area */}
        <div className="flex-1 overflow-auto">
          {activeTab === 'context' && <ContextIntakePanel workspace={workspace} />}
          {activeTab === 'strategy' && <StrategyCanvasPanel workspace={workspace} />}
          {activeTab === 'rationales' && <RationalesPanel workspace={workspace} />}
        </div>
      </div>
    );
  }

  // Desktop 3-pane layout
  return (
    <div className="flex h-screen gap-4 p-4 bg-[#EAE0D2]">
      {/* Left pane: Context Intake (25% width) */}
      <div className="w-1/4 bg-white rounded-lg shadow-sm border border-[#D7C9AE] flex flex-col overflow-hidden">
        <div className="px-4 py-3 border-b border-[#D7C9AE]">
          <h2 className="text-lg font-semibold text-[#2D2D2D]">Context</h2>
          <p className="text-sm text-[#2D2D2D]/60 mt-1">Add evidence and insights</p>
        </div>
        <div className="flex-1 overflow-auto">
          <ContextIntakePanel workspace={workspace} />
        </div>
      </div>

      {/* Center pane: Strategy Canvas (50% width) */}
      <div className="w-1/2 bg-white rounded-lg shadow-sm border border-[#D7C9AE] flex flex-col overflow-hidden">
        <div className="px-4 py-3 border-b border-[#D7C9AE]">
          <h2 className="text-lg font-semibold text-[#2D2D2D]">Strategy</h2>
          <p className="text-sm text-[#2D2D2D]/60 mt-1">Jobs, ICPs, Channels & AISAS</p>
        </div>
        <div className="flex-1 overflow-auto">
          <StrategyCanvasPanel workspace={workspace} />
        </div>
      </div>

      {/* Right pane: Rationales (25% width) */}
      <div className="w-1/4 bg-white rounded-lg shadow-sm border border-[#D7C9AE] flex flex-col overflow-hidden">
        <div className="px-4 py-3 border-b border-[#D7C9AE]">
          <h2 className="text-lg font-semibold text-[#2D2D2D]">Why</h2>
          <p className="text-sm text-[#2D2D2D]/60 mt-1">Evidence & explanations</p>
        </div>
        <div className="flex-1 overflow-auto">
          <RationalesPanel workspace={workspace} />
        </div>
      </div>
    </div>
  );
}
