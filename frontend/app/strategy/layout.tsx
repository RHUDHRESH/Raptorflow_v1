/**
 * Strategy Workspace Layout
 * Main layout wrapper for the strategy workspace featuring 3-pane design:
 * - Left: Context Intake
 * - Center: Strategy Canvas
 * - Right: Rationales & Explanations
 */

import React from 'react';

export default function StrategyLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="flex h-screen bg-[#EAE0D2]">
      {/* Main content area */}
      <main className="flex-1 overflow-hidden">
        {children}
      </main>
    </div>
  );
}
