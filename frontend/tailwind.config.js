/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        mine: '#2D2D2D',
        akaroa: '#D7C9AE',
        barley: '#A68763',
        whiterock: '#EAE0D2',
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      },
      fontSize: {
        display: ['40px', { lineHeight: '1.15' }],
        h1: ['32px', { lineHeight: '1.2' }],
        h2: ['24px', { lineHeight: '1.25' }],
        body: ['17px', { lineHeight: '1.6' }],
      },
      maxWidth: {
        content: '1140px',
        message: '720px',
      },
      spacing: {
        // 8pt grid
        ...Array.from({ length: 100 }, (_, i) => i * 8).reduce((acc, val) => {
          acc[val] = `${val}px`;
          return acc;
        }, {}),
      },
      backdropBlur: {
        xs: '2px',
        sm: '4px',
        DEFAULT: '8px',
        md: '10px',
        lg: '12px',
      },
      boxShadow: {
        card: '0 10px 30px rgba(0,0,0,.35), inset 0 1px 0 rgba(255,255,255,.04)',
        'card-hover': '0 16px 40px rgba(0,0,0,.45), inset 0 1px 0 rgba(255,255,255,.06)',
        focus: '0 0 0 2px var(--barley), 0 0 0 8px var(--glow)',
      },
      keyframes: {
        floatIn: {
          from: { opacity: '0', transform: 'translateY(8px) scale(.99)', filter: 'blur(4px)' },
          to: { opacity: '1', transform: 'translateY(0) scale(1)', filter: 'blur(0)' },
        },
        shimmer: {
          '0%': { backgroundPosition: '-200% 0' },
          '100%': { backgroundPosition: '200% 0' },
        },
        breathe: {
          '0%, 100%': { boxShadow: '0 0 0 2px var(--barley), 0 0 0 8px var(--glow)' },
          '50%': { boxShadow: '0 0 0 2px rgba(166,135,99,.6), 0 0 0 10px rgba(166,135,99,.26)' },
        },
        dots: {
          '0%': { opacity: '.2', transform: 'translateY(0)' },
          '50%': { opacity: '1', transform: 'translateY(-2px)' },
          '100%': { opacity: '.2', transform: 'translateY(0)' },
        },
        pulse: {
          '0%, 100%': { opacity: '0.18' },
          '50%': { opacity: '0.22' },
        },
      },
      animation: {
        floatIn: 'floatIn .22s cubic-bezier(.22,.61,.36,1) both',
        shimmer: 'shimmer 1.2s linear infinite',
        breathe: 'breathe 6s ease-in-out infinite',
        dots: 'dots .9s ease-in-out infinite',
        'dots-delay-1': 'dots .9s ease-in-out infinite .15s',
        'dots-delay-2': 'dots .9s ease-in-out infinite .3s',
        pulse: 'pulse 6s ease-in-out infinite',
      },
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
    require('@tailwindcss/typography'),
  ],
}
