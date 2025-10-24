'use client'

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react'
import Cookies from 'js-cookie'
import axios from 'axios'

export interface User {
  id: string
  email: string
  name: string
  picture?: string
  org_id: string
  role: 'owner' | 'admin' | 'editor' | 'viewer'
}

export interface AuthContextType {
  user: User | null
  token: string | null
  loading: boolean
  error: string | null
  login: (token: string, user: User) => Promise<void>
  logout: () => Promise<void>
  verifyToken: () => Promise<void>
  isAuthenticated: boolean
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [token, setToken] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  // Initialize auth from cookies and verify token on mount
  useEffect(() => {
    const initializeAuth = async () => {
      try {
        const savedToken = Cookies.get('auth_token')
        if (savedToken) {
          setToken(savedToken)
          // Configure axios default header
          axios.defaults.headers.common['Authorization'] = `Bearer ${savedToken}`
          // Verify token with backend
          await verifyTokenWithBackend(savedToken)
        }
      } catch (err) {
        console.error('Auth initialization failed:', err)
        Cookies.remove('auth_token')
        setToken(null)
        setUser(null)
      } finally {
        setLoading(false)
      }
    }

    initializeAuth()
  }, [])

  const verifyTokenWithBackend = async (authToken: string) => {
    try {
      const response = await axios.post(
        `${API_URL}/api/auth/verify-token`,
        {},
        {
          headers: { Authorization: `Bearer ${authToken}` }
        }
      )
      setUser(response.data.user)
      setError(null)
    } catch (err) {
      console.error('Token verification failed:', err)
      throw err
    }
  }

  const login = async (newToken: string, userData: User) => {
    try {
      setError(null)
      setLoading(true)
      
      // Save token to cookie (secure flag in production)
      Cookies.set('auth_token', newToken, {
        expires: 7,
        sameSite: 'Strict'
      })

      // Set axios default header
      axios.defaults.headers.common['Authorization'] = `Bearer ${newToken}`

      setToken(newToken)
      setUser(userData)
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Login failed'
      setError(errorMessage)
      throw err
    } finally {
      setLoading(false)
    }
  }

  const logout = async () => {
    try {
      setLoading(true)
      
      // Call backend logout endpoint
      await axios.post(
        `${API_URL}/api/auth/logout`,
        {},
        {
          headers: { Authorization: `Bearer ${token}` }
        }
      )
    } catch (err) {
      console.error('Logout error:', err)
    } finally {
      // Clear everything regardless of backend response
      Cookies.remove('auth_token')
      delete axios.defaults.headers.common['Authorization']
      setToken(null)
      setUser(null)
      setError(null)
      setLoading(false)
    }
  }

  const verifyToken = async () => {
    if (!token) {
      setError('No token available')
      return
    }
    await verifyTokenWithBackend(token)
  }

  const value: AuthContextType = {
    user,
    token,
    loading,
    error,
    login,
    logout,
    verifyToken,
    isAuthenticated: !!user && !!token
  }

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}
