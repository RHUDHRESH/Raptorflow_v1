'use client'

import React, { useState } from 'react'
import { GoogleOAuthProvider, GoogleLogin, CredentialResponse } from '@react-oauth/google'
import { useAuth } from '@/context/AuthContext'
import { useRouter } from 'next/navigation'
import axios from 'axios'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

function GoogleLoginButtonContent() {
  const { login } = useAuth()
  const router = useRouter()
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)

  const handleSuccess = async (credentialResponse: CredentialResponse) => {
    try {
      setError(null)
      setLoading(true)

      const idToken = credentialResponse.credential
      if (!idToken) {
        throw new Error('No credential received from Google')
      }

      // Exchange credential with backend
      const response = await axios.post(`${API_URL}/api/auth/google/callback`, {
        id_token: idToken
      })

      const { jwt_token, user } = response.data

      // Login via auth context
      await login(jwt_token, user)

      // Redirect to dashboard
      router.push('/dashboard')
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Login failed'
      setError(errorMessage)
      console.error('Login error:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleError = () => {
    setError('Login failed. Please try again.')
  }

  return (
    <div className="w-full">
      {error && (
        <div className="mb-4 p-4 bg-red-900/20 border border-red-600 rounded-lg text-red-400 text-sm">
          {error}
        </div>
      )}
      <div className="flex justify-center">
        <GoogleLogin
          onSuccess={handleSuccess}
          onError={handleError}
          text="signin_with"
          width="300"
        />
      </div>
    </div>
  )
}

export function GoogleLoginButton() {
  const googleClientId = process.env.NEXT_PUBLIC_GOOGLE_CLIENT_ID
  
  if (!googleClientId) {
    return (
      <div className="p-4 bg-red-900/20 border border-red-600 rounded-lg text-red-400 text-sm">
        Google Client ID is not configured. Please check your environment variables.
      </div>
    )
  }

  return (
    <GoogleOAuthProvider clientId={googleClientId}>
      <GoogleLoginButtonContent />
    </GoogleOAuthProvider>
  )
}
