'use client'

import React, { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { useAuth } from '@/context/AuthContext'
import { GoogleLoginButton } from '@/components/auth/GoogleLoginButton'
import { motion } from 'framer-motion'

export default function LoginPage() {
  const { isAuthenticated, loading } = useAuth()
  const router = useRouter()

  useEffect(() => {
    if (!loading && isAuthenticated) {
      router.push('/dashboard')
    }
  }, [isAuthenticated, loading, router])

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-mine via-mine to-black flex items-center justify-center">
        <div className="text-center">
          <div className="w-12 h-12 border-4 border-barley border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-ink/70">Loading...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-mine via-mine to-black flex items-center justify-center p-6">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="w-full max-w-md"
      >
        {/* Logo Section */}
        <div className="text-center mb-12">
          <div className="flex items-center justify-center space-x-3 mb-6">
            <div className="w-12 h-12 bg-barley rounded-lg flex items-center justify-center">
              <span className="text-whiterock font-bold text-2xl">R</span>
            </div>
            <span className="text-whiterock font-display text-3xl">RaptorFlow</span>
          </div>
          <h1 className="text-3xl md:text-4xl font-display font-bold text-whiterock mb-3">
            Welcome Back
          </h1>
          <p className="text-ink/70">
            Sign in to your account to continue
          </p>
        </div>

        {/* Login Card */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.5, delay: 0.1 }}
          className="card p-8 mb-8"
        >
          <GoogleLoginButton />

          {/* Divider */}
          <div className="flex items-center my-8">
            <div className="flex-1 border-t border-hairline"></div>
            <span className="px-4 text-ink/50 text-sm">or</span>
            <div className="flex-1 border-t border-hairline"></div>
          </div>

          {/* Email Login (Placeholder) */}
          <div className="space-y-4">
            <div>
              <label className="block text-whiterock text-sm font-medium mb-2">
                Email Address
              </label>
              <input
                type="email"
                placeholder="you@example.com"
                className="w-full px-4 py-3 bg-mine/80 border border-hairline rounded-lg text-whiterock placeholder-ink/40 focus:outline-none focus:ring-2 focus:ring-barley transition-all"
                disabled
              />
              <p className="text-ink/50 text-xs mt-2">Coming soon - Email login</p>
            </div>
          </div>
        </motion.div>

        {/* Footer */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.5, delay: 0.2 }}
          className="text-center text-ink/50 text-sm"
        >
          <p>
            By signing in, you agree to our{' '}
            <a href="#" className="text-akaroa hover:text-barley transition-colors">
              Terms of Service
            </a>
            {' '}and{' '}
            <a href="#" className="text-akaroa hover:text-barley transition-colors">
              Privacy Policy
            </a>
          </p>
        </motion.div>
      </motion.div>
    </div>
  )
}
