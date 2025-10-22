/**
 * PricingTierSelector Component
 * Allows developers to switch between pricing tiers in dev mode
 * NEW FEATURE: Pricing tier selection with feature limiting
 */

'use client';

import React, { useState } from 'react';
import {
  usePricingTier,
  TIER_CONFIG,
  getTierIcon,
  getTierColor,
  formatTierPrice,
  isDevelopmentMode,
  type PricingTier,
} from '@/lib/hooks/usePricingTier';

interface PricingTierSelectorProps {
  onTierChange?: (tier: PricingTier) => void;
  showDescription?: boolean;
  compact?: boolean;
}

/**
 * Main PricingTierSelector component
 * Shows 3 tiers and allows selection in dev mode only
 */
export function PricingTierSelector({
  onTierChange,
  showDescription = true,
  compact = false,
}: PricingTierSelectorProps) {
  const { currentTier, setTier, isLoading, error, isDevelopmentMode: isDevMode } =
    usePricingTier();
  const [selectedTier, setSelectedTier] = useState<PricingTier | null>(currentTier);

  if (!isDevMode) {
    return null;
  }

  const handleTierChange = async (tier: PricingTier) => {
    try {
      setSelectedTier(tier);
      await setTier(tier);
      onTierChange?.(tier);
    } catch (err) {
      console.error('Failed to change tier:', err);
      setSelectedTier(currentTier);
    }
  };

  if (compact) {
    return (
      <div className="rounded-lg border border-amber-200 bg-amber-50 p-3">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-xs font-semibold uppercase text-amber-900">Dev Mode</p>
            <p className="text-sm font-medium text-amber-900">
              {selectedTier ? TIER_CONFIG[selectedTier].name : 'Select tier'}
            </p>
          </div>
          <select
            value={selectedTier || ''}
            onChange={(e) => handleTierChange(e.target.value as PricingTier)}
            disabled={isLoading}
            className="rounded-md border border-amber-300 bg-white px-2 py-1 text-xs font-medium text-amber-900 hover:bg-amber-100 disabled:opacity-50"
          >
            <option value="">Select tier...</option>
            {Object.entries(TIER_CONFIG).map(([tier, config]) => (
              <option key={tier} value={tier}>
                {config.name} ({config.maxIcps} ICPs, {config.maxMoves} Moves)
              </option>
            ))}
          </select>
        </div>
      </div>
    );
  }

  return (
    <div className="w-full space-y-6 rounded-lg border border-gray-200 bg-white p-6 shadow-sm">
      {/* Dev Mode Banner */}
      <div className="rounded-lg border border-amber-200 bg-amber-50 p-4">
        <div className="flex items-start gap-3">
          <span className="text-xl">🛠️</span>
          <div>
            <p className="font-semibold text-amber-900">Development Mode</p>
            <p className="mt-1 text-sm text-amber-800">
              You can change pricing tiers in development mode. This feature is disabled in production.
            </p>
          </div>
        </div>
      </div>

      {/* Header */}
      <div>
        <h2 className="text-lg font-semibold text-gray-900">Pricing Tiers</h2>
        <p className="mt-1 text-sm text-gray-600">Select a pricing tier to test feature limiting</p>
      </div>

      {/* Tier Cards */}
      <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
        {Object.entries(TIER_CONFIG).map(([tierKey, tier]) => {
          const isSelected = selectedTier === tierKey;
          const color = getTierColor(tierKey as PricingTier);
          const icon = getTierIcon(tierKey as PricingTier);

          return (
            <div
              key={tierKey}
              className={`relative rounded-lg border-2 p-6 transition-all ${
                isSelected
                  ? 'border-current shadow-lg'
                  : 'border-gray-200 hover:border-gray-300'
              }`}
              style={{
                borderColor: isSelected ? color : undefined,
                backgroundColor: isSelected ? `${color}08` : undefined,
              }}
            >
              {/* Badge */}
              {isSelected && (
                <div
                  className="absolute right-4 top-4 rounded-full px-3 py-1 text-xs font-semibold text-white"
                  style={{ backgroundColor: color }}
                >
                  Selected
                </div>
              )}

              {/* Header */}
              <div className="flex items-start gap-2">
                <span className="text-2xl">{icon}</span>
                <div className="flex-1">
                  <h3 className="text-lg font-semibold text-gray-900">{tier.name}</h3>
                  <p className="mt-1 text-xs text-gray-600">{tier.description}</p>
                </div>
              </div>

              {/* Price */}
              <div className="mt-4 space-y-1 border-t border-gray-200 pt-4">
                <p className="text-xs font-medium uppercase text-gray-500">Price</p>
                <p className="text-2xl font-bold text-gray-900">
                  {formatTierPrice(tier.monthlyPrice, tier.currency)}
                </p>
              </div>

              {/* Limits */}
              <div className="mt-4 space-y-2 border-t border-gray-200 pt-4">
                <p className="text-xs font-medium uppercase text-gray-500">Limits</p>
                <div className="space-y-1 text-sm text-gray-700">
                  <div className="flex items-center justify-between">
                    <span>Max ICPs</span>
                    <span className="font-semibold">{tier.maxIcps}</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span>Max Moves</span>
                    <span className="font-semibold">
                      {tier.maxMoves === 999 ? 'Unlimited' : tier.maxMoves}
                    </span>
                  </div>
                </div>
              </div>

              {/* Features */}
              <div className="mt-4 space-y-2 border-t border-gray-200 pt-4">
                <p className="text-xs font-medium uppercase text-gray-500">Features</p>
                <ul className="space-y-1 text-xs text-gray-600">
                  {tier.features.slice(0, 4).map((feature, idx) => (
                    <li key={idx} className="flex items-start gap-2">
                      <span
                        className="mt-1 flex-shrink-0"
                        style={{ color }}
                      >
                        ✓
                      </span>
                      <span>{feature}</span>
                    </li>
                  ))}
                  {tier.features.length > 4 && (
                    <li className="italic text-gray-500">
                      +{tier.features.length - 4} more features
                    </li>
                  )}
                </ul>
              </div>

              {/* Select Button */}
              <button
                onClick={() => handleTierChange(tierKey as PricingTier)}
                disabled={isSelected || isLoading}
                className={`mt-6 w-full rounded-md py-2 text-sm font-medium transition-all ${
                  isSelected
                    ? 'bg-gray-100 text-gray-600 cursor-default'
                    : 'border text-gray-900 hover:bg-gray-50'
                }`}
                style={{
                  borderColor: color,
                  backgroundColor: isSelected ? `${color}20` : undefined,
                  color: isSelected ? color : undefined,
                }}
              >
                {isLoading ? 'Changing...' : isSelected ? 'Current Tier' : 'Select Tier'}
              </button>
            </div>
          );
        })}
      </div>

      {/* Error Message */}
      {error && (
        <div className="rounded-lg border border-red-200 bg-red-50 p-4">
          <p className="text-sm font-medium text-red-900">Error</p>
          <p className="mt-1 text-sm text-red-700">{error}</p>
        </div>
      )}

      {/* Current Tier Details */}
      {selectedTier && (
        <div className="rounded-lg border border-blue-200 bg-blue-50 p-4">
          <h3 className="font-semibold text-blue-900">
            {TIER_CONFIG[selectedTier].name} Plan Details
          </h3>
          <div className="mt-3 space-y-2 text-sm text-blue-800">
            <div className="flex items-center justify-between">
              <span>Maximum ICPs (Initial Conditions):</span>
              <span className="font-semibold">{TIER_CONFIG[selectedTier].maxIcps}</span>
            </div>
            <div className="flex items-center justify-between">
              <span>Maximum Moves per Analysis:</span>
              <span className="font-semibold">
                {TIER_CONFIG[selectedTier].maxMoves === 999
                  ? 'Unlimited'
                  : TIER_CONFIG[selectedTier].maxMoves}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span>Monthly Price:</span>
              <span className="font-semibold">
                {formatTierPrice(TIER_CONFIG[selectedTier].monthlyPrice, 'INR')}
              </span>
            </div>
          </div>
          <div className="mt-3 border-t border-blue-200 pt-3">
            <p className="text-xs font-medium text-blue-700">All Features:</p>
            <ul className="mt-2 space-y-1 text-xs text-blue-800">
              {TIER_CONFIG[selectedTier].features.map((feature, idx) => (
                <li key={idx} className="flex items-start gap-2">
                  <span className="flex-shrink-0">✓</span>
                  <span>{feature}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>
      )}

      {/* Note */}
      <div className="rounded-lg border border-gray-200 bg-gray-50 p-4">
        <p className="text-xs text-gray-600">
          <span className="font-semibold">Note:</span> Pricing tier selection is a development-mode
          feature. In production, tiers are managed through the billing system. Changing tiers will
          immediately apply feature limits to your account.
        </p>
      </div>
    </div>
  );
}

/**
 * Tier Badge Component - Shows current tier
 */
export function TierBadge() {
  const { currentTier } = usePricingTier();

  if (!currentTier) return null;

  const tier = TIER_CONFIG[currentTier];
  const color = getTierColor(currentTier);
  const icon = getTierIcon(currentTier);

  return (
    <div
      className="inline-flex items-center gap-2 rounded-full px-3 py-1"
      style={{
        backgroundColor: `${color}15`,
        color: color,
      }}
    >
      <span>{icon}</span>
      <span className="text-xs font-semibold">{tier.name}</span>
    </div>
  );
}

/**
 * Tier Limits Display - Shows current tier's limits
 */
export function TierLimitsDisplay() {
  const { currentTier } = usePricingTier();

  if (!currentTier) return null;

  const tier = TIER_CONFIG[currentTier];
  const color = getTierColor(currentTier);

  return (
    <div className="space-y-2 rounded-lg border border-gray-200 bg-gray-50 p-4">
      <h3
        className="text-sm font-semibold"
        style={{ color }}
      >
        {tier.name} Plan Limits
      </h3>
      <div className="space-y-2 text-sm text-gray-700">
        <div className="flex items-center justify-between">
          <span>Maximum ICPs:</span>
          <span className="font-semibold">{tier.maxIcps}</span>
        </div>
        <div className="flex items-center justify-between">
          <span>Maximum Moves:</span>
          <span className="font-semibold">
            {tier.maxMoves === 999 ? 'Unlimited' : tier.maxMoves}
          </span>
        </div>
      </div>
    </div>
  );
}

/**
 * Feature Availability Indicator
 */
export function FeatureAvailability({ feature }: { feature: string }) {
  const { currentTier } = usePricingTier();

  if (!currentTier) return null;

  const isAvailable = TIER_CONFIG[currentTier].features.includes(feature);
  const color = getTierColor(currentTier);

  return (
    <div
      className="inline-flex items-center gap-1 rounded-full px-2 py-1 text-xs"
      style={{
        backgroundColor: isAvailable ? `${color}15` : '#e5e7eb',
        color: isAvailable ? color : '#6b7280',
      }}
    >
      <span>{isAvailable ? '✓' : '✕'}</span>
      <span>{feature}</span>
    </div>
  );
}
