'use client';

import { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Modal } from '@/components/ui/Modal';
import { TypingIndicator } from '@/components/ui/TypingIndicator';
import { ImagePlaceholder } from '@/components/ui/ImagePlaceholder';
import { SkeletonCard } from '@/components/ui/Skeleton';

export default function PositioningPage() {
  const [loading, setLoading] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [options, setOptions] = useState<any[]>([]);
  const [selectedIndex, setSelectedIndex] = useState<number | null>(null);
  const [showDetails, setShowDetails] = useState<number | null>(null);

  useEffect(() => {
    fetchPositioning();
  }, []);

  const fetchPositioning = async () => {
    setLoading(true);
    try {
      const businessId = localStorage.getItem('business_id');
      const response = await fetch(`/api/positioning/${businessId}`);
      const result = await response.json();
      if (result?.options) {
        setOptions(result.options);
      }
    } catch (error) {
      console.error('Error:', error);
    } finally {
      setLoading(false);
    }
  };

  const generateOptions = async () => {
    setGenerating(true);
    try {
      const businessId = localStorage.getItem('business_id');
      const response = await fetch(`/api/positioning/${businessId}`, { method: 'POST' });
      const result = await response.json();
      setOptions(result.options);
    } catch (error) {
      console.error('Error:', error);
    } finally {
      setGenerating(false);
    }
  };

  const selectOption = async (index: number) => {
    try {
      const businessId = localStorage.getItem('business_id');
      await fetch(`/api/positioning/${businessId}/select`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ option_index: index })
      });
      setSelectedIndex(index);
      
      // Navigate to ICPs after short delay
      setTimeout(() => {
        window.location.href = '/dashboard/icps';
      }, 1500);
    } catch (error) {
      console.error('Error:', error);
    }
  };

  if (loading) {
    return (
      <div className="max-w-content mx-auto px-6 space-y-8">
        <SkeletonCard />
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <SkeletonCard />
          <SkeletonCard />
          <SkeletonCard />
        </div>
      </div>
    );
  }

  if (!options.length) {
    return (
      <div className="max-w-content mx-auto px-6">
        <Card className="p-12 text-center">
          <div className="w-24 h-24 mx-auto mb-6 rounded-2xl bg-gradient-to-br from-barley to-akaroa flex items-center justify-center">
            <svg className="w-12 h-12 text-mine" fill="currentColor" viewBox="0 0 20 20">
              <path d="M9 2a1 1 0 000 2h2a1 1 0 100-2H9z" />
              <path fillRule="evenodd" d="M4 5a2 2 0 012-2 3 3 0 003 3h2a3 3 0 003-3 2 2 0 012 2v11a2 2 0 01-2 2H6a2 2 0 01-2-2V5zm3 4a1 1 0 000 2h.01a1 1 0 100-2H7zm3 0a1 1 0 000 2h3a1 1 0 100-2h-3zm-3 4a1 1 0 100 2h.01a1 1 0 100-2H7zm3 0a1 1 0 100 2h3a1 1 0 100-2h-3z" clipRule="evenodd" />
            </svg>
          </div>
          <h2 className="text-h1 text-whiterock mb-4">create positioning options</h2>
          <p className="text-secondary mb-8 max-w-md mx-auto">
            using ries & trout laws, we'll generate 3 distinct positioning strategies for your business
          </p>
          <Button variant="primary" onClick={generateOptions} disabled={generating}>
            {generating ? (
              <span className="flex items-center gap-3">
                <TypingIndicator />
                <span>generating options...</span>
              </span>
            ) : (
              'generate positioning'
            )}
          </Button>
        </Card>
      </div>
    );
  }

  return (
    <div className="max-w-content mx-auto px-6 space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-display text-whiterock mb-2">choose your position</h1>
        <p className="text-secondary">select the positioning that best captures your unique value</p>
      </div>

      {/* Options Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <AnimatePresence>
          {options.map((option, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: index * 0.1 }}
            >
              <Card
                className={`p-6 cursor-pointer transition-all ${
                  selectedIndex === index
                    ? 'ring-2 ring-barley shadow-focus'
                    : 'hover:shadow-card-hover'
                }`}
                onClick={() => setShowDetails(index)}
              >
                {/* Score Badge */}
                <div className="flex items-center justify-between mb-4">
                  <span className="text-xs text-muted">option {index + 1}</span>
                  <div className="px-3 py-1 rounded-full bg-[color:rgba(166,135,99,.12)] text-barley text-sm font-semibold">
                    {(option.composite_score * 100).toFixed(0)}%
                  </div>
                </div>

                {/* Word */}
                <h3 className="text-h1 text-whiterock mb-4">{option.word}</h3>

                {/* Big Idea */}
                <div className="mb-4 p-3 rounded-lg bg-[color:rgba(255,255,255,.02)]">
                  <div className="text-xs text-muted mb-1">big idea</div>
                  <p className="text-sm text-secondary">{option.big_idea}</p>
                </div>

                {/* Purple Cow */}
                <div className="mb-6 p-3 rounded-lg bg-[color:rgba(255,255,255,.02)]">
                  <div className="text-xs text-muted mb-1">purple cow moment</div>
                  <p className="text-sm text-secondary line-clamp-2">{option.purple_cow}</p>
                </div>

                {/* Scores */}
                <div className="space-y-2 mb-6">
                  <div className="flex items-center justify-between text-xs">
                    <span className="text-muted">differentiation</span>
                    <span className="text-whiterock">{(option.differentiation_score * 100).toFixed(0)}%</span>
                  </div>
                  <div className="h-1 bg-[color:var(--hairline)] rounded-full overflow-hidden">
                    <motion.div
                      initial={{ width: 0 }}
                      animate={{ width: `${option.differentiation_score * 100}%` }}
                      className="h-full bg-barley"
                    />
                  </div>
                </div>

                {/* Actions */}
                <div className="flex gap-3">
                  <Button
                    variant="ghost"
                    size="sm"
                    className="flex-1"
                    onClick={(e) => {
                      e.stopPropagation();
                      setShowDetails(index);
                    }}
                  >
                    details
                  </Button>
                  <Button
                    variant="primary"
                    size="sm"
                    className="flex-1"
                    onClick={(e) => {
                      e.stopPropagation();
                      selectOption(index);
                    }}
                    disabled={selectedIndex !== null}
                  >
                    {selectedIndex === index ? ' selected' : 'select'}
                  </Button>
                </div>
              </Card>
            </motion.div>
          ))}
        </AnimatePresence>
      </div>

      {/* Details Modal */}
      <Modal
        isOpen={showDetails !== null}
        onClose={() => setShowDetails(null)}
        title={showDetails !== null ? options[showDetails]?.word : ''}
        size="lg"
      >
        {showDetails !== null && (
          <div className="space-y-6">
            {/* Rationale */}
            <div>
              <h3 className="text-h2 text-whiterock mb-3">rationale</h3>
              <p className="text-secondary">{options[showDetails].rationale}</p>
            </div>

            {/* Visual Hammers */}
            <div>
              <h3 className="text-h2 text-whiterock mb-3">visual hammer concepts</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {options[showDetails].visual_hammers?.slice(0, 4).map((hammer: any, i: number) => (
                  <div key={i} className="p-4 rounded-xl bg-[color:rgba(255,255,255,.02)] border border-[color:var(--hairline)]">
                    <div className="flex items-center gap-2 mb-2">
                      <span className="text-xs text-muted">concept {i + 1}</span>
                      <span className="text-xs text-barley">({hammer.type})</span>
                    </div>
                    <h4 className="text-sm text-whiterock font-semibold mb-2">{hammer.name}</h4>
                    <p className="text-xs text-secondary">{hammer.description}</p>
                  </div>
                ))}
              </div>
            </div>

            {/* Sacrifices Required */}
            <div>
              <h3 className="text-h2 text-whiterock mb-3">required sacrifices</h3>
              <div className="space-y-3">
                {options[showDetails].sacrifices?.slice(0, 5).map((sacrifice: any, i: number) => (
                  <div key={i} className="flex gap-3">
                    <div className={`w-6 h-6 rounded flex items-center justify-center flex-shrink-0 ${
                      sacrifice.difficulty === 'high'
                        ? 'bg-red-500 bg-opacity-20 text-red-400'
                        : sacrifice.difficulty === 'medium'
                        ? 'bg-yellow-500 bg-opacity-20 text-yellow-400'
                        : 'bg-green-500 bg-opacity-20 text-green-400'
                    }`}>
                      !
                    </div>
                    <div>
                      <p className="text-sm text-whiterock">{sacrifice.sacrifice}</p>
                      <p className="text-xs text-muted">{sacrifice.rationale}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Conflicts */}
            {options[showDetails].conflicts?.length > 0 && (
              <div>
                <h3 className="text-h2 text-whiterock mb-3">competitive conflicts</h3>
                <div className="space-y-2">
                  {options[showDetails].conflicts.map((conflict: any, i: number) => (
                    <div key={i} className="p-3 rounded-lg bg-[color:rgba(166,135,99,.08)] border border-barley border-opacity-20">
                      <p className="text-sm text-whiterock">
                        Similar to <span className="font-semibold">{conflict.competitor}</span>: {conflict.their_position}
                      </p>
                      <p className="text-xs text-muted mt-1">
                        Similarity: {(conflict.similarity_score * 100).toFixed(0)}%
                      </p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Action */}
            <div className="pt-4 border-t border-[color:var(--hairline)]">
              <Button
                variant="primary"
                className="w-full"
                onClick={() => {
                  selectOption(showDetails);
                  setShowDetails(null);
                }}
                disabled={selectedIndex !== null}
              >
                {selectedIndex === showDetails ? ' selected' : 'select this positioning'}
              </Button>
            </div>
          </div>
        )}
      </Modal>

      {/* Comparison Table */}
      <Card className="p-8">
        <h2 className="text-h2 text-whiterock mb-6">comparison</h2>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-[color:var(--hairline)]">
                <th className="text-left text-sm text-muted py-3 px-4">metric</th>
                {options.map((_, i) => (
                  <th key={i} className="text-center text-sm text-muted py-3 px-4">option {i + 1}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {['differentiation_score', 'sacrifice_score', 'composite_score'].map((metric) => (
                <tr key={metric} className="border-b border-[color:var(--hairline)]">
                  <td className="text-sm text-secondary py-3 px-4 capitalize">
                    {metric.replace(/_/g, ' ')}
                  </td>
                  {options.map((option, i) => (
                    <td key={i} className="text-center py-3 px-4">
                      <span className="text-whiterock font-semibold">
                        {(option[metric] * 100).toFixed(0)}%
                      </span>
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  );
}
