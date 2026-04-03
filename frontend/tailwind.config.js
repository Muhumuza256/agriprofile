/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        primary: {
          900: '#1B4332',
          700: '#2D6A4F',
          500: '#40916C',
          200: '#B7E4C7',
          50:  '#D8F3DC',
        },
        accent: {
          700: '#B45309',
          500: '#D97706',
          100: '#FEF3C7',
        },
        band: {
          platinum: '#7C3AED',
          gold:     '#D97706',
          silver:   '#6B7280',
          bronze:   '#B45309',
          unscored: '#9CA3AF',
        },
      },
      fontFamily: {
        display: ['IBM Plex Sans', 'sans-serif'],
        body:    ['Inter', 'sans-serif'],
        mono:    ['IBM Plex Mono', 'monospace'],
      },
    },
  },
  plugins: [],
}
