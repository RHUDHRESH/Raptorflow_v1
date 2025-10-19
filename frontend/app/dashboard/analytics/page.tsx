'use client';

import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Modal } from '@/components/ui/Modal';
import { TypingIndicator } from '@/components/ui/TypingIndicator';
import { ImagePlaceholder } from '@/components/ui/ImagePlaceholder';
import { SkeletonCard } from '@/components/ui/Skeleton';

export default function AnalyticsPage() {
  const [loading, setLoading] = useState(false);
  const [moves, setMoves] = useState<any[]>([]);
  const [selectedMove, setSelectedMove] = useState<any>(null);
  const [showMetrics, setShowMetrics] = useState(false);
  const [analyzing, setAnalyzing] = useState(false);
  const [analysis, setAnalysis] = useState<any>(null);
  const [metricsData, setMetricsData] = useState({
    impressions: '',
    engagements: '',
    clicks: '',
    conversions: '',
    revenue: ''
  });

  useEffect(() => {
    fetchMoves();
  }, []);

  const fetchMoves = async () => {
    setLoading(true);
    try {
      const businessId = localStorage.getItem('business_id');
      const response = await fetch(`/api/moves/business/${businessId}`);
      const result = await response.json();
      setMoves(result.moves || []);
    } catch (error) {
      console.error('Error:', error);
    } finally {
      setLoading(false);
    }
  };

  const analyzePerformance = async () => {
    setAnalyzing(true);
    try {
      const response = await fetch('/api/analytics/measure', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          move_id: selectedMove.id,
          metrics: {
            impressions: parseInt(metricsData.impressions),
            engagements: parseInt(metricsData.engagements),
            clicks: parseInt(metricsData.clicks),
            conversions: parseInt(metricsData.conversions),
            revenue: parseFloat(metricsData.revenue)
          }
        })
      });
      const result = await response.json();
      setAnalysis(result);
      setShowMetrics(false);
    } catch (error) {
      console.error('Error:', error);
    } finally {
      setAnalyzing(false);
    }
  };

  if (loading) {
    return (
      <div className="max-w-content mx-auto px-6 space-y-8">
        <SkeletonCard />
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <SkeletonCard />
          <SkeletonCard />
        </div>
      </div>
    );
  }

  if (moves.length === 0) {
    return (
      <div className="max-w-content mx-auto px-6">
        <Card className="p-12 text-center">
          <div className="w-24 h-24 mx-auto mb-6 rounded-2xl bg-gradient-to-br from-barley to-akaroa flex items-center justify-center">
            <svg className="w-12 h-12 text-mine" fill="currentColor" viewBox="0 0 20 20">
              <path d="M2 11a1 1 0 011-1h2a1 1 0 011 1v5a1 1 0 01-1 1H3a1 1 0 01-1-1v-5zM8 7a1 1 0 011-1h2a1 1 0 011 1v9a1 1 0 01-1 1H9a1 1 0 01-1-1V7zM14 4a1 1 0 011-1h2a1 1 0 011 1v12a1 1 0 01-1 1h-2a1 1 0 01-1-1V4z" />
            </svg>
          </div>
          <h2 className="text-h1 text-whiterock mb-4">no campaigns to analyze</h2>
          <p className="text-secondary mb-8 max-w-md mx-auto">
            create and run campaigns first, then come back to measure performance
          </p>
          <Button variant="primary" onClick={() => window.location.href = '/dashboard/moves'}>
            create campaign
          </Button>
        </Card>
      </div>
    );
  }

  return (
    <div className="max-w-content mx-auto px-6 space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-display text-whiterock mb-2">analytics</h1>
        <p className="text-secondary">amec framework + clv + route-back logic</p>
      </div>

      {/* Select Campaign */}
      {!selectedMove && (
        <Card className="p-8">
          <h2 className="text-h2 text-whiterock mb-6">select campaign to analyze</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {moves.map((move, i) => (
              <motion.div
                key={move.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.05 }}
              >
                <button
                  onClick={() => {
                    setSelectedMove(move);
                    setShowMetrics(true);
                  }}
                  className="w-full p-6 rounded-xl bg-[color:rgba(255,255,255,.02)] border border-[color:var(--hairline)] text-left hover:border-barley transition-all"
                >
                  <h3 className="text-lg text-whiterock mb-2">{move.goal}</h3>
                  <p className="text-sm text-secondary mb-3 capitalize">{move.platform}  {move.duration_days} days</p>
                  <div className={`inline-block px-3 py-1 rounded-full text-xs font-semibold ${
                    move.status === 'active'
                      ? 'bg-green-500 bg-opacity-20 text-green-400'
                      : 'bg-gray-500 bg-opacity-20 text-gray-400'
                  }`}>
                    {move.status}
                  </div>
                </button>
              </motion.div>
            ))}
          </div>
        </Card>
      )}

      {/* Analysis Results */}
      {analysis && (
        <>
          {/* AMEC Ladder */}
          <Card className="p-8">
            <h2 className="text-h2 text-whiterock mb-6">amec evaluation ladder</h2>
            <div className="space-y-6">
              {['input', 'output', 'outcome', 'impact'].map((level, i) => {
                const data = analysis.amec_analysis?.amec_analysis?.[level];
                return (
                  <div key={level}>
                    <div className="flex items-center justify-between mb-3">
                      <h3 className="text-lg text-whiterock capitalize">{level}</h3>
                      <div className="text-h2 text-barley">
                        {(data?.score * 100).toFixed(0)}%
                      </div>
                    </div>
                    <div className="h-2 bg-[color:var(--hairline)] rounded-full overflow-hidden mb-3">
                      <motion.div
                        initial={{ width: 0 }}
                        animate={{ width: `${data?.score * 100}%` }}
                        className="h-full bg-barley"
                      />
                    </div>
                    <p className="text-sm text-secondary">{data?.notes || data?.summary}</p>
                  </div>
                );
              })}
            </div>
          </Card>

          {/* CLV Analysis */}
          <Card className="p-8">
            <h2 className="text-h2 text-whiterock mb-6">customer lifetime value</h2>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
              {[
                { label: 'CLV (NPV)', value: `${analysis.clv_analysis?.clv_metrics?.npv_clv?.toFixed(0)}` },
                { label: 'CAC', value: `${analysis.clv_analysis?.clv_metrics?.cac?.toFixed(0)}` },
                { label: 'LTV:CAC', value: `${analysis.clv_analysis?.clv_metrics?.ltv_cac_ratio?.toFixed(1)}:1` },
                { label: 'Payback', value: `${analysis.clv_analysis?.clv_metrics?.payback_period_months?.toFixed(1)}mo` }
              ].map((metric, i) => (
                <div key={i} className="p-4 rounded-xl bg-[color:rgba(255,255,255,.02)]">
                  <p className="text-xs text-muted mb-2">{metric.label}</p>
                  <p className="text-h2 text-whiterock">{metric.value}</p>
                </div>
              ))}
            </div>

            <div className={`mt-6 p-4 rounded-lg ${
              analysis.clv_analysis?.health === 'HEALTHY'
                ? 'bg-green-500 bg-opacity-10 border border-green-500 border-opacity-30'
                : analysis.clv_analysis?.health === 'VIABLE'
                ? 'bg-yellow-500 bg-opacity-10 border border-yellow-500 border-opacity-30'
                : 'bg-red-500 bg-opacity-10 border border-red-500 border-opacity-30'
            }`}>
              <p className="text-sm text-whiterock font-semibold mb-1">
                Health: {analysis.clv_analysis?.health}
              </p>
              <p className="text-sm text-secondary">{analysis.clv_analysis?.health_note}</p>
            </div>
          </Card>

          {/* Route-Back Decision */}
          {analysis.route_back_needed && (
            <Card className="p-8 bg-gradient-to-br from-red-500 to-transparent bg-opacity-5 border-red-500 border-opacity-30">
              <div className="flex items-start gap-4">
                <div className="w-12 h-12 rounded-xl bg-red-500 bg-opacity-20 flex items-center justify-center flex-shrink-0">
                  <svg className="w-6 h-6 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                  </svg>
                </div>
                <div className="flex-1">
                  <h3 className="text-h2 text-whiterock mb-2">route-back required</h3>
                  <p className="text-sm text-secondary mb-4">
                    Campaign performance indicates need to revisit: <span className="text-red-400 font-semibold">{analysis.route_back_to}</span>
                  </p>
                  <div className="space-y-2 mb-4">
                    {analysis.route_back_decision?.evidence?.map((evidence: string, i: number) => (
                      <div key={i} className="flex gap-2">
                        <span className="text-red-400"></span>
                        <p className="text-sm text-secondary">{evidence}</p>
                      </div>
                    ))}
                  </div>
                  <Button
                    variant="ghost"
                    onClick={() => window.location.href = `/dashboard/${analysis.route_back_to}`}
                  >
                    go to {analysis.route_back_to} 
                  </Button>
                </div>
              </div>
            </Card>
          )}

          {/* Visualization Placeholders */}
          <Card className="p-8">
            <h2 className="text-h2 text-whiterock mb-6">performance visualizations</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {[1, 2, 3, 4].map((i) => (
                <ImagePlaceholder
                  key={i}
                  src={`/images/chart-${i}.jpg`}
                  alt={`Chart ${i}`}
                  aspectRatio="aspect-video"
                  caption={`visualization ${i}`}
                />
              ))}
            </div>
          </Card>
        </>
      )}

      {/* Metrics Input Modal */}
      <Modal
        isOpen={showMetrics}
        onClose={() => setShowMetrics(false)}
        title="enter campaign metrics"
        size="md"
      >
        <div className="space-y-4">
          <p className="text-sm text-secondary mb-6">
            provide performance data for: <span className="text-whiterock font-semibold">{selectedMove?.goal}</span>
          </p>

          <Input
            label="impressions"
            type="number"
            placeholder="10000"
            value={metricsData.impressions}
            onChange={(e) => setMetricsData({ ...metricsData, impressions: e.target.value })}
          />

          <Input
            label="engagements (likes, shares, comments)"
            type="number"
            placeholder="500"
            value={metricsData.engagements}
            onChange={(e) => setMetricsData({ ...metricsData, engagements: e.target.value })}
          />

          <Input
            label="clicks"
            type="number"
            placeholder="200"
            value={metricsData.clicks}
            onChange={(e) => setMetricsData({ ...metricsData, clicks: e.target.value })}
          />

          <Input
            label="conversions"
            type="number"
            placeholder="25"
            value={metricsData.conversions}
            onChange={(e) => setMetricsData({ ...metricsData, conversions: e.target.value })}
          />

          <Input
            label="revenue ()"
            type="number"
            placeholder="50000"
            value={metricsData.revenue}
            onChange={(e) => setMetricsData({ ...metricsData, revenue: e.target.value })}
          />

          <Button
            variant="primary"
            className="w-full"
            onClick={analyzePerformance}
            disabled={analyzing}
          >
            {analyzing ? (
              <span className="flex items-center gap-3">
                <TypingIndicator />
                <span>analyzing...</span>
              </span>
            ) : (
              'analyze performance'
            )}
          </Button>
        </div>
      </Modal>
    </div>
  );
}
