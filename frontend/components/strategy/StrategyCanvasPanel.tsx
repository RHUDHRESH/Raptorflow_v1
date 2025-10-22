/**
 * Strategy Canvas Panel
 * Center pane showing Jobs, ICPs, Channel Matrix, and AISAS positioning
 */

'use client';

import React, { useState } from 'react';

interface StrategyCanvasPanelProps {
  workspace: any;
}

export default function StrategyCanvasPanel({ workspace }: StrategyCanvasPanelProps) {
  const [activeSection, setActiveSection] = useState<'jobs' | 'icps' | 'channels'>('jobs');

  return (
    <div className="p-4 h-full flex flex-col">
      {/* Section Tabs */}
      <div className="flex gap-2 mb-4 border-b border-[#D7C9AE]">
        <button
          onClick={() => setActiveSection('jobs')}
          className={`px-3 py-2 text-sm font-medium border-b-2 transition-colors ${
            activeSection === 'jobs'
              ? 'border-[#A68763] text-[#A68763]'
              : 'border-transparent text-[#2D2D2D] hover:text-[#A68763]'
          }`}
        >
          Jobs ({workspace?.jtbds?.length || 0})
        </button>
        <button
          onClick={() => setActiveSection('icps')}
          className={`px-3 py-2 text-sm font-medium border-b-2 transition-colors ${
            activeSection === 'icps'
              ? 'border-[#A68763] text-[#A68763]'
              : 'border-transparent text-[#2D2D2D] hover:text-[#A68763]'
          }`}
        >
          ICPs ({workspace?.icps?.length || 0})
        </button>
        <button
          onClick={() => setActiveSection('channels')}
          className={`px-3 py-2 text-sm font-medium border-b-2 transition-colors ${
            activeSection === 'channels'
              ? 'border-[#A68763] text-[#A68763]'
              : 'border-transparent text-[#2D2D2D] hover:text-[#A68763]'
          }`}
        >
          Channels ({workspace?.channels?.length || 0})
        </button>
      </div>

      {/* Content Area */}
      <div className="flex-1 overflow-auto">
        {activeSection === 'jobs' && (
          <JobsSection workspace={workspace} />
        )}
        {activeSection === 'icps' && (
          <ICPsSection workspace={workspace} />
        )}
        {activeSection === 'channels' && (
          <ChannelsSection workspace={workspace} />
        )}
      </div>
    </div>
  );
}

function JobsSection({ workspace }: any) {
  if (!workspace?.jtbds || workspace.jtbds.length === 0) {
    return (
      <div className="text-center py-12 text-[#2D2D2D]/60">
        <p className="text-sm">No jobs extracted yet</p>
        <p className="text-xs mt-1">Add context and run analysis to extract jobs</p>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {workspace.jtbds.map((job: any) => (
        <div key={job.id} className="p-3 bg-[#EAE0D2]/30 rounded-lg border border-[#D7C9AE]">
          <p className="font-medium text-[#2D2D2D] text-sm">{job.why}</p>
          <p className="text-xs text-[#2D2D2D]/60 mt-2">
            <strong>When:</strong> {job.circumstances}
          </p>
          <div className="flex gap-2 mt-2 text-xs">
            <button className="px-2 py-1 text-[#A68763] hover:bg-[#A68763]/10 rounded">
              Edit
            </button>
            <button className="px-2 py-1 text-[#A68763] hover:bg-[#A68763]/10 rounded">
              Merge
            </button>
            <button className="px-2 py-1 text-red-600 hover:bg-red-50 rounded">
              Delete
            </button>
          </div>
        </div>
      ))}
    </div>
  );
}

function ICPsSection({ workspace }: any) {
  if (!workspace?.icps || workspace.icps.length === 0) {
    return (
      <div className="text-center py-12 text-[#2D2D2D]/60">
        <p className="text-sm">No ICPs built yet</p>
        <p className="text-xs mt-1">Run analysis to generate customer profiles</p>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {workspace.icps.map((icp: any) => (
        <div key={icp.id} className="p-3 bg-[#EAE0D2]/30 rounded-lg border border-[#D7C9AE]">
          <div className="flex items-start gap-3">
            <div className="w-10 h-10 rounded-full flex items-center justify-center text-lg"
              style={{ backgroundColor: icp.avatarColor || '#A68763' }}>
              👤
            </div>
            <div className="flex-1">
              <p className="font-medium text-[#2D2D2D] text-sm">{icp.name}</p>
              {icp.painPoints && icp.painPoints.length > 0 && (
                <p className="text-xs text-[#2D2D2D]/60 mt-1">
                  {icp.painPoints[0]}
                </p>
              )}
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}

function ChannelsSection({ workspace }: any) {
  if (!workspace?.channels || workspace.channels.length === 0) {
    return (
      <div className="text-center py-12 text-[#2D2D2D]/60">
        <p className="text-sm">No channels mapped yet</p>
        <p className="text-xs mt-1">Run analysis to generate channel recommendations</p>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {workspace.channels.map((channel: any) => (
        <div key={channel.id} className="p-3 bg-[#EAE0D2]/30 rounded-lg border border-[#D7C9AE]">
          <div className="flex items-center justify-between">
            <p className="font-medium text-[#2D2D2D] text-sm">{channel.channelName}</p>
            <div className="flex items-center gap-2">
              <div className="w-24 h-2 bg-[#D7C9AE] rounded-full overflow-hidden">
                <div
                  className="h-full bg-[#A68763]"
                  style={{ width: `${channel.aisasStage}%` }}
                />
              </div>
              <span className="text-xs font-medium text-[#2D2D2D] w-8 text-right">
                {Math.round(channel.aisasStage)}%
              </span>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}
