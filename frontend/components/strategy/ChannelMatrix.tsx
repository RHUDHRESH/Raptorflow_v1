/**
 * Channel Matrix Component
 * Grid showing ICP × Job combinations with channel recommendations
 * Each cell represents potential channel placements for that ICP/Job pair
 */

'use client';

import React, { useState } from 'react';
import AISASSlider from './AISASSlider';

interface Channel {
  id: string;
  channelName: string;
  aisasStage: number;
}

interface ChannelMatrixProps {
  icps: Array<{ id: string; name: string }>;
  jobs: Array<{ id: string; why: string }>;
  channels: Channel[];
  onChannelUpdate: (icpId: string, jobId: string, channelName: string, aisasStage: number) => Promise<void>;
  onChannelAdd: (icpId: string, jobId: string) => void;
  onChannelRemove: (channelId: string) => void;
  loading?: boolean;
}

export default function ChannelMatrix({
  icps,
  jobs,
  channels,
  onChannelUpdate,
  onChannelAdd,
  onChannelRemove,
  loading = false,
}: ChannelMatrixProps) {
  const [expandedCell, setExpandedCell] = useState<string | null>(null);
  const [editingChannelId, setEditingChannelId] = useState<string | null>(null);

  const getCellChannels = (icpId: string, jobId: string) => {
    return channels.filter((ch) => ch.icpId === icpId && ch.jtbdId === jobId);
  };

  const cellKey = (icpId: string, jobId: string) => `${icpId}-${jobId}`;

  if (icps.length === 0 || jobs.length === 0) {
    return (
      <div className="text-center py-12 text-[#2D2D2D]/60">
        <p className="text-sm">No ICPs or Jobs yet</p>
        <p className="text-xs mt-1">Run analysis to generate customers and jobs</p>
      </div>
    );
  }

  return (
    <div className="overflow-auto">
      {/* Matrix Grid */}
      <table className="w-full border-collapse">
        {/* Header Row */}
        <thead>
          <tr>
            <th className="p-2 bg-[#EAE0D2] border border-[#D7C9AE] text-left text-xs font-medium text-[#2D2D2D] sticky left-0 z-10">
              ICP / Job
            </th>
            {jobs.map((job) => (
              <th
                key={job.id}
                className="p-2 bg-[#EAE0D2] border border-[#D7C9AE] text-left text-xs font-medium text-[#2D2D2D] min-w-max"
              >
                <div className="truncate max-w-40" title={job.why}>
                  {job.why.substring(0, 20)}...
                </div>
              </th>
            ))}
          </tr>
        </thead>

        {/* Body Rows */}
        <tbody>
          {icps.map((icp) => (
            <tr key={icp.id}>
              {/* ICP Name Cell */}
              <td className="p-2 bg-[#F5F5F5] border border-[#D7C9AE] font-medium text-sm text-[#2D2D2D] sticky left-0 z-10">
                <div className="truncate max-w-40" title={icp.name}>
                  {icp.name}
                </div>
              </td>

              {/* Matrix Cells */}
              {jobs.map((job) => {
                const key = cellKey(icp.id, job.id);
                const cellChannels = getCellChannels(icp.id, job.id);
                const isExpanded = expandedCell === key;

                return (
                  <td
                    key={key}
                    className="p-0 border border-[#D7C9AE] hover:bg-[#EAE0D2]/20 transition-colors cursor-pointer"
                    onClick={() =>
                      setExpandedCell(isExpanded ? null : key)
                    }
                  >
                    <div className="p-2 min-h-24 h-24">
                      {cellChannels.length === 0 ? (
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            onChannelAdd(icp.id, job.id);
                          }}
                          className="w-full h-full flex items-center justify-center text-[#A68763] hover:bg-[#A68763]/5 rounded border border-dashed border-[#D7C9AE]"
                          title="Add channel for this ICP/Job pair"
                        >
                          <span className="text-2xl">+</span>
                        </button>
                      ) : (
                        <div className="space-y-1">
                          {cellChannels.map((channel) => (
                            <div
                              key={channel.id}
                              className="p-1.5 bg-[#A68763] text-white rounded text-xs font-medium flex items-center justify-between group"
                            >
                              <span className="truncate">{channel.channelName}</span>
                              <button
                                onClick={(e) => {
                                  e.stopPropagation();
                                  onChannelRemove(channel.id);
                                }}
                                className="opacity-0 group-hover:opacity-100 text-xs ml-1"
                              >
                                ✕
                              </button>
                            </div>
                          ))}
                        </div>
                      )}

                      {/* Expanded View */}
                      {isExpanded && cellChannels.length > 0 && (
                        <div
                          className="fixed z-50 bg-white border border-[#D7C9AE] rounded-lg shadow-xl p-4 min-w-80"
                          onClick={(e) => e.stopPropagation()}
                        >
                          <div className="mb-4">
                            <p className="font-medium text-[#2D2D2D] text-sm mb-1">
                              {icp.name} → {job.why.substring(0, 40)}...
                            </p>
                            <p className="text-xs text-[#2D2D2D]/60">
                              Channels ({cellChannels.length})
                            </p>
                          </div>

                          <div className="space-y-4">
                            {cellChannels.map((channel) => (
                              <div key={channel.id} className="border-t border-[#D7C9AE] pt-3">
                                <div className="flex items-center justify-between mb-2">
                                  <p className="font-medium text-[#2D2D2D] text-sm">
                                    {channel.channelName}
                                  </p>
                                  <button
                                    onClick={() => onChannelRemove(channel.id)}
                                    className="text-red-600 hover:text-red-700 text-sm"
                                  >
                                    Remove
                                  </button>
                                </div>

                                {/* AISAS Slider */}
                                <AISASSlider
                                  value={channel.aisasStage}
                                  onChange={(aisas) =>
                                    onChannelUpdate(
                                      icp.id,
                                      job.id,
                                      channel.channelName,
                                      aisas
                                    )
                                  }
                                  size="sm"
                                />
                              </div>
                            ))}
                          </div>

                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              onChannelAdd(icp.id, job.id);
                              setExpandedCell(null);
                            }}
                            className="mt-4 w-full px-3 py-2 text-sm font-medium text-[#A68763] hover:bg-[#A68763]/10 rounded border border-[#A68763]"
                          >
                            + Add Another Channel
                          </button>
                        </div>
                      )}
                    </div>
                  </td>
                );
              })}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
