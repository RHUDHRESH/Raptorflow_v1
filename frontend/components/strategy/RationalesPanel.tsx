/**
 * Rationales Panel
 * Right pane showing explanations with evidence citations
 */

'use client';

import React, { useState } from 'react';

interface RationalesPanelProps {
  workspace: any;
}

export default function RationalesPanel({ workspace }: RationalesPanelProps) {
  const [filterType, setFilterType] = useState<string>('all');
  const [expandedIds, setExpandedIds] = useState<Set<string>>(new Set());

  const explanations = workspace?.explanations || [];

  const filtered = filterType === 'all'
    ? explanations
    : explanations.filter((e: any) => e.explanationType === filterType);

  const toggleExpanded = (id: string) => {
    const newSet = new Set(expandedIds);
    if (newSet.has(id)) {
      newSet.delete(id);
    } else {
      newSet.add(id);
    }
    setExpandedIds(newSet);
  };

  return (
    <div className="p-4 h-full flex flex-col">
      {/* Filter Dropdown */}
      <div className="mb-4">
        <select
          value={filterType}
          onChange={(e) => setFilterType(e.target.value)}
          className="w-full px-3 py-2 border border-[#D7C9AE] rounded-lg text-sm bg-white text-[#2D2D2D]"
        >
          <option value="all">All Explanations</option>
          <option value="context_summary">From Context</option>
          <option value="platform_strategy">Platform Strategy</option>
          <option value="aisas_positioning">AISAS Positioning</option>
          <option value="confidence_assessment">Confidence</option>
        </select>
      </div>

      {/* Explanations List */}
      <div className="flex-1 overflow-auto space-y-2">
        {filtered.length === 0 ? (
          <div className="text-center py-12 text-[#2D2D2D]/60">
            <p className="text-sm">No explanations available</p>
            <p className="text-xs mt-1">Explanations appear after strategy analysis</p>
          </div>
        ) : (
          filtered.map((explanation: any) => (
            <div
              key={explanation.id}
              className="p-3 bg-[#EAE0D2]/30 rounded-lg border border-[#D7C9AE] cursor-pointer hover:border-[#A68763] transition-colors"
              onClick={() => toggleExpanded(explanation.id)}
            >
              <div className="flex items-start gap-2">
                <span className="text-lg leading-5">
                  {expandedIds.has(explanation.id) ? '▼' : '▶'}
                </span>
                <div className="flex-1">
                  <p className="font-medium text-[#2D2D2D] text-sm">
                    {explanation.title}
                  </p>
                  <p className="text-xs text-[#2D2D2D]/60 mt-1">
                    {explanation.explanationType
                      .replace('_', ' ')
                      .split(' ')
                      .map((w: string) => w.charAt(0).toUpperCase() + w.slice(1))
                      .join(' ')}
                  </p>

                  {/* Expanded content */}
                  {expandedIds.has(explanation.id) && (
                    <div className="mt-3 pt-3 border-t border-[#D7C9AE]/50">
                      <p className="text-xs text-[#2D2D2D] leading-relaxed">
                        {explanation.rationale}
                      </p>

                      {/* Citations */}
                      {explanation.citationIds && explanation.citationIds.length > 0 && (
                        <div className="mt-3 text-xs">
                          <p className="font-medium text-[#2D2D2D] mb-2">Evidence:</p>
                          <div className="space-y-1">
                            {explanation.citationIds.map((cid: string, i: number) => (
                              <p key={cid} className="text-[#A68763] hover:underline">
                                [Citation #{i + 1}]
                              </p>
                            ))}
                          </div>
                        </div>
                      )}

                      {/* Confidence Score */}
                      <div className="mt-3 pt-3 border-t border-[#D7C9AE]/50 flex items-center gap-2">
                        <span className="text-xs text-[#2D2D2D]">Confidence:</span>
                        <div className="h-1 flex-1 bg-[#D7C9AE] rounded-full overflow-hidden">
                          <div
                            className="h-full bg-[#A68763]"
                            style={{ width: `${(explanation.confidenceScore || 0.8) * 100}%` }}
                          />
                        </div>
                        <span className="text-xs font-medium text-[#2D2D2D]">
                          {Math.round((explanation.confidenceScore || 0.8) * 100)}%
                        </span>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
