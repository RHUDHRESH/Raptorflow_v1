/**
 * AISAS Slider Component
 * Interactive slider for positioning on customer journey (0-100)
 * Segments: Attention (red) → Interest (orange) → Search (yellow) → Action (blue) → Share (green)
 */

'use client';

import React, { useState, useRef, useEffect } from 'react';

interface AISASSliderProps {
  value: number; // 0-100
  onChange: (value: number) => void;
  disabled?: boolean;
  showLabel?: boolean;
  size?: 'sm' | 'md' | 'lg';
}

const SEGMENTS = [
  { name: 'Attention', color: 'bg-red-500', range: [0, 20] },
  { name: 'Interest', color: 'bg-orange-500', range: [20, 40] },
  { name: 'Search', color: 'bg-yellow-500', range: [40, 60] },
  { name: 'Action', color: 'bg-blue-500', range: [60, 80] },
  { name: 'Share', color: 'bg-green-500', range: [80, 100] },
];

export default function AISASSlider({
  value,
  onChange,
  disabled = false,
  showLabel = true,
  size = 'md',
}: AISASSliderProps) {
  const sliderRef = useRef<HTMLDivElement>(null);
  const [isDragging, setIsDragging] = useState(false);

  const getCurrentSegment = () => {
    return SEGMENTS.find((seg) => value >= seg.range[0] && value <= seg.range[1]);
  };

  const currentSegment = getCurrentSegment();

  const handleMouseDown = () => {
    setIsDragging(true);
  };

  const handleMouseUp = () => {
    setIsDragging(false);
  };

  useEffect(() => {
    if (!isDragging) return;

    const handleMouseMove = (e: MouseEvent) => {
      if (!sliderRef.current) return;

      const rect = sliderRef.current.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const percentage = Math.max(0, Math.min(100, (x / rect.width) * 100));

      onChange(Math.round(percentage));
    };

    document.addEventListener('mousemove', handleMouseMove);
    document.addEventListener('mouseup', handleMouseUp);

    return () => {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
    };
  }, [isDragging, onChange]);

  const sizeClasses = {
    sm: 'h-1.5',
    md: 'h-2',
    lg: 'h-3',
  };

  const thumbSizeClasses = {
    sm: 'w-3 h-3',
    md: 'w-4 h-4',
    lg: 'w-6 h-6',
  };

  return (
    <div className="w-full">
      {/* Label with current stage */}
      {showLabel && (
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm font-medium text-[#2D2D2D]">AISAS Position</span>
          <div className="flex items-center gap-2">
            <span className={`text-sm font-medium ${currentSegment ? `text-${currentSegment.color.split('-')[1]}-600` : 'text-[#2D2D2D]'}`}>
              {currentSegment?.name || 'Unknown'}
            </span>
            <span className="text-sm text-[#2D2D2D]/60">{value}%</span>
          </div>
        </div>
      )}

      {/* Slider Track */}
      <div
        ref={sliderRef}
        className={`relative w-full rounded-full cursor-pointer overflow-hidden ${sizeClasses[size]} ${disabled ? 'opacity-50 cursor-not-allowed' : ''}`}
        onClick={(e) => {
          if (disabled) return;
          const rect = e.currentTarget.getBoundingClientRect();
          const x = e.clientX - rect.left;
          const percentage = Math.max(0, Math.min(100, (x / rect.width) * 100));
          onChange(Math.round(percentage));
        }}
      >
        {/* Segment background */}
        <div className="absolute inset-0 flex h-full">
          {SEGMENTS.map((segment, i) => (
            <div
              key={i}
              className={`flex-1 ${segment.color} opacity-90`}
              style={{
                width: `${segment.range[1] - segment.range[0]}%`,
              }}
            />
          ))}
        </div>

        {/* Progress fill */}
        <div
          className={`absolute inset-y-0 left-0 ${currentSegment?.color || 'bg-[#A68763]'} transition-all`}
          style={{
            width: `${value}%`,
            opacity: 0.7,
          }}
        />
      </div>

      {/* Slider Thumb */}
      <div
        className={`relative -top-1.5`}
        style={{
          left: `${value}%`,
          transform: 'translateX(-50%)',
        }}
      >
        <div
          onMouseDown={handleMouseDown}
          className={`${thumbSizeClasses[size]} rounded-full bg-white border-2 border-[#A68763] shadow-lg cursor-grab active:cursor-grabbing transition-all ${disabled ? 'pointer-events-none' : ''}`}
        />
      </div>

      {/* Segment Labels */}
      <div className="flex justify-between mt-3 px-1">
        {SEGMENTS.map((segment) => (
          <span key={segment.name} className="text-xs text-[#2D2D2D]/60 flex-1 text-center">
            {segment.name.slice(0, 1)}
          </span>
        ))}
      </div>

      {/* Full segment names on hover (optional) */}
      <div className="mt-2 p-2 bg-[#EAE0D2]/30 rounded-lg text-xs text-[#2D2D2D]/60">
        <strong>AISAS:</strong> Attention → Interest → Search → Action → Share
      </div>
    </div>
  );
}
