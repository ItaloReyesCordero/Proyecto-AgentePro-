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
      },
      animation: {
        'fade-in': 'fade-in 0.3s ease-out',
        shimmer: 'shimmer 1.6s infinite',
      },
    },
  },
  plugins: [],
}

export default config
