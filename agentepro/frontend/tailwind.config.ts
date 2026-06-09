import type { Config } from 'tailwindcss'

// Los colores referencian variables CSS (definidas en index.css) en formato de
// canales "R G B", por eso usamos rgb(var(--x) / <alpha-value>): así siguen
// funcionando los modificadores de opacidad de Tailwind (ej. bg-primary/10).
// Esto habilita modo claro/oscuro y color de marca por cliente sin recompilar.
const c = (v: string) => `rgb(var(${v}) / <alpha-value>)`

const config: Config = {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        background: c('--background'),
        surface: c('--surface'),
        card: c('--card'),
        border: c('--border'),
        primary: c('--primary'),
        secondary: c('--secondary'),
        warning: c('--warning'),
        'text-primary': c('--text-primary'),
        'text-secondary': c('--text-secondary'),
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
        heading: ['Syne', 'sans-serif'],
      },
      keyframes: {
        'fade-in': {
          from: { opacity: '0', transform: 'translateY(4px)' },
          to: { opacity: '1', transform: 'translateY(0)' },
        },
        shimmer: {
          '100%': { transform: 'translateX(100%)' },
        },
        /* ── Reflejo del marco de vidrio del celular (.glass-phone) ── */
        'shimmer-glass': {
          '0%':   { transform: 'translateX(-100%) rotate(-45deg)' },
          '100%': { transform: 'translateX(200%) rotate(-45deg)' },
        },
        /* ── Onda de voz (pantalla de llamada de la demo) ── */
        'voice-bar-1': {
          '0%, 100%': { height: '8px' },
          '25%': { height: '28px' },
          '50%': { height: '14px' },
          '75%': { height: '32px' },
        },
        'voice-bar-2': {
          '0%, 100%': { height: '12px' },
          '30%': { height: '34px' },
          '60%': { height: '10px' },
          '85%': { height: '24px' },
        },
        'voice-bar-3': {
          '0%, 100%': { height: '6px' },
          '20%': { height: '22px' },
          '45%': { height: '36px' },
          '70%': { height: '16px' },
        },
      },
      animation: {
        'fade-in': 'fade-in 0.3s ease-out',
        shimmer: 'shimmer 1.6s infinite',
        'shimmer-glass': 'shimmer-glass 4s ease-in-out infinite',
        'voice-bar-1': 'voice-bar-1 1.1s ease-in-out infinite',
        'voice-bar-2': 'voice-bar-2 0.9s ease-in-out infinite',
        'voice-bar-3': 'voice-bar-3 1.3s ease-in-out infinite',
      },
    },
  },
  plugins: [],
}

export default config
