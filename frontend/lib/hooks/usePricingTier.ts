/**
 * usePricingTier Hook
 * Manages pricing tier selection for development mode
 */

import { useEffect, useState, useCallback } from 'react';
import { apiClient } from '@/lib/api-client';

// ============ TYPES ============

export type PricingTier = 'basic' | 'pro' | 'enterprise';

export interface TierFeatures {
  tier: PricingTier;
  name: string;
  monthlyPrice: number;
  currency: string;
  maxIcps: number;
  maxMoves: number;
  features: string[];
  description: string;
}

interface UsePricingTierReturn {
  currentTier: PricingTier | null;
  tierFeatures: TierFeatures | null;
  isLoading: boolean;
  error: string | null;
  setTier: (tier: PricingTier) => Promise<void>;
  getTierInfo: (tier: PricingTier) => TierFeatures;
  isDevelopmentMode: boolean;
  allTiers: TierFeatures[];
}

// ============ TIER CONFIGURATION ============

export const TIER_CONFIG: Record<PricingTier, TierFeatures> = {
  basic: {
    tier: 'basic',
    name: 'Basic',
    monthlyPrice: 2000,
    currency: 'INR',
    maxIcps: 3,
    maxMoves: 5,
    description: 'Perfect for getting started with agent workflows',
    features: [
      'Up to 3 ICPs (Initial Conditions/Premises)',
      'Up to 5 Moves per analysis',
      'Real-time agent monitoring',
      'Token usage tracking',
      'Basic analytics',
      'Email support',
    ],
  },
  pro: {
    tier: 'pro',
    name: 'Professional',
    monthlyPrice: 3500,
    currency: 'INR',
    maxIcps: 6,
    maxMoves: 15,
    description: 'For advanced users and small teams',
    features: [
      'Up to 6 ICPs (Initial Conditions/Premises)',
      'Up to 15 Moves per analysis',
      'Real-time agent monitoring',
      'Token usage tracking with cost breakdown',
      'Advanced analytics',
      'Priority email support',
      'Custom context items',
      'Batch processing',
    ],
  },
  enterprise: {
    tier: 'enterprise',
    name: 'Enterprise',
    monthlyPrice: 5000,
    currency: 'INR',
    maxIcps: 9,
    maxMoves: 999,
    description: 'For large-scale deployments and teams',
    features: [
      'Up to 9 ICPs (Initial Conditions/Premises)',
      'Unlimited Moves per analysis',
      'Real-time agent monitoring',
      'Token usage tracking with detailed analytics',
      'Advanced analytics and reporting',
      '24/7 dedicated support',
      'Custom integrations',
      'Batch processing',
      'API access',
      'Custom SLAs',
      'Team collaboration features',
    ],
  },
};

// ============ UTILITY FUNCTIONS ============

/**
 * Check if running in development mode
 */
export function isDevelopmentMode(): boolean {
  if (typeof window === 'undefined') return false;
  return process.env.NODE_ENV === 'development' || window.location.hostname === 'localhost';
}

/**
 * Format tier price with currency
 */
export function formatTierPrice(price: number, currency: string = 'INR'): string {
  if (currency === 'INR') {
    return `₹${price.toLocaleString('en-IN')}/month`;
  }
  return `$${(price / 100).toLocaleString()}/month`;
}

/**
 * Get color for tier badge
 */
export function getTierColor(tier: PricingTier): string {
  switch (tier) {
    case 'basic':
      return '#3b82f6'; // blue
    case 'pro':
      return '#8b5cf6'; // purple
    case 'enterprise':
      return '#ef4444'; // red
    default:
      return '#6b7280'; // gray
  }
}

/**
 * Get icon for tier
 */
export function getTierIcon(tier: PricingTier): string {
  switch (tier) {
    case 'basic':
      return '⭐';
    case 'pro':
      return '✨';
    case 'enterprise':
      return '🚀';
    default:
      return '•';
  }
}

// ============ HOOK IMPLEMENTATION ============

/**
 * usePricingTier hook
 * Manages pricing tier selection and feature limiting
 */
export function usePricingTier(): UsePricingTierReturn {
  const [currentTier, setCurrentTier] = useState<PricingTier | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [devMode] = useState(isDevelopmentMode());

  /**
   * Fetch current tier from backend
   */
  const fetchCurrentTier = useCallback(async () => {
    if (!devMode) {
      setError('Pricing tier selection is only available in development mode');
      return;
    }

    setIsLoading(true);
    setError(null);
    try {
      const response = await apiClient.getCurrentTier();

      if (response?.error) {
        throw new Error(response.error.message);
      }

      if (response?.data?.tier) {
        setCurrentTier(response.data.tier as PricingTier);
        // Store in localStorage for persistence
        localStorage.setItem('selectedPricingTier', response.data.tier);
      }
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to fetch current tier';
      setError(message);
      console.error('Tier fetch error:', message);

      // Fall back to localStorage
      const savedTier = localStorage.getItem('selectedPricingTier') as PricingTier | null;
      if (savedTier && TIER_CONFIG[savedTier]) {
        setCurrentTier(savedTier);
      } else {
        setCurrentTier('basic'); // Default to basic
      }
    } finally {
      setIsLoading(false);
    }
  }, [devMode]);

  /**
   * Set pricing tier (dev mode only)
   */
  const setTierHandler = useCallback(
    async (tier: PricingTier) => {
      if (!devMode) {
        throw new Error('Pricing tier selection is only available in development mode');
      }

      if (!TIER_CONFIG[tier]) {
        throw new Error(`Invalid tier: ${tier}`);
      }

      setIsLoading(true);
      setError(null);
      try {
        const response = await apiClient.setPricingTier(tier);

        if (response?.error) {
          throw new Error(response.error.message);
        }

        setCurrentTier(tier);
        localStorage.setItem('selectedPricingTier', tier);
        console.log(`✓ Pricing tier updated to: ${tier}`);
      } catch (err) {
        const message = err instanceof Error ? err.message : 'Failed to set pricing tier';
        setError(message);
        console.error('Tier set error:', message);
        throw err;
      } finally {
        setIsLoading(false);
      }
    },
    [devMode]
  );

  /**
   * Get tier info by tier name
   */
  const getTierInfo = useCallback((tier: PricingTier): TierFeatures => {
    return TIER_CONFIG[tier];
  }, []);

  /**
   * Get current tier features
   */
  const tierFeatures = currentTier ? TIER_CONFIG[currentTier] : null;

  /**
   * Initialize tier on mount
   */
  useEffect(() => {
    if (devMode) {
      fetchCurrentTier();
    }
  }, [devMode, fetchCurrentTier]);

  return {
    currentTier,
    tierFeatures,
    isLoading,
    error,
    setTier: setTierHandler,
    getTierInfo,
    isDevelopmentMode: devMode,
    allTiers: Object.values(TIER_CONFIG),
  };
}

/**
 * Hook to check if feature is available in current tier
 */
export function useFeatureAvailable(featureName: string) {
  const { currentTier } = usePricingTier();

  return {
    isAvailable: currentTier ? TIER_CONFIG[currentTier].features.includes(featureName) : false,
    currentTier,
  };
}

/**
 * Hook to get tier limits
 */
export function useTierLimits() {
  const { currentTier } = usePricingTier();

  if (!currentTier) {
    return {
      maxIcps: TIER_CONFIG['basic'].maxIcps,
      maxMoves: TIER_CONFIG['basic'].maxMoves,
      currentTier: 'basic' as PricingTier,
    };
  }

  const tierInfo = TIER_CONFIG[currentTier];

  return {
    maxIcps: tierInfo.maxIcps,
    maxMoves: tierInfo.maxMoves,
    currentTier,
  };
}

/**
 * Hook to format tier display
 */
export function useTierDisplay(tier: PricingTier) {
  const tierInfo = TIER_CONFIG[tier];

  return {
    name: tierInfo.name,
    icon: getTierIcon(tier),
    color: getTierColor(tier),
    price: formatTierPrice(tierInfo.monthlyPrice, tierInfo.currency),
    description: tierInfo.description,
    features: tierInfo.features,
    maxIcps: tierInfo.maxIcps,
    maxMoves: tierInfo.maxMoves,
  };
}
