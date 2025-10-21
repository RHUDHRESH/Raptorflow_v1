import type { Config } from 'tailwindcss'

const config: Config = {
  content: [
    './app/**/*.{ts,tsx}',
    './components/**/*.{ts,tsx}',
    './pages/**/*.{ts,tsx}'
  ],
  theme: {
    extend: {
      colors: {
        mine: '#2D2D2D',
        akaroa: '#D7C9AE',
        barley: '#A68763',
        whiterock: '#EAE0D2',
        ink: 'rgba(234, 224, 210, .92)',
        hairline: 'rgba(215, 201, 174, .16)',
        panel: 'rgba(255, 255, 255, .03)',
        glow: 'rgba(166, 135, 99, .18)',
      },
      fontFamily: {
        sans: ['var(--font-inter)', 'system-ui', 'sans-serif'],
        display: ['var(--font-space-grotesk)', 'system-ui', 'sans-serif'],
      },
      animation: {
        'floatIn': 'floatIn 0.6s ease-out forwards',
        'shimmer': 'shimmer 2s linear infinite',
        'breathe': 'breathe 4s ease-in-out infinite',
        'slideUp': 'slideUp 0.3s ease-out',
        'slideDown': 'slideDown 0.3s ease-out',
        'scaleIn': 'scaleIn 0.2s ease-out',
        'pulse-glow': 'pulseGlow 2s ease-in-out infinite',
      },
      keyframes: {
        floatIn: {
          '0%': { opacity: '0', transform: 'translateY(20px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        shimmer: {
          '0%': { backgroundPosition: '200% 0' },
          '100%': { backgroundPosition: '-200% 0' },
        },
        breathe: {
          '0%, 100%': { opacity: '1' },
          '50%': { opacity: '0.7' },
        },
        slideUp: {
          '0%': { opacity: '0', transform: 'translateY(10px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        slideDown: {
          '0%': { opacity: '0', transform: 'translateY(-10px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        scaleIn: {
          '0%': { opacity: '0', transform: 'scale(0.95)' },
          '100%': { opacity: '1', transform: 'scale(1)' },
        },
        pulseGlow: {
          '0%, 100%': { boxShadow: '0 0 20px rgba(166, 135, 99, 0.3)' },
          '50%': { boxShadow: '0 0 40px rgba(166, 135, 99, 0.5)' },
        },
      },
      boxShadow: {
        'card': '0 4px 20px rgba(0, 0, 0, 0.1), 0 1px 3px rgba(0, 0, 0, 0.05)',
        'card-hover': '0 8px 30px rgba(0, 0, 0, 0.15), 0 2px 6px rgba(0, 0, 0, 0.08)',
        'focus': '0 0 0 1px rgba(166, 135, 99, 0.3), 0 0 20px rgba(166, 135, 99, 0.2)',
        'glow': '0 0 40px rgba(166, 135, 99, 0.3)',
      },
      backdropBlur: {
        xs: '2px',
      },
      spacing: {
        '18': '4.5rem',
        '88': '22rem',
        '128': '32rem',
      },
      borderRadius: {
        '4xl': '2rem',
      },
      gradientColorStops: {
        'barley/10': 'rgba(166, 135, 99, 0.1)',
        'barley/20': 'rgba(166, 135, 99, 0.2)',
        'akaroa/10': 'rgba(215, 201, 174, 0.1)',
        'akaroa/20': 'rgba(215, 201, 174, 0.2)',
      },
    },
  },
  plugins: [],
}

export default config
