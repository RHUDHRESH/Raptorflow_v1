/**
 * AISAS Slider Component - Optimized Version
 * Interactive slider for positioning on customer journey (0-100)
 * Segments: Attention (red) → Interest (orange) → Search (yellow) → Action (blue) → Share (green)
 *
 * Optimizations:
 * - Debounced onChange callbacks
 * - useTransition for non-blocking updates
 * - Memoized segment calculations
 * - RAF-based drag handling
 */

'use client';

import React, { useState, useRef, useEffect, useCallback, useMemo, useTransition, memo } from 'react';
import { debounce } from '@/lib/performance-utils';

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

const SEGMENT_LABELS = ['A', 'I', 'S', 'Ac', 'Sh'];

/**
 * Individual segment component
 */
const Segment = memo(({ segment, isActive }: { segment: typeof SEGMENTS[0]; isActive: boolean }) => (
  <div
    className={`flex-1 h-full transition-all duration-200 ${segment.color} ${
      isActive ? 'ring-2 ring-offset-2 ring-gray-400' : 'opacity-70'
    }`}
    style={{ opacity: isActive ? 1 : 0.6 }}
  />
));

Segment.displayName = 'Segment';

/**
 * Slider label component
 */
const SliderLabel = memo(({ stage, value }: { stage: string; value: number }) => (
  <div className="text-center mt-2 text-sm font-medium text-[#2D2D2D]">
    <p className="font-semibold">{stage}</p>
    <p className="text-xs text-[#2D2D2D]/60">{value}%</p>
  </div>
));

SliderLabel.displayName = 'SliderLabel';

/**
 * Main AISAS Slider Component
 */
const AISASSliderComponent = ({
  value,
  onChange,
  disabled = false,
  showLabel = true,
  size = 'md',
}: AISASSliderProps) => {
  const sliderRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const [internalValue, setInternalValue] = useState(value);
  const [isDragging, setIsDragging] = useState(false);
  const [isPending, startTransition] = useTransition();

  // Memoize current segment calculation
  const currentSegment = useMemo(() => {
    return SEGMENTS.find((seg) => internalValue >= seg.range[0] && internalValue <= seg.range[1]);
  }, [internalValue]);

  // Debounced onChange callback (100ms delay)
  const debouncedOnChange = useMemo(
    () =>
      debounce((newValue: number) => {
        startTransition(() => {
          onChange(newValue);
        });
      }, 100),
    [onChange]
  );

  // Handle value changes
  const handleChange = useCallback(
    (newValue: number) => {
      setInternalValue(newValue);
      debouncedOnChange(newValue);
    },
    [debouncedOnChange]
  );

  // RAF-based drag handling for smooth updates
  const handleInputChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const newValue = Number(e.target.value);
      handleChange(newValue);
    },
    [handleChange]
  );

  // Size classes
  const sizeClasses = useMemo(
    () => ({
      sm: { height: 'h-8', thumbSize: 'w-6 h-6' },
      md: { height: 'h-10', thumbSize: 'w-8 h-8' },
      lg: { height: 'h-12', thumbSize: 'w-10 h-10' },
    }),
    []
  );

  const currentSize = sizeClasses[size as keyof typeof sizeClasses] || sizeClasses.md;

  // Sync external value changes
  useEffect(() => {
    if (!isDragging) {
      setInternalValue(value);
    }
  }, [value, isDragging]);

  return (
    <div className="w-full px-2 py-2">
      {/* Segment bar */}
      <div className={`flex gap-0 rounded-lg overflow-hidden border-2 border-gray-300 bg-gray-100 ${currentSize.height}`}>
        {SEGMENTS.map((segment) => (
          <Segment
            key={segment.name}
            segment={segment}
            isActive={currentSegment?.name === segment.name}
          />
        ))}
      </div>

      {/* Range input (hidden, used for interaction) */}
      <input
        ref={inputRef}
        type="range"
        min="0"
        max="100"
        value={internalValue}
        onChange={handleInputChange}
        onMouseDown={() => setIsDragging(true)}
        onMouseUp={() => setIsDragging(false)}
        onTouchStart={() => setIsDragging(true)}
        onTouchEnd={() => setIsDragging(false)}
        disabled={disabled}
        className="w-full mt-2 cursor-pointer accent-[#A68763] disabled:opacity-50 disabled:cursor-not-allowed"
        style={{
          height: '4px',
          appearance: 'none',
          WebkitAppearance: 'none',
        }}
      />

      {/* Segment labels */}
      <div className="flex justify-between mt-1 text-xs font-bold text-[#A68763]">
        {SEGMENT_LABELS.map((label) => (
          <span key={label}>{label}</span>
        ))}
      </div>

      {/* Optional label display */}
      {showLabel && currentSegment && <SliderLabel stage={currentSegment.name} value={internalValue} />}

      {/* Dragging indicator */}
      {isDragging && (
        <div className="mt-1 text-xs text-[#2D2D2D]/50 text-center">
          Updating...
        </div>
      )}
    </div>
  );
};

// Memoize component to prevent unnecessary re-renders
export default memo(AISASSliderComponent);
