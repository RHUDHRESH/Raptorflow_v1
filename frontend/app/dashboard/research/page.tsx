'use client';

import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { SkeletonCard, SkeletonText } from '@/components/ui/Skeleton';
import { TypingIndicator } from '@/components/ui/TypingIndicator';
import { ImagePlaceholder } from '@/components/ui/ImagePlaceholder';
import { staggerContainer, fadeInUp } from '@/components/animations/variants';

export default function ResearchPage() {
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState<any>(null);
  const [runningAnalysis, setRunningAnalysis] = useState(false);

  useEffect(() => {
    fetchResearch();
  }, []);

  const fetchResearch = async () => {
    setLoading(true);
    try {
      const businessId = localStorage.getItem('business_id');
      const response = await fetch(`/api/research/${businessId}`);
      const result = await response.json();
      setData(result);
    } catch (error) {
      console.error('Error:', error);
    } finally {
      setLoading(false);
    }
  };

  const runAnalysis = async () => {
    setRunningAnalysis(true);
    try {
      const businessId = localStorage.getItem('business_id');
      const response = await fetch(`/api/research/${businessId}`, { method: 'POST' });
      const result = await response.json();
      setData(result);
    } catch (error) {
      console.error('Error:', error);
    } finally {
      setRunningAnalysis(false);
    }
  };

  if (loading) {
    return (
      <div className="max-w-content mx-auto px-6 space-y-8">
        <SkeletonCard />
        <SkeletonCard />
      </div>
    );
  }

  if (!data?.sostac) {
    return (
      <div className="max-w-content mx-auto px-6">
        <Card className="p-12 text-center">
          <div className="w-24 h-24 mx-auto mb-6 rounded-2xl bg-gradient-to-br from-barley to-akaroa flex items-center justify-center">
            <svg className="w-12 h-12 text-mine" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M6 2a2 2 0 00-2 2v12a2 2 0 002 2h8a2 2 0 002-2V7.414A2 2 0 0015.414 6L12 2.586A2 2 0 0010.586 2H6zm5 6a1 1 0 10-2 0v3.586l-1.293-1.293a1 1 0 10-1.414 1.414l3 3a1 1 0 001.414 0l3-3a1 1 0 00-1.414-1.414L11 11.586V8z" clipRule="evenodd" />
            </svg>
          </div>
          <h2 className="text-h1 text-whiterock mb-4">ready to research?</h2>
          <p className="text-secondary mb-8 max-w-md mx-auto">
            we'll analyze your market using sostac framework and build your competitive positioning ladder
          </p>
          <Button variant="primary" onClick={runAnalysis} disabled={runningAnalysis}>
            {runningAnalysis ? (
              <span className="flex items-center gap-3">
                <TypingIndicator />
                <span>analyzing...</span>
              </span>
            ) : (
              'start research'
            )}
          </Button>
        </Card>
      </div>
    );
  }

  return (
    <div className="max-w-content mx-auto px-6 space-y-8">
      {/* Header */}
      <motion.div variants={fadeInUp} initial="initial" animate="animate">
        <div className="flex items-center justify-between mb-2">
          <h1 className="text-display text-whiterock">research</h1>
          <Button variant="ghost" onClick={runAnalysis} disabled={runningAnalysis}>
            {runningAnalysis ? <TypingIndicator /> : 're-run analysis'}
          </Button>
        </div>
        <p className="text-secondary">sostac framework + competitive analysis</p>
      </motion.div>

      {/* SOSTAC Analysis */}
      <Card className="p-8">
        <h2 className="text-h2 text-whiterock mb-6">sostac analysis</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {['situation', 'objectives', 'strategy', 'tactics', 'action', 'control'].map((phase, i) => (
            <motion.div
              key={phase}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.1 }}
              className="p-6 rounded-xl bg-[color:rgba(255,255,255,.02)] border border-[color:var(--hairline)]"
            >
              <h3 className="text-h2 text-whiterock mb-3 capitalize">{phase}</h3>
              <p className="text-sm text-secondary line-clamp-3">
                {data.sostac?.[phase] || 'analyzing...'}
              </p>
            </motion.div>
          ))}
        </div>
      </Card>

      {/* Competitor Ladder */}
      <Card className="p-8">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-h2 text-whiterock">competitor ladder</h2>
          <span className="text-sm text-muted">{data.competitor_ladder?.length || 0} competitors mapped</span>
        </div>

        <div className="space-y-4">
          {data.competitor_ladder?.map((comp: any, i: number) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: i * 0.05 }}
              className="flex items-center gap-4 p-4 rounded-xl bg-[color:rgba(255,255,255,.02)] border border-[color:var(--hairline)]"
            >
              <div className="w-12 h-12 rounded-lg bg-gradient-to-br from-barley to-akaroa flex items-center justify-center text-mine font-bold">
                #{i + 1}
              </div>
              <div className="flex-1">
                <h3 className="text-lg text-whiterock font-semibold">{comp.competitor_name}</h3>
                <p className="text-sm text-secondary">owns: <span className="text-barley">{comp.word_owned}</span></p>
              </div>
              <div className="text-right">
                <div className="text-sm text-muted">strength</div>
                <div className="text-lg text-whiterock font-semibold">{(comp.position_strength * 100).toFixed(0)}%</div>
              </div>
            </motion.div>
          ))}
        </div>
      </Card>

      {/* Evidence Graph Visualization */}
      <Card className="p-8">
        <h2 className="text-h2 text-whiterock mb-6">evidence network</h2>
        <p className="text-secondary mb-6">
          {data.evidence_count || 0} evidence nodes supporting your positioning claims
        </p>
        
        <ImagePlaceholder
          src="/images/evidence-graph.jpg"
          alt="Evidence knowledge graph"
          aspectRatio="aspect-video"
          caption="knowledge graph visualization (click to explore)"
          className="cursor-pointer hover:scale-[1.02] transition-transform"
        />
      </Card>

      {/* Next Step */}
      <Card className="p-6 bg-gradient-to-br from-[color:rgba(166,135,99,.08)] to-transparent border-barley border-opacity-20">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-h2 text-whiterock mb-2">next: build positioning</h3>
            <p className="text-secondary">use research insights to create 3 positioning options</p>
          </div>
          <Button variant="primary" onClick={() => window.location.href = '/dashboard/positioning'}>
            continue 
          </Button>
        </div>
      </Card>
    </div>
  );
}
