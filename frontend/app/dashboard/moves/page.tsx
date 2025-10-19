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

export default function MovesPage() {
  const [loading, setLoading] = useState(false);
  const [moves, setMoves] = useState<any[]>([]);
  const [showCreate, setShowCreate] = useState(false);
  const [showCalendar, setShowCalendar] = useState<any>(null);
  const [creating, setCreating] = useState(false);
  const [formData, setFormData] = useState({
    goal: '',
    platform: 'twitter',
    duration_days: 7
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

  const createMove = async () => {
    setCreating(true);
    try {
      const businessId = localStorage.getItem('business_id');
      const response = await fetch(`/api/moves?business_id=${businessId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      });
      const result = await response.json();
      
      setMoves([result, ...moves]);
      setShowCreate(false);
      setShowCalendar(result);
    } catch (error) {
      console.error('Error:', error);
    } finally {
      setCreating(false);
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

  return (
    <div className="max-w-content mx-auto px-6 space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-display text-whiterock mb-2">campaigns</h1>
          <p className="text-secondary">{moves.length} active moves</p>
        </div>
        <Button variant="primary" onClick={() => setShowCreate(true)}>
          + create campaign
        </Button>
      </div>

      {/* Empty State */}
      {moves.length === 0 && (
        <Card className="p-12 text-center">
          <div className="w-24 h-24 mx-auto mb-6 rounded-2xl bg-gradient-to-br from-barley to-akaroa flex items-center justify-center">
            <svg className="w-12 h-12 text-mine" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M6 2a1 1 0 00-1 1v1H4a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V6a2 2 0 00-2-2h-1V3a1 1 0 10-2 0v1H7V3a1 1 0 00-1-1zm0 5a1 1 0 000 2h8a1 1 0 100-2H6z" clipRule="evenodd" />
            </svg>
          </div>
          <h2 className="text-h1 text-whiterock mb-4">no campaigns yet</h2>
          <p className="text-secondary mb-8 max-w-md mx-auto">
            create your first campaign to generate platform-specific content calendars
          </p>
          <Button variant="primary" onClick={() => setShowCreate(true)}>
            create first campaign
          </Button>
        </Card>
      )}

      {/* Moves Grid */}
      {moves.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {moves.map((move, i) => (
            <motion.div
              key={move.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.05 }}
            >
              <Card className="p-6 cursor-pointer" hover onClick={() => setShowCalendar(move)}>
                {/* Header */}
                <div className="flex items-center justify-between mb-4">
                  <div className={`px-3 py-1 rounded-full text-xs font-semibold ${
                    move.status === 'active'
                      ? 'bg-green-500 bg-opacity-20 text-green-400'
                      : 'bg-gray-500 bg-opacity-20 text-gray-400'
                  }`}>
                    {move.status}
                  </div>
                  <span className="text-xs text-muted capitalize">{move.platform}</span>
                </div>

                {/* Goal */}
                <h3 className="text-h2 text-whiterock mb-3">{move.goal}</h3>

                {/* Stats */}
                <div className="grid grid-cols-3 gap-4 mb-4">
                  <div>
                    <p className="text-xs text-muted mb-1">duration</p>
                    <p className="text-sm text-whiterock">{move.duration_days} days</p>
                  </div>
                  <div>
                    <p className="text-xs text-muted mb-1">posts</p>
                    <p className="text-sm text-whiterock">{move.calendar?.statistics?.total_posts || 0}</p>
                  </div>
                  <div>
                    <p className="text-xs text-muted mb-1">ratio</p>
                    <p className="text-sm text-whiterock">{move.calendar?.statistics?.value_ratio || 'N/A'}</p>
                  </div>
                </div>

                {/* Thumbnail */}
                <ImagePlaceholder
                  src={`/images/platform-${move.platform}.jpg`}
                  alt={`${move.platform} campaign`}
                  aspectRatio="aspect-video"
                  className="mb-4"
                />

                <Button variant="ghost" size="sm" className="w-full">
                  view calendar 
                </Button>
              </Card>
            </motion.div>
          ))}
        </div>
      )}

      {/* Create Modal */}
      <Modal
        isOpen={showCreate}
        onClose={() => setShowCreate(false)}
        title="create new campaign"
        size="md"
      >
        <div className="space-y-6">
          <Input
            label="campaign goal"
            placeholder="e.g., Generate 100 leads in 30 days"
            value={formData.goal}
            onChange={(e) => setFormData({ ...formData, goal: e.target.value })}
          />

          <div>
            <label className="block text-sm text-secondary mb-2">platform</label>
            <div className="grid grid-cols-2 gap-3">
              {['twitter', 'linkedin', 'instagram', 'youtube'].map((platform) => (
                <button
                  key={platform}
                  onClick={() => setFormData({ ...formData, platform })}
                  className={`p-4 rounded-xl border transition-all ${
                    formData.platform === platform
                      ? 'border-barley bg-[color:rgba(166,135,99,.12)]'
                      : 'border-[color:var(--hairline)] hover:border-akaroa'
                  }`}
                >
                  <p className="text-sm text-whiterock capitalize">{platform}</p>
                </button>
              ))}
            </div>
          </div>

          <div>
            <label className="block text-sm text-secondary mb-2">duration (days)</label>
            <div className="flex gap-3">
              {[7, 14, 30].map((days) => (
                <button
                  key={days}
                  onClick={() => setFormData({ ...formData, duration_days: days })}
                  className={`flex-1 p-3 rounded-lg border transition-all ${
                    formData.duration_days === days
                      ? 'border-barley bg-[color:rgba(166,135,99,.12)]'
                      : 'border-[color:var(--hairline)] hover:border-akaroa'
                  }`}
                >
                  <p className="text-lg text-whiterock font-semibold">{days}</p>
                  <p className="text-xs text-muted">days</p>
                </button>
              ))}
            </div>
          </div>

          <Button
            variant="primary"
            className="w-full"
            onClick={createMove}
            disabled={creating || !formData.goal}
          >
            {creating ? (
              <span className="flex items-center gap-3">
                <TypingIndicator />
                <span>generating calendar...</span>
              </span>
            ) : (
              'create campaign'
            )}
          </Button>
        </div>
      </Modal>

      {/* Calendar Modal */}
      <Modal
        isOpen={showCalendar !== null}
        onClose={() => setShowCalendar(null)}
        title={showCalendar?.goal}
        size="xl"
      >
        {showCalendar && (
          <div className="space-y-6">
            {/* Stats Summary */}
            <div className="grid grid-cols-4 gap-4">
              {[
                { label: 'total posts', value: showCalendar.calendar?.statistics?.total_posts },
                { label: 'value posts', value: showCalendar.calendar?.statistics?.value_posts },
                { label: 'promotional', value: showCalendar.calendar?.statistics?.promotional_posts },
                { label: 'ratio', value: showCalendar.calendar?.statistics?.value_ratio }
              ].map((stat, i) => (
                <div key={i} className="p-4 rounded-lg bg-[color:rgba(255,255,255,.02)]">
                  <p className="text-xs text-muted mb-1">{stat.label}</p>
                  <p className="text-h2 text-whiterock">{stat.value}</p>
                </div>
              ))}
            </div>

            {/* Calendar Days */}
            <div className="space-y-6">
              {showCalendar.calendar?.calendar?.map((day: any, i: number) => (
                <div key={i}>
                  <h3 className="text-lg text-whiterock mb-4 flex items-center gap-3">
                    <span className="w-8 h-8 rounded-lg bg-barley bg-opacity-20 flex items-center justify-center text-barley text-sm font-semibold">
                      {day.day}
                    </span>
                    Day {day.day}
                  </h3>

                  <div className="space-y-4">
                    {day.posts?.map((post: any, j: number) => (
                      <div
                        key={j}
                        className="p-4 rounded-xl bg-[color:rgba(255,255,255,.02)] border border-[color:var(--hairline)]"
                      >
                        <div className="flex items-start justify-between mb-3">
                          <div className="flex items-center gap-3">
                            <span className="text-xs text-muted">{post.time}</span>
                            <span className={`px-2 py-1 rounded text-xs ${
                              post.content_type === 'promotional'
                                ? 'bg-barley bg-opacity-20 text-barley'
                                : 'bg-green-500 bg-opacity-20 text-green-400'
                            }`}>
                              {post.content_type}
                            </span>
                            <span className="text-xs text-muted">{post.race_phase}</span>
                          </div>
                          {post.valid === false && (
                            <span className="px-2 py-1 rounded text-xs bg-red-500 bg-opacity-20 text-red-400">
                              needs review
                            </span>
                          )}
                        </div>

                        <p className="text-sm text-whiterock mb-3">{post.text}</p>

                        {post.hashtags?.length > 0 && (
                          <div className="flex flex-wrap gap-2">
                            {post.hashtags.map((tag: string, k: number) => (
                              <span key={k} className="text-xs text-barley">
                                #{tag}
                              </span>
                            ))}
                          </div>
                        )}

                        {post.media_description && (
                          <div className="mt-3 p-3 rounded-lg bg-[color:rgba(255,255,255,.02)]">
                            <p className="text-xs text-muted mb-1">media brief</p>
                            <p className="text-xs text-secondary">{post.media_description}</p>
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>

            {/* Export */}
            <div className="pt-4 border-t border-[color:var(--hairline)] flex gap-3">
              <Button variant="ghost" className="flex-1">
                export as CSV
              </Button>
              <Button variant="ghost" className="flex-1">
                copy to clipboard
              </Button>
              <Button variant="primary" className="flex-1">
                schedule posts
              </Button>
            </div>
          </div>
        )}
      </Modal>
    </div>
  );
}
