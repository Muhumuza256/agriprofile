/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        primary: {
          900: '#1B4332', 800: '#1F5239', 700: '#2D6A4F',
          600: '#3A7D5E', 500: '#40916C', 300: '#74C69D',
          200: '#B7E4C7', 100: '#D8F3DC',
        },
        accent: { 700: '#B45309', 500: '#D97706', 100: '#FEF3C7' },
      },
    },
  },
  plugins: [],
}
