'use client';

import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Modal } from '@/components/ui/Modal';
import { TypingIndicator } from '@/components/ui/TypingIndicator';
import { ImagePlaceholder } from '@/components/ui/ImagePlaceholder';
import { SkeletonCard } from '@/components/ui/Skeleton';

export default function ICPsPage() {
  const [loading, setLoading] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [icps, setIcps] = useState<any[]>([]);
  const [selectedIcp, setSelectedIcp] = useState<any>(null);

  useEffect(() => {
    fetchIcps();
  }, []);

  const fetchIcps = async () => {
    setLoading(true);
    try {
      const businessId = localStorage.getItem('business_id');
      const response = await fetch(`/api/icps/${businessId}`);
      const result = await response.json();
      setIcps(result.icps || []);
    } catch (error) {
      console.error('Error:', error);
    } finally {
      setLoading(false);
    }
  };

  const generateIcps = async () => {
    setGenerating(true);
    try {
      const businessId = localStorage.getItem('business_id');
      const response = await fetch(`/api/icps/${businessId}`, { method: 'POST' });
      const result = await response.json();
      setIcps(result.icps);
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
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <SkeletonCard />
          <SkeletonCard />
          <SkeletonCard />
        </div>
      </div>
    );
  }

  if (!icps.length) {
    return (
      <div className="max-w-content mx-auto px-6">
        <Card className="p-12 text-center">
          <div className="w-24 h-24 mx-auto mb-6 rounded-2xl bg-gradient-to-br from-barley to-akaroa flex items-center justify-center">
            <svg className="w-12 h-12 text-mine" fill="currentColor" viewBox="0 0 20 20">
              <path d="M9 6a3 3 0 11-6 0 3 3 0 016 0zM17 6a3 3 0 11-6 0 3 3 0 016 0zM12.93 17c.046-.327.07-.66.07-1a6.97 6.97 0 00-1.5-4.33A5 5 0 0119 16v1h-6.07zM6 11a5 5 0 015 5v1H1v-1a5 5 0 015-5z" />
            </svg>
          </div>
          <h2 className="text-h1 text-whiterock mb-4">create customer personas</h2>
          <p className="text-secondary mb-8 max-w-md mx-auto">
            generate detailed ideal customer profiles with demographics, psychographics, and jobs-to-be-done
          </p>
          <Button variant="primary" onClick={generateIcps} disabled={generating}>
            {generating ? (
              <span className="flex items-center gap-3">
                <TypingIndicator />
                <span>creating personas...</span>
              </span>
            ) : (
              'generate icps'
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
          <h1 className="text-display text-whiterock mb-2">ideal customer profiles</h1>
          <p className="text-secondary">{icps.length} personas created</p>
        </div>
        <Button variant="ghost" onClick={generateIcps} disabled={generating}>
          {generating ? <TypingIndicator /> : 'regenerate'}
        </Button>
      </div>

      {/* ICP Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {icps.map((icp, index) => (
          <motion.div
            key={index}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
          >
            <Card className="p-6 cursor-pointer" hover onClick={() => setSelectedIcp(icp)}>
              {/* Avatar Placeholder */}
              <div className="mb-4">
                <ImagePlaceholder
                  src={`/images/persona-${index + 1}.jpg`}
                  alt={icp.name}
                  aspectRatio="aspect-square"
                  className="rounded-xl"
                  icon={
                    <svg className="w-16 h-16 opacity-40" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z" clipRule="evenodd" />
                    </svg>
                  }
                />
              </div>

              {/* Name & Archetype */}
              <h3 className="text-h2 text-whiterock mb-1">{icp.name}</h3>
              <p className="text-sm text-barley mb-4">{icp.archetype}</p>

              {/* Quick Stats */}
              <div className="space-y-2 mb-4">
                <div className="flex items-center justify-between text-sm">
                  <span className="text-muted">age</span>
                  <span className="text-whiterock">{icp.demographics?.age}</span>
                </div>
                <div className="flex items-center justify-between text-sm">
                  <span className="text-muted">income</span>
                  <span className="text-whiterock">{icp.demographics?.income}</span>
                </div>
                <div className="flex items-center justify-between text-sm">
                  <span className="text-muted">location</span>
                  <span className="text-whiterock">{icp.demographics?.location}</span>
                </div>
              </div>

              {/* Quote */}
              <div className="p-3 rounded-lg bg-[color:rgba(255,255,255,.02)] border-l-2 border-barley">
                <p className="text-xs text-secondary italic">"{icp.quote}"</p>
              </div>

              {/* View Details */}
              <Button variant="ghost" size="sm" className="w-full mt-4">
                view full profile 
              </Button>
            </Card>
          </motion.div>
        ))}
      </div>

      {/* ICP Detail Modal */}
      <Modal
        isOpen={selectedIcp !== null}
        onClose={() => setSelectedIcp(null)}
        title={selectedIcp?.name}
        size="xl"
      >
        {selectedIcp && (
          <div className="space-y-6">
            {/* Header */}
            <div className="flex gap-6">
              <ImagePlaceholder
                src={`/images/persona-${icps.indexOf(selectedIcp) + 1}.jpg`}
                alt={selectedIcp.name}
                aspectRatio="aspect-square"
                className="w-32 h-32 rounded-xl flex-shrink-0"
              />
              <div className="flex-1">
                <p className="text-barley text-sm mb-1">{selectedIcp.archetype}</p>
                <h2 className="text-h1 text-whiterock mb-2">{selectedIcp.name}</h2>
                <p className="text-secondary mb-4">
                  {selectedIcp.demographics?.age}  {selectedIcp.demographics?.occupation}  {selectedIcp.demographics?.location}
                </p>
                <div className="flex flex-wrap gap-2">
                  {selectedIcp.psychographics?.personality_traits?.slice(0, 5).map((trait: string, i: number) => (
                    <span key={i} className="px-3 py-1 rounded-full bg-[color:rgba(166,135,99,.12)] text-barley text-xs">
                      {trait}
                    </span>
                  ))}
                </div>
              </div>
            </div>

            {/* Demographics */}
            <div>
              <h3 className="text-h2 text-whiterock mb-3">demographics</h3>
              <div className="grid grid-cols-2 gap-4">
                {Object.entries(selectedIcp.demographics || {}).map(([key, value]) => (
                  <div key={key} className="p-3 rounded-lg bg-[color:rgba(255,255,255,.02)]">
                    <div className="text-xs text-muted mb-1 capitalize">{key.replace(/_/g, ' ')}</div>
                    <div className="text-sm text-whiterock">{value as string}</div>
                  </div>
                ))}
              </div>
            </div>

            {/* Psychographics */}
            <div>
              <h3 className="text-h2 text-whiterock mb-3">psychographics</h3>
              <div className="space-y-4">
                {['core_values', 'fears', 'desires'].map((category) => (
                  <div key={category}>
                    <h4 className="text-sm text-muted mb-2 capitalize">{category.replace(/_/g, ' ')}</h4>
                    <div className="flex flex-wrap gap-2">
                      {selectedIcp.psychographics?.[category]?.map((item: string, i: number) => (
                        <span key={i} className="px-3 py-1 rounded-lg bg-[color:rgba(255,255,255,.02)] text-secondary text-sm">
                          {item}
                        </span>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Jobs-to-be-Done */}
            <div>
              <h3 className="text-h2 text-whiterock mb-3">jobs to be done</h3>
              <div className="space-y-3">
                {['functional_jobs', 'emotional_jobs', 'social_jobs'].map((jobType) => (
                  <div key={jobType}>
                    <h4 className="text-sm text-barley mb-2 capitalize">{jobType.replace(/_/g, ' ')}</h4>
                    <div className="space-y-2">
                      {selectedIcp.jtbd?.[jobType]?.slice(0, 2).map((job: any, i: number) => (
                        <div key={i} className="p-3 rounded-lg bg-[color:rgba(255,255,255,.02)] border border-[color:var(--hairline)]">
                          <p className="text-sm text-whiterock mb-1">{job.statement}</p>
                          <div className="flex items-center gap-4 text-xs text-muted">
                            <span>frequency: {job.frequency}</span>
                            <span>importance: {job.importance}</span>
                            <span>satisfaction: {job.satisfaction_level}/10</span>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Monitoring Tags */}
            <div>
              <h3 className="text-h2 text-whiterock mb-3">trend monitoring tags</h3>
              <div className="flex flex-wrap gap-2">
                {selectedIcp.monitoring_tags?.map((tag: string, i: number) => (
                  <span key={i} className="px-3 py-1 rounded-full border border-[color:var(--hairline)] text-secondary text-sm">
                    #{tag}
                  </span>
                ))}
              </div>
            </div>
          </div>
        )}
      </Modal>

      {/* Next Step */}
      <Card className="p-6 bg-gradient-to-br from-[color:rgba(166,135,99,.08)] to-transparent border-barley border-opacity-20">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-h2 text-whiterock mb-2">next: build strategy</h3>
            <p className="text-secondary">create 7Ps marketing mix and strategic bets</p>
          </div>
          <Button variant="primary" onClick={() => window.location.href = '/dashboard/strategy'}>
            continue 
          </Button>
        </div>
      </Card>
    </div>
  );
}
