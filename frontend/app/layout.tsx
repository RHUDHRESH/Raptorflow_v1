import type { Metadata } from 'next'
import { Inter, Space_Grotesk } from 'next/font/google'
import '../styles/globals.css'

const inter = Inter({ subsets: ['latin'], variable: '--font-inter' })
const spaceGrotesk = Space_Grotesk({ subsets: ['latin'], variable: '--font-space-grotesk' })

export const metadata: Metadata = {
  title: 'RaptorFlow ADAPT - AI Marketing Intelligence',
  description: 'Transform your marketing strategy with AI-powered insights, automated campaigns, and real-time analytics.',
  keywords: ['AI marketing', 'marketing automation', 'campaign optimization', 'marketing intelligence'],
  authors: [{ name: 'RaptorFlow' }],
  openGraph: {
    title: 'RaptorFlow ADAPT',
    description: 'AI-powered marketing strategy platform',
    type: 'website',
    locale: 'en_US',
  },
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" className={`${inter.variable} ${spaceGrotesk.variable}`}>
      <body className="font-sans antialiased">
        <div className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-slate-50">
          {children}
        </div>
        <div id="modal-root" />
      </body>
    </html>
  )
}
