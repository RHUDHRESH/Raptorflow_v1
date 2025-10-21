'use client'

import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/Button'

export default function HomePage() {
  const [scrolled, setScrolled] = useState(false)
  const [activeTab, setActiveTab] = useState('research')

  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 20)
    }
    window.addEventListener('scroll', handleScroll)
    return () => window.removeEventListener('scroll', handleScroll)
  }, [])

  return (
    <div className="min-h-screen bg-gradient-to-br from-mine via-mine to-black">
      {/* Header */}
      <header className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${
        scrolled ? 'bg-mine/90 backdrop-blur-md border-b border-hairline' : ''
      }`}>
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <div className="w-10 h-10 bg-barley rounded-lg flex items-center justify-center">
                <span className="text-whiterock font-bold text-xl">R</span>
              </div>
              <span className="text-whiterock font-display text-xl">RaptorFlow</span>
            </div>
            <nav className="hidden md:flex items-center space-x-8">
              <a href="#features" className="text-ink hover:text-akaroa transition-colors">Features</a>
              <a href="#pricing" className="text-ink hover:text-akaroa transition-colors">Pricing</a>
              <a href="#how-it-works" className="text-ink hover:text-akaroa transition-colors">How It Works</a>
              <Button variant="primary" className="btn-primary">
                Get Started
              </Button>
            </nav>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="relative pt-32 pb-20 px-6 overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-b from-transparent via-barley/5 to-transparent" />
        <div className="container mx-auto text-center relative z-10">
          <div className="max-w-4xl mx-auto">
            <h1 className="font-display text-5xl md:text-7xl font-bold text-whiterock mb-6 animate-floatIn">
              AI-Powered Marketing
              <span className="block text-barley">Intelligence</span>
            </h1>
            <p className="text-xl text-ink/80 mb-8 max-w-2xl mx-auto leading-relaxed animate-floatIn" style={{ animationDelay: '0.2s' }}>
              Transform your marketing strategy with AI-powered insights, automated campaigns, 
              and real-time analytics. Get professional results at startup-friendly costs.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center animate-floatIn" style={{ animationDelay: '0.4s' }}>
              <Button variant="primary" className="btn-primary px-8 py-4 text-lg">
                Start Free Trial
              </Button>
              <Button variant="ghost" className="btn-ghost px-8 py-4 text-lg">
                Watch Demo
              </Button>
            </div>
            
            {/* Budget Badge */}
            <div className="mt-8 inline-flex items-center space-x-2 bg-barley/20 rounded-full px-4 py-2 animate-floatIn" style={{ animationDelay: '0.6s' }}>
              <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
              <span className="text-whiterock text-sm">Starting at just $10/month</span>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-20 px-6">
        <div className="container mx-auto">
          <div className="text-center mb-16">
            <h2 className="font-display text-4xl md:text-5xl font-bold text-whiterock mb-4">
              Everything You Need to Scale
            </h2>
            <p className="text-xl text-ink/70 max-w-2xl mx-auto">
              Professional marketing tools that adapt to your business needs
            </p>
          </div>

          {/* Feature Tabs */}
          <div className="max-w-6xl mx-auto">
            <div className="flex flex-wrap justify-center gap-4 mb-12">
              {['research', 'positioning', 'icp', 'campaigns', 'analytics'].map((tab) => (
                <button
                  key={tab}
                  onClick={() => setActiveTab(tab)}
                  className={`px-6 py-3 rounded-lg capitalize transition-all ${
                    activeTab === tab 
                      ? 'bg-barley text-whiterock' 
                      : 'bg-panel text-ink hover:bg-barley/20'
                  }`}
                >
                  {tab === 'icp' ? 'Ideal Customers' : tab}
                </button>
              ))}
            </div>

            {/* Feature Content */}
            <div className="grid md:grid-cols-2 gap-12 items-center">
              <div className="space-y-6">
                <h3 className="font-display text-3xl font-bold text-whiterock">
                  {activeTab === 'research' && 'Market Intelligence'}
                  {activeTab === 'positioning' && 'Strategic Positioning'}
                  {activeTab === 'icp' && 'Customer Profiles'}
                  {activeTab === 'campaigns' && 'Campaign Automation'}
                  {activeTab === 'analytics' && 'Performance Analytics'}
                </h3>
                <p className="text-ink/80 leading-relaxed">
                  {activeTab === 'research' && 'Get comprehensive market analysis, competitor insights, and trend identification powered by AI. Understand your landscape with data-driven intelligence.'}
                  {activeTab === 'positioning' && 'Develop compelling positioning strategies that resonate with your target audience. Stand out in crowded markets with unique value propositions.'}
                  {activeTab === 'icp' && 'Create detailed ideal customer profiles with psychographics, behaviors, and preferences. Know exactly who you\'re targeting and why.'}
                  {activeTab === 'campaigns' && 'Launch automated marketing campaigns across multiple channels. AI-optimized content and timing for maximum engagement.'}
                  {activeTab === 'analytics' && 'Track performance, measure ROI, and get actionable insights. Real-time analytics help you optimize continuously.'}
                </p>
                <div className="flex flex-wrap gap-3">
                  {activeTab === 'research' && ['Competitor Analysis', 'Market Trends', 'Opportunity Identification'].map((tag) => (
                    <span key={tag} className="px-3 py-1 bg-barley/20 rounded-full text-sm text-whiterock">{tag}</span>
                  ))}
                  {activeTab === 'positioning' && ['Value Proposition', 'Brand Strategy', 'Market Differentiation'].map((tag) => (
                    <span key={tag} className="px-3 py-1 bg-barley/20 rounded-full text-sm text-whiterock">{tag}</span>
                  ))}
                  {activeTab === 'icp' && ['Demographics', 'Psychographics', 'Behavior Patterns'].map((tag) => (
                    <span key={tag} className="px-3 py-1 bg-barley/20 rounded-full text-sm text-whiterock">{tag}</span>
                  ))}
                  {activeTab === 'campaigns' && ['Multi-Channel', 'AI Content', 'Automation'].map((tag) => (
                    <span key={tag} className="px-3 py-1 bg-barley/20 rounded-full text-sm text-whiterock">{tag}</span>
                  ))}
                  {activeTab === 'analytics' && ['Real-Time Data', 'ROI Tracking', 'Predictive Insights'].map((tag) => (
                    <span key={tag} className="px-3 py-1 bg-barley/20 rounded-full text-sm text-whiterock">{tag}</span>
                  ))}
                </div>
              </div>
              <div className="card p-8 h-96 flex items-center justify-center">
                <div className="text-center">
                  <div className="w-20 h-20 bg-barley/20 rounded-2xl flex items-center justify-center mx-auto mb-4">
                    <span className="text-3xl">📊</span>
                  </div>
                  <p className="text-ink/70">Interactive Demo</p>
                  <p className="text-sm text-ink/50 mt-2">Experience the power of AI</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Pricing Section */}
      <section id="pricing" className="py-20 px-6 bg-gradient-to-b from-transparent to-barley/5">
        <div className="container mx-auto">
          <div className="text-center mb-16">
            <h2 className="font-display text-4xl md:text-5xl font-bold text-whiterock mb-4">
              Simple, Transparent Pricing
            </h2>
            <p className="text-xl text-ink/70 max-w-2xl mx-auto">
              Professional marketing tools that fit your budget
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8 max-w-6xl mx-auto">
            {/* Basic Plan */}
            <div className="card p-8 relative">
              <h3 className="font-display text-2xl font-bold text-whiterock mb-2">Basic</h3>
              <div className="text-3xl font-bold text-barley mb-6">$10<span className="text-lg text-ink/70">/month</span></div>
              <ul className="space-y-3 mb-8">
                <li className="flex items-center text-ink/80">
                  <span className="w-5 h-5 bg-barley rounded-full mr-3"></span>
                  3 ICPs
                </li>
                <li className="flex items-center text-ink/80">
                  <span className="w-5 h-5 bg-barley rounded-full mr-3"></span>
                  5 Campaigns/month
                </li>
                <li className="flex items-center text-ink/80">
                  <span className="w-5 h-5 bg-barley rounded-full mr-3"></span>
                  Basic Analytics
                </li>
                <li className="flex items-center text-ink/80">
                  <span className="w-5 h-5 bg-barley rounded-full mr-3"></span>
                  Email Support
                </li>
              </ul>
              <Button variant="primary" className="btn-primary w-full">Get Started</Button>
            </div>

            {/* Pro Plan */}
            <div className="card p-8 relative border-barley/50">
              <div className="absolute -top-4 left-1/2 transform -translate-x-1/2 bg-barley text-whiterock px-4 py-1 rounded-full text-sm">
                Most Popular
              </div>
              <h3 className="font-display text-2xl font-bold text-whiterock mb-2">Pro</h3>
              <div className="text-3xl font-bold text-barley mb-6">$25<span className="text-lg text-ink/70">/month</span></div>
              <ul className="space-y-3 mb-8">
                <li className="flex items-center text-ink/80">
                  <span className="w-5 h-5 bg-barley rounded-full mr-3"></span>
                  6 ICPs
                </li>
                <li className="flex items-center text-ink/80">
                  <span className="w-5 h-5 bg-barley rounded-full mr-3"></span>
                  15 Campaigns/month
                </li>
                <li className="flex items-center text-ink/80">
                  <span className="w-5 h-5 bg-barley rounded-full mr-3"></span>
                  Advanced Analytics
                </li>
                <li className="flex items-center text-ink/80">
                  <span className="w-5 h-5 bg-barley rounded-full mr-3"></span>
                  Priority Support
                </li>
                <li className="flex items-center text-ink/80">
                  <span className="w-5 h-5 bg-barley rounded-full mr-3"></span>
                  Custom Integrations
                </li>
              </ul>
              <Button variant="primary" className="btn-primary w-full">Get Started</Button>
            </div>

            {/* Enterprise Plan */}
            <div className="card p-8 relative">
              <h3 className="font-display text-2xl font-bold text-whiterock mb-2">Enterprise</h3>
              <div className="text-3xl font-bold text-barley mb-6">$50<span className="text-lg text-ink/70">/month</span></div>
              <ul className="space-y-3 mb-8">
                <li className="flex items-center text-ink/80">
                  <span className="w-5 h-5 bg-barley rounded-full mr-3"></span>
                  Unlimited ICPs
                </li>
                <li className="flex items-center text-ink/80">
                  <span className="w-5 h-5 bg-barley rounded-full mr-3"></span>
                  Unlimited Campaigns
                </li>
                <li className="flex items-center text-ink/80">
                  <span className="w-5 h-5 bg-barley rounded-full mr-3"></span>
                  Premium Analytics
                </li>
                <li className="flex items-center text-ink/80">
                  <span className="w-5 h-5 bg-barley rounded-full mr-3"></span>
                  Dedicated Support
                </li>
                <li className="flex items-center text-ink/80">
                  <span className="w-5 h-5 bg-barley rounded-full mr-3"></span>
                  White-label Options
                </li>
              </ul>
              <Button variant="ghost" className="btn-ghost w-full">Contact Sales</Button>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 px-6">
        <div className="container mx-auto text-center">
          <div className="card p-12 max-w-4xl mx-auto">
            <h2 className="font-display text-4xl font-bold text-whiterock mb-4">
              Ready to Transform Your Marketing?
            </h2>
            <p className="text-xl text-ink/80 mb-8">
              Join thousands of businesses using AI to scale their marketing efforts
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Button variant="primary" className="btn-primary px-8 py-4 text-lg">
                Start Free Trial
              </Button>
              <Button variant="ghost" className="btn-ghost px-8 py-4 text-lg">
                Schedule Demo
              </Button>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-hairline py-12 px-6">
        <div className="container mx-auto">
          <div className="grid md:grid-cols-4 gap-8 mb-8">
            <div>
              <div className="flex items-center space-x-2 mb-4">
                <div className="w-8 h-8 bg-barley rounded-lg flex items-center justify-center">
                  <span className="text-whiterock font-bold">R</span>
                </div>
                <span className="text-whiterock font-display text-lg">RaptorFlow</span>
              </div>
              <p className="text-ink/60 text-sm">
                AI-powered marketing intelligence for modern businesses.
              </p>
            </div>
            <div>
              <h4 className="text-whiterock font-semibold mb-4">Product</h4>
              <ul className="space-y-2 text-ink/60 text-sm">
                <li><a href="#" className="hover:text-akaroa transition-colors">Features</a></li>
                <li><a href="#" className="hover:text-akaroa transition-colors">Pricing</a></li>
                <li><a href="#" className="hover:text-akaroa transition-colors">API</a></li>
              </ul>
            </div>
            <div>
              <h4 className="text-whiterock font-semibold mb-4">Company</h4>
              <ul className="space-y-2 text-ink/60 text-sm">
                <li><a href="#" className="hover:text-akaroa transition-colors">About</a></li>
                <li><a href="#" className="hover:text-akaroa transition-colors">Blog</a></li>
                <li><a href="#" className="hover:text-akaroa transition-colors">Careers</a></li>
              </ul>
            </div>
            <div>
              <h4 className="text-whiterock font-semibold mb-4">Support</h4>
              <ul className="space-y-2 text-ink/60 text-sm">
                <li><a href="#" className="hover:text-akaroa transition-colors">Help Center</a></li>
                <li><a href="#" className="hover:text-akaroa transition-colors">Contact</a></li>
                <li><a href="#" className="hover:text-akaroa transition-colors">Status</a></li>
              </ul>
            </div>
          </div>
          <div className="border-t border-hairline pt-8 text-center text-ink/60 text-sm">
            <p>&copy; 2024 RaptorFlow. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  )
}
