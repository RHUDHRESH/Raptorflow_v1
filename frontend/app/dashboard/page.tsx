'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { Button } from '@/components/ui/Button'

interface BudgetStatus {
  daily_budget: number
  daily_spent: number
  monthly_budget: number
  monthly_spent: number
  remaining_daily: number
  remaining_monthly: number
  status: 'healthy' | 'warning' | 'critical'
}

interface Metric {
  label: string
  value: string
  change: string
  trend: 'up' | 'down' | 'neutral'
}

export default function DashboardHome() {
  const [budgetStatus, setBudgetStatus] = useState<BudgetStatus | null>(null)
  const [loading, setLoading] = useState(true)

  const sections = [
    { 
      href: '/dashboard/positioning', 
      label: 'Positioning', 
      description: 'Strategic market positioning analysis',
      icon: '🎯',
      color: 'bg-barley/20 text-barley'
    },
    { 
      href: '/dashboard/research', 
      label: 'Research', 
      description: 'Market intelligence and competitor analysis',
      icon: '🔍',
      color: 'bg-akaroa/20 text-akaroa'
    },
    { 
      href: '/dashboard/icps', 
      label: 'ICPs', 
      description: 'Ideal customer profile generation',
      icon: '👥',
      color: 'bg-barley/20 text-barley'
    },
    { 
      href: '/dashboard/moves', 
      label: 'Campaigns', 
      description: 'AI-powered campaign creation',
      icon: '🚀',
      color: 'bg-akaroa/20 text-akaroa'
    },
    { 
      href: '/dashboard/analytics', 
      label: 'Analytics', 
      description: 'Performance tracking and insights',
      icon: '📊',
      color: 'bg-barley/20 text-barley'
    },
    { 
      href: '/dashboard/settings', 
      label: 'Settings', 
      description: 'Account and billing management',
      icon: '⚙️',
      color: 'bg-akaroa/20 text-akaroa'
    }
  ]

  const metrics: Metric[] = [
    { label: 'Active Campaigns', value: '3', change: '+2 this week', trend: 'up' },
    { label: 'Customer Profiles', value: '6', change: '+1 this month', trend: 'up' },
    { label: 'AI Credits Used', value: '84%', change: '16% remaining', trend: 'neutral' },
    { label: 'Engagement Rate', value: '4.2%', change: '+0.8% vs last month', trend: 'up' }
  ]

  useEffect(() => {
    // Simulate fetching budget status
    const fetchBudgetStatus = async () => {
      try {
        const response = await fetch('/api/budget/status')
        if (response.ok) {
          const data = await response.json()
          setBudgetStatus(data)
        } else {
          // Fallback mock data
          setBudgetStatus({
            daily_budget: 0.50,
            daily_spent: 0.32,
            monthly_budget: 15.00,
            monthly_spent: 8.47,
            remaining_daily: 0.18,
            remaining_monthly: 6.53,
            status: 'healthy'
          })
        }
      } catch (error) {
        console.error('Failed to fetch budget status:', error)
        // Fallback mock data
        setBudgetStatus({
          daily_budget: 0.50,
          daily_spent: 0.32,
          monthly_budget: 15.00,
          monthly_spent: 8.47,
          remaining_daily: 0.18,
          remaining_monthly: 6.53,
          status: 'healthy'
        })
      } finally {
        setLoading(false)
      }
    }

    fetchBudgetStatus()
  }, [])

  const getBudgetColor = (status: string) => {
    switch (status) {
      case 'critical': return 'text-red-400'
      case 'warning': return 'text-yellow-400'
      default: return 'text-green-400'
    }
  }

  const getTrendIcon = (trend: string) => {
    switch (trend) {
      case 'up': return '↑'
      case 'down': return '↓'
      default: return '→'
    }
  }

  return (
    <div className="min-h-screen bg-mine">
      {/* Header */}
      <header className="header">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <Link href="/" className="flex items-center space-x-2">
                <div className="w-8 h-8 bg-barley rounded-lg flex items-center justify-center">
                  <span className="text-whiterock font-bold">R</span>
                </div>
                <span className="text-whiterock font-display text-lg">RaptorFlow</span>
              </Link>
              <div className="hidden md:block w-px h-6 bg-hairline"></div>
              <h1 className="text-whiterock font-display text-xl">Dashboard</h1>
            </div>
            <div className="flex items-center space-x-4">
              <Button variant="ghost" className="btn-ghost">
                Notifications
              </Button>
              <div className="w-8 h-8 bg-barley/20 rounded-full flex items-center justify-center">
                <span className="text-whiterock text-sm">JD</span>
              </div>
            </div>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-6 py-8">
        {/* Welcome Section */}
        <div className="mb-8">
          <h2 className="font-display text-3xl font-bold text-whiterock mb-2">
            Welcome back, John
          </h2>
          <p className="text-ink/70">
            Here's what's happening with your marketing campaigns today.
          </p>
        </div>

        {/* Budget Status Card */}
        <div className="card p-6 mb-8">
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-display text-xl font-bold text-whiterock">Budget Status</h3>
            {loading ? (
              <div className="skeleton w-20 h-6"></div>
            ) : (
              <div className={`flex items-center space-x-2 ${getBudgetColor(budgetStatus?.status || 'healthy')}`}>
                <div className={`w-2 h-2 rounded-full ${
                  budgetStatus?.status === 'critical' ? 'bg-red-400' :
                  budgetStatus?.status === 'warning' ? 'bg-yellow-400' : 'bg-green-400'
                } animate-pulse`}></div>
                <span className="text-sm font-medium capitalize">{budgetStatus?.status}</span>
              </div>
            )}
          </div>
          
          {loading ? (
            <div className="grid grid-cols-2 gap-4">
              <div className="skeleton h-20"></div>
              <div className="skeleton h-20"></div>
            </div>
          ) : budgetStatus && (
            <div className="grid md:grid-cols-2 gap-6">
              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span className="text-ink/70">Daily Budget</span>
                  <span className="text-whiterock">${budgetStatus.daily_budget.toFixed(2)}</span>
                </div>
                <div className="w-full bg-panel rounded-full h-2">
                  <div 
                    className="bg-barley h-2 rounded-full transition-all duration-300"
                    style={{ width: `${(budgetStatus.daily_spent / budgetStatus.daily_budget) * 100}%` }}
                  ></div>
                </div>
                <div className="flex justify-between text-xs text-ink/60">
                  <span>Spent: ${budgetStatus.daily_spent.toFixed(2)}</span>
                  <span>Remaining: ${budgetStatus.remaining_daily.toFixed(2)}</span>
                </div>
              </div>
              
              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span className="text-ink/70">Monthly Budget</span>
                  <span className="text-whiterock">${budgetStatus.monthly_budget.toFixed(2)}</span>
                </div>
                <div className="w-full bg-panel rounded-full h-2">
                  <div 
                    className="bg-akaroa h-2 rounded-full transition-all duration-300"
                    style={{ width: `${(budgetStatus.monthly_spent / budgetStatus.monthly_budget) * 100}%` }}
                  ></div>
                </div>
                <div className="flex justify-between text-xs text-ink/60">
                  <span>Spent: ${budgetStatus.monthly_spent.toFixed(2)}</span>
                  <span>Remaining: ${budgetStatus.remaining_monthly.toFixed(2)}</span>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Metrics Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {metrics.map((metric, index) => (
            <div key={index} className="card p-6">
              <div className="flex items-center justify-between mb-2">
                <span className="text-ink/70 text-sm">{metric.label}</span>
                <span className={`text-lg ${
                  metric.trend === 'up' ? 'text-green-400' :
                  metric.trend === 'down' ? 'text-red-400' : 'text-ink/60'
                }`}>
                  {getTrendIcon(metric.trend)}
                </span>
              </div>
              <div className="font-display text-2xl font-bold text-whiterock mb-1">
                {metric.value}
              </div>
              <div className="text-xs text-ink/60">
                {metric.change}
              </div>
            </div>
          ))}
        </div>

        {/* Quick Actions */}
        <div className="card p-6 mb-8">
          <h3 className="font-display text-xl font-bold text-whiterock mb-4">Quick Actions</h3>
          <div className="flex flex-wrap gap-3">
            <Button variant="primary" className="btn-primary">
              Create New Campaign
            </Button>
            <Button variant="ghost" className="btn-ghost">
              Generate ICP
            </Button>
            <Button variant="ghost" className="btn-ghost">
              Run Research
            </Button>
            <Button variant="ghost" className="btn-ghost">
              View Analytics
            </Button>
          </div>
        </div>

        {/* Navigation Grid */}
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {sections.map((section) => (
            <Link
              key={section.href}
              href={section.href}
              className="card p-6 hover:scale-[1.02] transition-all duration-200 group"
            >
              <div className="flex items-start space-x-4">
                <div className={`w-12 h-12 rounded-xl ${section.color} flex items-center justify-center text-2xl group-hover:scale-110 transition-transform`}>
                  {section.icon}
                </div>
                <div className="flex-1">
                  <h4 className="font-display text-lg font-semibold text-whiterock mb-1">
                    {section.label}
                  </h4>
                  <p className="text-sm text-ink/70">
                    {section.description}
                  </p>
                </div>
              </div>
            </Link>
          ))}
        </div>
      </main>
    </div>
  )
}
