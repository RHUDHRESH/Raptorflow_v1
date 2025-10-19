/**
 * Frontend API Hooks - Clean TypeScript interfaces for backend integration
 * Handles all API communication with proper error handling and state management
 */

import { useCallback, useState, useEffect, useRef } from 'react'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

// ==================== TYPE DEFINITIONS ====================

export interface Business {
  id: string
  name: string
  industry: string
  location: string
  description: string
  goals: { text: string }
  created_at: string
}

export interface SOSTAC {
  situation: string
  objectives: string
  market_size_estimate: string
  current_positioning: string
  main_challenges: string[]
}

export interface CompetitorPosition {
  competitor: string
  word_owned: string
  position_strength: number
  description: string
}

export interface PositioningOption {
  option_number: number
  word: string
  rationale: string
  category: string
  differentiation: string
  sacrifice: string[]
  purple_cow: string
  big_idea: string
  customer_promise: string
  overall_score: number
  status: string
}

export interface ICPPersona {
  name: string
  demographics: {
    age_range: string
    income: string
    location: string
    occupation: string
    education: string
  }
  psychographics: {
    values: string[]
    fears: string[]
    desires: string[]
    triggers: string[]
  }
  behavior: {
    top_platforms: string[]
    content_preferences: {
      formats: string[]
      tone: string
      topics: string[]
    }
    purchase_behavior: string
    brand_loyalties: string[]
  }
  quote: string
  jtbd?: any
  scores?: {
    fit_score: number
    urgency_score: number
    accessibility_score: number
  }
  monitoring_tags?: string[]
}

export interface Subscription {
  id: string
  business_id: string
  tier: 'trial' | 'basic' | 'pro' | 'enterprise'
  max_icps: number
  max_moves: number
  status: string
  razorpay_subscription_id?: string
}

// ==================== INTAKE HOOKS ====================

export function useIntakeBusiness() {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const createBusiness = useCallback(
    async (data: {
      name: string
      industry: string
      location: string
      description: string
      goals: string
    }) => {
      setLoading(true)
      setError(null)

      try {
        const response = await fetch(`${API_URL}/api/intake`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(data),
        })

        if (!response.ok) throw new Error('Failed to create business')

        const result = await response.json()
        return result

      } catch (err) {
        const message = err instanceof Error ? err.message : 'Unknown error'
        setError(message)
        throw err
      } finally {
        setLoading(false)
      }
    },
    []
  )

  return { createBusiness, loading, error }
}

export function useFetchBusiness(businessId: string) {
  const [business, setBusiness] = useState<Business | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!businessId) return

    const fetchBusiness = async () => {
      try {
        const response = await fetch(`${API_URL}/api/business/${businessId}`)
        if (!response.ok) throw new Error('Failed to fetch business')
        const data = await response.json()
        setBusiness(data)
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Unknown error')
      } finally {
        setLoading(false)
      }
    }

    fetchBusiness()
  }, [businessId])

  return { business, loading, error }
}

// ==================== RESEARCH HOOKS ====================

export function useResearchStream(businessId: string) {
  const [progress, setProgress] = useState(0)
  const [stage, setStage] = useState('')
  const [status, setStatus] = useState('idle')
  const [data, setData] = useState<any>(null)
  const [error, setError] = useState<string | null>(null)
  const wsRef = useRef<WebSocket | null>(null)

  const startResearch = useCallback(() => {
    if (!businessId) return

    const wsUrl = `${API_URL.replace('http', 'ws')}/api/research/${businessId}`

    const ws = new WebSocket(wsUrl)

    ws.onopen = () => {
      setStatus('running')
      setError(null)
    }

    ws.onmessage = (event) => {
      const update = JSON.parse(event.data)
      setStage(update.stage)
      setProgress(update.progress || 0)
      setStatus(update.status)
      if (update.data) setData(update.data)
    }

    ws.onerror = () => {
      setError('WebSocket error')
      setStatus('failed')
    }

    ws.onclose = () => {
      setStatus('completed')
    }

    wsRef.current = ws
  }, [businessId])

  const stop = useCallback(() => {
    if (wsRef.current) {
      wsRef.current.close()
    }
  }, [])

  return { startResearch, stop, progress, stage, status, data, error }
}

export function useFetchResearch(businessId: string) {
  const [research, setResearch] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!businessId) return

    const fetchResearch = async () => {
      try {
        const response = await fetch(`${API_URL}/api/research/${businessId}`)
        if (!response.ok) throw new Error('Research not found')
        const data = await response.json()
        setResearch(data)
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Unknown error')
      } finally {
        setLoading(false)
      }
    }

    fetchResearch()
  }, [businessId])

  return { research, loading, error }
}

// ==================== POSITIONING HOOKS ====================

export function usePositioningStream(businessId: string) {
  const [progress, setProgress] = useState(0)
  const [stage, setStage] = useState('')
  const [status, setStatus] = useState('idle')
  const [options, setOptions] = useState<PositioningOption[]>([])
  const [error, setError] = useState<string | null>(null)
  const wsRef = useRef<WebSocket | null>(null)

  const startAnalysis = useCallback(() => {
    if (!businessId) return

    const wsUrl = `${API_URL.replace('http', 'ws')}/api/positioning/${businessId}`

    const ws = new WebSocket(wsUrl)

    ws.onopen = () => {
      setStatus('running')
      setError(null)
    }

    ws.onmessage = (event) => {
      const update = JSON.parse(event.data)
      setStage(update.stage)
      setProgress(update.progress || 0)
      setStatus(update.status)
      if (update.data?.options) {
        setOptions(update.data.options)
      }
    }

    ws.onerror = () => {
      setError('WebSocket error')
      setStatus('failed')
    }

    ws.onclose = () => {
      setStatus('completed')
    }

    wsRef.current = ws
  }, [businessId])

  const stop = useCallback(() => {
    if (wsRef.current) {
      wsRef.current.close()
    }
  }, [])

  return { startAnalysis, stop, progress, stage, status, options, error }
}

export function useSelectPositioning(businessId: string) {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const selectOption = useCallback(
    async (optionIndex: number) => {
      setLoading(true)
      setError(null)

      try {
        const response = await fetch(
          `${API_URL}/api/positioning/${businessId}/select`,
          {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ option_index: optionIndex }),
          }
        )

        if (!response.ok) throw new Error('Failed to select positioning')

        const result = await response.json()
        return result

      } catch (err) {
        const message = err instanceof Error ? err.message : 'Unknown error'
        setError(message)
        throw err
      } finally {
        setLoading(false)
      }
    },
    [businessId]
  )

  return { selectOption, loading, error }
}

export function useFetchPositioning(businessId: string) {
  const [positioning, setPositioning] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!businessId) return

    const fetchPositioning = async () => {
      try {
        const response = await fetch(`${API_URL}/api/positioning/${businessId}`)
        if (!response.ok) throw new Error('Positioning not found')
        const data = await response.json()
        setPositioning(data)
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Unknown error')
      } finally {
        setLoading(false)
      }
    }

    fetchPositioning()
  }, [businessId])

  return { positioning, loading, error }
}

// ==================== ICP HOOKS ====================

export function useICPStream(businessId: string) {
  const [progress, setProgress] = useState(0)
  const [stage, setStage] = useState('')
  const [status, setStatus] = useState('idle')
  const [icps, setICPs] = useState<ICPPersona[]>([])
  const [error, setError] = useState<string | null>(null)
  const wsRef = useRef<WebSocket | null>(null)

  const startGeneration = useCallback(() => {
    if (!businessId) return

    const wsUrl = `${API_URL.replace('http', 'ws')}/api/icps/${businessId}`

    const ws = new WebSocket(wsUrl)

    ws.onopen = () => {
      setStatus('running')
      setError(null)
    }

    ws.onmessage = (event) => {
      const update = JSON.parse(event.data)
      setStage(update.stage)
      setProgress(update.progress || 0)
      setStatus(update.status)
      if (update.data?.icps) {
        setICPs(update.data.icps)
      }
    }

    ws.onerror = () => {
      setError('WebSocket error')
      setStatus('failed')
    }

    ws.onclose = () => {
      setStatus('completed')
    }

    wsRef.current = ws
  }, [businessId])

  const stop = useCallback(() => {
    if (wsRef.current) {
      wsRef.current.close()
    }
  }, [])

  return { startGeneration, stop, progress, stage, status, icps, error }
}

export function useFetchICPs(businessId: string) {
  const [icps, setICPs] = useState<ICPPersona[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!businessId) return

    const fetchICPs = async () => {
      try {
        const response = await fetch(`${API_URL}/api/icps/${businessId}`)
        if (!response.ok) throw new Error('ICPs not found')
        const data = await response.json()
        setICPs(data.icps || [])
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Unknown error')
      } finally {
        setLoading(false)
      }
    }

    fetchICPs()
  }, [businessId])

  return { icps, loading, error }
}

// ==================== PAYMENT HOOKS ====================

export function usePaymentCheckout() {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const createCheckout = useCallback(
    async (businessId: string, tier: 'basic' | 'pro' | 'enterprise') => {
      setLoading(true)
      setError(null)

      try {
        const response = await fetch(`${API_URL}/api/payment/checkout`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ business_id: businessId, tier }),
        })

        if (!response.ok) throw new Error('Failed to create checkout')

        return await response.json()

      } catch (err) {
        const message = err instanceof Error ? err.message : 'Unknown error'
        setError(message)
        throw err
      } finally {
        setLoading(false)
      }
    },
    []
  )

  return { createCheckout, loading, error }
}

// ==================== SUBSCRIPTION HOOKS ====================

export function useFetchSubscription(businessId: string) {
  const [subscription, setSubscription] = useState<Subscription | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!businessId) return

    const fetchSubscription = async () => {
      try {
        const response = await fetch(`${API_URL}/api/subscription/${businessId}`)
        if (!response.ok) throw new Error('Subscription not found')
        const data = await response.json()
        setSubscription(data)
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Unknown error')
      } finally {
        setLoading(false)
      }
    }

    fetchSubscription()
  }, [businessId])

  return { subscription, loading, error }
}
