'use client'

import React from 'react'
import { useRouter } from 'next/navigation'
import { useAuth } from '@/context/AuthContext'
import { motion } from 'framer-motion'

export default function AccountPage() {
  const { user, logout, loading } = useAuth()
  const router = useRouter()
  const [loggingOut, setLoggingOut] = React.useState(false)

  const handleLogout = async () => {
    try {
      setLoggingOut(true)
      await logout()
      router.push('/auth/login')
    } catch (err) {
      console.error('Logout failed:', err)
      setLoggingOut(false)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="w-12 h-12 border-4 border-barley border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-ink/70">Loading account...</p>
        </div>
      </div>
    )
  }

  if (!user) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <p className="text-ink/70">User not found</p>
      </div>
    )
  }

  return (
    <div className="py-12 px-6">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="max-w-2xl mx-auto"
      >
        <h1 className="text-4xl font-display font-bold text-whiterock mb-8">Account Settings</h1>

        {/* Profile Card */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.5, delay: 0.1 }}
          className="card p-8 mb-8"
        >
          <h2 className="text-2xl font-display font-bold text-whiterock mb-6">Profile Information</h2>
          
          <div className="flex items-center mb-8">
            <div className="w-20 h-20 bg-barley/20 rounded-full flex items-center justify-center mr-6">
              {user.picture ? (
                <img
                  src={user.picture}
                  alt={user.name}
                  className="w-20 h-20 rounded-full object-cover"
                />
              ) : (
                <span className="text-3xl">👤</span>
              )}
            </div>
            <div>
              <h3 className="text-xl font-semibold text-whiterock">{user.name}</h3>
              <p className="text-ink/70">{user.email}</p>
              <span className="inline-block mt-2 px-3 py-1 bg-barley/20 rounded-full text-sm text-akaroa capitalize">
                {user.role}
              </span>
            </div>
          </div>

          <div className="space-y-4 border-t border-hairline pt-8">
            <div>
              <label className="block text-ink/50 text-sm mb-2">User ID</label>
              <input
                type="text"
                value={user.id}
                readOnly
                className="w-full px-4 py-2 bg-mine/80 border border-hairline rounded-lg text-whiterock/70 font-mono text-sm"
              />
            </div>
            <div>
              <label className="block text-ink/50 text-sm mb-2">Organization ID</label>
              <input
                type="text"
                value={user.org_id}
                readOnly
                className="w-full px-4 py-2 bg-mine/80 border border-hairline rounded-lg text-whiterock/70 font-mono text-sm"
              />
            </div>
            <div>
              <label className="block text-ink/50 text-sm mb-2">Email Address</label>
              <input
                type="email"
                value={user.email}
                readOnly
                className="w-full px-4 py-2 bg-mine/80 border border-hairline rounded-lg text-whiterock/70"
              />
            </div>
            <div>
              <label className="block text-ink/50 text-sm mb-2">Role</label>
              <input
                type="text"
                value={user.role.charAt(0).toUpperCase() + user.role.slice(1)}
                readOnly
                className="w-full px-4 py-2 bg-mine/80 border border-hairline rounded-lg text-whiterock/70"
              />
            </div>
          </div>
        </motion.div>

        {/* Security Settings */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.5, delay: 0.2 }}
          className="card p-8 mb-8"
        >
          <h2 className="text-2xl font-display font-bold text-whiterock mb-6">Security</h2>
          
          <div className="space-y-4">
            <div className="flex items-center justify-between p-4 bg-mine/80 rounded-lg">
              <div>
                <h3 className="text-whiterock font-semibold">Authentication Method</h3>
                <p className="text-ink/70 text-sm">Google OAuth</p>
              </div>
              <span className="px-3 py-1 bg-green-900/20 border border-green-600 rounded-full text-green-400 text-sm">
                Connected
              </span>
            </div>

            <div className="p-4 bg-mine/80 rounded-lg">
              <h3 className="text-whiterock font-semibold mb-2">Session</h3>
              <p className="text-ink/70 text-sm mb-4">
                You are currently logged in. Your session will expire after 7 days of inactivity.
              </p>
              <button
                onClick={handleLogout}
                disabled={loggingOut}
                className="px-4 py-2 bg-red-900/20 border border-red-600 rounded-lg text-red-400 hover:bg-red-900/30 transition-colors disabled:opacity-50"
              >
                {loggingOut ? 'Signing out...' : 'Sign out from this session'}
              </button>
            </div>
          </div>
        </motion.div>

        {/* Logout Section */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.5, delay: 0.3 }}
          className="card p-8 border-red-900/20"
        >
          <h2 className="text-2xl font-display font-bold text-whiterock mb-4">Danger Zone</h2>
          <p className="text-ink/70 mb-6">
            Logging out will end your current session and you'll need to sign in again to access your account.
          </p>
          <button
            onClick={handleLogout}
            disabled={loggingOut}
            className="px-6 py-3 bg-red-900/20 border border-red-600 rounded-lg text-red-400 hover:bg-red-900/30 transition-colors font-semibold disabled:opacity-50"
          >
            {loggingOut ? 'Logging out...' : 'Logout from Account'}
          </button>
        </motion.div>
      </motion.div>
    </div>
  )
}
