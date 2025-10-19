'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import { useRouter } from 'next/navigation';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Textarea } from '@/components/ui/Textarea';
import { ImagePlaceholder } from '@/components/ui/ImagePlaceholder';
import { staggerContainer, fadeInUp } from '@/components/animations/variants';

export default function IntakePage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    industry: '',
    location: '',
    description: '',
    goals: ''
  });

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setLoading(true);

    try {
      const response = await fetch('/api/intake', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      });

      const data = await response.json();

      if (data.success) {
        localStorage.setItem('business_id', data.business_id);
        router.push('/dashboard');
      }
    } catch (error) {
      console.error('Error submitting intake form:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex flex-col">
      {/* Hero Section */}
      <section className="relative min-h-[60vh] flex items-center justify-center overflow-hidden">
        {/* Background Image Placeholder */}
        <div className="absolute inset-0 opacity-40">
          <ImagePlaceholder
            src="/images/hero-bg.jpg"
            alt="Hero background"
            aspectRatio="aspect-[16/9]"
            className="w-full h-full"
          />
        </div>

        {/* Content */}
        <motion.div
          variants={staggerContainer}
          initial="initial"
          animate="animate"
          className="relative z-10 text-center max-w-4xl mx-auto px-6"
        >
          <motion.div variants={fadeInUp}>
            <h1 className="text-display text-whiterock mb-6">
              mist over black sand
            </h1>
            <p className="text-body text-secondary max-w-2xl mx-auto mb-12">
              ai-powered marketing strategy that adapts. positioning, personas, content built on ries &amp; trout principles.
            </p>
          </motion.div>

          <motion.div variants={fadeInUp} className="flex items-center justify-center gap-4">
            <Button
              variant="primary"
              size="lg"
              onClick={() => document.getElementById('intake-form')?.scrollIntoView({ behavior: 'smooth' })}
            >
              start building
            </Button>
            <Button variant="ghost" size="lg">
              watch demo
            </Button>
          </motion.div>
        </motion.div>

        {/* Scroll Indicator */}
        <motion.div
          animate={{ y: [0, 8, 0] }}
          transition={{ repeat: Infinity, duration: 2 }}
          className="absolute bottom-8 left-1/2 -translate-x-1/2"
        >
          <svg className="w-6 h-6 text-muted" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 14l-7 7m0 0l-7-7m7 7V3" />
          </svg>
        </motion.div>
      </section>

      {/* Intake Form */}
      <section id="intake-form" className="py-24 px-6">
        <div className="max-w-2xl mx-auto">
          <Card className="p-8">
            <h2 className="text-h1 text-whiterock mb-2">tell us about your business</h2>
            <p className="text-secondary mb-8">we&apos;ll analyze your market and build your strategy</p>

            <form onSubmit={handleSubmit} className="space-y-6">
              <Input
                label="business name"
                placeholder="acme inc."
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                required
              />

              <Input
                label="industry"
                placeholder="saas, retail, consulting..."
                value={formData.industry}
                onChange={(e) => setFormData({ ...formData, industry: e.target.value })}
                required
              />

              <Input
                label="location"
                placeholder="chennai, india"
                value={formData.location}
                onChange={(e) => setFormData({ ...formData, location: e.target.value })}
                required
              />

              <Textarea
                label="what do you do?"
                placeholder="describe your product or service in 2-3 sentences"
                rows={4}
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                required
              />

              <Textarea
                label="what are your goals?"
                placeholder="e.g., generate 100 leads/month, increase brand awareness..."
                rows={3}
                value={formData.goals}
                onChange={(e) => setFormData({ ...formData, goals: e.target.value })}
                required
              />

              <Button
                type="submit"
                variant="primary"
                className="w-full"
                disabled={loading}
              >
                {loading ? (
                  <span className="flex items-center justify-center gap-2">
                    <span className="typing-dot animate-dots" />
                    <span className="typing-dot animate-dots-delay-1" />
                    <span className="typing-dot animate-dots-delay-2" />
                  </span>
                ) : (
                  'start research'
                )}
              </Button>
            </form>
          </Card>

          {/* Features Grid */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-16">
            {[
              { icon: '', title: 'research', desc: 'sostac + competitive analysis' },
              { icon: '', title: 'positioning', desc: 'find your unique word' },
              { icon: '', title: 'execution', desc: 'calendar + performance tracking' }
            ].map((feature, i) => (
              <motion.div
                key={feature.title}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.1 + 0.3 }}
              >
                <Card className="p-6 text-center" hover>
                  <div className="text-4xl mb-4">{feature.icon}</div>
                  <h3 className="text-h2 text-whiterock mb-2">{feature.title}</h3>
                  <p className="text-muted text-sm">{feature.desc}</p>
                </Card>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Gallery Section - Image Placeholders */}
      <section className="py-24 px-6 bg-[color:rgba(255,255,255,.01)]">
        <div className="max-w-content mx-auto">
          <h2 className="text-h1 text-whiterock text-center mb-4">built on proven frameworks</h2>
          <p className="text-secondary text-center mb-12 max-w-2xl mx-auto">
            ries &amp; trout positioning laws, sostac planning, amec measurement
          </p>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {[1, 2, 3, 4, 5, 6].map((i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, scale: 0.95 }}
                whileInView={{ opacity: 1, scale: 1 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.05 }}
              >
                <ImagePlaceholder
                  src={`/images/gallery-${i}.jpg`}
                  alt={`Framework visualization ${i}`}
                  aspectRatio="aspect-square"
                  caption={`framework ${i}`}
                  className="hover:scale-103 transition-transform duration-300"
                />
              </motion.div>
            ))}
          </div>
        </div>
      </section>
    </div>
  );
}
