'use client';

import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Modal } from '@/components/ui/Modal';
import { TypingIndicator } from '@/components/ui/TypingIndicator';
import { SkeletonCard } from '@/components/ui/Skeleton';

export default function StrategyPage() {
  const [loading, setLoading] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [strategy, setStrategy] = useState<any>(null);
  const [showSection, setShowSection] = useState<string | null>(null);

  useEffect(() => {
    fetchStrategy();
  }, []);

  const fetchStrategy = async () => {
    setLoading(true);
    try {
      const businessId = localStorage.getItem('business_id');
      const response = await fetch(`/api/strategy/${businessId}`);
      const result = await response.json();
      setStrategy(result.strategy);
    } catch (error) {
      console.error('Error:', error);
    } finally {
      setLoading(false);
    }
  };

  const generateStrategy = async () => {
    setGenerating(true);
    try {
      const businessId = localStorage.getItem('business_id');
      const response = await fetch(`/api/strategy/${businessId}`, { method: 'POST' });
      const result = await response.json();
      setStrategy(result.strategy);
    } catch (error) {
      console.error('Error:', error);
    } finally {
      setGenerating(false);
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

  if (!strategy) {
    return (
      <div className="max-w-content mx-auto px-6">
        <Card className="p-12 text-center">
          <div className="w-24 h-24 mx-auto mb-6 rounded-2xl bg-gradient-to-br from-barley to-akaroa flex items-center justify-center">
            <svg className="w-12 h-12 text-mine" fill="currentColor" viewBox="0 0 20 20">
              <path d="M3 4a1 1 0 011-1h12a1 1 0 011 1v2a1 1 0 01-1 1H4a1 1 0 01-1-1V4zM3 10a1 1 0 011-1h6a1 1 0 011 1v6a1 1 0 01-1 1H4a1 1 0 01-1-1v-6zM14 9a1 1 0 00-1 1v6a1 1 0 001 1h2a1 1 0 001-1v-6a1 1 0 00-1-1h-2z" />
            </svg>
          </div>
          <h2 className="text-h1 text-whiterock mb-4">build your strategy</h2>
          <p className="text-secondary mb-8 max-w-md mx-auto">
            create comprehensive 7Ps marketing mix, define north star metric, and set strategic bets
          </p>
          <Button variant="primary" onClick={generateStrategy} disabled={generating}>
            {generating ? (
              <span className="flex items-center gap-3">
                <TypingIndicator />
                <span>building strategy...</span>
              </span>
            ) : (
              'generate strategy'
            )}
          </Button>
        </Card>
      </div>
    );
  }

  return (
    <div className="max-w-content mx-auto px-6 space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-display text-whiterock mb-2">marketing strategy</h1>
          <p className="text-secondary">7Ps framework + north star + strategic bets</p>
        </div>
        <Button variant="ghost" onClick={generateStrategy} disabled={generating}>
          {generating ? <TypingIndicator /> : 'regenerate'}
        </Button>
      </div>

      {/* North Star Metric */}
      <Card className="p-8 bg-gradient-to-br from-[color:rgba(166,135,99,.08)] to-transparent">
        <div className="flex items-center gap-4 mb-4">
          <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-barley to-akaroa flex items-center justify-center">
            <svg className="w-8 h-8 text-mine" fill="currentColor" viewBox="0 0 20 20">
              <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
            </svg>
          </div>
          <div className="flex-1">
            <h2 className="text-h2 text-whiterock mb-1">north star metric</h2>
            <p className="text-display text-barley">{strategy.north_star?.metric || 'Active Users'}</p>
          </div>
        </div>
        <p className="text-secondary mb-4">{strategy.north_star?.why}</p>
        <div className="grid grid-cols-3 gap-4">
          {strategy.north_star?.sub_metrics?.map((metric: string, i: number) => (
            <div key={i} className="p-3 rounded-lg bg-[color:rgba(255,255,255,.02)]">
              <p className="text-xs text-muted mb-1">supporting</p>
              <p className="text-sm text-whiterock">{metric}</p>
            </div>
          ))}
        </div>
      </Card>

      {/* 7Ps Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {['product', 'price', 'place', 'promotion', 'people', 'process', 'physical_evidence'].map((p, i) => (
          <motion.div
            key={p}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.05 }}
          >
            <Card
              className="p-6 cursor-pointer h-full"
              hover
              onClick={() => setShowSection(p)}
            >
              <div className="flex items-center justify-between mb-3">
                <h3 className="text-h2 text-whiterock capitalize">{p.replace(/_/g, ' ')}</h3>
                <svg className="w-5 h-5 text-muted" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                </svg>
              </div>
              <p className="text-sm text-secondary line-clamp-3">
                {strategy['7ps']?.[p]?.summary || 'Click to view details'}
              </p>
            </Card>
          </motion.div>
        ))}
      </div>

      {/* Strategic Bets */}
      <Card className="p-8">
        <h2 className="text-h2 text-whiterock mb-6">strategic bets</h2>
        <div className="space-y-4">
          {strategy.bets?.map((bet: any, i: number) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: i * 0.1 }}
              className="p-6 rounded-xl bg-[color:rgba(255,255,255,.02)] border border-[color:var(--hairline)]"
            >
              <div className="flex items-start justify-between mb-3">
                <div className="flex-1">
                  <h3 className="text-lg text-whiterock font-semibold mb-2">{bet.hypothesis}</h3>
                  <p className="text-sm text-secondary mb-4">{bet.rationale}</p>
                </div>
                <div className={`px-3 py-1 rounded-full text-xs font-semibold ${
                  bet.risk_level === 'high'
                    ? 'bg-red-500 bg-opacity-20 text-red-400'
                    : bet.risk_level === 'medium'
                    ? 'bg-yellow-500 bg-opacity-20 text-yellow-400'
                    : 'bg-green-500 bg-opacity-20 text-green-400'
                }`}>
                  {bet.risk_level} risk
                </div>
              </div>

              <div className="grid grid-cols-3 gap-4 mb-4">
                <div className="p-3 rounded-lg bg-[color:rgba(255,255,255,.02)]">
                  <p className="text-xs text-muted mb-1">success threshold</p>
                  <p className="text-sm text-whiterock">{bet.success_threshold?.target}</p>
                </div>
                <div className="p-3 rounded-lg bg-[color:rgba(255,255,255,.02)]">
                  <p className="text-xs text-muted mb-1">kill switch</p>
                  <p className="text-sm text-whiterock">{bet.kill_switch?.threshold}</p>
                </div>
                <div className="p-3 rounded-lg bg-[color:rgba(255,255,255,.02)]">
                  <p className="text-xs text-muted mb-1">resources</p>
                  <p className="text-sm text-whiterock">{bet.resources?.budget_percentage}% budget</p>
                </div>
              </div>

              <div className="flex items-center gap-2">
                <div className="flex-1 h-2 bg-[color:var(--hairline)] rounded-full overflow-hidden">
                  <motion.div
                    initial={{ width: 0 }}
                    animate={{ width: `${bet.confidence * 100}%` }}
                    className="h-full bg-barley"
                  />
                </div>
                <span className="text-xs text-muted">{(bet.confidence * 100).toFixed(0)}% confidence</span>
              </div>
            </motion.div>
          ))}
        </div>
      </Card>

      {/* 7Ps Detail Modal */}
      <Modal
        isOpen={showSection !== null}
        onClose={() => setShowSection(null)}
        title={showSection ? showSection.replace(/_/g, ' ').toUpperCase() : ''}
        size="lg"
      >
        {showSection && strategy['7ps']?.[showSection] && (
          <div className="space-y-4">
            {Object.entries(strategy['7ps'][showSection]).map(([key, value]) => (
              <div key={key}>
                <h3 className="text-sm text-muted mb-2 capitalize">{key.replace(/_/g, ' ')}</h3>
                <div className="p-4 rounded-lg bg-[color:rgba(255,255,255,.02)]">
                  {Array.isArray(value) ? (
                    <ul className="space-y-2">
                      {value.map((item, i) => (
                        <li key={i} className="text-sm text-secondary flex gap-2">
                          <span className="text-barley"></span>
                          <span>{item}</span>
                        </li>
                      ))}
                    </ul>
                  ) : (
                    <p className="text-sm text-secondary">{value as string}</p>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </Modal>

      {/* Next Step */}
      <Card className="p-6 bg-gradient-to-br from-[color:rgba(166,135,99,.08)] to-transparent border-barley border-opacity-20">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-h2 text-whiterock mb-2">next: create campaigns</h3>
            <p className="text-secondary">build content calendars and execute your moves</p>
          </div>
          <Button variant="primary" onClick={() => window.location.href = '/dashboard/moves'}>
            continue 
          </Button>
        </div>
      </Card>
    </div>
  );
}
